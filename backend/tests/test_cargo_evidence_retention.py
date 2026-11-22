from datetime import UTC, datetime

import pytest

from app.domains.cargo.evidence_retention import (
    calculate_retention_expiry,
    deletion_block_reason,
)


def test_accounting_documents_receive_ten_year_retention_from_record_date():
    start = datetime(2026, 1, 1, tzinfo=UTC)
    _, expiry = calculate_retention_expiry(
        delivery_closed_at=start,
        accounting_document=True,
        commercial_correspondence=False,
        accounting_record_date=datetime(2025, 7, 15, tzinfo=UTC),
        correspondence_date=None,
        dpia_reference=None,
        retention_justification=None,
    )
    assert expiry == datetime(2035, 7, 15, tzinfo=UTC)


def test_commercial_correspondence_receives_ten_year_retention_from_correspondence_date():
    start = datetime(2026, 1, 1, tzinfo=UTC)
    code, expiry = calculate_retention_expiry(
        delivery_closed_at=start,
        accounting_document=False,
        commercial_correspondence=True,
        accounting_record_date=None,
        correspondence_date=datetime(2024, 3, 20, tzinfo=UTC),
        dpia_reference=None,
        retention_justification=None,
    )
    assert code == "EC-2"
    assert expiry == datetime(2034, 3, 20, tzinfo=UTC)


def test_overlapping_accounting_and_correspondence_use_latest_mandatory_expiry():
    start = datetime(2026, 1, 1, tzinfo=UTC)
    code, expiry = calculate_retention_expiry(
        delivery_closed_at=start,
        accounting_document=True,
        commercial_correspondence=True,
        accounting_record_date=datetime(2020, 1, 1, tzinfo=UTC),
        correspondence_date=datetime(2022, 6, 1, tzinfo=UTC),
        dpia_reference=None,
        retention_justification=None,
    )
    assert code == "EC-1+EC-2"
    assert expiry == datetime(2032, 6, 1, tzinfo=UTC)


def test_residual_operational_evidence_requires_dpia_and_justification():
    start = datetime(2026, 1, 31, tzinfo=UTC)
    with pytest.raises(ValueError):
        calculate_retention_expiry(
            delivery_closed_at=start,
            accounting_document=False,
            commercial_correspondence=False,
            accounting_record_date=None,
            correspondence_date=None,
            dpia_reference=None,
            retention_justification=None,
        )
    code, expiry = calculate_retention_expiry(
        delivery_closed_at=start,
        accounting_document=False,
        commercial_correspondence=False,
        accounting_record_date=None,
        correspondence_date=None,
        dpia_reference="DPIA-2026-001",
        retention_justification="Documented operational dispute-resolution purpose",
    )
    assert code == "EC-3"
    assert expiry == datetime(2028, 1, 31, tzinfo=UTC)


def _deletion_check(**overrides):
    values = {
        "classification_status": "ordinary",
        "accounting_document": False,
        "commercial_correspondence": False,
        "retention_expires_at": datetime(2025, 1, 1, tzinfo=UTC),
        "retention_dpo_reviewed_at": datetime(2024, 1, 1, tzinfo=UTC),
        "dpia_reference": "DPIA-2024-001",
        "dpo_deletion_suspended": False,
        "rights_review_status": "reviewed",
        "active_hold": False,
        "active_policy": True,
        "now": datetime(2026, 1, 1, tzinfo=UTC),
    }
    values.update(overrides)
    return deletion_block_reason(**values)


@pytest.mark.parametrize(
    ("override", "expected"),
    [
        ({"accounting_document": True}, "mandatory_ten_year_retention"),
        ({"commercial_correspondence": True}, "mandatory_ten_year_retention"),
        ({"active_hold": True}, "active_legal_hold"),
        ({"dpo_deletion_suspended": True}, "dpo_deletion_suspension"),
        ({"rights_review_status": "pending"}, "pending_data_subject_rights_review"),
        ({"active_policy": False}, "retention_policy_not_active"),
        ({"classification_status": "statutory"}, "unclassified_or_nonordinary_evidence"),
        ({"retention_expires_at": datetime(2027, 1, 1, tzinfo=UTC)}, "retention_period_not_expired"),
        ({"retention_dpo_reviewed_at": None}, "missing_independent_dpo_or_dpia_review"),
    ],
)
def test_deletion_interlock_fails_closed(override, expected):
    assert _deletion_check(**override) == expected


def test_deletion_interlock_allows_only_expired_reviewed_residual_operational_evidence():
    assert _deletion_check() is None
