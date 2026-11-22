from io import BytesIO

import pytest

from app.domains.fleet import object_storage


class FakeS3:
    def __init__(self, *, payload=b"%PDF-1.7 synthetic delivery proof", content_type="application/pdf"):
        self.payload = payload
        self.content_type = content_type
        self.presign_args = None
        self.deleted = []

    def delete_object(self, *, Bucket, Key):
        self.deleted.append((Bucket, Key))

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



def test_cargo_download_url_is_private_and_bounded(fake_s3):
    url = object_storage.create_cargo_delivery_download_url(
        object_key="cargo-delivery/carrier-a/dispatch-a/object-1",
        carrier_organization_id="carrier-a", dispatch_id="dispatch-a",
        expires_in_seconds=60,
    )
    assert url == "https://storage.invalid/presigned-put"
    operation, params, ttl = fake_s3.presign_args
    assert operation == "get_object"
    assert params == {
        "Bucket": "synthetic-private",
        "Key": "cargo-delivery/carrier-a/dispatch-a/object-1",
    }
    assert ttl == 60


@pytest.mark.parametrize("ttl", [0, 301])
def test_cargo_download_url_rejects_unbounded_lifetime(fake_s3, ttl):
    with pytest.raises(ValueError):
        object_storage.create_cargo_delivery_download_url(
            object_key="cargo-delivery/carrier-a/dispatch-a/object-1",
            carrier_organization_id="carrier-a", dispatch_id="dispatch-a",
            expires_in_seconds=ttl,
        )


def test_cargo_delete_targets_only_private_cargo_key(fake_s3):
    key = "cargo-delivery/carrier-a/dispatch-a/object-1"
    object_storage.delete_cargo_delivery_object(
        object_key=key, carrier_organization_id="carrier-a", dispatch_id="dispatch-a",
    )
    assert fake_s3.deleted == [("synthetic-private", key)]


def test_cargo_delete_rejects_path_traversal(fake_s3):
    with pytest.raises(object_storage.InvalidStoredObject):
        object_storage.delete_cargo_delivery_object(
            object_key="cargo-delivery/carrier-a/../other/object-1",
            carrier_organization_id="carrier-a", dispatch_id="dispatch-a",
        )


def test_cargo_verification_storage_outage_is_retryable(monkeypatch):
    class UnavailableS3:
        def head_object(self, **kwargs):
            raise TimeoutError("synthetic timeout")

    monkeypatch.setattr(object_storage, "_client", lambda: UnavailableS3())
    with pytest.raises(object_storage.StorageOperationFailed):
        object_storage.verify_cargo_delivery_object(
            object_key="cargo-delivery/carrier-a/dispatch-a/object-1",
            carrier_organization_id="carrier-a",
            dispatch_id="dispatch-a",
        )


def test_audit_redacts_private_evidence_references():
    from app.domains.audit.service import redact_metadata

    result = redact_metadata({
        "evidence_reference": "cargo-delivery/private/key",
        "object_key": "cargo-delivery/private/key",
        "evidence_id": "synthetic-evidence-id",
    })
    assert result["evidence_reference"] == "[REDACTED]"
    assert result["object_key"] == "[REDACTED]"
    assert result["evidence_id"] == "synthetic-evidence-id"



def test_provisional_retention_uses_calendar_months_and_month_end():
    from datetime import UTC, datetime

    from app.domains.cargo.evidence_lifecycle import add_calendar_months

    assert add_calendar_months(datetime(2026, 1, 31, tzinfo=UTC), 1) == datetime(2026, 2, 28, tzinfo=UTC)
    assert add_calendar_months(datetime(2024, 2, 29, tzinfo=UTC), 24) == datetime(2026, 2, 28, tzinfo=UTC)



def test_cargo_download_and_delete_reject_cross_dispatch_keys(fake_s3):
    key = "cargo-delivery/carrier-a/dispatch-b/object-1"
    with pytest.raises(object_storage.InvalidStoredObject):
        object_storage.create_cargo_delivery_download_url(
            object_key=key, carrier_organization_id="carrier-a",
            dispatch_id="dispatch-a", expires_in_seconds=30,
        )
    with pytest.raises(object_storage.InvalidStoredObject):
        object_storage.delete_cargo_delivery_object(
            object_key=key, carrier_organization_id="carrier-a", dispatch_id="dispatch-a",
        )
