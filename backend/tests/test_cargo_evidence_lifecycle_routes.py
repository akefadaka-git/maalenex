# ruff: noqa: I001
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException
import pytest

from app.jobs import cargo_evidence_cleanup
from app.routers import cargo_evidence_lifecycle as routes


class FakeDB:
    def __init__(self, *, gets=None, scalars=None):
        self.gets = gets or {}
        self.scalar_values = list(scalars or [])
        self.added = []
        self.commits = 0

    def get(self, model, key):
        return self.gets.get((model.__name__, key))

    def scalar(self, statement):
        return self.scalar_values.pop(0) if self.scalar_values else None

    def add(self, value):
        self.added.append(value)

    def flush(self):
        return None

    def commit(self):
        self.commits += 1


def actor(user_id=None):
    return SimpleNamespace(user=SimpleNamespace(id=user_id or uuid4()))


def test_platform_download_requires_both_permission_and_active_case_grant(monkeypatch):
    evidence_id, user_id = uuid4(), uuid4()
    evidence = SimpleNamespace(
        id=evidence_id, carrier_organization_id=uuid4(), dispatch_id=uuid4(),
        lifecycle_state="attached", storage_deleted_at=None,
        object_key="cargo-delivery/carrier/dispatch/evidence.pdf",
    )
    dispatch = SimpleNamespace(carrier_organization_id=evidence.carrier_organization_id)
    db = FakeDB(
        gets={
            ("CargoDeliveryEvidence", evidence_id): evidence,
            ("CargoDispatch", evidence.dispatch_id): dispatch,
        },
        scalars=[None],
    )
    monkeypatch.setattr(routes, "_allowed", lambda _db, _ctx, code, organization_id=None:
                        code == "platform.cargo.delivery_proof.evidence.read")
    monkeypatch.setattr(routes, "_audit", lambda *args, **kwargs: None)
    with pytest.raises(HTTPException) as error:
        routes.get_private_evidence_download(
            evidence_id, SimpleNamespace(), actor(user_id), db,
        )
    assert error.value.status_code == 403


def test_platform_download_succeeds_only_with_case_grant(monkeypatch):
    evidence_id, user_id = uuid4(), uuid4()
    evidence = SimpleNamespace(
        id=evidence_id, carrier_organization_id=uuid4(), dispatch_id=uuid4(),
        lifecycle_state="attached", storage_deleted_at=None,
        object_key="cargo-delivery/carrier/dispatch/evidence.pdf",
    )
    dispatch = SimpleNamespace(carrier_organization_id=evidence.carrier_organization_id)
    grant = SimpleNamespace(id=uuid4(), user_id=user_id)
    db = FakeDB(
        gets={
            ("CargoDeliveryEvidence", evidence_id): evidence,
            ("CargoDispatch", evidence.dispatch_id): dispatch,
        },
        scalars=[grant],
    )
    monkeypatch.setattr(routes, "_allowed", lambda _db, _ctx, code, organization_id=None:
                        code == "platform.cargo.delivery_proof.evidence.read")
    monkeypatch.setattr(routes, "verify_cargo_delivery_object", lambda **kwargs: {})
    monkeypatch.setattr(routes, "create_cargo_delivery_download_url", lambda **kwargs: "https://private.invalid/short")
    monkeypatch.setattr(routes, "_audit", lambda *args, **kwargs: None)
    result = routes.get_private_evidence_download(
        evidence_id, SimpleNamespace(), actor(user_id), db,
    )
    assert result == {"download_url": "https://private.invalid/short", "expires_in_seconds": 60}


def test_dpo_cannot_review_own_legal_hold(monkeypatch):
    user_id, hold_id = uuid4(), uuid4()
    hold = SimpleNamespace(id=hold_id, issued_by=user_id, released_at=None)
    db = FakeDB(scalars=[hold])
    monkeypatch.setattr(routes, "_allowed", lambda *args, **kwargs: True)
    monkeypatch.setattr(routes, "require_csrf", lambda *args, **kwargs: None)
    with pytest.raises(HTTPException) as error:
        routes.review_evidence_hold(
            hold_id, routes.EvidenceHoldReview(outcome="reviewed", note="Independent review"),
            SimpleNamespace(), actor(user_id), db,
        )
    assert error.value.status_code == 409


