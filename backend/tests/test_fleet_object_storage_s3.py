"""Real S3-compatible upload smoke test; enabled only by the S3-compatible local storage CI service."""
from __future__ import annotations

import time
from uuid import uuid4

import httpx
import pytest
from botocore.exceptions import ClientError

from app.domains.fleet import object_storage


@pytest.mark.parametrize(
    ("content_type", "payload"),
    [
        ("application/pdf", b"%PDF-1.7\nMaaleNex synthetic compliance smoke fixture\n"),
        ("image/jpeg", b"\xff\xd8\xff\xe0MaaleNex synthetic JPEG fixture"),
        ("image/png", b"\x89PNG\r\n\x1a\nMaaleNex synthetic PNG fixture"),
    ],
)
def test_real_local_s3_presigned_upload_and_object_verification(
    content_type: str, payload: bytes
) -> None:
    endpoint = object_storage.settings.object_storage_endpoint_url
    bucket = object_storage.settings.object_storage_bucket
    assert object_storage.settings.object_storage_enabled is True
    assert endpoint.startswith("http://127.0.0.1:"), "Smoke test must target local S3-compatible local storage only."
    assert bucket.startswith("maalenex-synthetic-")

    client = None
    for attempt in range(30):
        try:
            client = object_storage._client()
            client.list_buckets()
            break
        except Exception:
            if attempt == 29:
                raise
            time.sleep(2)
    assert client is not None

    bucket_created = False
    try:
        try:
            client.create_bucket(Bucket=bucket)
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") not in {
                "BucketAlreadyOwnedByYou", "BucketAlreadyExists"
            }:
                raise
        bucket_created = True

        organization_id = f"synthetic-org-{uuid4().hex}"
        vehicle_id = f"synthetic-vehicle-{uuid4().hex}"
        intent = object_storage.create_compliance_upload_intent(
            organization_id=organization_id,
            vehicle_id=vehicle_id,
            content_type=content_type,
            content_length=len(payload),
        )

        response = httpx.put(
            intent["upload_url"],
            content=payload,
            headers={"Content-Type": content_type},
            timeout=20,
        )
        assert response.status_code in {200, 204}, response.text

        verified = object_storage.verify_compliance_object(
            object_key=intent["object_key"],
            organization_id=organization_id,
            vehicle_id=vehicle_id,
        )
        assert verified == {
            "content_type": content_type,
            "content_length": len(payload),
        }

        downloaded = client.get_object(Bucket=bucket, Key=intent["object_key"])
        try:
            assert downloaded["Body"].read() == payload
        finally:
            downloaded["Body"].close()

        with pytest.raises(object_storage.InvalidStoredObject, match="scoped"):
            object_storage.verify_compliance_object(
                object_key=intent["object_key"],
                organization_id="different-synthetic-org",
                vehicle_id=vehicle_id,
            )
    finally:
        # This dedicated CI bucket is disposable and contains synthetic fixtures only.
        if bucket_created:
            for item in client.list_objects_v2(Bucket=bucket).get("Contents", []):
                client.delete_object(Bucket=bucket, Key=item["Key"])
            client.delete_bucket(Bucket=bucket)
