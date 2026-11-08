from datetime import timedelta
import hashlib
import hmac
from secrets import randbelow
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.bookings.models import (
    Booking, BookingAccessChallenge, BookingContact,
    GuestAccessRateLimit,
)
from app.domains.reservations.models import BookingAccessGrant
from app.domains.identity.security import hash_secret, issue_opaque_token, token_digest, verify_secret


class BookingAccessError(Exception):
    pass


class BookingAccessRateLimited(Exception):
    pass


def _normalize_phone(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit() or ch == "+")



def _check_challenge_rate_limit(
    db: Session, *, client_ip: str, now, key_prefix: str = "guest-access:",
) -> None:
    key_hash = hashlib.sha256((key_prefix + client_ip).encode("utf-8")).hexdigest()
    attempt = db.scalar(select(GuestAccessRateLimit).where(
        GuestAccessRateLimit.key_hash == key_hash
    ).with_for_update())
    if attempt is None:
        try:
            with db.begin_nested():
                attempt = GuestAccessRateLimit(
                    key_hash=key_hash, window_started_at=now,
                    request_count=0, locked_until=None,
                )
                db.add(attempt)
                db.flush()
        except IntegrityError:
            attempt = db.scalar(select(GuestAccessRateLimit).where(
                GuestAccessRateLimit.key_hash == key_hash
            ).with_for_update())
    if attempt is None:
        raise BookingAccessRateLimited()
    window_start = attempt.window_started_at
    locked_until = attempt.locked_until
    if window_start.tzinfo is None and now.tzinfo is not None:
        window_start = window_start.replace(tzinfo=now.tzinfo)
    if locked_until is not None and locked_until.tzinfo is None and now.tzinfo is not None:
        locked_until = locked_until.replace(tzinfo=now.tzinfo)
    if locked_until is not None and locked_until > now:
        raise BookingAccessRateLimited()
    if window_start < now - timedelta(minutes=15):
        attempt.window_started_at = now
        attempt.request_count = 0
        attempt.locked_until = None
    attempt.request_count += 1
    if attempt.request_count > 10:
        attempt.locked_until = now + timedelta(minutes=15)
        raise BookingAccessRateLimited()

def create_access_challenge(
    db: Session, *, booking_reference: str, contact_phone: str, client_ip: str,
) -> tuple[BookingAccessChallenge, str]:
    now = db.scalar(select(func.now()))
    _check_challenge_rate_limit(db, client_ip=client_ip, now=now)
    normalized_phone = _normalize_phone(contact_phone)
    booking = db.scalar(
        select(Booking).join(BookingContact, BookingContact.id == Booking.booking_contact_id).where(
            Booking.booking_reference == booking_reference.strip(),
            BookingContact.phone_normalized == normalized_phone,
        )
    )
    code = f"{randbelow(1_000_000):06d}"
    challenge = BookingAccessChallenge(
        booking_id=booking.id if booking is not None else None,
        code_hash=hash_secret(code),
        requester_ip_hash=hashlib.sha256(client_ip.encode("utf-8")).hexdigest(),
        expires_at=now + timedelta(minutes=10),
        attempt_count=0,
    )
    db.add(challenge)
    record_event(
        db, event_type="booking.access.challenge.created", actor_type="guest",
        actor_id=None, resource_type="booking_access_challenge",
        resource_id=str(challenge.id), action="create", outcome="accepted",
        metadata={"booking_match": booking is not None},
    )
    db.flush()
    return challenge, code


def verify_access_challenge(
    db: Session, *, challenge_id: UUID, code: str, client_ip: str,
) -> tuple[Booking, BookingAccessGrant, str, str]:
    now = db.scalar(select(func.now()))
    # Verification attempts have their own durable per-IP bucket, independent of
    # challenge IDs, so requesting another challenge cannot reset the IP budget.
    _check_challenge_rate_limit(
        db, client_ip=client_ip, now=now, key_prefix="guest-verification:",
    )
    challenge = db.scalar(select(BookingAccessChallenge).where(
        BookingAccessChallenge.id == challenge_id
    ).with_for_update())
    ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()
    if (
        challenge is None or challenge.consumed_at is not None
        or challenge.expires_at <= now or challenge.requester_ip_hash != ip_hash
        or challenge.attempt_count >= 5
    ):
        raise BookingAccessError()
    if not verify_secret(code, challenge.code_hash):
        challenge.attempt_count += 1
        if challenge.attempt_count >= 5:
            challenge.consumed_at = now
        record_event(
            db, event_type="booking.access.challenge.failed", actor_type="guest",
            actor_id=None, resource_type="booking_access_challenge",
            resource_id=str(challenge.id), action="verify", outcome="denied",
            reason_code="invalid_or_expired_challenge",
        )
        db.flush()
        raise BookingAccessError()
    if challenge.booking_id is None:
        challenge.consumed_at = now
        db.flush()
        raise BookingAccessError()
    booking = db.scalar(select(Booking).where(
        Booking.id == challenge.booking_id
    ).with_for_update())
    if booking is None:
        raise BookingAccessError()
    challenge.consumed_at = now
    access_token = issue_opaque_token()
    csrf_token = issue_opaque_token()
    grant = BookingAccessGrant(
        booking_id=booking.id, credential_hash=token_digest(access_token),
        csrf_token_hash=token_digest(csrf_token), scope="manage",
        expires_at=now + timedelta(hours=2),
    )
    db.add(grant)
    record_event(
        db, event_type="booking.access.grant.issued", actor_type="guest",
        actor_id=None, resource_type="booking", resource_id=str(booking.id),
        action="grant_access", outcome="success",
    )
    db.flush()
    return booking, grant, access_token, csrf_token


def resolve_booking_grant(
    db: Session, *, booking_id: UUID, raw_token: str | None,
) -> BookingAccessGrant:
    if not raw_token:
        raise BookingAccessError()
    now = db.scalar(select(func.now()))
    grant = db.scalar(select(BookingAccessGrant).where(
        BookingAccessGrant.booking_id == booking_id,
        BookingAccessGrant.credential_hash == token_digest(raw_token),
        BookingAccessGrant.revoked_at.is_(None),
        BookingAccessGrant.expires_at > now,
    ))
    if grant is None:
        raise BookingAccessError()
    grant.last_used_at = now
    return grant


def verify_booking_csrf(
    grant: BookingAccessGrant, *, cookie_token: str | None, header_token: str | None,
) -> bool:
    if not cookie_token or not header_token:
        return False
    return hmac.compare_digest(cookie_token, header_token) and hmac.compare_digest(
        token_digest(cookie_token), grant.csrf_token_hash,
    )


def enforce_guest_access_rate_limit(db: Session, *, client_ip: str) -> None:
    now = db.scalar(select(func.now()))
    _check_challenge_rate_limit(db, client_ip=client_ip, now=now)


def revoke_booking_grants(db: Session, *, booking_id: UUID) -> int:
    now = db.scalar(select(func.now()))
    grants = list(db.scalars(select(BookingAccessGrant).where(
        BookingAccessGrant.booking_id == booking_id,
        BookingAccessGrant.revoked_at.is_(None),
        BookingAccessGrant.expires_at > now,
    ).with_for_update()))
    for grant in grants:
        grant.revoked_at = now
    record_event(
        db, event_type="booking.access.grants.revoked", actor_type="guest",
        actor_id=None, resource_type="booking", resource_id=str(booking_id),
        action="revoke_access", outcome="success",
        metadata={"revoked_grant_count": len(grants)},
    )
    db.flush()
    return len(grants)