def test_retention_deletion_request_fails_closed_without_active_policy(monkeypatch):
    evidence_id, user_id = uuid4(), uuid4()
    evidence = SimpleNamespace(
        id=evidence_id, storage_deleted_at=None, retention_policy_version="provisional",
        classification_status="ordinary", retention_dpo_reviewed_at=datetime.now(UTC),
        retention_expires_at=datetime.now(UTC) - timedelta(days=1),
        accounting_document=False, commercial_correspondence=False,
        dpia_reference="DPIA-TEST-001", dpo_deletion_suspended=False,
        rights_review_status="reviewed",
    )
    db = FakeDB(scalars=[evidence, None, None])
    monkeypatch.setattr(routes, "_allowed", lambda *args, **kwargs: True)
    monkeypatch.setattr(routes, "require_csrf", lambda *args, **kwargs: None)
    with pytest.raises(HTTPException) as error:
        routes.request_evidence_deletion(
            evidence_id, routes.EvidenceDeletionRequestCreate(reason="Retention period elapsed"),
            SimpleNamespace(), actor(user_id), db,
        )
    assert error.value.status_code == 409
    assert not db.added


def test_deletion_approval_requires_a_distinct_second_person(monkeypatch):
    user_id, request_id = uuid4(), uuid4()
    item = SimpleNamespace(id=request_id, status="requested", requested_by=user_id)
    db = FakeDB(scalars=[item])
    monkeypatch.setattr(routes, "_allowed", lambda *args, **kwargs: True)
    monkeypatch.setattr(routes, "require_csrf", lambda *args, **kwargs: None)
    with pytest.raises(HTTPException) as error:
        routes.approve_and_execute_evidence_deletion(
            request_id, routes.EvidenceDeletionApproval(confirmation="approve"),
            SimpleNamespace(), actor(user_id), db,
        )
    assert error.value.status_code == 409


def test_retention_worker_deletes_only_dispatch_scoped_object(monkeypatch):
    evidence = SimpleNamespace(
        id=uuid4(), lifecycle_state="attached", classification_status="ordinary",
        retention_dpo_reviewed_at=datetime.now(UTC), retention_expires_at=datetime.now(UTC),
        retention_policy_version="active-v1", carrier_organization_id=uuid4(),
        dispatch_id=uuid4(), object_key="cargo-delivery/carrier/dispatch/object",
        storage_deleted_at=None, deletion_failure_code=None,
    )

    class Results:
        def all(self):
            return [evidence]

    class DB:
        def __init__(self):
            self.scalar_values = ["active-v1", None, None]
            self.commits = 0

        def scalars(self, statement):
            return Results()

        def scalar(self, statement):
            return self.scalar_values.pop(0)

        def commit(self):
            self.commits += 1

    captured = {}
    monkeypatch.setattr(cargo_evidence_cleanup, "delete_cargo_delivery_object",
                        lambda **kwargs: captured.update(kwargs))
    monkeypatch.setattr(cargo_evidence_cleanup, "record_event", lambda *args, **kwargs: None)
    result = cargo_evidence_cleanup.process_expired_retention_evidence(
        DB(), now=datetime.now(UTC) + timedelta(seconds=1),
    )
    assert result["deleted"] == 1
    assert captured["carrier_organization_id"] == str(evidence.carrier_organization_id)
    assert captured["dispatch_id"] == str(evidence.dispatch_id)


def test_due_legal_hold_review_is_escalated_once(monkeypatch):
    hold = SimpleNamespace(
        id=uuid4(), evidence_id=uuid4(), released_at=None,
        review_due_at=datetime.now(UTC) - timedelta(minutes=1),
        review_alerted_at=None,
    )

    class Results:
        def all(self):
            return [hold]

    class DB:
        def scalars(self, statement):
            return Results()

        def commit(self):
            return None

    events = []
    monkeypatch.setattr(cargo_evidence_cleanup, "record_event",
                        lambda *args, **kwargs: events.append(kwargs))
    now = datetime.now(UTC)
    result = cargo_evidence_cleanup.alert_due_legal_hold_reviews(DB(), now=now)
    assert result == {"review_due": 1}
    assert hold.review_alerted_at == now
    assert events[0]["event_type"] == "cargo.delivery_evidence.hold_review_due"


