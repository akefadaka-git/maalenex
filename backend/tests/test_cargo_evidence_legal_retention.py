from datetime import UTC, datetime
from types import SimpleNamespace

from app.domains.cargo.legal_retention import deletion_block_reason, effective_retention_deadline
from app.jobs import cargo_evidence_cleanup


def test_ten_year_accounting_deadline_uses_document_preparation_date():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=True,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=False,
        accounting_document_date=datetime(2020, 2, 29, tzinfo=UTC),
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="none",
    )
    assert effective_retention_deadline(evidence) == datetime(2030, 2, 28, tzinfo=UTC)


def test_overlapping_accounting_and_correspondence_uses_later_ten_year_deadline():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=True,
        is_commercial_correspondence=True, is_ordinary_operational_evidence=True,
        accounting_document_date=datetime(2020, 1, 1, tzinfo=UTC),
        commercial_correspondence_date=datetime(2022, 6, 1, tzinfo=UTC),
        operational_retention_started_at=datetime(2024, 1, 1, tzinfo=UTC),
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="none",
    )
    assert effective_retention_deadline(evidence) == datetime(2032, 6, 1, tzinfo=UTC)


def test_pure_operational_evidence_requires_dpia_and_documented_legal_basis():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=False,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=True,
        operational_retention_started_at=datetime(2024, 1, 1, tzinfo=UTC),
        operational_legal_basis="contract",
        operational_retention_justification="Documented delivery dispute window",
        operational_dpia_reference="DPIA-2026-01",
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="none",
    )
    assert effective_retention_deadline(evidence) == datetime(2026, 1, 1, tzinfo=UTC)


def test_unclassified_or_missing_source_date_fails_closed():
    evidence = SimpleNamespace(
        classification_complete=False, is_accounting_document=True,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=False,
        accounting_document_date=None, retention_dpo_reviewed_at=None,
        rights_request_status="none",
    )
    assert effective_retention_deadline(evidence) is None
    assert deletion_block_reason(evidence, now=datetime(2040, 1, 1, tzinfo=UTC)) == "legal_classification_incomplete"


def test_rights_request_blocks_deletion_even_after_retention_expiry():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=False,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=True,
        operational_retention_started_at=datetime(2020, 1, 1, tzinfo=UTC),
        operational_legal_basis="legitimate_interests",
        operational_retention_justification="Documented",
        operational_dpia_reference="DPIA-1",
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="pending",
    )
    assert deletion_block_reason(evidence, now=datetime(2027, 1, 1, tzinfo=UTC)) == "data_subject_rights_request_pending"


def test_sensitive_data_requires_specific_handling_review():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=False,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=True,
        operational_retention_started_at=datetime(2020, 1, 1, tzinfo=UTC),
        operational_legal_basis="consent",
        operational_retention_justification="Documented",
        operational_dpia_reference="DPIA-1",
        contains_sensitive_personal_data=True,
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="none",
    )
    assert deletion_block_reason(evidence, now=datetime(2027, 1, 1, tzinfo=UTC)) == "sensitive_data_review_missing"



def test_early_erasure_can_override_only_residual_operational_retention():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=False,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=True,
        operational_retention_started_at=datetime(2025, 1, 1, tzinfo=UTC),
        operational_legal_basis="contract",
        operational_retention_justification="Documented purpose and necessity",
        operational_dpia_reference="DPIA-ERASURE-001",
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="eligible_for_erasure",
        contains_sensitive_personal_data=False,
    )
    assert deletion_block_reason(evidence, now=datetime(2026, 2, 1, tzinfo=UTC)) is None


def test_erasure_cannot_override_ten_year_accounting_retention():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=True,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=True,
        accounting_document_date=datetime(2023, 1, 1, tzinfo=UTC),
        operational_retention_started_at=datetime(2023, 1, 1, tzinfo=UTC),
        operational_legal_basis="contract",
        operational_retention_justification="Documented",
        operational_dpia_reference="DPIA-ERASURE-002",
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="eligible_for_erasure",
        contains_sensitive_personal_data=False,
    )
    assert deletion_block_reason(evidence, now=datetime(2026, 2, 1, tzinfo=UTC)) == "statutory_retention_overrides_erasure_request"



def test_dpo_deletion_suspension_blocks_every_deletion_path():
    evidence = SimpleNamespace(
        classification_complete=True, is_accounting_document=False,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=True,
        operational_retention_started_at=datetime(2020, 1, 1, tzinfo=UTC),
        operational_legal_basis="contract",
        operational_retention_justification="Documented operational purpose",
        operational_dpia_reference="DPIA-DPO-SUSPEND-001",
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="none", contains_sensitive_personal_data=False,
        deletion_suspended=True,
    )
    assert deletion_block_reason(evidence, now=datetime(2027, 1, 1, tzinfo=UTC)) == "deletion_suspended_by_dpo"



def test_orphan_cleanup_requires_active_policy_and_never_deletes_without_it(monkeypatch):
    evidence = SimpleNamespace(
        id="synthetic-evidence", delivery_proof_id=None,
        upload_intent_expires_at=datetime(2025, 1, 1, tzinfo=UTC),
        lifecycle_state="pending", storage_deleted_at=None,
        classification_complete=True, is_accounting_document=False,
        is_commercial_correspondence=False, is_ordinary_operational_evidence=True,
        operational_retention_started_at=datetime(2020, 1, 1, tzinfo=UTC),
        operational_legal_basis="contract",
        operational_retention_justification="Documented purpose",
        operational_dpia_reference="DPIA-ORPHAN-001",
        retention_dpo_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
        rights_request_status="none", contains_sensitive_personal_data=False,
        deletion_suspended=False, retention_policy_version="not-active",
        object_key="cargo-delivery/carrier/dispatch/orphan",
        carrier_organization_id="carrier", dispatch_id="dispatch",
    )

    class Results:
        def all(self):
            return [evidence]

    class DB:
        def scalars(self, statement):
            return Results()

        def scalar(self, statement):
            return None

        def commit(self):
            return None

    monkeypatch.setattr(
        cargo_evidence_cleanup, "delete_cargo_delivery_object",
        lambda **kwargs: pytest.fail("Orphan object deletion ran without an active retention policy."),
    )
    monkeypatch.setattr(cargo_evidence_cleanup, "record_event", lambda *args, **kwargs: None)
    result = cargo_evidence_cleanup.cleanup_expired_unattached_evidence(
        DB(), now=datetime(2026, 11, 22, tzinfo=UTC), grace_period=__import__("datetime").timedelta(days=1),
    )
    assert result["deleted"] == 0
    assert result["held"] == 1
