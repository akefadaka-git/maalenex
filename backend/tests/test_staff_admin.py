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
    }.issubset(paths)


def test_staff_admin_dashboard_requires_staff_session():
    client = TestClient(app)
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401


def test_staff_role_catalog_requires_staff_session():
    client = TestClient(app)
    response = client.get("/api/v1/admin/access/roles")
    assert response.status_code == 401
