import hashlib
import hmac
import secrets

ITERATIONS = 600_000
SALT_BYTES = 16
DIGEST_BYTES = 32


def hash_secret(secret: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, ITERATIONS)
    return "pbkdf2_sha256$" + str(ITERATIONS) + "$" + salt.hex() + "$" + digest.hex()


def verify_secret(secret: str, encoded: str) -> bool:
    try:
        algorithm, iterations_text, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        # Only accept the exact cost and digest format emitted by hash_secret().
        # This prevents attacker-controlled database values from causing unbounded CPU work.
        if int(iterations_text) != ITERATIONS:
            return False
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)
        if len(salt) != SALT_BYTES or len(expected_digest) != DIGEST_BYTES:
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, ITERATIONS)
        return hmac.compare_digest(candidate, expected_digest)
    except (AttributeError, TypeError, ValueError):
        return False


def issue_opaque_token() -> str:
    return secrets.token_urlsafe(32)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
