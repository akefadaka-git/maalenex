import hashlib
import hmac
import secrets
ITERATIONS = 600_000
def hash_secret(secret: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, ITERATIONS)
    return "pbkdf2_sha256$" + str(ITERATIONS) + "$" + salt.hex() + "$" + digest.hex()
def verify_secret(secret: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (ValueError, TypeError):
        return False
def issue_opaque_token() -> str:
    return secrets.token_urlsafe(32)
def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
