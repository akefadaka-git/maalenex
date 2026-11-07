from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class Schedule(Base):
    __tablename__ = "schedules"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    route_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("routes.id", ondelete="RESTRICT"))
    boarding_terminal_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("terminals.id", ondelete="RESTRICT"))
    departure_rule: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="draft")
class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    route_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("routes.id", ondelete="RESTRICT"))
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
