"""Private S3-compatible object storage for synthetic fleet-compliance fixtures."""
from __future__ import annotations

import uuid
from typing import Any
from urllib.parse import urlparse

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {
    "application/pdf": b"%PDF-",
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
PRESIGN_TTL_SECONDS = 300


class StorageNotConfigured(RuntimeError):
    """Raised when object storage has not been explicitly configured."""


class InvalidStoredObject(ValueError):
    """Raised when an uploaded object is missing or fails validation."""


def _client() -> Any:
    if not settings.object_storage_enabled:
        raise StorageNotConfigured("Object storage is disabled.")
    if settings.object_storage_provider != "r2":
        raise StorageNotConfigured("Only the approved R2 provider is supported.")
    if not all((
        settings.object_storage_endpoint_url,
        settings.object_storage_bucket,
        settings.object_storage_access_key_id,
        settings.object_storage_secret_access_key,
    )):
        raise StorageNotConfigured("R2 runtime configuration is incomplete.")

    parsed = urlparse(settings.object_storage_endpoint_url)
    host = (parsed.hostname or "").lower()
    local_endpoint = host in {"localhost", "127.0.0.1", "::1"}
    if not (local_endpoint and parsed.scheme == "http") and not (
        parsed.scheme == "https" and host.endswith(".r2.cloudflarestorage.com")
    ):
        raise StorageNotConfigured("Endpoint must be a local test service or a Cloudflare R2 endpoint.")

    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=settings.object_storage_endpoint_url,
        region_name="auto",
        aws_access_key_id=settings.object_storage_access_key_id,
        aws_secret_access_key=settings.object_storage_secret_access_key,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def create_compliance_upload_intent(
    *, organization_id: str, vehicle_id: str, content_type: str, content_length: int,
) -> dict[str, Any]:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidStoredObject("Only PDF, JPEG and PNG evidence files are accepted.")
    if content_length < 1 or content_length > MAX_UPLOAD_BYTES:
        raise InvalidStoredObject("Evidence file must be between 1 byte and 10 MiB.")

    key = f"fleet-compliance/{organization_id}/{vehicle_id}/{uuid.uuid4().hex}"
    url = _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.object_storage_bucket,
            "Key": key,
            "ContentType": content_type,
            "ContentLength": content_length,
        },
        ExpiresIn=PRESIGN_TTL_SECONDS,
    )
    return {
        "object_key": key,
        "upload_url": url,
        "method": "PUT",
        "content_type": content_type,
        "max_bytes": MAX_UPLOAD_BYTES,
        "expires_in_seconds": PRESIGN_TTL_SECONDS,
    }


def verify_compliance_object(
    *, object_key: str, organization_id: str, vehicle_id: str,
) -> dict[str, Any]:
    expected_prefix = f"fleet-compliance/{organization_id}/{vehicle_id}/"
    if not object_key.startswith(expected_prefix) or ".." in object_key or object_key.endswith("/"):
        raise InvalidStoredObject("Evidence object key is not scoped to this vehicle and operator.")

    client = _client()
    try:
        head = client.head_object(Bucket=settings.object_storage_bucket, Key=object_key)
        length = int(head.get("ContentLength", 0))
        content_type = str(head.get("ContentType", "")).lower()
        if length < 1 or length > MAX_UPLOAD_BYTES:
            raise InvalidStoredObject("Stored evidence size is outside the permitted limit.")
        signature = ALLOWED_CONTENT_TYPES.get(content_type)
        if signature is None:
            raise InvalidStoredObject("Stored evidence media type is not permitted.")
        response = client.get_object(
            Bucket=settings.object_storage_bucket, Key=object_key, Range="bytes=0-15",
        )
        sample = response["Body"].read(16)
        if not sample.startswith(signature):
            raise InvalidStoredObject("Stored evidence file signature does not match its media type.")
    except InvalidStoredObject:
        raise
    except Exception as exc:
        raise InvalidStoredObject("Evidence object could not be verified in private storage.") from exc

    return {"content_type": content_type, "content_length": length}
