"""Dispatch and append-only tracking records for cargo consignments."""
# ruff: noqa: I001
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CargoDispatch(Base):
    __tablename__ = "cargo_dispatches"
    __table_args__ = (
        UniqueConstraint("consignment_id", "dispatch_reference", name="uq_cargo_dispatch_reference"),
        UniqueConstraint("consignment_id", "idempotency_key", name="uq_cargo_dispatch_idempotency"),
        CheckConstraint("status IN ('offered','accepted','rejected','picked_up','in_transit','delivered','failed','cancelled')", name="ck_cargo_dispatch_status"),
        Index("ix_cargo_dispatch_carrier_status", "carrier_organization_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    consignment_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False)
    dispatch_reference: Mapped[str] = mapped_column(String(80), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    carrier_organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False)
    vehicle_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="offered", server_default="offered")
    offered_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False)
    responded_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CargoTrackingEvent(Base):
    __tablename__ = "cargo_tracking_events"
    __table_args__ = (
        UniqueConstraint("dispatch_id", "idempotency_key", name="uq_cargo_tracking_idempotency"),
        UniqueConstraint("dispatch_id", "sequence_number", name="uq_cargo_tracking_sequence"),
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="ck_cargo_tracking_latitude"),
        CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="ck_cargo_tracking_longitude"),
        Index("ix_cargo_tracking_consignment_occurred", "consignment_id", "occurred_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    dispatch_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False)
    consignment_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    recorded_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False)
