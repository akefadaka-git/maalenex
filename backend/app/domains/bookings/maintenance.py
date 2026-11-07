from datetime import timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.bookings.models import (
    Booking, BookingAccessChallenge, GuestAccessRateLimit, IdempotencyRecord,
    SeatAllocation, SeatHold,
)
from app.domains.reservations.models import BookingAccessGrant


def expire_stale_holds(db: Session, *, batch_size: int = 500) -> int:
    if not 1 <= batch_size <= 5000:
        raise ValueError("batch_size must be between 1 and 5000")
    now = db.scalar(select(func.now()))
    holds = list(db.scalars(
        select(SeatHold).where(
            SeatHold.status == "active",
            SeatHold.expires_at <= now,
        ).order_by(SeatHold.expires_at, SeatHold.id)
        .limit(batch_size).with_for_update(skip_locked=True)
    ))
    if not holds:
        return 0
    hold_ids = [item.id for item in holds]
    booking_ids = sorted({item.booking_id for item in holds}, key=str)
    db.execute(update(SeatHold).where(SeatHold.id.in_(hold_ids)).values(
        status="expired", released_at=now, release_reason="hold_expired",
    ))
    db.execute(update(SeatAllocation).where(
        SeatAllocation.booking_id.in_(booking_ids),
        SeatAllocation.status == "active",
        SeatAllocation.trip_seat_id.in_([item.trip_seat_id for item in holds]),
    ).values(status="expired", released_at=now))
    bookings = list(db.scalars(select(Booking).where(
        Booking.id.in_(booking_ids), Booking.status == "held",
        Booking.expires_at <= now,
    ).with_for_update()))
    for booking in bookings:
        booking.status = "expired"
        booking.version += 1
        record_event(
            db, event_type="booking.hold.expired", actor_type="system",
            actor_id=None, resource_type="booking", resource_id=str(booking.id),
            action="expire_hold", outcome="success",
            metadata={"expired_seat_count": sum(1 for h in holds if h.booking_id == booking.id)},
        )
    return len(holds)


def purge_expired_ephemeral_records(db: Session) -> dict[str, int]:
    now = db.scalar(select(func.now()))
    challenge_cutoff = now - timedelta(days=1)
    grant_cutoff = now - timedelta(days=30)
    rate_limit_cutoff = now - timedelta(days=30)
    idempotency_result = db.execute(delete(IdempotencyRecord).where(
        IdempotencyRecord.expires_at <= now,
    ))
    challenge_result = db.execute(delete(BookingAccessChallenge).where(
        (BookingAccessChallenge.expires_at <= challenge_cutoff)
        | (BookingAccessChallenge.consumed_at <= challenge_cutoff),
    ))
    grant_result = db.execute(delete(BookingAccessGrant).where(
        (BookingAccessGrant.expires_at <= grant_cutoff)
        | (BookingAccessGrant.revoked_at <= grant_cutoff),
    ))
    rate_limit_result = db.execute(delete(GuestAccessRateLimit).where(
        GuestAccessRateLimit.window_started_at <= rate_limit_cutoff,
    ))
    return {
        "idempotency_records": idempotency_result.rowcount or 0,
        "access_challenges": challenge_result.rowcount or 0,
        "access_grants": grant_result.rowcount or 0,
        "guest_rate_limits": rate_limit_result.rowcount or 0,
    }


def run_booking_maintenance(db: Session, *, batch_size: int = 500) -> dict:
    expired_holds = expire_stale_holds(db, batch_size=batch_size)
    purged = purge_expired_ephemeral_records(db)
    db.commit()
    return {"expired_holds": expired_holds, "purged": purged}
