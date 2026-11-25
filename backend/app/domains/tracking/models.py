from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrackingDevice(Base):
    __tablename__ = "tracking_devices"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    device_identifier: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    credential_ciphertext: Mapped[str] = mapped_column(String(512))
    credential_version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    last_sequence: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class VehicleDeviceAssignment(Base):
    __tablename__ = "vehicle_device_assignments"
    __table_args__ = (
        Index(
            "uq_active_device_assignment_device", "device_id", unique=True,
            postgresql_where=text("unassigned_at IS NULL"),
        ),
        Index(
            "uq_active_device_assignment_vehicle", "vehicle_id", unique=True,
            postgresql_where=text("unassigned_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tracking_devices.id", ondelete="RESTRICT"), index=True
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), index=True
    )
    assigned_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    unassigned_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    unassigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class VehicleTelemetry(Base):
    __tablename__ = "vehicle_telemetry"
    __table_args__ = (
        UniqueConstraint("device_id", "sequence", name="uq_vehicle_telemetry_device_sequence"),
        Index("ix_vehicle_telemetry_vehicle_recorded", "vehicle_id", "recorded_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tracking_devices.id", ondelete="RESTRICT"), index=True
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    latitude: Mapped[float] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float] = mapped_column(Numeric(10, 7))
    speed_kph: Mapped[float] = mapped_column(Numeric(6, 2))
    heading_degrees: Mapped[float] = mapped_column(Numeric(6, 2))
    accuracy_meters: Mapped[float] = mapped_column(Numeric(7, 2))
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
