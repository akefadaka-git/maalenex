"""Carrier operations, delivery proof and exception records."""
# ruff: noqa: I001
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CarrierOperationalProfile(Base):
    __tablename__ = "carrier_operational_profiles"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_carrier_operation_org"),
        CheckConstraint("operational_status IN ('pending','active','restricted','suspended')", name="ck_carrier_operation_status"),
        Index("ix_carrier_operation_status", "operational_status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False)
    operational_status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", server_default="pending")
    service_area: Mapped[str | None] = mapped_column(String(240), nullable=True)
    operating_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CargoDeliveryProof(Base):
    __tablename__ = "cargo_delivery_proofs"
    __table_args__ = (
        UniqueConstraint("dispatch_id", name="uq_cargo_delivery_proof_dispatch"),
        UniqueConstraint("idempotency_key", name="uq_cargo_delivery_proof_idempotency"),
        CheckConstraint("status IN ('submitted','accepted','rejected')", name="ck_cargo_delivery_proof_status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    dispatch_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False)
    consignment_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    received_by_name: Mapped[str] = mapped_column(String(160), nullable=False)
    evidence_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="submitted", server_default="submitted")
    submitted_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False)
    reviewed_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True)
    review_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CargoExceptionCase(Base):
    __tablename__ = "cargo_exception_cases"
    __table_args__ = (
        UniqueConstraint("dispatch_id", "idempotency_key", name="uq_cargo_exception_idempotency"),
        CheckConstraint("status IN ('open','investigating','resolved','closed')", name="ck_cargo_exception_status"),
        Index("ix_cargo_exception_carrier_status", "carrier_organization_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    dispatch_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False)
    consignment_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False)
    carrier_organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    exception_code: Mapped[str] = mapped_column(String(48), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="open", server_default="open")
    resolution_code: Mapped[str | None] = mapped_column(String(48), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reported_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False)
    resolved_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
