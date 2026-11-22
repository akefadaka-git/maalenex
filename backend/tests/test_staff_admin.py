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
