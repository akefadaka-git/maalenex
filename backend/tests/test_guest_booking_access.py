from datetime import datetime, timezone
from uuid import uuid4

from app.routers.bookings import _verification_payload

from app.main import app


def test_guest_booking_recovery_support_and_revocation_routes_are_registered():
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/bookings/{booking_id}",
        "/api/v1/bookings/{booking_id}/access/revoke",
        "/api/v1/bookings/{booking_id}/reservation/qr.svg",
        "/api/v1/bookings/{booking_id}/support-cases",
        "/api/v1/passenger-access/challenges",
        "/api/v1/passenger-access/challenges/{challenge_id}/verify",
        "/api/v1/auth/operator-invitations/accept",
    }
    assert expected.issubset(paths)


def test_native_webview_receives_csrf_token_in_verification_payload():
    booking_id = uuid4()
    expiry = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc).isoformat()
    payload = _verification_payload(
        booking_id=booking_id,
        scope="manage",
        expires_at=expiry,
        csrf_token="synthetic-csrf-token",
    )
    assert payload == {
        "booking_id": str(booking_id),
        "scope": "manage",
        "expires_at": expiry,
        "csrf_token": "synthetic-csrf-token",
    }
