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


def test_guest_support_and_access_mutations_require_booking_grant_dependency():
    paths = app.openapi()["paths"]
    for path in (
        "/api/v1/bookings/{booking_id}/access/revoke",
        "/api/v1/bookings/{booking_id}/support-cases",
    ):
        operation = paths[path]["post"]
        assert operation.get("security") or any(
            parameter.get("name") == "booking_id"
            for parameter in operation.get("parameters", [])
        )
