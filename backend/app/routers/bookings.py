from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.bookings.access import (
    BookingAccessError, BookingAccessRateLimited, create_access_challenge,
    enforce_guest_access_rate_limit, resolve_booking_grant,
    verify_access_challenge, verify_booking_csrf, revoke_booking_grants,
)
from app.domains.bookings.models import (
    Booking, BookingContact, BookingFareSnapshot,
    BookingPassenger, Passenger, SeatHold,
)
from app.domains.bookings.service import BookingConflict, accept_reservation, create_seat_hold
from app.domains.trips.models import TripSeat
from app.domains.reservations.models import BookingAccessGrant

router = APIRouter(tags=["passenger-bookings"])
ACCESS_COOKIE = "mnm_booking_access"
CSRF_COOKIE = "mnm_booking_csrf"


class PassengerInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)


class CreateHoldRequest(BaseModel):
    trip_id: UUID
    booking_contact_name: str = Field(min_length=1, max_length=160)
    booking_contact_phone: str = Field(min_length=1, max_length=32)
    passengers: list[PassengerInput] = Field(min_length=1, max_length=10)
    seat_ids: list[UUID] = Field(min_length=1, max_length=10)


class ChallengeRequest(BaseModel):
    booking_reference: str = Field(min_length=8, max_length=64)
    contact_phone: str = Field(min_length=1, max_length=32)


class ChallengeVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern="^[0-9]{6}$")


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _require_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")


def current_booking_grant(
    booking_id: UUID, request: Request, db: Session = Depends(get_db),
) -> BookingAccessGrant:
    try:
        grant = resolve_booking_grant(
            db, booking_id=booking_id, raw_token=request.cookies.get(ACCESS_COOKIE),
        )
        db.commit()
        return grant
    except BookingAccessError:
        raise HTTPException(status_code=401, detail="Booking access verification required.")


@router.post("/bookings/holds", status_code=status.HTTP_201_CREATED)
def create_booking_hold(
    payload: CreateHoldRequest, request: Request, db: Session = Depends(get_db),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=128),
) -> dict:
    try:
        enforce_guest_access_rate_limit(db, client_ip=_client_ip(request))
        booking = create_seat_hold(
            db, trip_id=payload.trip_id,
            contact_name=payload.booking_contact_name,
            contact_phone=payload.booking_contact_phone,
            passengers=[item.model_dump() for item in payload.passengers],
            seat_ids=payload.seat_ids, idempotency_key=idempotency_key,
            hold_minutes=10,
        )
        snapshot = db.scalar(select(BookingFareSnapshot).where(
            BookingFareSnapshot.booking_id == booking.id
        ))
        db.commit()
    except BookingAccessRateLimited:
        db.commit()
        raise HTTPException(status_code=429, detail="Too many booking requests. Try again later.")
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc))
    except BookingConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
    return {
        "booking_id": str(booking.id),
        "booking_reference": booking.booking_reference,
        "status": booking.status,
        "hold_expires_at": booking.expires_at.isoformat(),
        "fare": {
            "amount_minor_units": snapshot.amount_minor_units,
            "currency_code": snapshot.currency_code,
        } if snapshot else None,
        "payment_enabled": False,
        "ticketing_enabled": False,
        "next_step": "verify_booking_contact",
    }


@router.post("/passenger-access/challenges", status_code=status.HTTP_202_ACCEPTED)
def request_booking_access_challenge(
    payload: ChallengeRequest, request: Request, db: Session = Depends(get_db),
) -> dict:
    try:
        challenge, code = create_access_challenge(
            db, booking_reference=payload.booking_reference,
            contact_phone=payload.contact_phone, client_ip=_client_ip(request),
        )
        db.commit()
    except BookingAccessRateLimited:
        db.commit()
        raise HTTPException(status_code=429, detail="Too many verification requests. Try again later.")
    result = {"challenge_id": str(challenge.id), "accepted": True, "expires_in_seconds": 600}
    if settings.app_env in {"development", "test"} and settings.synthetic_data_only:
        result["synthetic_test_code"] = code
    return result


@router.post("/passenger-access/challenges/{challenge_id}/verify")
def verify_booking_access_challenge(
    challenge_id: UUID, payload: ChallengeVerifyRequest,
    request: Request, response: Response, db: Session = Depends(get_db),
) -> dict:
    _require_origin(request)
    try:
        booking, grant, access_token, csrf_token = verify_access_challenge(
            db, challenge_id=challenge_id, code=payload.code,
            client_ip=_client_ip(request),
        )
        db.commit()
    except BookingAccessError:
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid or expired booking verification.")
    secure_cookie = request.url.scheme == "https"
    cookie_path = f"{settings.api_prefix}/bookings/{booking.id}"
    response.set_cookie(
        ACCESS_COOKIE, access_token, max_age=2 * 60 * 60,
        httponly=True, secure=secure_cookie, samesite="lax", path=cookie_path,
    )
    response.set_cookie(
        CSRF_COOKIE, csrf_token, max_age=2 * 60 * 60,
        httponly=False, secure=secure_cookie, samesite="lax", path="/",
    )
    return {"booking_id": str(booking.id), "scope": grant.scope, "expires_at": grant.expires_at.isoformat()}


