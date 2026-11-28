import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings, settings
from app.db.session import get_db
from app.main import app

client = TestClient(app)

PRODUCTION_DATABASE_URL = (
    "postgresql+psycopg://maalenex:secret@db.example.net:5432/maalenex"
    "?sslmode=verify-full&sslrootcert=/path/to/provider-ca.pem"
)
PRODUCTION_CORS_ORIGINS = (
    "https://passenger.example.com,https://appassets.androidplatform.net"
)


def production_settings(**overrides) -> Settings:
    values = {
        "app_env": "production",
        "database_url": PRODUCTION_DATABASE_URL,
        "cors_origins": PRODUCTION_CORS_ORIGINS,
        "synthetic_data_only": False,
        "secure_cookies": True,
    }
    values.update(overrides)
    return Settings(**values)


def test_health_endpoint_is_available() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "synthetic-development"}


def test_readiness_endpoint_checks_database(monkeypatch) -> None:
    class ReadyDatabase:
        def execute(self, statement):
            assert str(statement) == "SELECT 1"
            return 1

    def override_database():
        yield ReadyDatabase()

    monkeypatch.setitem(app.dependency_overrides, get_db, override_database)
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "mode": "synthetic-development"}


def test_readiness_endpoint_fails_closed_when_database_is_unavailable(monkeypatch) -> None:
    class UnavailableDatabase:
        def execute(self, statement):
            raise SQLAlchemyError("database unavailable")

    def override_database():
        yield UnavailableDatabase()

    monkeypatch.setitem(app.dependency_overrides, get_db, override_database)
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database readiness check failed."


def test_root_discloses_development_and_synthetic_only_status() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "MaaleNex Moto",
        "environment": settings.app_env,
        "status": "development",
        "synthetic_data_only": True,
    }


def test_production_runtime_requires_explicit_production_configuration() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production")


def test_production_runtime_accepts_remote_tls_postgres_and_https_origins() -> None:
    configured = production_settings()
    assert configured.app_env == "production"
    assert configured.synthetic_data_only is False
    assert configured.secure_cookies is True
    assert configured.allowed_origins == [
        "https://passenger.example.com",
        "https://appassets.androidplatform.net",
    ]


def test_production_runtime_requires_secure_cookies() -> None:
    with pytest.raises(ValidationError):
        production_settings(secure_cookies=False)


def test_production_runtime_requires_tls_database_identity_verification() -> None:
    with pytest.raises(ValidationError):
        production_settings(database_url=PRODUCTION_DATABASE_URL.replace("sslmode=verify-full", "sslmode=require"))
    with pytest.raises(ValidationError):
        production_settings(database_url=PRODUCTION_DATABASE_URL.replace("&sslrootcert=/path/to/provider-ca.pem", ""))


def test_production_runtime_rejects_wildcard_or_insecure_cors_origins() -> None:
    with pytest.raises(ValidationError):
        production_settings(cors_origins="*")
    with pytest.raises(ValidationError):
        production_settings(cors_origins="http://passenger.example.com")


def test_disabling_synthetic_only_mode_is_rejected_in_development() -> None:
    with pytest.raises(ValidationError):
        Settings(synthetic_data_only=False)


def test_non_postgresql_database_url_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite+pysqlite:///:memory:")


def test_remote_database_host_is_rejected_in_development() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url=PRODUCTION_DATABASE_URL)


def test_non_development_database_name_is_rejected_in_development() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="postgresql+psycopg://maalenex:maalenex@localhost:5432/production")
