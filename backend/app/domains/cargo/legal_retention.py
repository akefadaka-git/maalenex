"""Legal retention policy helpers for cargo delivery evidence.

Retention classifications are overlapping flags, not a single exclusive enum.
Deletion eligibility is fail-closed: unknown or incomplete classifications never
become deletion candidates.
"""
from calendar import monthrange
from datetime import datetime


def add_calendar_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))


def add_calendar_years(value: datetime, years: int) -> datetime:
    year = value.year + years
    return value.replace(year=year, day=min(value.day, monthrange(year, value.month)[1]))


def effective_retention_deadline(evidence) -> datetime | None:
    """Return the latest applicable mandatory deadline; None means not classifiable."""
    deadlines = []
    if not getattr(evidence, "classification_complete", False):
        return None

    accounting = bool(getattr(evidence, "is_accounting_document", False))
    correspondence = bool(getattr(evidence, "is_commercial_correspondence", False))
    operational = bool(getattr(evidence, "is_ordinary_operational_evidence", False))

    if not (accounting or correspondence or operational):
        return None

    if accounting:
        source_date = getattr(evidence, "accounting_document_date", None)
        if source_date is None:
            return None
        deadlines.append(add_calendar_years(source_date, 10))

    if correspondence:
        source_date = getattr(evidence, "commercial_correspondence_date", None)
        if source_date is None:
            return None
        deadlines.append(add_calendar_years(source_date, 10))

    if operational and not (accounting or correspondence):
        started_at = getattr(evidence, "operational_retention_started_at", None)
        if started_at is None:
            return None
        if not getattr(evidence, "operational_legal_basis", None):
            return None
        if not getattr(evidence, "operational_retention_justification", None):
            return None
        if not getattr(evidence, "operational_dpia_reference", None):
            return None
        deadlines.append(add_calendar_months(started_at, 24))

    # EC-1/EC-2 override the shorter EC-3 period when classifications overlap.
    if not deadlines:
        return None
    return max(deadlines)


def deletion_block_reason(evidence, *, now: datetime) -> str | None:
    if now.tzinfo is None:
        return "timezone_aware_clock_required"
    if not getattr(evidence, "classification_complete", False):
        return "legal_classification_incomplete"
    if getattr(evidence, "retention_dpo_reviewed_at", None) is None:
        return "independent_dpo_review_missing"
    if getattr(evidence, "deletion_suspended", False):
        return "deletion_suspended_by_dpo"
    if (getattr(evidence, "contains_sensitive_personal_data", False)
            and not getattr(evidence, "sensitive_data_handling_review_reference", None)):
        return "sensitive_data_review_missing"
    rights_status = getattr(evidence, "rights_request_status", "none")
    if rights_status in {"pending", "restricted", "under_review"}:
        return "data_subject_rights_request_pending"
    has_statutory_category = (
        getattr(evidence, "is_accounting_document", False)
        or getattr(evidence, "is_commercial_correspondence", False)
    )
    if rights_status == "eligible_for_erasure" and not has_statutory_category:
        return None
    if rights_status == "eligible_for_erasure" and has_statutory_category:
        return "statutory_retention_overrides_erasure_request"
    deadline = effective_retention_deadline(evidence)
    if deadline is None:
        return "retention_deadline_cannot_be_established"
    if deadline > now:
        return "mandatory_retention_period_not_expired"
    if rights_status == "eligible_for_erasure" and has_statutory_category:
        return "statutory_retention_overrides_erasure_request"
    return None
