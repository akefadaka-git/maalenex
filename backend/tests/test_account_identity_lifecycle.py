import os
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.identity.accounts import AccountIdentifier
from app.domains.identity.account_service import (
    AccountAuthenticationError, authenticate_account, complete_password_recovery,
    decrypt_identifier, enroll_password, register_account, request_password_recovery,
    resolve_account_session, verify_identifier,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def _configure_identity_keys(monkeypatch):
    monkeypatch.setattr(settings, "identity_encryption_key", "synthetic-test-encryption-key-32-bytes-min")
    monkeypatch.setattr(settings, "identity_lookup_key", "synthetic-test-lookup-key-32-bytes-min")


def test_registration_verification_enrollment_login_and_recovery(monkeypatch):
    _configure_identity_keys(monkeypatch)
    identifier = f"person-{uuid4().hex}@maalenex.invalid"
    original_password = "Synthetic-Account-Password-2026!"
    recovered_password = "Synthetic-Recovered-Password-2026!"

    with SessionLocal.begin() as db:
        account, verification_token = register_account(
            db, display_name="Synthetic account", identifier_type="email",
            identifier_value=identifier,
        )
        assert account.status == "pending"
        stored_identifier = db.scalar(select(AccountIdentifier).where(
            AccountIdentifier.account_id == account.id
        ))
        assert stored_identifier is not None
        assert identifier.encode() not in stored_identifier.encrypted_value
        assert decrypt_identifier("email", stored_identifier.encrypted_value) == identifier

        verified_account, enrollment_token = verify_identifier(
            db, raw_token=verification_token
        )
        assert verified_account.status == "active"
        account_id = enroll_password(
            db, raw_token=enrollment_token, password=original_password
        )
        assert account_id == account.id

        authenticated, session, raw_session, _csrf = authenticate_account(
            db, identifier_type="email", identifier_value=identifier,
            password=original_password, client_ip="127.0.0.1",
        )
        assert authenticated.id == account.id
        assert session.secret_digest != raw_session
        resolved_account, resolved_session = resolve_account_session(db, raw_session)
        assert resolved_account.id == account.id
        assert resolved_session.id == session.id

        recovery_token = request_password_recovery(
            db, identifier_type="email", identifier_value=identifier
        )
        assert recovery_token
        recovered_id = complete_password_recovery(
            db, raw_token=recovery_token, new_password=recovered_password
        )
        assert recovered_id == account.id
        with pytest.raises(AccountAuthenticationError):
            resolve_account_session(db, raw_session)

        with pytest.raises(ValueError, match="invalid or expired"):
            complete_password_recovery(
                db, raw_token=recovery_token, new_password="Another-Password-2026!"
            )

        new_account, _new_session, _new_raw, _new_csrf = authenticate_account(
            db, identifier_type="email", identifier_value=identifier,
            password=recovered_password, client_ip="127.0.0.1",
        )
        assert new_account.id == account.id


def test_identifier_normalization_and_ethiopian_phone_format(monkeypatch):
    _configure_identity_keys(monkeypatch)
    from app.domains.identity.account_service import normalize_identifier

    assert normalize_identifier("email", "  PERSON@Example.COM ") == "person@example.com"
    assert normalize_identifier("phone", "0911 234 567") == "+251911234567"
    assert normalize_identifier("phone", "+251 911-234-567") == "+251911234567"
    with pytest.raises(ValueError):
        normalize_identifier("phone", "not-a-number")


def test_challenge_resend_cooldown_hourly_limit_and_token_rotation(monkeypatch):
    from app.domains.identity.accounts import AccountChallengeRequest
    from app.domains.identity.account_service import resend_account_challenge, _now

    _configure_identity_keys(monkeypatch)
    identifier = f"resend-{uuid4().hex}@maalenex.invalid"
    with SessionLocal.begin() as db:
        account, original_token = register_account(
            db, display_name="Synthetic resend account", identifier_type="email",
            identifier_value=identifier,
        )
        first = resend_account_challenge(
            db, identifier_type="email", identifier_value=identifier,
            purpose="identifier_verification", client_ip="192.0.2.10",
        )
        assert first is not None
        assert first[0].id == account.id
        rotated_token = first[1]
        assert rotated_token != original_token

        # Immediate resend is blocked by the 60-second cooldown.
        assert resend_account_challenge(
            db, identifier_type="email", identifier_value=identifier,
            purpose="identifier_verification", client_ip="192.0.2.10",
        ) is None

        key = db.query(AccountChallengeRequest).one()
        for _ in range(4):
            key.last_requested_at = _now(db) - timedelta(seconds=61)
            db.flush()
            assert resend_account_challenge(
                db, identifier_type="email", identifier_value=identifier,
                purpose="identifier_verification", client_ip="192.0.2.10",
            ) is not None
        key.last_requested_at = _now(db) - __import__("datetime").timedelta(seconds=61)
        db.flush()
        assert resend_account_challenge(
            db, identifier_type="email", identifier_value=identifier,
            purpose="identifier_verification", client_ip="192.0.2.10",
        ) is None
