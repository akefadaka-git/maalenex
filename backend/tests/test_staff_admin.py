from fastapi.testclient import TestClient

from app.main import app


def test_staff_admin_routes_are_registered():
    paths = app.openapi()["paths"]
    assert {
        "/api/v1/admin/dashboard",
        "/api/v1/admin/access/roles",
        "/api/v1/admin/access/users",
        "/api/v1/admin/access/users/{user_id}/roles",
        "/api/v1/admin/access/role-assignments/{assignment_id}",
        "/api/v1/admin/operations/scheduler",
        "/api/v1/catalog/locations",
        "/api/v1/catalog/terminals",
        "/api/v1/catalog/routes",
        "/api/v1/catalog/routes/{route_id}/stops",
        "/api/v1/catalog/locations/{location_id}",
        "/api/v1/catalog/terminals/{terminal_id}",
        "/api/v1/catalog/routes/{route_id}",
        "/api/v1/catalog/locations/{location_id}/archive",
        "/api/v1/catalog/terminals/{terminal_id}/archive",
        "/api/v1/catalog/routes/{route_id}/archive",
        "/api/v1/admin/fleet/vehicles",
        "/api/v1/operators/{organization_id}/fleet",
        "/api/v1/vehicles/{vehicle_id}/seat-layouts",
        "/api/v1/vehicles/{vehicle_id}",
        "/api/v1/seat-layouts/{layout_id}",
        "/api/v1/operators/{organization_id}/dispatch/options",
        "/api/v1/operators/{organization_id}/trips",
        "/api/v1/admin/dispatch/trips",
    }.issubset(paths)


def test_staff_admin_dashboard_requires_staff_session():
    client = TestClient(app)
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401


def test_staff_role_catalog_requires_staff_session():
    client = TestClient(app)
    response = client.get("/api/v1/admin/access/roles")
    assert response.status_code == 401


def test_catalog_lists_require_staff_session():
    client = TestClient(app)
    for path in (
        "/api/v1/catalog/locations",
        "/api/v1/catalog/terminals",
        "/api/v1/catalog/routes",
    ):
        response = client.get(path)
        assert response.status_code == 401


def test_catalog_permission_checks_fail_closed(monkeypatch):
    from types import SimpleNamespace
    from uuid import uuid4

    import pytest
    from fastapi import HTTPException

    from app.routers import admin

    checked = []

    def deny_permission(_db, **kwargs):
        checked.append(kwargs["permission_code"])
        return False

    monkeypatch.setattr(admin, "has_permission", deny_permission)
    context = SimpleNamespace(user=SimpleNamespace(id=uuid4()))

    for permission in ("platform.catalog.manage", "platform.catalog.publish"):
        with pytest.raises(HTTPException) as error:
            admin._authorize(object(), context, permission)
        assert error.value.status_code == 403

    assert checked == ["platform.catalog.manage", "platform.catalog.publish"]


def test_catalog_mutations_require_staff_session():
    client = TestClient(app)
    paths = (
        ("/api/v1/catalog/locations/00000000-0000-0000-0000-000000000001", "PATCH"),
        ("/api/v1/catalog/terminals/00000000-0000-0000-0000-000000000001", "PATCH"),
        ("/api/v1/catalog/routes/00000000-0000-0000-0000-000000000001", "PATCH"),
        ("/api/v1/catalog/routes/00000000-0000-0000-0000-000000000001/stops", "PUT"),
        ("/api/v1/catalog/locations/00000000-0000-0000-0000-000000000001/archive", "POST"),
        ("/api/v1/catalog/terminals/00000000-0000-0000-0000-000000000001/archive", "POST"),
        ("/api/v1/catalog/routes/00000000-0000-0000-0000-000000000001/archive", "POST"),
    )
    for path, method in paths:
        response = client.request(method, path, json={})
        assert response.status_code == 401


