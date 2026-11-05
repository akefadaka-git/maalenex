import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import app

client = TestClient(app)


def test_health_endpoint_is_available() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "synthetic-development"}


def test_root_discloses_development_and_synthetic_only_status() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "MaaleNex Moto",
        "environment": "development",
        "status": "development",
        "synthetic_data_only": True,
    }


def test_non_development_runtime_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production")


def test_disabling_synthetic_only_mode_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(synthetic_data_only=False)


def test_non_postgresql_database_url_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite+pysqlite:///:memory:")


def test_remote_database_host_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="postgresql+psycopg://maalenex:maalenex@example.com:5432/maalenex_dev")


def test_non_development_database_name_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="postgresql+psycopg://maalenex:maalenex@localhost:5432/production")
