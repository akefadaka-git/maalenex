"""Authenticated passenger-owned booking management."""
# ruff: noqa: B008
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.domains.bookings.models import Booking, BookingFareSnapshot, BookingPassenger, Passenger, SeatHold
from app.domains.bookings.service import BookingConflict, cancel_unconfirmed_booking
from app.domains.identity.passenger_service import PassengerContext, verify_passenger_csrf
from app.domains.reservations.models import ReservationReference
from app.domains.trips.models import Trip, TripSeat
from app.routers.passenger_auth import current_passenger_context

router = APIRouter(prefix="/passenger/bookings", tags=["passenger-bookings"])

def _require_mutation(request: Request, context: PassengerContext) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")
    if not verify_passenger_csrf(context, cookie_token=request.cookies.get("mnm_passenger_csrf"), header_token=request.headers.get("X-CSRF-Token")):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")

def _booking_payload(db: Session, booking: Booking) -> dict:
    trip = db.get(Trip, booking.trip_id)
    fare = db.scalar(select(BookingFareSnapshot).where(BookingFareSnapshot.booking_id == booking.id))
    reservation = db.scalar(select(ReservationReference).where(
        ReservationReference.booking_id == booking.id, ReservationReference.status == "active"
    ).order_by(ReservationReference.created_at.desc()).limit(1))
    passengers = db.execute(
        select(Passenger.display_name, TripSeat.seat_code_snapshot)
        .join(BookingPassenger, BookingPassenger.passenger_id == Passenger.id)
        .join(TripSeat, TripSeat.id == BookingPassenger.trip_seat_id)
        .where(BookingPassenger.booking_id == booking.id)
        .order_by(BookingPassenger.passenger_sequence)
    ).all()
    active_holds = db.scalar(select(func.count()).select_from(SeatHold).where(
        SeatHold.booking_id == booking.id, SeatHold.status == "active"
    )) or 0
    return {
        "booking_id": str(booking.id), "booking_reference": booking.booking_reference,
        "status": booking.status, "created_at": booking.created_at.isoformat() if booking.created_at else None,
        "confirmed_at": booking.confirmed_at.isoformat() if booking.confirmed_at else None,
        "hold_expires_at": booking.expires_at.isoformat() if booking.expires_at else None,
        "can_cancel": booking.status == "held" and active_holds > 0,
        "departure_at": trip.departure_at.isoformat() if trip else None,
        "arrival_estimate_at": trip.arrival_estimate_at.isoformat() if trip and trip.arrival_estimate_at else None,
        "passengers": [{"name": name, "seat": seat} for name, seat in passengers],
        "fare": {"amount_minor_units": fare.amount_minor_units, "currency_code": fare.currency_code} if fare else None,
        "reservation_reference": reservation.public_reference if reservation else None,
        "payment_collected": False, "ticket_issued": False, "boarding_authorized": False,
    }

@router.get("")
def list_my_bookings(context: PassengerContext = Depends(current_passenger_context), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Booking).where(
        Booking.passenger_account_id == context.passenger.id
    ).order_by(Booking.created_at.desc(), Booking.id.desc()).limit(100)).all()
    return {"items": [_booking_payload(db, row) for row in rows], "limit": 100}

@router.get("/{booking_id}")
def get_my_booking(booking_id: UUID, context: PassengerContext = Depends(current_passenger_context), db: Session = Depends(get_db)) -> dict:
    booking = db.scalar(select(Booking).where(
        Booking.id == booking_id, Booking.passenger_account_id == context.passenger.id
    ))
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return _booking_payload(db, booking)

@router.post("/{booking_id}/cancel")
def cancel_my_booking(booking_id: UUID, request: Request, context: PassengerContext = Depends(current_passenger_context), db: Session = Depends(get_db)) -> dict:
    _require_mutation(request, context)
    booking = db.scalar(select(Booking).where(
        Booking.id == booking_id, Booking.passenger_account_id == context.passenger.id
    ))
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    try:
        cancelled = cancel_unconfirmed_booking(db, booking_id=booking.id, actor_type="passenger", actor_id=str(context.passenger.id))
        db.commit()
    except BookingConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
    return {"booking_id": str(cancelled.id), "booking_reference": cancelled.booking_reference,
            "status": cancelled.status, "payment_collected": False, "refund_required": False}