def test_catalog_manager_seed_grants_manage_and_publish():
    import importlib.util
    from pathlib import Path

    migration_path = Path(__file__).parents[1] / "migrations" / "versions" / "0015_scheduler_operations_rbac.py"
    spec = importlib.util.spec_from_file_location("scheduler_operations_rbac", migration_path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    grants = set(migration.ROLE_GRANTS["platform_catalog_manager"])
    assert {"platform.catalog.manage", "platform.catalog.publish"}.issubset(grants)
    assert "platform.catalog.manage" in migration.ROLE_GRANTS["platform_operations_manager"]
    assert "operator.fleet.manage" in migration.ROLE_GRANTS["operator_fleet_manager"]
    assert "platform.fleet.review" in migration.ROLE_GRANTS["platform_fleet_reviewer"]


def test_fleet_read_routes_require_staff_session():
    client = TestClient(app)
    for path in (
        "/api/v1/admin/fleet/vehicles",
        "/api/v1/operators/00000000-0000-0000-0000-000000000001/fleet",
        "/api/v1/vehicles/00000000-0000-0000-0000-000000000001/seat-layouts",
    ):
        response = client.get(path)
        assert response.status_code == 401


def test_operator_fleet_permission_is_organization_scoped(monkeypatch):
    from types import SimpleNamespace
    from uuid import uuid4

    import pytest
    from fastapi import HTTPException

    from app.routers import admin

    organization_id = uuid4()
    calls = []

    def deny_permission(_db, **kwargs):
        calls.append(kwargs)
        return False

    monkeypatch.setattr(admin, "has_permission", deny_permission)
    context = SimpleNamespace(user=SimpleNamespace(id=uuid4()))
    with pytest.raises(HTTPException) as error:
        admin._authorize(object(), context, "operator.fleet.manage", organization_id)
    assert error.value.status_code == 403
    assert calls[0]["permission_code"] == "operator.fleet.manage"
    assert calls[0]["organization_id"] == organization_id


def test_fleet_draft_mutations_require_staff_session():
    client = TestClient(app)
    paths = (
        ("/api/v1/vehicles/00000000-0000-0000-0000-000000000001", "PATCH"),
        ("/api/v1/seat-layouts/00000000-0000-0000-0000-000000000001", "PUT"),
    )
    for path, method in paths:
        response = client.request(method, path, json={})
        assert response.status_code == 401


def test_structured_seat_layout_request_supports_seat_positions():
    from app.routers.admin import SeatLayoutCreate

    payload = SeatLayoutCreate(seats=[
        {"seat_code": "A1", "row_label": "A", "column_index": 0, "seat_type": "standard"},
        {"seat_code": "A2", "row_label": "A", "column_index": 1, "seat_type": "accessible", "is_sellable": False},
    ])
    assert len(payload.seats) == 2
    assert payload.seats[1].seat_type == "accessible"
    assert payload.seats[1].is_sellable is False


def test_dispatch_read_routes_require_staff_session():
    client = TestClient(app)
    paths = (
        "/api/v1/operators/00000000-0000-0000-0000-000000000001/dispatch/options",
        "/api/v1/operators/00000000-0000-0000-0000-000000000001/trips",
        "/api/v1/admin/dispatch/trips",
    )
    for path in paths:
        response = client.get(path)
        assert response.status_code == 401


def test_operator_trip_permission_is_organization_scoped(monkeypatch):
    from types import SimpleNamespace
    from uuid import uuid4

    import pytest
    from fastapi import HTTPException

    from app.routers import admin

    organization_id = uuid4()
    calls = []

    def deny_permission(_db, **kwargs):
        calls.append(kwargs)
        return False

    monkeypatch.setattr(admin, "has_permission", deny_permission)
    context = SimpleNamespace(user=SimpleNamespace(id=uuid4()))
    with pytest.raises(HTTPException) as error:
        admin._authorize(object(), context, "operator.trip.manage", organization_id)
    assert error.value.status_code == 403
    assert calls[0]["permission_code"] == "operator.trip.manage"
    assert calls[0]["organization_id"] == organization_id


def test_dispatch_roles_receive_expected_trip_permissions():
    import importlib.util
    from pathlib import Path

    migration_path = Path(__file__).parents[1] / "migrations" / "versions" / "0015_scheduler_operations_rbac.py"
    spec = importlib.util.spec_from_file_location("scheduler_operations_rbac_dispatch", migration_path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert {"operator.trip.manage", "operator.trip.manifest.read"}.issubset(
        set(migration.ROLE_GRANTS["operator_dispatcher"])
    )
    assert {"platform.trip.approve", "platform.trip.publish"}.issubset(
        set(migration.ROLE_GRANTS["platform_dispatch_manager"])
    )
