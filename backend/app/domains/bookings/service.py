from datetime import timedelta
from secrets import token_urlsafe
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.bookings.models import (
    Booking, BookingContact, BookingFareSnapshot, BookingPassenger,
    Passenger, SeatAllocation, SeatHold,
)
from app.domains.fares.models import Fare, FareVersion
from app.domains.reservations.models import ReservationReference
from app.domains.trips.models import Trip, TripSeat


class BookingConflict(Exception):
    """A booking precondition or inventory invariant was not satisfied."""


def create_seat_hold(
    db: Session, *, trip_id: UUID, contact_name: str, contact_phone: str,
    passengers: list[dict[str, str]], seat_ids: list[UUID], hold_minutes: int = 10,
) -> Booking:
    if not passengers or len(passengers) != len(seat_ids):
        raise ValueError("Each passenger must be assigned exactly one distinct seat.")
    if len(set(seat_ids)) != len(seat_ids):
        raise ValueError("A seat may only be requested once per booking.")
    if not 1 <= hold_minutes <= 10:
        raise ValueError("Synthetic hold duration must be between 1 and 10 minutes.")
    name = " ".join(contact_name.split())
    phone = "".join(ch for ch in contact_phone if ch.isdigit() or ch == "+")
    if not name or not phone or len(name) > 160 or len(phone) > 32:
        raise ValueError("A valid booking contact name and phone are required.")

    # Serialize all contenders on stable trip-seat rows, then recheck expiry and
    # allocation state inside this transaction. The caller owns commit/rollback.
    now = db.scalar(select(func.now()))
    trip = db.scalar(select(Trip).where(Trip.id == trip_id).with_for_update())
    if trip is None or trip.status != "published":
        raise BookingConflict("Trip is not available for reservation.")

    seats = list(db.scalars(
        select(TripSeat).where(TripSeat.trip_id == trip_id, TripSeat.id.in_(seat_ids))
        .order_by(TripSeat.id).with_for_update()
    ))
    if len(seats) != len(seat_ids):
        raise BookingConflict("One or more requested seats are unavailable.")
    seats_by_id = {seat.id: seat for seat in seats}
    seats = [seats_by_id[seat_id] for seat_id in seat_ids]
    if any(seat.sellable_status != "sellable" for seat in seats):
        raise BookingConflict("One or more requested seats are unavailable.")

    expired_holds = list(db.scalars(
        select(SeatHold).where(
            SeatHold.trip_id == trip_id, SeatHold.trip_seat_id.in_(seat_ids),
            SeatHold.status == "active", SeatHold.expires_at <= now,
        ).with_for_update()
    ))
    expired_booking_ids = set()
    for hold in expired_holds:
        hold.status = "expired"
        hold.released_at = now
        hold.release_reason = "hold_expired"
        expired_booking_ids.add(hold.booking_id)
    if expired_booking_ids:
        db.execute(
            update(SeatAllocation)
            .where(SeatAllocation.booking_id.in_(expired_booking_ids),
                   SeatAllocation.trip_seat_id.in_(seat_ids),
                   SeatAllocation.status == "active")
            .values(status="expired", released_at=now)
        )
        for booking_id in expired_booking_ids:
            expired_booking = db.get(Booking, booking_id)
            if expired_booking is not None and expired_booking.status == "held":
                expired_booking.status = "expired"
                expired_booking.version += 1

    allocated = set(db.scalars(
        select(SeatAllocation.trip_seat_id).where(
            SeatAllocation.trip_id == trip_id,
            SeatAllocation.trip_seat_id.in_(seat_ids),
            SeatAllocation.status == "active",
        )
    ))
    held = set(db.scalars(
        select(SeatHold.trip_seat_id).where(
            SeatHold.trip_id == trip_id,
            SeatHold.trip_seat_id.in_(seat_ids),
            SeatHold.status == "active",
            SeatHold.expires_at > now,
        )
    ))
    if allocated or held:
        raise BookingConflict("One or more requested seats are already allocated or held.")

    fare_version = db.scalar(
        select(FareVersion).join(Fare, Fare.id == FareVersion.fare_id).where(
            Fare.route_id == trip.route_id,
            or_(Fare.trip_id == trip.id, Fare.trip_id.is_(None)),
            Fare.organization_id == trip.organization_id,
            FareVersion.status == "published",
            FareVersion.currency_code == "ETB",
            FareVersion.effective_from <= now,
            or_(FareVersion.effective_to.is_(None), FareVersion.effective_to > now),
        ).order_by(Fare.trip_id.is_not(None).desc(), FareVersion.effective_from.desc())
    )
    if fare_version is None:
        raise BookingConflict("No currently published ETB fare applies to this trip.")

    contact = BookingContact(name=name, phone_normalized=phone)
    db.add(contact)
    db.flush()
    booking = Booking(
        id=uuid4(), booking_reference=token_urlsafe(12).replace("-", "").replace("_", ""),
        booking_contact_id=contact.id, trip_id=trip.id, status="held",
        currency_code="ETB", expires_at=now + timedelta(minutes=hold_minutes), version=1,
    )
    db.add(booking)
    db.flush()
    fare_snapshot = BookingFareSnapshot(
        booking_id=booking.id, fare_version_id=fare_version.id,
        amount_minor_units=fare_version.amount_minor_units * len(passengers),
        currency_code="ETB", fare_description_snapshot="Passenger fare snapshot",
    )
    db.add(fare_snapshot)

    for sequence, (passenger_data, seat) in enumerate(zip(passengers, seats), start=1):
        passenger_name = " ".join(str(passenger_data.get("name", "")).split())
        if not passenger_name or len(passenger_name) > 160:
            raise ValueError("Each passenger must have a name of at most 160 characters.")
        passenger = Passenger(display_name=passenger_name)
        db.add(passenger)
        db.flush()
        booking_passenger = BookingPassenger(
            booking_id=booking.id, passenger_id=passenger.id,
            trip_seat_id=seat.id, passenger_sequence=sequence,
        )
        db.add(booking_passenger)
        db.flush()
        db.add(SeatHold(
            booking_id=booking.id, trip_id=trip.id, trip_seat_id=seat.id,
            status="active", expires_at=booking.expires_at,
        ))
        db.add(SeatAllocation(
            booking_id=booking.id, booking_passenger_id=booking_passenger.id,
            trip_id=trip.id, trip_seat_id=seat.id, status="active",
        ))

    record_event(
        db, event_type="booking.seats.held", actor_type="guest", actor_id=None,
        resource_type="booking", resource_id=str(booking.id), action="create_hold",
        outcome="success", organization_id=trip.organization_id,
        metadata={"passenger_count": len(passengers), "hold_minutes": hold_minutes},
    )
    db.flush()
    return booking


