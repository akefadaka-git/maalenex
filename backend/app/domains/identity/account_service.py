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


def verify_identifier(db: Session, *, raw_token: str) -> tuple[PlatformAccount, str]:
    challenge, identifier, account = _locked_challenge(
        db, raw_token=raw_token, purpose="identifier_verification"
    )
    if account.status != "pending" or identifier.revoked_at is not None:
        raise ValueError("The challenge is invalid or expired.")
    now = _now(db)
    identifier.verified_at = now
    challenge.consumed_at = now
    account.status = "active"
    enrollment_token = _issue_challenge(
        db, account=account, identifier=identifier, purpose="credential_enrollment"
    )
    _audit(db, event="account.identifier.verified", account_id=account.id,
           action="verify_identifier", outcome="success")
    db.flush()
    return account, enrollment_token


def enroll_password(db: Session, *, raw_token: str, password: str) -> UUID:
    if len(password) < 14 or len(password) > 256:
        raise ValueError("Password must contain 14 to 256 characters.")
    challenge, identifier, account = _locked_challenge(
        db, raw_token=raw_token, purpose="credential_enrollment"
    )
    if account.status != "active" or identifier.verified_at is None or identifier.revoked_at is not None:
        raise ValueError("A verified identifier is required before credential enrollment.")
    current = db.scalar(select(AccountCredential.id).where(
        AccountCredential.account_id == account.id,
        AccountCredential.credential_type == "password",
        AccountCredential.status == "active",
        AccountCredential.revoked_at.is_(None),
    ).limit(1))
    if current is not None:
        raise ValueError("A password credential is already enrolled.")
    challenge.consumed_at = _now(db)
    db.add(AccountCredential(
        account_id=account.id, credential_type="password",
        verifier=hash_secret(password), status="active",
    ))
    _audit(db, event="account.credential.enrolled", account_id=account.id,
           action="enroll_password", outcome="success")
    db.flush()
    return account.id
