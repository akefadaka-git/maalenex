"""Governed lifecycle metadata for private cargo delivery evidence."""
from calendar import monthrange
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CargoDeliveryEvidence(Base):
    __tablename__ = "cargo_delivery_evidence"
    __table_args__ = (
        UniqueConstraint("object_key", name="uq_cargo_delivery_evidence_object_key"),
        UniqueConstraint("delivery_proof_id", name="uq_cargo_delivery_evidence_proof"),
        Index("ix_cargo_delivery_evidence_dispatch_state", "dispatch_id", "lifecycle_state"),
        Index("ix_cargo_delivery_evidence_retention", "retention_expires_at", "lifecycle_state"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    carrier_organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False,
    )
    dispatch_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False,
    )
    delivery_proof_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cargo_delivery_proofs.id", ondelete="RESTRICT"),
    )
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120))
    content_length: Mapped[int | None] = mapped_column(Integer)
    upload_intent_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    upload_intent_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", server_default="pending")
    retention_policy_version: Mapped[str | None] = mapped_column(String(40))
    retention_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retention_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accounting_document: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    commercial_correspondence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    personal_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    sensitive_personal_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    accounting_record_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    correspondence_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    privacy_processing_basis: Mapped[str | None] = mapped_column(String(40))
    retention_justification: Mapped[str | None] = mapped_column(String(500))
    dpia_reference: Mapped[str | None] = mapped_column(String(160))
    rights_review_status: Mapped[str] = mapped_column(String(24), nullable=False, default="not_reviewed", server_default="not_reviewed")
    dpo_deletion_suspended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    audit_retention_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tombstone_retention_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    audit_retention_justification: Mapped[str | None] = mapped_column(String(500))
    tombstone_retention_justification: Mapped[str | None] = mapped_column(String(500))
    audit_retention_classified_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    audit_retention_reviewed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    audit_retention_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tombstone_retention_classified_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    tombstone_retention_reviewed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    tombstone_retention_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    classification_status: Mapped[str] = mapped_column(String(24), nullable=False, default="unclassified", server_default="unclassified")
    retention_legal_review_reference: Mapped[str | None] = mapped_column(String(160))
    retention_classified_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    retention_classified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retention_dpo_reviewed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    retention_dpo_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    storage_deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deletion_failure_code: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )


class CargoDeliveryEvidenceHold(Base):
    __tablename__ = "cargo_delivery_evidence_holds"
    __table_args__ = (Index("ix_cargo_evidence_hold_evidence_active", "evidence_id", "released_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    evidence_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False,
    )
    case_reference: Mapped[str] = mapped_column(String(120), nullable=False)
    legal_basis: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dpo_reviewed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    dpo_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    review_alerted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    released_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    release_note: Mapped[str | None] = mapped_column(String(500))
    release_conclusion_reference: Mapped[str | None] = mapped_column(String(160))
    release_confirmed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CargoDeliveryEvidenceDeletionRequest(Base):
    __tablename__ = "cargo_delivery_evidence_deletion_requests"
    __table_args__ = (
        Index("ix_cargo_evidence_deletion_status", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    evidence_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False,
    )
    requested_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False)
    approved_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    executed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="requested", server_default="requested")
    failure_code: Mapped[str | None] = mapped_column(String(80))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


PROVISIONAL_RETENTION_MONTHS = 24
PROVISIONAL_POLICY_VERSION = "owner-approved-provisional-24m-v1"


def add_calendar_months(value: datetime, months: int) -> datetime:
    """Add calendar months without overflowing at month-end."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))



class CargoDeliveryEvidenceAccessGrant(Base):
    __tablename__ = "cargo_delivery_evidence_access_grants"
    __table_args__ = (
        Index("ix_cargo_evidence_access_user_active", "user_id", "revoked_at", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    evidence_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False,
    )
    granted_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)



class CargoDeliveryEvidenceRetentionPolicy(Base):
    __tablename__ = "cargo_delivery_evidence_retention_policies"

    version: Mapped[str] = mapped_column(String(40), primary_key=True)
    retention_months: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="provisional")
    legal_validation_reference: Mapped[str | None] = mapped_column(String(160))
    validated_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    dpo_reviewed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    activated_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)



class CargoDeliveryEvidenceRightsRequest(Base):
    __tablename__ = "cargo_delivery_evidence_rights_requests"
    __table_args__ = (Index("ix_cargo_evidence_rights_status", "status", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    evidence_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False,
    )
    request_type: Mapped[str] = mapped_column(String(24), nullable=False)
    requested_by_reference: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", server_default="pending")
    decision: Mapped[str | None] = mapped_column(String(24))
    decision_reason: Mapped[str | None] = mapped_column(String(500))
    reviewed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
