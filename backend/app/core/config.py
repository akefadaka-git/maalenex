import ipaddress
from urllib.parse import urlsplit

from pydantic import model_validator
from sqlalchemy.engine import make_url
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MaaleNex Moto"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://localhost:5432/maalenex_dev"
    cors_origins: str = "http://localhost:5173"
    trusted_proxy_ips: str = ""
    canonical_hosts: str = ""
    synthetic_data_only: bool = True
    secure_cookies: bool = False
    identity_encryption_key: str | None = None
    identity_lookup_key: str | None = None
    identity_expose_test_tokens: bool = False
    identity_email_delivery_enabled: bool = False
    identity_smtp_host: str | None = None
    identity_smtp_port: int = 587
    identity_smtp_username: str | None = None
    identity_smtp_password: str | None = None
    identity_smtp_from_email: str | None = None
    identity_smtp_from_name: str = "MaaleNex"
    identity_smtp_starttls: bool = True
    identity_smtp_use_ssl: bool = False
    identity_smtp_timeout_seconds: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def enforce_development_boundary(self) -> "Settings":
        if self.identity_smtp_port < 1 or self.identity_smtp_port > 65535:
            raise ValueError("IDENTITY_SMTP_PORT must be between 1 and 65535.")
        if self.identity_smtp_timeout_seconds < 1 or self.identity_smtp_timeout_seconds > 30:
            raise ValueError("IDENTITY_SMTP_TIMEOUT_SECONDS must be between 1 and 30.")
        if self.identity_email_delivery_enabled:
            if not self.identity_smtp_host or not self.identity_smtp_from_email:
                raise ValueError("Enabled email delivery requires SMTP host and sender address.")
            if self.identity_smtp_use_ssl and self.identity_smtp_starttls:
                raise ValueError("SMTP implicit SSL and STARTTLS cannot both be enabled.")
            if not self.identity_smtp_use_ssl and not self.identity_smtp_starttls:
                raise ValueError("Enabled email delivery requires STARTTLS or implicit TLS.")
            if bool(self.identity_smtp_username) != bool(self.identity_smtp_password):
                raise ValueError("SMTP username and password must be configured together.")
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

        origins = [item.strip() for item in self.cors_origins.split(",") if item.strip()]
        if not origins:
            raise ValueError("CORS_ORIGINS must contain at least one exact origin.")
        if len({item.lower() for item in origins}) != len(origins):
            raise ValueError("CORS_ORIGINS must not contain duplicate origins.")
        for origin in origins:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path
                or parsed.query
                or parsed.fragment
                or origin == "null"
                or "*" in origin
            ):
                raise ValueError("CORS_ORIGINS entries must be exact HTTP(S) origins without paths or wildcards.")
            if parsed.scheme == "http" and parsed.hostname.lower() not in {
                "localhost", "127.0.0.1", "::1"
            }:
                raise ValueError("CORS_ORIGINS non-loopback origins must use HTTPS.")
            try:
                if parsed.port is not None and not 1 <= parsed.port <= 65535:
                    raise ValueError("CORS origin port is invalid.")
            except ValueError as exc:
                raise ValueError("CORS origin port is invalid.") from exc
        if len({_canonical_origin(item) for item in origins}) != len(origins):
            raise ValueError("CORS_ORIGINS must not contain duplicate normalized origins.")

        proxy_entries = [item.strip() for item in self.trusted_proxy_ips.split(",") if item.strip()]
        if len({item.lower() for item in proxy_entries}) != len(proxy_entries):
            raise ValueError("TRUSTED_PROXY_IPS must not contain duplicates.")
        for entry in proxy_entries:
            try:
                network = ipaddress.ip_network(entry, strict=False)
            except ValueError as exc:
                raise ValueError("TRUSTED_PROXY_IPS must contain valid IP addresses or CIDRs.") from exc
            minimum_prefix = 24 if network.version == 4 else 64
            if network.prefixlen < minimum_prefix:
                raise ValueError(
                    "TRUSTED_PROXY_IPS CIDRs are too broad; use IPv4 /24 or narrower "
                    "and IPv6 /64 or narrower ranges."
                )
        hosts = [item.strip() for item in self.canonical_hosts.split(",") if item.strip()]
        if bool(proxy_entries) != bool(hosts):
            raise ValueError("TRUSTED_PROXY_IPS and CANONICAL_HOSTS must be configured together.")
        if len({item.lower() for item in hosts}) != len(hosts):
            raise ValueError("CANONICAL_HOSTS must not contain duplicates.")
        for host in hosts:
            parsed = urlsplit("//" + host)
            if (
                not parsed.hostname or parsed.username is not None or parsed.password is not None
                or parsed.path or parsed.query or parsed.fragment or "*" in host
            ):
                raise ValueError("CANONICAL_HOSTS entries must be exact host[:port] values.")
            try:
                if parsed.port is not None and not 1 <= parsed.port <= 65535:
                    raise ValueError("CANONICAL_HOSTS port is invalid.")
            except ValueError as exc:
                raise ValueError("CANONICAL_HOSTS port is invalid.") from exc
        return self

    def should_use_secure_cookies(self, request_scheme: str) -> bool:
        """Use explicit policy or a scheme already normalized by trusted-proxy middleware."""
        return self.secure_cookies or request_scheme.lower() == "https"

    @property
    def allowed_origins(self) -> list[str]:
        return [
            _canonical_origin(item)
            for item in self.cors_origins.split(",") if item.strip()
        ]

    @property
    def trusted_proxy_networks(self) -> tuple:
        return tuple(
            ipaddress.ip_network(item.strip(), strict=False)
            for item in self.trusted_proxy_ips.split(",") if item.strip()
        )

    @property
    def allowed_hosts(self) -> frozenset[str]:
        return frozenset(item.strip().lower() for item in self.canonical_hosts.split(",") if item.strip())


settings = Settings()
