from urllib.parse import urlsplit

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    app_name: str = "MaaleNex Moto"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://localhost:5432/maalenex_dev"
    cors_origins: str = "http://localhost:5173,https://appassets.androidplatform.net"
    synthetic_data_only: bool = True
    secure_cookies: bool = False
    scheduler_enabled: bool = False
    scheduler_interval_seconds: int = 30
    scheduler_lease_seconds: int = 90
    scheduler_batch_size: int = 100
    cargo_evidence_orphan_grace_hours: int = 0
    object_storage_enabled: bool = False
    object_storage_provider: str = "r2"
    object_storage_endpoint_url: str = ""
    object_storage_bucket: str = ""
    object_storage_access_key_id: str = ""
    object_storage_secret_access_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def enforce_runtime_boundary(self) -> "Settings":
        self.app_env = self.app_env.strip().lower()
        if self.app_env not in {"development", "test", "production"}:
            raise ValueError("APP_ENV must be development, test or production.")

        database = make_url(self.database_url)
        if database.drivername != "postgresql+psycopg":
            raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver.")

        if self.app_env in {"development", "test"}:
            if not self.synthetic_data_only:
                raise ValueError("Synthetic-only mode is mandatory in development/test.")
            if database.host not in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("Development/test database host must be local.")
            if database.database != "maalenex_dev":
                raise ValueError("Development/test database name must be maalenex_dev.")
        else:
            if self.synthetic_data_only:
                raise ValueError("Production must explicitly disable synthetic-only mode.")
            if not self.secure_cookies:
                raise ValueError("Production must enable SECURE_COOKIES.")
            if database.host in {None, "localhost", "127.0.0.1", "::1"}:
                raise ValueError("Production requires a remote managed PostgreSQL database.")
            if database.database in {None, "maalenex_dev"}:
                raise ValueError("Production must not use the development database.")
            if not database.username or not database.password:
                raise ValueError("Production DATABASE_URL must include database credentials.")
            sslmode = database.query.get("sslmode")
            if sslmode not in {"require", "verify-ca", "verify-full"}:
                raise ValueError("Production PostgreSQL must require TLS using sslmode=require or stronger.")
            origins = self.allowed_origins
            if not origins:
                raise ValueError("Production must explicitly configure CORS_ORIGINS.")
            for origin in origins:
                parsed = urlsplit(origin)
                if (
                    parsed.scheme != "https"
                    or not parsed.netloc
                    or parsed.username
                    or parsed.password
                    or parsed.path
                    or parsed.query
                    or parsed.fragment
                    or "*" in origin
                ):
                    raise ValueError("Production CORS origins must be exact HTTPS origins without paths or wildcards.")

        if not 5 <= self.scheduler_interval_seconds <= 3600:
            raise ValueError("Scheduler interval must be between 5 and 3600 seconds.")
        if self.scheduler_lease_seconds < self.scheduler_interval_seconds * 2:
            raise ValueError("Scheduler lease must be at least twice the polling interval.")
        if not 1 <= self.scheduler_batch_size <= 1000:
            raise ValueError("Scheduler batch size must be between 1 and 1000.")
        if self.cargo_evidence_orphan_grace_hours < 0:
            raise ValueError("Cargo evidence orphan grace hours cannot be negative; zero disables orphan deletion.")
        if self.object_storage_enabled and not all((
            self.object_storage_endpoint_url,
            self.object_storage_bucket,
            self.object_storage_access_key_id,
            self.object_storage_secret_access_key,
        )):
            raise ValueError("Enabled object storage requires endpoint, bucket and credentials.")
        return self

    def should_use_secure_cookies(self, request_scheme: str) -> bool:
        """Honor explicit TLS configuration without trusting arbitrary forwarded headers."""
        return self.secure_cookies or request_scheme.lower() == "https"

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
