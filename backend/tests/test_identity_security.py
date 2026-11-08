from app.core.config import settings
from app.domains.identity.security import hash_secret, issue_opaque_token, token_digest, verify_secret

def test_secret_hash_verifies_without_storing_plaintext():
    raw = "synthetic-test-password"
    encoded = hash_secret(raw)
    assert raw not in encoded
    assert verify_secret(raw, encoded)
    assert not verify_secret("wrong-password", encoded)


def test_secret_verification_rejects_untrusted_cost_and_malformed_hash_parameters():
    encoded = hash_secret("synthetic-test-password")
    algorithm, iterations, salt, digest = encoded.split("$")
    assert not verify_secret("synthetic-test-password", f"{algorithm}$999999999999${salt}${digest}")
    assert not verify_secret("synthetic-test-password", f"{algorithm}$1${salt}${digest}")
    assert not verify_secret("synthetic-test-password", f"{algorithm}${iterations}$abcd${digest}")
    assert not verify_secret("synthetic-test-password", f"{algorithm}${iterations}${salt}$abcd")
    assert not verify_secret("synthetic-test-password", "not-a-valid-hash")

def test_secure_cookie_setting_overrides_http_scheme_for_tls_terminating_proxy(monkeypatch):
    monkeypatch.setattr(settings, "secure_cookies", True)
    assert settings.should_use_secure_cookies("http")

def test_https_scheme_always_uses_secure_cookies(monkeypatch):
    monkeypatch.setattr(settings, "secure_cookies", False)
    assert settings.should_use_secure_cookies("https")

def test_opaque_tokens_are_random_and_digest_is_stable():
    first = issue_opaque_token()
    second = issue_opaque_token()
    assert first != second
    assert token_digest(first) == token_digest(first)
    assert token_digest(first) != first
