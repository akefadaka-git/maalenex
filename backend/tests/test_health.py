from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_is_available() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "synthetic-development"}


def test_root_discloses_development_status() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "development"
