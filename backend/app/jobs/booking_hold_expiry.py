"""Concurrent-safe expiry worker for unconfirmed passenger seat holds."""
# ruff: noqa: I001
from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domains.audit.service import record_event
from app.domains.bookings.models import Booking, SeatAllocation, SeatHold
from app.domains.bookings.service import _notify_booking_status

def expire_due_booking_holds(db: Session, *, batch_size: int = 100) -> int:
    """Expire a bounded batch; SKIP LOCKED permits concurrent worker instances."""
    now = datetime.now(UTC)
    due = list(db.scalars(
        select(Booking).where(Booking.status == "held", Booking.expires_at.is_not(None), Booking.expires_at <= now)
        .order_by(Booking.expires_at, Booking.id).limit(batch_size).with_for_update(skip_locked=True)
    ))
    for booking in due:
        holds = list(db.scalars(select(SeatHold).where(
            SeatHold.booking_id == booking.id, SeatHold.status == "active"
        ).with_for_update()))
        for hold in holds:
            hold.status = "expired"; hold.released_at = now; hold.release_reason = "hold_expired"
        allocations = list(db.scalars(select(SeatAllocation).where(
            SeatAllocation.booking_id == booking.id, SeatAllocation.status == "active"
        ).with_for_update()))
        for allocation in allocations:
            allocation.status = "expired"; allocation.released_at = now
        booking.status = "expired"; booking.version += 1
        record_event(db, event_type="booking.hold.expired", actor_type="system", actor_id=None,
            resource_type="booking", resource_id=str(booking.id), action="expire_hold", outcome="success",
            metadata={"released_holds": len(holds), "released_allocations": len(allocations)})
        _notify_booking_status(db, booking, "expired")
    db.flush()
    return len(due)
