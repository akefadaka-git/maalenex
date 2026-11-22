from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.domains.cargo.legal_retention import (
    add_calendar_years, deletion_block_reason, effective_retention_deadline,
)


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
