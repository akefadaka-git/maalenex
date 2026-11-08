import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.domains.platform.models import PlatformService, ServiceAreaAvailability
from app.main import app
from scripts.seed_platform_services import seed


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def test_platform_registry_seed_is_idempotent_and_never_advertises_test_as_live():
    seed()
    seed()

    with SessionLocal() as db:
        assert db.scalar(select(func.count(PlatformService.code))) == 8
        assert db.scalar(select(func.count(ServiceAreaAvailability.id))) == 32

    client = TestClient(app)
    response = client.get("/api/v1/platform/services", params={"area_code": "ET-SO-JINKA"})
    assert response.status_code == 200
    services = {item["code"]: item for item in response.json()}
    assert set(services) == {"move", "transit", "delivery", "cargo", "market", "fleet", "business", "pay"}

    transit = services["transit"]
    assert transit["rollout_status"] == "synthetic_test"
    assert transit["availability"] == [{
        "area_code": "ET-SO-JINKA",
        "area_name": "Jinka",
        "availability_status": "synthetic_test",
        "is_enabled": True,
        "is_available": False,
        "synthetic_test_available": True,
    }]
    assert all(
        item["availability"][0]["is_available"] is False
        for item in services.values()
    )


def test_unknown_area_does_not_infer_or_enable_service_availability():
    seed()
    response = TestClient(app).get(
        "/api/v1/platform/services", params={"area_code": "ET-UNKNOWN-AREA"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 8
    assert all(item["availability"] == [] for item in response.json())
