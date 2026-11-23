"""Device request signing primitives; raw device credentials are never persisted."""
from __future__ import annotations

import hashlib
import hmac


def credential_digest(raw_credential: str) -> str:
    if len(raw_credential) < 32:
        raise ValueError("device credential must contain at least 32 characters")
    return hashlib.sha256(raw_credential.encode("utf-8")).hexdigest()


def sign_telemetry(raw_credential: str, request_timestamp: str, body: bytes) -> str:
    """Sign timestamp and exact request bytes using the digest-derived HMAC key."""
    key = bytes.fromhex(credential_digest(raw_credential))
    message = request_timestamp.encode("ascii") + b"\n" + body
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def verify_telemetry_signature(
    stored_credential_digest: str,
    request_timestamp: str,
    body: bytes,
    supplied_signature: str,
) -> bool:
    try:
        key = bytes.fromhex(stored_credential_digest)
        if len(key) != hashlib.sha256().digest_size:
            return False
        message = request_timestamp.encode("ascii") + b"\n" + body
        expected = hmac.new(key, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, supplied_signature.lower())
    except (ValueError, UnicodeEncodeError, AttributeError):
        return False
