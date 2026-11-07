from fastapi.routing import APIRoute

from app.main import app


def test_administration_router_is_registered_under_api_prefix():
    routes = [
        route for route in app.routes
        if isinstance(route, APIRoute) and "platform-administration" in route.tags
    ]
    assert routes
    paths = {route.path for route in routes}
    assert "/api/v1/operators" in paths
    assert "/api/v1/catalog/routes" in paths
    assert "/api/v1/vehicles/{vehicle_id}/review" in paths
    assert "/api/v1/trips/{trip_id}/publish" in paths
    assert "/api/v1/fares/{fare_id}/versions/{version_id}/review" in paths
    assert "/api/v1/audit/events" in paths


def test_every_administration_route_requires_staff_session_context():
    routes = [
        route for route in app.routes
        if isinstance(route, APIRoute) and "platform-administration" in route.tags
    ]
    for route in routes:
        dependency_names = {
            getattr(dependency.call, "__name__", "")
            for dependency in route.dependant.dependencies
        }
        assert "current_staff_context" in dependency_names, route.path
