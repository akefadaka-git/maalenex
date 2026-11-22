"""Typed, fail-closed MaaleNex integration boundary for IROKA.

This module intentionally contains no network transport until IROKA publishes
and verifies a deployed service contract and service-credential profile.
"""
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


DecisionCode = Literal["ALLOW", "DENY", "REQUIRE_APPROVAL", "ESCALATE"]
DataClassification = Literal["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"]


class IrokaContractError(ValueError):
    """Raised when an IROKA contract envelope is internally inconsistent."""


class IrokaUnavailableError(RuntimeError):
    """Raised when the IROKA service is disabled or cannot be trusted."""


class IrokaAuthorizationRequest(BaseModel):
    """Minimized, authenticated-context request; never accepts caller authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_id: Literal["MN-IROKA-IFACE-001"] = "MN-IROKA-IFACE-001"
    contract_version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID
    correlation_id: UUID
    tenant_id: str | None = Field(default=None, min_length=1, max_length=128)
    actor_subject: str = Field(min_length=1, max_length=128)
    capability: str = Field(min_length=3, max_length=120, pattern=r"^[a-z][a-z0-9_.-]+$")
    resource: str = Field(min_length=3, max_length=240)
    policy_version: str = Field(min_length=1, max_length=64)
    requested_at: datetime
    data_classification: DataClassification
    context: dict[str, str | int | bool | None] = Field(default_factory=dict)

    @field_validator("requested_at")
    @classmethod
    def require_aware_utc_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("requested_at must be timezone-aware")
        return value.astimezone(UTC)


class IrokaDecisionEnvelope(BaseModel):
    """Decision evidence bound to one exact request and policy snapshot."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_id: Literal["MN-IROKA-IFACE-001"]
    contract_version: Literal["1.0.0"]
    request_id: UUID
    correlation_id: UUID
    tenant_id: str | None
    actor_subject: str
    capability: str
    resource: str
    policy_version: str
    decision_id: str = Field(min_length=1, max_length=128)
    decision: DecisionCode
    reason_code: str = Field(min_length=1, max_length=120)
    issued_at: datetime
    expires_at: datetime
    audit_receipt_id: str = Field(min_length=1, max_length=128)
    evidence_refs: tuple[str, ...] = ()

    @field_validator("issued_at", "expires_at")
    @classmethod
    def require_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("decision timestamps must be timezone-aware")
        return value.astimezone(UTC)

    def validate_binding(
        self, request: IrokaAuthorizationRequest, *, now: datetime | None = None
    ) -> None:
        """Reject cross-request, cross-tenant, stale-policy and expired decisions."""
        bindings = (
            "contract_id",
            "contract_version",
            "request_id",
            "correlation_id",
            "tenant_id",
            "actor_subject",
            "capability",
            "resource",
            "policy_version",
        )
        if any(getattr(self, field) != getattr(request, field) for field in bindings):
            raise IrokaContractError("IROKA decision does not bind to the original request")
        instant = (now or datetime.now(UTC)).astimezone(UTC)
        if self.issued_at > instant or self.expires_at <= instant:
            raise IrokaContractError("IROKA decision is not currently valid")
        if self.expires_at <= self.issued_at:
            raise IrokaContractError("IROKA decision expiry must follow issuance")
        if not self.audit_receipt_id:
            raise IrokaContractError("IROKA decision requires an audit receipt")


class IrokaDecisionGateway(Protocol):
    """Transport-independent boundary; implementations must verify service identity."""

    def decide(self, request: IrokaAuthorizationRequest) -> IrokaDecisionEnvelope:
        """Return authenticated decision evidence or raise IrokaUnavailableError."""


class DisabledIrokaGateway:
    """Default gateway until a reviewed IROKA service binding is provisioned."""

    def decide(self, request: IrokaAuthorizationRequest) -> IrokaDecisionEnvelope:
        del request
        raise IrokaUnavailableError(
            "IROKA integration is not enabled: no verified service endpoint and trust profile"
        )
