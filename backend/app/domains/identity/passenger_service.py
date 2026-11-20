"""Passenger account lifecycle. This service never reads or writes staff identities."""
import hashlib
import hmac
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.identity.passenger_models import (
    PassengerAccount,
    PassengerCredential,
    PassengerLoginAttempt,
    PassengerSession,
)
from app.domains.identity.security import (
    hash_secret,
    issue_opaque_token,
    token_digest,
    verify_secret,
)


class PassengerAuthenticationError(Exception):
    pass

class PassengerRateLimited(Exception):
    pass

@dataclass
class IssuedPassengerSession:
    passenger: PassengerAccount
    session: PassengerSession
    session_token: str
    csrf_token: str

@dataclass
class PassengerContext:
    passenger: PassengerAccount
    session: PassengerSession

def _now(db: Session) -> datetime:
    value = db.scalar(select(func.now()))
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value

def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value

def register_passenger(db: Session, *, login_identifier: str, display_name: str, password: str) -> PassengerAccount:
    passenger = PassengerAccount(
        login_identifier=login_identifier.strip().lower(),
        display_name=display_name.strip(),
        status="active",
    )
    db.add(passenger)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise PassengerAuthenticationError("account_exists") from exc
    db.add(PassengerCredential(
        passenger_id=passenger.id, credential_type="password",
        secret_hash=hash_secret(password), status="active",
    ))
    record_event(
        db, event_type="passenger.account.registered", actor_type="passenger",
        actor_id=str(passenger.id), resource_type="passenger_account",
        resource_id=str(passenger.id), action="register", outcome="success",
        metadata={"contact_verified": False},
    )
    db.flush()
    return passenger

def create_passenger_session(db: Session, *, login_identifier: str, password: str, client_ip: str) -> IssuedPassengerSession:
    now = _now(db)
    normalized = login_identifier.strip().lower()
    key_hash = hashlib.sha256(f"{normalized}|{client_ip}".encode()).hexdigest()
    attempt = db.scalar(select(PassengerLoginAttempt).where(PassengerLoginAttempt.key_hash == key_hash).with_for_update())
    if attempt is None:
        try:
            with db.begin_nested():
                attempt = PassengerLoginAttempt(key_hash=key_hash, window_started_at=now, failed_count=0, locked_until=None)
                db.add(attempt)
                db.flush()
        except IntegrityError:
            attempt = db.scalar(select(PassengerLoginAttempt).where(PassengerLoginAttempt.key_hash == key_hash).with_for_update())
    if attempt is None:
        raise PassengerRateLimited()
    if _utc(attempt.window_started_at) < now - timedelta(minutes=15):
        attempt.window_started_at, attempt.failed_count, attempt.locked_until = now, 0, None
    if attempt.locked_until is not None and _utc(attempt.locked_until) > now:
        raise PassengerRateLimited()
    passenger = db.scalar(select(PassengerAccount).where(
        PassengerAccount.login_identifier == normalized, PassengerAccount.status == "active",
    ))
    credential = None
    if passenger is not None:
        credential = db.scalar(select(PassengerCredential).where(
            PassengerCredential.passenger_id == passenger.id,
            PassengerCredential.credential_type == "password",
            PassengerCredential.status == "active",
            PassengerCredential.revoked_at.is_(None),
        ).order_by(PassengerCredential.created_at.desc()).limit(1))
    valid = (
        passenger is not None and credential is not None
        and (credential.expires_at is None or _utc(credential.expires_at) > now)
        and verify_secret(password, credential.secret_hash)
    )
    if not valid:
        attempt.failed_count += 1
        if attempt.failed_count >= 5:
            attempt.locked_until = now + timedelta(minutes=15)
        record_event(
            db, event_type="passenger.authentication.failed", actor_type="anonymous",
            actor_id=None, resource_type="passenger_authentication", resource_id=None,
            action="login", outcome="denied", reason_code="invalid_credentials",
            metadata={"attempt_key_hash": key_hash},
        )
        raise PassengerAuthenticationError("invalid_credentials")
    attempt.failed_count, attempt.locked_until = 0, None
    raw_session, raw_csrf = issue_opaque_token(), issue_opaque_token()
    session = PassengerSession(
        passenger_id=passenger.id, secret_hash=token_digest(raw_session),
        csrf_token_hash=token_digest(raw_csrf), expires_at=now + timedelta(hours=12),
    )
    db.add(session)
    record_event(
        db, event_type="passenger.authentication.succeeded", actor_type="passenger",
        actor_id=str(passenger.id), resource_type="passenger_session", resource_id=None,
        action="login", outcome="success",
    )
    db.flush()
    return IssuedPassengerSession(passenger, session, raw_session, raw_csrf)

def resolve_passenger_session(db: Session, *, raw_token: str | None) -> PassengerContext:
    if not raw_token:
        raise PassengerAuthenticationError("authentication_required")
    now = _now(db)
    cutoff = now.replace(tzinfo=None) if db.bind.dialect.name == "sqlite" else now
    session = db.scalar(select(PassengerSession).where(
        PassengerSession.secret_hash == token_digest(raw_token),
        PassengerSession.revoked_at.is_(None), PassengerSession.expires_at > cutoff,
    ))
    if session is None:
        raise PassengerAuthenticationError("authentication_required")
    passenger = db.get(PassengerAccount, session.passenger_id)
    if passenger is None or passenger.status != "active":
        raise PassengerAuthenticationError("authentication_required")
    session.last_seen_at = now
    return PassengerContext(passenger, session)

def verify_passenger_csrf(context: PassengerContext, *, cookie_token: str | None, header_token: str | None) -> bool:
    if not cookie_token or not header_token:
        return False
    return hmac.compare_digest(cookie_token, header_token) and hmac.compare_digest(
        token_digest(cookie_token), context.session.csrf_token_hash,
    )
