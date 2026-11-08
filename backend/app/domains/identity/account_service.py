"""Secure general-account identity lifecycle.

Delivery of verification/recovery challenges is deliberately adapter-neutral.
Raw challenge tokens are returned only when the explicit development-test switch
is enabled; production delivery must be provided by an approved provider adapter.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import re
import secrets
from uuid import UUID

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.audit.service import record_event
from app.domains.identity.accounts import (
    AccountChallenge, AccountCredential, AccountIdentifier, AccountLoginAttempt,
    AccountSession, PlatformAccount,
)
from app.domains.identity.security import hash_secret, issue_opaque_token, token_digest, verify_secret


class AccountAuthenticationError(Exception):
    pass


class AccountRateLimited(Exception):
    pass


def _now(db: Session) -> datetime:
    value = db.scalar(select(func.now()))
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def normalize_identifier(kind: str, value: str) -> str:
    raw = value.strip()
    if kind == "email":
        normalized = raw.casefold()
        if len(normalized) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
            raise ValueError("Enter a valid email address.")
        return normalized
    if kind == "phone":
        compact = re.sub(r"[\s()\-]", "", raw)
        if compact.startswith("09") or compact.startswith("07"):
            compact = "+251" + compact[1:]
        elif compact.startswith("251"):
            compact = "+" + compact
        if not re.fullmatch(r"\+[1-9][0-9]{7,14}", compact):
            raise ValueError("Enter a phone number in international format.")
        return compact
    raise ValueError("Identifier type must be email or phone.")


def _key_material(value: str | None, label: str) -> bytes:
    if not value or len(value.encode("utf-8")) < 32:
        raise RuntimeError(f"{label} must be configured with at least 32 bytes.")
    return hashlib.sha256(value.encode("utf-8")).digest()


def identifier_digest(kind: str, normalized: str) -> str:
    key = _key_material(settings.identity_lookup_key, "IDENTITY_LOOKUP_KEY")
    return hmac.new(key, f"{kind}:{normalized}".encode("utf-8"), hashlib.sha256).hexdigest()


def encrypt_identifier(kind: str, normalized: str) -> bytes:
    key = _key_material(settings.identity_encryption_key, "IDENTITY_ENCRYPTION_KEY")
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(key).encrypt(nonce, normalized.encode("utf-8"), kind.encode("ascii"))
    return nonce + ciphertext


def decrypt_identifier(kind: str, encrypted: bytes) -> str:
    key = _key_material(settings.identity_encryption_key, "IDENTITY_ENCRYPTION_KEY")
    return AESGCM(key).decrypt(encrypted[:12], encrypted[12:], kind.encode("ascii")).decode("utf-8")


def _audit(db: Session, *, event: str, account_id: UUID | None, action: str,
           outcome: str, reason: str | None = None) -> None:
    record_event(
        db, event_type=event, actor_type="account" if account_id else "anonymous",
        actor_id=str(account_id) if account_id else None,
        resource_type="platform_account", resource_id=str(account_id) if account_id else None,
        action=action, outcome=outcome, reason_code=reason,
    )


def _issue_challenge(db: Session, *, account: PlatformAccount,
                     identifier: AccountIdentifier, purpose: str) -> str:
    now = _now(db)
    db.execute(
        AccountChallenge.__table__.update()
        .where(AccountChallenge.account_id == account.id,
               AccountChallenge.purpose == purpose,
               AccountChallenge.consumed_at.is_(None))
        .values(consumed_at=now)
    )
    raw = issue_opaque_token()
    db.add(AccountChallenge(
        account_id=account.id, identifier_id=identifier.id, purpose=purpose,
        token_digest=token_digest(raw),
        expires_at=now + (timedelta(minutes=15) if purpose == "identifier_verification"
                          else timedelta(minutes=30)),
    ))
    return raw


def register_account(db: Session, *, display_name: str, identifier_type: str,
                     identifier_value: str, preferred_locale: str = "am-ET") -> tuple[PlatformAccount, str]:
    normalized = normalize_identifier(identifier_type, identifier_value)
    digest = identifier_digest(identifier_type, normalized)
    now = _now(db)
    existing = db.scalar(select(AccountIdentifier).where(
        AccountIdentifier.identifier_type == identifier_type,
        AccountIdentifier.lookup_digest == digest,
        AccountIdentifier.revoked_at.is_(None),
    ).with_for_update())
    if existing is not None:
        raise ValueError("An account already uses this identifier.")
    account = PlatformAccount(
        display_name=display_name.strip(), preferred_locale=preferred_locale, status="pending"
    )
    db.add(account)
    db.flush()
    identifier = AccountIdentifier(
        account_id=account.id, identifier_type=identifier_type, lookup_digest=digest,
        encrypted_value=encrypt_identifier(identifier_type, normalized),
    )
    db.add(identifier)
    db.flush()
    raw = _issue_challenge(db, account=account, identifier=identifier,
                           purpose="identifier_verification")
    _audit(db, event="account.registration.created", account_id=account.id,
           action="register", outcome="success")
    db.flush()
    return account, raw


def _locked_challenge(db: Session, *, raw_token: str, purpose: str) -> tuple[AccountChallenge, AccountIdentifier, PlatformAccount]:
    now = _now(db)
    challenge = db.scalar(select(AccountChallenge).where(
        AccountChallenge.token_digest == token_digest(raw_token),
        AccountChallenge.purpose == purpose,
        AccountChallenge.consumed_at.is_(None),
        AccountChallenge.expires_at > now,
    ).with_for_update())
    if challenge is None or challenge.failed_attempts >= 5:
        raise ValueError("The challenge is invalid or expired.")
    identifier = db.scalar(select(AccountIdentifier).where(
        AccountIdentifier.id == challenge.identifier_id
    ).with_for_update())
    account = db.scalar(select(PlatformAccount).where(
        PlatformAccount.id == challenge.account_id
    ).with_for_update())
    if identifier is None or account is None:
        raise ValueError("The challenge is invalid or expired.")
    return challenge, identifier, account


def verify_identifier(db: Session, *, raw_token: str) -> PlatformAccount:
    challenge, identifier, account = _locked_challenge(
        db, raw_token=raw_token, purpose="identifier_verification"
    )
    if account.status != "pending" or identifier.revoked_at is not None:
        raise ValueError("The challenge is invalid or expired.")
    now = _now(db)
    identifier.verified_at = now
    challenge.consumed_at = now
    account.status = "active"
    _audit(db, event="account.identifier.verified", account_id=account.id,
           action="verify_identifier", outcome="success")
    db.flush()
    return account


def enroll_password(db: Session, *, identifier_type: str, identifier_value: str,
                    password: str) -> UUID:
    if len(password) < 14 or len(password) > 256:
        raise ValueError("Password must contain 14 to 256 characters.")
    normalized = normalize_identifier(identifier_type, identifier_value)
    digest = identifier_digest(identifier_type, normalized)
    identifier = db.scalar(select(AccountIdentifier).where(
        AccountIdentifier.identifier_type == identifier_type,
        AccountIdentifier.lookup_digest == digest,
        AccountIdentifier.verified_at.is_not(None),
        AccountIdentifier.revoked_at.is_(None),
    ).with_for_update())
    if identifier is None:
        raise ValueError("A verified identifier is required before credential enrollment.")
    account = db.scalar(select(PlatformAccount).where(
        PlatformAccount.id == identifier.account_id
    ).with_for_update())
    if account is None or account.status != "active":
        raise ValueError("Account is not eligible for credential enrollment.")
    current = db.scalar(select(AccountCredential.id).where(
        AccountCredential.account_id == account.id,
        AccountCredential.credential_type == "password",
        AccountCredential.status == "active",
        AccountCredential.revoked_at.is_(None),
    ).limit(1))
    if current is not None:
        raise ValueError("A password credential is already enrolled.")
    db.add(AccountCredential(
        account_id=account.id, credential_type="password",
        verifier=hash_secret(password), status="active",
    ))
    _audit(db, event="account.credential.enrolled", account_id=account.id,
           action="enroll_password", outcome="success")
    db.flush()
    return account.id


def authenticate_account(db: Session, *, identifier_type: str, identifier_value: str,
                         password: str, client_ip: str) -> tuple[PlatformAccount, AccountSession, str, str]:
    normalized = normalize_identifier(identifier_type, identifier_value)
    digest = identifier_digest(identifier_type, normalized)
    now = _now(db)
    attempt_key = hashlib.sha256(f"{digest}|{client_ip}".encode("utf-8")).hexdigest()
    attempt = db.scalar(select(AccountLoginAttempt).where(
        AccountLoginAttempt.key_digest == attempt_key
    ).with_for_update())
    if attempt is None:
        try:
            with db.begin_nested():
                attempt = AccountLoginAttempt(
                    key_digest=attempt_key, window_started_at=now, failed_count=0
                )
                db.add(attempt)
                db.flush()
        except IntegrityError:
            attempt = db.scalar(select(AccountLoginAttempt).where(
                AccountLoginAttempt.key_digest == attempt_key
            ).with_for_update())
    if attempt is None:
        raise AccountRateLimited()
    if _utc(attempt.window_started_at) < now - timedelta(minutes=15):
        attempt.window_started_at, attempt.failed_count, attempt.locked_until = now, 0, None
    if attempt.locked_until and _utc(attempt.locked_until) > now:
        raise AccountRateLimited()

    identifier = db.scalar(select(AccountIdentifier).where(
        AccountIdentifier.identifier_type == identifier_type,
        AccountIdentifier.lookup_digest == digest,
        AccountIdentifier.verified_at.is_not(None),
        AccountIdentifier.revoked_at.is_(None),
    ))
    account = db.get(PlatformAccount, identifier.account_id) if identifier else None
    credentials = db.scalars(select(AccountCredential).where(
        AccountCredential.account_id == account.id if account else False,
        AccountCredential.credential_type == "password",
        AccountCredential.status == "active",
        AccountCredential.revoked_at.is_(None),
    ).order_by(AccountCredential.created_at.desc())).all() if account else []
    credential = credentials[0] if credentials else None
    valid = account is not None and account.status == "active" and credential is not None
    valid = bool(valid and (credential.expires_at is None or _utc(credential.expires_at) > now)
                 and verify_secret(password, credential.verifier))
    if not valid:
        attempt.failed_count += 1
        if attempt.failed_count >= 5:
            attempt.locked_until = now + timedelta(minutes=15)
        _audit(db, event="account.authentication.failed", account_id=None,
               action="login", outcome="denied", reason="invalid_credentials")
        raise AccountAuthenticationError()
    attempt.failed_count, attempt.locked_until = 0, None
    session_token, csrf_token = issue_opaque_token(), issue_opaque_token()
    session = AccountSession(
        account_id=account.id, secret_digest=token_digest(session_token),
        csrf_digest=token_digest(csrf_token), expires_at=now + timedelta(hours=12),
    )
    db.add(session)
    _audit(db, event="account.authentication.succeeded", account_id=account.id,
           action="login", outcome="success")
    db.flush()
    return account, session, session_token, csrf_token


def resolve_account_session(db: Session, raw_token: str | None) -> tuple[PlatformAccount, AccountSession]:
    if not raw_token:
        raise AccountAuthenticationError()
    now = _now(db)
    session = db.scalar(select(AccountSession).where(
        AccountSession.secret_digest == token_digest(raw_token),
        AccountSession.revoked_at.is_(None), AccountSession.expires_at > now,
    ))
    account = db.get(PlatformAccount, session.account_id) if session else None
    if session is None or account is None or account.status != "active":
        raise AccountAuthenticationError()
    session.last_seen_at = now
    return account, session


def revoke_account_sessions(db: Session, *, account_id: UUID, session_id: UUID | None = None) -> int:
    now = _now(db)
    query = AccountSession.__table__.update().where(
        AccountSession.account_id == account_id, AccountSession.revoked_at.is_(None)
    )
    if session_id is not None:
        query = query.where(AccountSession.id == session_id)
    result = db.execute(query.values(revoked_at=now))
    _audit(db, event="account.session.revoked", account_id=account_id,
           action="revoke_session" if session_id else "revoke_all_sessions",
           outcome="success")
    return result.rowcount or 0


def request_password_recovery(db: Session, *, identifier_type: str,
                              identifier_value: str) -> str | None:
    normalized = normalize_identifier(identifier_type, identifier_value)
    digest = identifier_digest(identifier_type, normalized)
    identifier = db.scalar(select(AccountIdentifier).where(
        AccountIdentifier.identifier_type == identifier_type,
        AccountIdentifier.lookup_digest == digest,
        AccountIdentifier.verified_at.is_not(None),
        AccountIdentifier.revoked_at.is_(None),
    ).with_for_update())
    account = db.get(PlatformAccount, identifier.account_id) if identifier else None
    if account is None or account.status != "active":
        return None
    raw = _issue_challenge(db, account=account, identifier=identifier,
                           purpose="password_recovery")
    _audit(db, event="account.recovery.requested", account_id=account.id,
           action="request_recovery", outcome="success")
    db.flush()
    return raw


def complete_password_recovery(db: Session, *, raw_token: str, new_password: str) -> UUID:
    if len(new_password) < 14 or len(new_password) > 256:
        raise ValueError("Password must contain 14 to 256 characters.")
    challenge, identifier, account = _locked_challenge(
        db, raw_token=raw_token, purpose="password_recovery"
    )
    if account.status != "active" or identifier.verified_at is None:
        raise ValueError("The challenge is invalid or expired.")
    now = _now(db)
    challenge.consumed_at = now
    db.execute(AccountCredential.__table__.update().where(
        AccountCredential.account_id == account.id,
        AccountCredential.credential_type == "password",
        AccountCredential.status == "active",
    ).values(status="revoked", revoked_at=now))
    db.add(AccountCredential(
        account_id=account.id, credential_type="password",
        verifier=hash_secret(new_password), status="active",
    ))
    revoked = revoke_account_sessions(db, account_id=account.id)
    _audit(db, event="account.recovery.completed", account_id=account.id,
           action="recover_password", outcome="success")
    db.flush()
    return account.id
