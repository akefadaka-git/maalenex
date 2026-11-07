from dataclasses import dataclass
from datetime import timedelta
import hashlib
import hmac

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.identity.models import AuthLoginAttempt, Credential, StaffSession, User
from app.domains.identity.security import issue_opaque_token, token_digest, verify_secret


class AuthenticationError(Exception):
    pass


class AuthenticationRateLimited(Exception):
    pass


@dataclass
class IssuedStaffSession:
    user: User
    session: StaffSession
    session_token: str
    csrf_token: str


@dataclass
class StaffContext:
    user: User
    session: StaffSession


def _login_attempt_key(login_identifier: str, client_ip: str) -> str:
    material = login_identifier.strip().lower() + "|" + client_ip
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def authenticate_staff(
    db: Session, *, login_identifier: str, password: str, client_ip: str,
) -> IssuedStaffSession:
    now = db.scalar(select(func.now()))
    normalized_login = login_identifier.strip().lower()
    key_hash = _login_attempt_key(normalized_login, client_ip)
    attempt = db.scalar(select(AuthLoginAttempt).where(
        AuthLoginAttempt.key_hash == key_hash
    ).with_for_update())
    if attempt is None:
        try:
            with db.begin_nested():
                attempt = AuthLoginAttempt(
                    key_hash=key_hash, window_started_at=now,
                    failed_count=0, locked_until=None,
                )
                db.add(attempt)
                db.flush()
        except IntegrityError:
            attempt = db.scalar(select(AuthLoginAttempt).where(
                AuthLoginAttempt.key_hash == key_hash
            ).with_for_update())
    if attempt is None:
        raise AuthenticationRateLimited()
    if attempt.window_started_at < now - timedelta(minutes=15):
        attempt.window_started_at = now
        attempt.failed_count = 0
        attempt.locked_until = None
    if attempt.locked_until is not None and attempt.locked_until > now:
        raise AuthenticationRateLimited()

    user = db.scalar(select(User).where(
        User.login_identifier == normalized_login,
        User.status == "active",
    ))
    credential = None
    if user is not None:
        credential = db.scalar(select(Credential).where(
            Credential.user_id == user.id,
            Credential.credential_type == "password",
            Credential.status == "active",
            Credential.revoked_at.is_(None),
        ).order_by(Credential.created_at.desc()).limit(1))
    valid = (
        user is not None and credential is not None
        and (credential.expires_at is None or credential.expires_at > now)
        and verify_secret(password, credential.secret_hash)
    )
    if not valid:
        attempt.failed_count += 1
        if attempt.failed_count >= 5:
            attempt.locked_until = now + timedelta(minutes=15)
        record_event(
            db, event_type="staff.authentication.failed", actor_type="anonymous",
            actor_id=None, resource_type="staff_authentication", resource_id=None,
            action="login", outcome="denied", reason_code="invalid_credentials",
            metadata={"attempt_key_hash": key_hash},
        )
        raise AuthenticationError()

    attempt.failed_count = 0
    attempt.locked_until = None
    session_token = issue_opaque_token()
    csrf_token = issue_opaque_token()
    session = StaffSession(
        user_id=user.id, secret_hash=token_digest(session_token),
        csrf_token_hash=token_digest(csrf_token),
        expires_at=now + timedelta(hours=8),
    )
    db.add(session)
    record_event(
        db, event_type="staff.authentication.succeeded", actor_type="staff",
        actor_id=str(user.id), resource_type="staff_session", resource_id=None,
        action="login", outcome="success",
    )
    db.flush()
    return IssuedStaffSession(user=user, session=session,
                              session_token=session_token, csrf_token=csrf_token)


def resolve_staff_session(db: Session, *, raw_token: str | None) -> StaffContext:
    if not raw_token:
        raise AuthenticationError()
    now = db.scalar(select(__import__("sqlalchemy").func.now()))
    session = db.scalar(select(StaffSession).where(
        StaffSession.secret_hash == token_digest(raw_token),
        StaffSession.revoked_at.is_(None),
        StaffSession.expires_at > now,
    ))
    if session is None:
        raise AuthenticationError()
    user = db.get(User, session.user_id)
    if user is None or user.status != "active":
        raise AuthenticationError()
    session.last_seen_at = now
    return StaffContext(user=user, session=session)


def verify_csrf(context: StaffContext, *, cookie_token: str | None,
                header_token: str | None) -> bool:
    if not cookie_token or not header_token:
        return False
    if not hmac.compare_digest(cookie_token, header_token):
        return False
    return hmac.compare_digest(token_digest(cookie_token), context.session.csrf_token_hash)