@router.get("/bookings/{booking_id}")
def read_guest_booking(
    booking_id: UUID, grant: BookingAccessGrant = Depends(current_booking_grant),
    db: Session = Depends(get_db),
) -> dict:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    contact = db.get(BookingContact, booking.booking_contact_id)
    snapshot = db.scalar(select(BookingFareSnapshot).where(BookingFareSnapshot.booking_id == booking.id))
    passengers = db.execute(
        select(Passenger.display_name, TripSeat.seat_code_snapshot)
        .join(BookingPassenger, BookingPassenger.passenger_id == Passenger.id)
        .join(TripSeat, TripSeat.id == BookingPassenger.trip_seat_id)
        .where(BookingPassenger.booking_id == booking.id)
        .order_by(BookingPassenger.passenger_sequence)
    ).all()
    phone = contact.phone_normalized if contact else ""
    masked_phone = ("*" * max(0, len(phone) - 3)) + phone[-3:] if phone else None
    return {
        "booking_id": str(booking.id),
        "booking_reference": booking.booking_reference,
        "status": booking.status,
        "contact_name": contact.name if contact else None,
        "contact_phone_masked": masked_phone,
        "passengers": [{"name": name, "seat": seat} for name, seat in passengers],
        "fare": {
            "amount_minor_units": snapshot.amount_minor_units,
            "currency_code": snapshot.currency_code,
        } if snapshot else None,
        "payment_enabled": False,
        "ticketing_enabled": False,
        "boarding_authorized": False,
    }


@router.post("/bookings/{booking_id}/reservation")
def accept_guest_reservation(
    booking_id: UUID, request: Request,
    grant: BookingAccessGrant = Depends(current_booking_grant),
    db: Session = Depends(get_db),
) -> dict:
    _require_origin(request)
    if grant.scope != "manage" or not verify_booking_csrf(
        grant, cookie_token=request.cookies.get(CSRF_COOKIE),
        header_token=request.headers.get("X-CSRF-Token"),
    ):
        raise HTTPException(status_code=403, detail="Booking mutation authorization failed.")
    try:
        reference = accept_reservation(db, booking_id=booking_id)
        db.commit()
    except BookingConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
    return {
        "reservation_reference": reference.public_reference,
        "qr_payload_version": reference.qr_payload_version,
        "qr_payload_reference": reference.qr_payload_reference,
        "status": "reserved",
        "payment_collected": False,
        "travel_ticket_issued": False,
        "boarding_authorized": False,
    }


@router.post("/bookings/{booking_id}/access/revoke")
def revoke_guest_booking_access(
    booking_id: UUID, request: Request, response: Response,
    grant: BookingAccessGrant = Depends(current_booking_grant),
    db: Session = Depends(get_db),
) -> dict:
    _require_origin(request)
    if grant.scope != "manage" or not verify_booking_csrf(
        grant, cookie_token=request.cookies.get(CSRF_COOKIE),
        header_token=request.headers.get("X-CSRF-Token"),
    ):
        raise HTTPException(status_code=403, detail="Booking access revocation authorization failed.")
    revoked = revoke_booking_grants(db, booking_id=booking_id)
    db.commit()
    response.delete_cookie(
        ACCESS_COOKIE, path=f"{settings.api_prefix}/bookings/{booking_id}",
        samesite="lax",
    )
    response.delete_cookie(CSRF_COOKIE, path="/", samesite="lax")
    return {"booking_id": str(booking_id), "revoked_grants": revoked, "access_revoked": True}


@router.post("/bookings/{booking_id}/cancel")
def cancel_guest_booking(
    booking_id: UUID, grant: BookingAccessGrant = Depends(current_booking_grant),
) -> None:
    raise HTTPException(status_code=409, detail={
        "code": "CAPABILITY_DISABLED",
        "message": "Live cancellation is disabled until the Owner-approved cancellation and refund policy is finalized.",
    })


@router.post("/tickets")
def disabled_ticket_issuance() -> None:
    raise HTTPException(status_code=409, detail={"code": "CAPABILITY_DISABLED", "message": "Travel-ticket issuance is disabled."})


@router.post("/boarding/validate")
def disabled_boarding_validation() -> None:
    raise HTTPException(status_code=409, detail={"code": "CAPABILITY_DISABLED", "message": "Boarding validation is disabled; a reservation reference is not a travel ticket."})
