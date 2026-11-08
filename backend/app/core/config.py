from pydantic import model_validator
from sqlalchemy.engine import make_url
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MaaleNex Moto"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://localhost:5432/maalenex_dev"
    cors_origins: str = "http://localhost:5173"
    synthetic_data_only: bool = True
    secure_cookies: bool = False
    identity_encryption_key: str | None = None
    identity_lookup_key: str | None = None
    identity_expose_test_tokens: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def enforce_development_boundary(self) -> "Settings":
        if self.app_env not in {"development", "test"}:
            raise ValueError("Only development/test environments are permitted in this G1 baseline.")
        if not self.synthetic_data_only:
            raise ValueError("Synthetic-only mode is mandatory in this G1 baseline.")
        database = make_url(self.database_url)
        if database.drivername != "postgresql+psycopg":
            raise ValueError("G1 database configuration must use PostgreSQL with psycopg.")
        if database.host not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("G1 database host must be local; remote databases are prohibited.")
        if database.database != "maalenex_dev":
            raise ValueError("G1 database name must be maalenex_dev.")
        return self

    def should_use_secure_cookies(self, request_scheme: str) -> bool:
        """Honor explicit proxy/TLS deployment configuration without trusting forwarded headers."""
        return self.secure_cookies or request_scheme.lower() == "https"

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
