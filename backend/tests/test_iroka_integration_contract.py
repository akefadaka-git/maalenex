from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.integrations.iroka import (
    DisabledIrokaGateway,
    IrokaAuthorizationRequest,
    IrokaContractError,
    IrokaDecisionEnvelope,
    IrokaUnavailableError,
)


def request_fixture() -> IrokaAuthorizationRequest:
    return IrokaAuthorizationRequest(
        request_id=uuid4(),
        correlation_id=uuid4(),
        tenant_id="tenant-synthetic-a",
        actor_subject="staff-synthetic-1",
        capability="booking.review",
        resource="booking:synthetic-42",
        policy_version="maalenex-policy-1",
        requested_at=datetime.now(UTC),
        data_classification="CONFIDENTIAL",
        context={"risk_band": "standard", "is_synthetic": True},
    )


def decision_fixture(request: IrokaAuthorizationRequest) -> IrokaDecisionEnvelope:
    now = datetime.now(UTC)
    return IrokaDecisionEnvelope(
        contract_id=request.contract_id,
        contract_version=request.contract_version,
        request_id=request.request_id,
        correlation_id=request.correlation_id,
        tenant_id=request.tenant_id,
        actor_subject=request.actor_subject,
        capability=request.capability,
        resource=request.resource,
        policy_version=request.policy_version,
        decision_id="decision-synthetic-1",
        decision="ALLOW",
        reason_code="POLICY_EVALUATED",
        issued_at=now - timedelta(seconds=1),
        expires_at=now + timedelta(seconds=30),
        audit_receipt_id="receipt-synthetic-1",
        evidence_refs=("evidence:synthetic-1",),
    )


def test_request_is_versioned_immutable_and_serializable() -> None:
    request = request_fixture()
    wire = request.model_dump(mode="json")
    assert wire["contract_id"] == "MN-IROKA-IFACE-001"
    assert wire["contract_version"] == "1.0.0"
    assert wire["actor_subject"] == "staff-synthetic-1"
    with pytest.raises(ValidationError):
        request.capability = "booking.delete"  # type: ignore[misc]


def test_request_rejects_unknown_fields_and_naive_timestamps() -> None:
    payload = request_fixture().model_dump()
    payload["unreviewed_authority"] = True
    with pytest.raises(ValidationError):
        IrokaAuthorizationRequest.model_validate(payload)

    payload = request_fixture().model_dump()
    payload["requested_at"] = datetime(2026, 1, 1)
    with pytest.raises(ValidationError):
        IrokaAuthorizationRequest.model_validate(payload)


def test_decision_must_bind_to_exact_request_and_policy() -> None:
    request = request_fixture()
    decision = decision_fixture(request)
    decision.validate_binding(request)

    changed = request.model_copy(update={"capability": "wallet.release"})
    with pytest.raises(IrokaContractError):
        decision.validate_binding(changed)


def test_decision_expiry_is_fail_closed() -> None:
    request = request_fixture()
    decision = decision_fixture(request)
    with pytest.raises(IrokaContractError):
        decision.validate_binding(request, now=datetime.now(UTC) + timedelta(minutes=2))


def test_decision_rejects_missing_audit_receipt() -> None:
    request = request_fixture()
    payload = decision_fixture(request).model_dump()
    payload["audit_receipt_id"] = ""
    with pytest.raises(ValidationError):
        IrokaDecisionEnvelope.model_validate(payload)


def test_disabled_gateway_never_claims_allow() -> None:
    with pytest.raises(IrokaUnavailableError):
        DisabledIrokaGateway().decide(request_fixture())
