from app.domains.identity.security import hash_secret, issue_opaque_token, token_digest, verify_secret

def test_secret_hash_verifies_without_storing_plaintext():
    raw = "synthetic-test-password"
    encoded = hash_secret(raw)
    assert raw not in encoded
    assert verify_secret(raw, encoded)
    assert not verify_secret("wrong-password", encoded)

def test_opaque_tokens_are_random_and_digest_is_stable():
    first = issue_opaque_token()
    second = issue_opaque_token()
    assert first != second
    assert token_digest(first) == token_digest(first)
    assert token_digest(first) != first
