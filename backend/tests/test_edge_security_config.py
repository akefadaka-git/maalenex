import asyncio
import ipaddress

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.core.config import Settings, settings
from app.core.proxy import TrustedProxyMiddleware
from app.core.request_security import require_allowed_origin


def _settings(**overrides):
    return Settings(_env_file=None, **overrides)


def test_smtp_delivery_requires_transport_tls():
    with pytest.raises(ValueError, match="requires STARTTLS or implicit TLS"):
        _settings(
            identity_email_delivery_enabled=True,
            identity_smtp_host="smtp.example.test",
            identity_smtp_from_email="noreply@example.test",
            identity_smtp_starttls=False,
            identity_smtp_use_ssl=False,
        )


def test_smtp_delivery_accepts_starttls():
    configured = _settings(
        identity_email_delivery_enabled=True,
        identity_smtp_host="smtp.example.test",
        identity_smtp_from_email="noreply@example.test",
        identity_smtp_starttls=True,
        identity_smtp_use_ssl=False,
    )
    assert configured.identity_smtp_starttls is True


@pytest.mark.parametrize("origin", ["*", "null", "https://example.test/path",
                                     "http://example.test", "https://*.example.test"])
def test_cors_rejects_non_exact_or_insecure_origins(origin):
    with pytest.raises(ValueError, match="CORS_ORIGINS"):
        _settings(cors_origins=origin)


def test_proxy_allowlist_rejects_world_wide_network():
    with pytest.raises(ValueError, match="entire address family"):
        _settings(trusted_proxy_ips="0.0.0.0/0", canonical_hosts="api.example.test")


def test_proxy_allowlist_and_canonical_hosts_are_paired():
    with pytest.raises(ValueError, match="configured together"):
        _settings(trusted_proxy_ips="10.0.0.10")


def test_non_development_runtime_remains_blocked():
    with pytest.raises(ValueError, match="Only development/test"):
        _settings(app_env="production")


def test_secure_cookie_policy_requires_secure_scheme_or_explicit_setting():
    assert settings.should_use_secure_cookies("http") is False
    assert settings.should_use_secure_cookies("https") is True
    assert _settings(secure_cookies=True).should_use_secure_cookies("http") is True


def _request(origin=None):
    headers = []
    if origin is not None:
        headers.append((b"origin", origin.encode("latin-1")))
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    })


def test_cookie_mutation_requires_exact_allowed_origin():
    require_allowed_origin(_request("http://localhost:5173"))
    with pytest.raises(HTTPException) as denied:
        require_allowed_origin(_request("https://attacker.example"))
    assert denied.value.status_code == 403
    with pytest.raises(HTTPException) as missing:
        require_allowed_origin(_request())
    assert missing.value.status_code == 403


def _run_middleware(peer, headers):
    captured = {"status": None, "scope": None, "headers": None}

    async def app(scope, receive, send):
        captured["scope"] = scope
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            captured["status"] = message["status"]
            captured["headers"] = message.get("headers", [])

    middleware = TrustedProxyMiddleware(
        app,
        trusted_proxy_networks=(ipaddress.ip_network("10.0.0.0/8"),),
        canonical_hosts=frozenset({"api.example.test"}),
    )
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": headers,
        "client": (peer, 54321),
        "server": ("internal", 8000),
    }
    asyncio.run(middleware(scope, receive, send))
    return captured


def test_untrusted_peer_cannot_spoof_https_or_host():
    result = _run_middleware(
        "198.51.100.20",
        [
            (b"host", b"api.example.test"),
            (b"x-forwarded-proto", b"https"),
            (b"x-forwarded-host", b"api.example.test"),
        ],
    )
    assert result["status"] == 204
    assert result["scope"]["scheme"] == "http"
    assert all(key.lower() != b"x-forwarded-proto"
               for key, _ in result["scope"]["headers"])
    assert all(key.lower() != b"x-forwarded-host"
               for key, _ in result["scope"]["headers"])


def test_trusted_proxy_sets_https_only_after_peer_validation_and_sanitizes_headers():
    result = _run_middleware(
        "10.0.0.15",
        [
            (b"host", b"internal"),
            (b"x-forwarded-proto", b"https"),
            (b"x-forwarded-host", b"api.example.test"),
            (b"x-forwarded-for", b"203.0.113.9"),
        ],
    )
    assert result["status"] == 204
    assert result["scope"]["scheme"] == "https"
    assert settings.should_use_secure_cookies(result["scope"]["scheme"]) is True
    assert (b"host", b"api.example.test") in result["scope"]["headers"]
    assert not any(key.lower().startswith(b"x-forwarded-")
                   for key, _ in result["scope"]["headers"])
    response_headers = dict(result["headers"])
    assert response_headers[b"x-content-type-options"] == b"nosniff"
    assert response_headers[b"x-frame-options"] == b"DENY"


def test_trusted_proxy_rejects_duplicate_or_downgrade_forwarded_scheme():
    for values in ([b"https", b"https"], [b"http"], [b"https,http"]):
        headers = [(b"host", b"api.example.test")]
        headers.extend((b"x-forwarded-proto", value) for value in values)
        result = _run_middleware("10.0.0.15", headers)
        assert result["status"] == 400


def test_trusted_proxy_rejects_unapproved_forwarded_host():
    result = _run_middleware(
        "10.0.0.15",
        [
            (b"host", b"internal"),
            (b"x-forwarded-proto", b"https"),
            (b"x-forwarded-host", b"attacker.example"),
        ],
    )
    assert result["status"] == 400

def test_cors_middleware_reflects_only_exact_allowed_origin():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )

    @app.get("/probe")
    def probe():
        return {"ok": True}

    client = TestClient(app)
    allowed = client.get("/probe", headers={"Origin": "http://localhost:5173"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert allowed.headers["access-control-allow-credentials"] == "true"
    assert "origin" in allowed.headers.get("vary", "").lower()

    denied = client.get("/probe", headers={"Origin": "https://localhost:5173.attacker.test"})
    assert "access-control-allow-origin" not in denied.headers

def test_trusted_proxy_without_https_metadata_does_not_upgrade_scheme():
    result = _run_middleware(
        "10.0.0.15",
        [(b"host", b"api.example.test")],
    )
    assert result["status"] == 204
    assert result["scope"]["scheme"] == "http"
    assert settings.should_use_secure_cookies(result["scope"]["scheme"]) is False


def test_canonical_host_configuration_rejects_wildcards():
    with pytest.raises(ValueError, match="CANONICAL_HOSTS"):
        _settings(trusted_proxy_ips="10.0.0.10", canonical_hosts="*.example.test")


def test_allowed_origins_are_normalized_to_browser_origin_form():
    configured = _settings(cors_origins="HTTPS://Example.Test:443")
    assert configured.allowed_origins == ["https://example.test"]
