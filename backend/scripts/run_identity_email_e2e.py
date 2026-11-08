"""Run one controlled synthetic verification-email delivery against an isolated CI database.

The script deliberately never prints the recipient, challenge token, message body,
SMTP credentials, identifier ciphertext, or raw database rows.
"""
import os
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.audit.models import AuditEvent
from app.domains.identity.accounts import AccountChallenge, AccountIdentifier, PlatformAccount
from app.main import app


def main() -> None:
    recipient = os.environ["E2E_RECIPIENT"].strip().casefold()
    allowed = os.environ["E2E_ALLOWED_RECIPIENT"].strip().casefold()
    if recipient != allowed:
        raise SystemExit("FAIL: recipient does not match the Owner-designated test mailbox.")
    if settings.app_env != "test" or not settings.synthetic_data_only:
        raise SystemExit("FAIL: test environment and synthetic-only mode are mandatory.")
    if settings.identity_expose_test_tokens:
        raise SystemExit("FAIL: challenge-token exposure must remain disabled.")
    if not settings.identity_email_delivery_enabled:
        raise SystemExit("FAIL: SMTP delivery is not enabled for this isolated test.")
    if settings.identity_smtp_host != "smtp.gmail.com":
        raise SystemExit("FAIL: only the approved Gmail SMTP host is allowed.")
    if not settings.identity_smtp_username or not settings.identity_smtp_password:
        raise SystemExit("FAIL: SMTP credentials are not configured.")

    display_name = f"MaaleNex Synthetic E2E {uuid4().hex[:10]}"
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/identity/registrations",
            json={
                "display_name": display_name,
                "identifier_type": "email",
                "identifier_value": recipient,
                "preferred_locale": "am-ET",
            },
        )

    if response.status_code != 202:
        raise SystemExit(f"FAIL: registration endpoint returned HTTP {response.status_code}.")
    payload = response.json()
    if payload.get("delivery_status") != "sent":
        raise SystemExit("FAIL: registration flow did not report SMTP acceptance.")
    if payload.get("development_challenge_token") is not None:
        raise SystemExit("FAIL: challenge token was exposed by the registration endpoint.")

    account_id = payload.get("account_id")
    if not account_id:
        raise SystemExit("FAIL: registration response omitted synthetic account ID.")

    with SessionLocal() as db:
        account = db.get(PlatformAccount, account_id)
        if account is None or account.status != "pending":
            raise SystemExit("FAIL: synthetic account was not persisted in pending state.")
        identifier = db.scalar(select(AccountIdentifier).where(
            AccountIdentifier.account_id == account.id,
            AccountIdentifier.identifier_type == "email",
            AccountIdentifier.revoked_at.is_(None),
        ))
        if identifier is None or not identifier.encrypted_value:
            raise SystemExit("FAIL: encrypted email identifier was not persisted.")
        challenge = db.scalar(select(AccountChallenge).where(
            AccountChallenge.account_id == account.id,
            AccountChallenge.purpose == "identifier_verification",
            AccountChallenge.consumed_at.is_(None),
        ))
        if challenge is None or len(challenge.token_digest) != 64:
            raise SystemExit("FAIL: one-time verification challenge was not stored as a digest only.")
        registration_event = db.scalar(select(AuditEvent).where(
            AuditEvent.event_type == "account.registration.created",
            AuditEvent.resource_id == str(account.id),
            AuditEvent.outcome == "success",
        ))
        if registration_event is None:
            raise SystemExit("FAIL: account-registration audit event is missing.")
        delivery_event = db.scalar(select(AuditEvent).where(
            AuditEvent.event_type == "account.challenge.delivery",
            AuditEvent.correlation_id == str(account.id),
        ))
        if delivery_event is None or delivery_event.outcome != "success":
            raise SystemExit("FAIL: successful email-delivery audit event is missing.")
        metadata = delivery_event.metadata_redacted or {}
        if metadata.get("channel") != "email" or metadata.get("provider") != "smtp":
            raise SystemExit("FAIL: email-delivery audit metadata is incomplete.")
        if metadata.get("purpose") != "identifier_verification":
            raise SystemExit("FAIL: audit event purpose does not match verification.")
        if metadata.get("delivery_status") != "sent":
            raise SystemExit("FAIL: audit event does not record SMTP acceptance.")
        if recipient in str(metadata).casefold():
            raise SystemExit("FAIL: recipient address leaked into audit metadata.")
        if any(key in metadata for key in ("token", "password", "secret", "authorization")):
            raise SystemExit("FAIL: sensitive audit metadata key was persisted.")

    print("PASS: synthetic account registration endpoint exercised.")
    print("PASS: one-time verification challenge persisted as a digest only.")
    print("PASS: Gmail SMTP accepted the verification message for the designated mailbox.")
    print("PASS: registration and delivery audit events verified; no recipient or token stored.")
    print("PASS: challenge token exposure disabled; no secrets or message body emitted.")
    print("NOTE: SMTP acceptance is verified; inbox placement/read receipt requires recipient-side confirmation.")


if __name__ == "__main__":
    main()
