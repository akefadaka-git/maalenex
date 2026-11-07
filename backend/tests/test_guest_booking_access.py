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


def test_guest_support_and_access_routes_require_booking_grant_dependency():
    protected_paths = {
        "/api/v1/bookings/{booking_id}/access/revoke",
        "/api/v1/bookings/{booking_id}/support-cases",
        "/api/v1/bookings/{booking_id}/support-cases",
    }
    routes = [
        route for route in app.routes
        if isinstance(route, APIRoute) and route.path in protected_paths
    ]
    assert routes
    for route in routes:
        dependency_names = {
            getattr(dependency.call, "__name__", "")
            for dependency in route.dependant.dependencies
        }
        assert "current_booking_grant" in dependency_names, route.path
