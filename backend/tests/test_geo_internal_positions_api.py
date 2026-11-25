from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.domains.geo.security import GeoAuthorizationError
from app.domains.identity.service import StaffContext
from app.main import app
from app.routers import geo as geo_router


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.statement = None
        self.parameters = None
        self.rollback_called = False

    def execute(self, statement, parameters=None):
        self.statement = str(statement)
        self.parameters = parameters or {}
        return FakeResult(self.rows)

    def rollback(self):
        self.rollback_called = True


def _client(monkeypatch, fake_db, authorize):
    user_id = uuid4()
    context = StaffContext(
        user=SimpleNamespace(id=user_id),
        session=SimpleNamespace(id=uuid4()),
    )
    monkeypatch.setattr(geo_router, "authorize_geo_tenant_context", authorize)
    app.dependency_overrides[geo_router.current_staff_context] = lambda: context

    def db_override():
        yield fake_db

    app.dependency_overrides[get_db] = db_override
    return TestClient(app), user_id


def teardown_function():
    app.dependency_overrides.clear()


def test_internal_positions_api_requires_staff_and_tenant_authorization(monkeypatch):
    organization_id = uuid4()
    vehicle_id = uuid4()
    recorded_at = datetime(2026, 11, 25, 7, 0, tzinfo=timezone.utc)
    received_at = datetime(2026, 11, 25, 7, 0, 5, tzinfo=timezone.utc)
    fake_db = FakeSession([{
        "vehicle_id": vehicle_id,
        "longitude": 37.0,
        "latitude": 6.0,
        "recorded_at": recorded_at,
        "received_at": received_at,
        "speed_kph": 12,
        "heading_degrees": 90,
        "accuracy_meters": 5,
        "is_synthetic": True,
    }])
    authorization_calls = []

    def authorize(db, **kwargs):
        authorization_calls.append(kwargs)

    client, user_id = _client(monkeypatch, fake_db, authorize)
    response = client.get(
        "/api/v1/geo/internal/vehicles/positions",
        params={"organization_id": str(organization_id)},
    )

    assert response.status_code == 200
    assert authorization_calls == [{
        "user_id": user_id,
        "organization_id": organization_id,
        "permission_code": "platform.tracking.read",
    }]
    assert fake_db.parameters["organization_id"] == organization_id
    assert "vp.organization_id = :organization_id" in fake_db.statement
    assert "device_id" not in response.json()["positions"][0]
    assert response.json()["positions"][0]["vehicle_id"] == str(vehicle_id)
    assert response.headers["cache-control"] == "no-store, private"


def test_internal_positions_api_fails_closed_without_tracking_permission(monkeypatch):
    organization_id = uuid4()
    fake_db = FakeSession()

    def deny(db, **kwargs):
        raise GeoAuthorizationError("denied")

    client, _ = _client(monkeypatch, fake_db, deny)
    response = client.get(
        "/api/v1/geo/internal/vehicles/positions",
        params={"organization_id": str(organization_id)},
    )

    assert response.status_code == 403
    assert fake_db.statement is None
    assert fake_db.rollback_called is True


def test_internal_positions_api_rejects_missing_staff_session(monkeypatch):
    fake_db = FakeSession()

    def db_override():
        yield fake_db

    def no_session():
        raise HTTPException(status_code=401, detail="Authentication required")

    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[geo_router.current_staff_context] = no_session
    response = TestClient(app).get(
        "/api/v1/geo/internal/vehicles/positions",
        params={"organization_id": str(uuid4())},
    )

    assert response.status_code == 401
    assert fake_db.statement is None
