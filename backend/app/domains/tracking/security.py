"""Authenticated encryption and request-signing primitives for synthetic MITP devices."""
from __future__ import annotations

import hashlib
import hmac
import re

from cryptography.fernet import Fernet, InvalidToken


def _fernet(encryption_key: str) -> Fernet:
    try:
        return Fernet(encryption_key.encode("ascii"))
    except (AttributeError, UnicodeEncodeError, ValueError) as exc:
        raise ValueError("MITP device encryption key must be a valid Fernet key") from exc


def encrypt_credential(raw_credential: str, encryption_key: str) -> str:
    if len(raw_credential) < 32:
        raise ValueError("device credential must contain at least 32 characters")
    return _fernet(encryption_key).encrypt(raw_credential.encode("utf-8")).decode("ascii")


def decrypt_credential(ciphertext: str, encryption_key: str) -> str:
    try:
        return _fernet(encryption_key).decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError, AttributeError) as exc:
        raise ValueError("stored device credential cannot be decrypted") from exc


def sign_telemetry(raw_credential: str, request_timestamp: str, body: bytes) -> str:
    """Sign timestamp and exact request bytes; the raw credential is never stored."""
    message = request_timestamp.encode("ascii") + b"\n" + body
    return hmac.new(raw_credential.encode("utf-8"), message, hashlib.sha256).hexdigest()


def verify_telemetry_signature(
    raw_credential: str,
    request_timestamp: str,
    body: bytes,
    supplied_signature: str,
) -> bool:
    if not re.fullmatch(r"[0-9a-fA-F]{64}", supplied_signature or ""):
        return False
    try:
        expected = sign_telemetry(raw_credential, request_timestamp, body)
        return hmac.compare_digest(expected, supplied_signature.lower())
    except (ValueError, UnicodeEncodeError, AttributeError):
        return False
