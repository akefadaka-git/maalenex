from io import BytesIO

import pytest

from app.domains.fleet import object_storage


class FakeS3:
    def __init__(self, *, payload=b"%PDF-1.7 synthetic delivery proof", content_type="application/pdf"):
        self.payload = payload
        self.content_type = content_type
        self.presign_args = None

    def generate_presigned_url(self, operation, *, Params, ExpiresIn):
        self.presign_args = (operation, Params, ExpiresIn)
        return "https://storage.invalid/presigned-put"

    def head_object(self, *, Bucket, Key):
        return {"ContentLength": len(self.payload), "ContentType": self.content_type}

    def get_object(self, *, Bucket, Key, Range):
        return {"Body": BytesIO(self.payload)}


@pytest.fixture
def fake_s3(monkeypatch):
    client = FakeS3()
    monkeypatch.setattr(object_storage, "_client", lambda: client)
    monkeypatch.setattr(object_storage.settings, "object_storage_bucket", "synthetic-private")
    return client


def test_cargo_upload_intent_is_private_short_lived_and_dispatch_scoped(fake_s3):
    result = object_storage.create_cargo_delivery_upload_intent(
        carrier_organization_id="carrier-a",
        dispatch_id="dispatch-a",
        content_type="application/pdf",
        content_length=128,
    )
    assert result["object_key"].startswith("cargo-delivery/carrier-a/dispatch-a/")
    assert result["upload_url"] == "https://storage.invalid/presigned-put"
    assert result["expires_in_seconds"] == 300
    operation, params, ttl = fake_s3.presign_args
    assert operation == "put_object"
    assert params == {
        "Bucket": "synthetic-private",
        "Key": result["object_key"],
        "ContentType": "application/pdf",
        "ContentLength": 128,
    }
    assert ttl == 300


@pytest.mark.parametrize(
    ("content_type", "content_length"),
    [("text/plain", 100), ("application/pdf", 0), ("application/pdf", 10 * 1024 * 1024 + 1)],
)
def test_cargo_upload_intent_rejects_unsupported_type_or_size(fake_s3, content_type, content_length):
    with pytest.raises(object_storage.InvalidStoredObject):
        object_storage.create_cargo_delivery_upload_intent(
            carrier_organization_id="carrier-a",
            dispatch_id="dispatch-a",
            content_type=content_type,
            content_length=content_length,
        )


def test_cargo_delivery_object_verification_checks_signature_and_size(fake_s3):
    result = object_storage.verify_cargo_delivery_object(
        object_key="cargo-delivery/carrier-a/dispatch-a/object-1",
        carrier_organization_id="carrier-a",
        dispatch_id="dispatch-a",
    )
    assert result == {
        "content_type": "application/pdf",
        "content_length": len(fake_s3.payload),
    }


def test_cargo_delivery_object_verification_rejects_cross_dispatch_key(fake_s3):
    with pytest.raises(object_storage.InvalidStoredObject, match="carrier dispatch"):
        object_storage.verify_cargo_delivery_object(
            object_key="cargo-delivery/carrier-a/dispatch-b/object-1",
            carrier_organization_id="carrier-a",
            dispatch_id="dispatch-a",
        )


def test_cargo_delivery_object_verification_rejects_mismatched_signature(monkeypatch):
    fake = FakeS3(payload=b"not a PDF", content_type="application/pdf")
    monkeypatch.setattr(object_storage, "_client", lambda: fake)
    with pytest.raises(object_storage.InvalidStoredObject, match="signature"):
        object_storage.verify_cargo_delivery_object(
            object_key="cargo-delivery/carrier-a/dispatch-a/object-1",
            carrier_organization_id="carrier-a",
            dispatch_id="dispatch-a",
        )
