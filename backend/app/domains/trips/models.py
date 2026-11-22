from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Schedule(Base):
    __tablename__ = "schedules"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    route_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("routes.id", ondelete="RESTRICT"))
    departure_rule: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="draft")
class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    route_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("routes.id", ondelete="RESTRICT"))
    boarding_terminal_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("terminals.id", ondelete="RESTRICT"))
    schedule_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("schedules.id", ondelete="SET NULL"), nullable=True)
    vehicle_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"))
    seat_layout_version_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("seat_layout_versions.id", ondelete="RESTRICT"))
    departure_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    arrival_estimate_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
class TripSeat(Base):
    __tablename__ = "trip_seats"
    __table_args__ = (UniqueConstraint("trip_id", "vehicle_seat_id", name="uq_trip_vehicle_seat"),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    vehicle_seat_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("vehicle_seats.id", ondelete="RESTRICT"))
    seat_code_snapshot: Mapped[str] = mapped_column(String(16))
    sellable_status: Mapped[str] = mapped_column(String(24), default="sellable")


class TripOperationalException(Base):
    __tablename__ = "trip_operational_exceptions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True,
    )
    category: Mapped[str] = mapped_column(String(40), index=True)
    severity: Mapped[str] = mapped_column(String(16), default="normal")
    description: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(24), default="open", index=True)
    created_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    reviewed_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True,
    )
    resolution: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
