from fastapi.routing import APIRoute

from app.main import app


def test_guest_booking_recovery_support_and_revocation_routes_are_registered():
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/bookings/{booking_id}",
        "/api/v1/bookings/{booking_id}/access/revoke",
        "/api/v1/bookings/{booking_id}/support-cases",
        "/api/v1/passenger-access/challenges",
        "/api/v1/passenger-access/challenges/{challenge_id}/verify",
        "/api/v1/auth/operator-invitations/accept",
    }
    assert expected.issubset(paths)

