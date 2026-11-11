from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class MoveRide(Base):
    __tablename__ = "move_rides"
    __table_args__ = (
        CheckConstraint("status IN ('requested', 'matched', 'accepted', 'arrived', 'in_progress', 'completed', 'cancelled')", name="ck_move_ride_status"),
        CheckConstraint("driver_account_id IS NULL OR driver_account_id <> passenger_account_id", name="ck_move_ride_distinct_participants"),
        CheckConstraint("status IN ('requested', 'cancelled') OR driver_account_id IS NOT NULL", name="ck_move_ride_driver_required"),
        CheckConstraint("completed_at IS NULL OR status = 'completed'", name="ck_move_ride_completed_timestamp"),
        CheckConstraint("cancelled_at IS NULL OR status = 'cancelled'", name="ck_move_ride_cancelled_timestamp"),
        Index("ix_move_rides_passenger_status", "passenger_account_id", "status"),
        Index("ix_move_rides_driver_status", "driver_account_id", "status"),
    )
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    service_code: Mapped[str] = mapped_column(String(32), ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False, default="move", server_default="move")
    passenger_account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="RESTRICT"), nullable=False)
    driver_account_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="RESTRICT"), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="requested", server_default="requested")
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    matched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