def accept_reservation(db: Session, *, booking_id: UUID) -> ReservationReference:
    now = db.scalar(select(func.now()))
    booking = db.scalar(select(Booking).where(Booking.id == booking_id).with_for_update())
    if booking is None or booking.status != "held":
        raise BookingConflict("Booking is not in a reservable state.")
    holds = list(db.scalars(
        select(SeatHold).where(SeatHold.booking_id == booking.id).with_for_update()
    ))
    if not holds or any(h.status != "active" or h.expires_at <= now for h in holds):
        raise BookingConflict("The seat hold has expired or is incomplete.")
    allocations = list(db.scalars(
        select(SeatAllocation).where(
            SeatAllocation.booking_id == booking.id, SeatAllocation.status == "active"
        ).with_for_update()
    ))
    if len(allocations) != len(holds):
        raise BookingConflict("Seat allocation integrity check failed.")
    for hold in holds:
        hold.status = "converted"
    booking.status = "reserved"
    booking.confirmed_at = now
    booking.version += 1
    reference = ReservationReference(
        booking_id=booking.id, public_reference=token_urlsafe(24),
        qr_payload_version=1, qr_payload_reference=token_urlsafe(18), status="active",
    )
    db.add(reference)
    record_event(
        db, event_type="booking.reservation.accepted", actor_type="system",
        actor_id=None, resource_type="booking", resource_id=str(booking.id),
        action="accept_reservation", outcome="success",
        metadata={"ticket_issued": False, "payment_collected": False},
    )
    db.flush()
    return reference