def test_cargo_evidence_maintenance_rejects_unsafe_bounds():
    with pytest.raises(ValueError):
        cargo_evidence_cleanup.alert_due_legal_hold_reviews(
            SimpleNamespace(), now=datetime.now(),
        )


def test_legal_hold_release_requires_proceeding_conclusion_and_distinct_releaser(monkeypatch):
    issuer, dpo, releaser, hold_id = uuid4(), uuid4(), uuid4(), uuid4()
    hold = SimpleNamespace(
        id=hold_id, issued_by=issuer, dpo_reviewed_by=dpo,
        dpo_reviewed_at=datetime.now(UTC), released_at=None,
    )
    db = FakeDB(scalars=[hold])
    monkeypatch.setattr(routes, "_allowed", lambda *args, **kwargs: True)
    monkeypatch.setattr(routes, "require_csrf", lambda *args, **kwargs: None)
    with pytest.raises(HTTPException) as error:
        routes.release_evidence_hold(
            hold_id,
            routes.EvidenceHoldRelease(
                note="Release requested", proceeding_concluded=False,
                conclusion_reference="CASE-CLOSE-001",
            ),
            SimpleNamespace(), actor(releaser), db,
        )
    assert error.value.status_code == 409


def test_data_subject_erasure_is_blocked_for_statutory_accounting_evidence(monkeypatch):
    request_id, evidence_id, dpo_id = uuid4(), uuid4(), uuid4()
    item = SimpleNamespace(id=request_id, evidence_id=evidence_id, status="pending")
    evidence = SimpleNamespace(
        id=evidence_id, retention_classified_by=uuid4(),
        accounting_document=True, commercial_correspondence=False,
    )
    db = FakeDB(scalars=[item, evidence])
    monkeypatch.setattr(routes, "_allowed", lambda *args, **kwargs: True)
    monkeypatch.setattr(routes, "require_csrf", lambda *args, **kwargs: None)
    with pytest.raises(HTTPException) as error:
        routes.review_evidence_rights_request(
            request_id,
            routes.EvidenceRightsRequestReview(
                decision="erase", reason="Erase request reviewed",
            ),
            SimpleNamespace(), actor(dpo_id), db,
        )
    assert error.value.status_code == 409


def test_dpo_deletion_suspension_is_persisted(monkeypatch):
    evidence_id = uuid4()
    evidence = SimpleNamespace(id=evidence_id, dpo_deletion_suspended=False)
    db = FakeDB(scalars=[evidence])
    monkeypatch.setattr(routes, "_allowed", lambda *args, **kwargs: True)
    monkeypatch.setattr(routes, "require_csrf", lambda *args, **kwargs: None)
    monkeypatch.setattr(routes, "_audit", lambda *args, **kwargs: None)
    result = routes.set_evidence_deletion_suspension(
        evidence_id,
        routes.EvidenceDeletionSuspension(
            suspended=True, reason="DPO review requires a temporary deletion pause",
        ),
        SimpleNamespace(), actor(), db,
    )
    assert result["deletion_suspended"] is True
    assert evidence.dpo_deletion_suspended is True


def test_auxiliary_retention_requires_distinct_dpo_review(monkeypatch):
    evidence_id, classifier = uuid4(), uuid4()
    evidence = SimpleNamespace(
        id=evidence_id, audit_retention_classified_by=classifier,
        tombstone_retention_classified_by=classifier,
        audit_retention_expires_at=datetime.now(UTC) + timedelta(days=365),
        tombstone_retention_expires_at=datetime.now(UTC) + timedelta(days=365),
    )
    db = FakeDB(scalars=[evidence])
    monkeypatch.setattr(routes, "_allowed", lambda *args, **kwargs: True)
    monkeypatch.setattr(routes, "require_csrf", lambda *args, **kwargs: None)
    with pytest.raises(HTTPException) as error:
        routes.review_evidence_auxiliary_retention(
            evidence_id, routes.EvidenceRetentionReview(note="Independent review completed"),
            SimpleNamespace(), actor(classifier), db,
        )
    assert error.value.status_code == 409
