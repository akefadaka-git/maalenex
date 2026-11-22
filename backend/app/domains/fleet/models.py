from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    func,
    Integer,
    JSON,
    String,
    text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    vehicle_reference: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
    review_status: Mapped[str] = mapped_column(String(24), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
class SeatLayoutVersion(Base):
    __tablename__ = "seat_layout_versions"
    __table_args__ = (UniqueConstraint("vehicle_id", "version_number", name="uq_vehicle_layout_version"),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    vehicle_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    geometry_metadata: Mapped[dict] = mapped_column(JSON, default=dict, server_default=text("'{}'"))
class VehicleSeat(Base):
    __tablename__ = "vehicle_seats"
    __table_args__ = (UniqueConstraint("seat_layout_version_id", "seat_code", name="uq_layout_seat_code"),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    seat_layout_version_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("seat_layout_versions.id", ondelete="CASCADE"), index=True)
    seat_code: Mapped[str] = mapped_column(String(16))
    row_label: Mapped[str | None] = mapped_column(String(12), nullable=True)
    position_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    seat_type: Mapped[str] = mapped_column(String(24), default="standard")
    is_sellable: Mapped[bool] = mapped_column(Boolean, default=True)


class VehicleComplianceDocument(Base):
    __tablename__ = "vehicle_compliance_documents"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    vehicle_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), index=True,
    )
    document_type: Mapped[str] = mapped_column(String(40), index=True)
    evidence_reference: Mapped[str] = mapped_column(String(255), unique=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    submitted_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    reviewed_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True,
    )
    review_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
