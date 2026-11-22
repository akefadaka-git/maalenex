"""Fail-closed Ethiopian cargo evidence retention policy calculations.

This module encodes the Owner-supplied legal-review schedule as a technical
control. It does not activate a retention policy or establish legal compliance.
"""
from calendar import monthrange
from datetime import datetime


def add_calendar_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))


def add_calendar_years(value: datetime, years: int) -> datetime:
    target_year = value.year + years
    return value.replace(
        year=target_year,
        day=min(value.day, monthrange(target_year, value.month)[1]),
    )


def calculate_retention_expiry(
    *,
    delivery_closed_at: datetime,
    accounting_document: bool,
    commercial_correspondence: bool,
    accounting_record_date: datetime | None,
    correspondence_date: datetime | None,
    dpia_reference: str | None,
    retention_justification: str | None,
) -> tuple[str, datetime]:
    """Return schedule code and latest mandatory expiry across overlapping classes."""
    dates: list[datetime] = []
    if delivery_closed_at.tzinfo is None or delivery_closed_at.utcoffset() is None:
        raise ValueError("Delivery closure must be timezone-aware.")
    if accounting_document:
        if accounting_record_date is None or accounting_record_date.tzinfo is None:
            raise ValueError("Accounting documents require a timezone-aware accounting record date.")
        dates.append(add_calendar_years(accounting_record_date, 10))
    if commercial_correspondence:
        if correspondence_date is None or correspondence_date.tzinfo is None:
            raise ValueError("Commercial correspondence requires a timezone-aware correspondence date.")
        dates.append(add_calendar_years(correspondence_date, 10))
    if dates:
        schedule = "EC-1+EC-2" if accounting_document and commercial_correspondence else (
            "EC-1" if accounting_document else "EC-2"
        )
        return schedule, max(dates)
    if not dpia_reference or not retention_justification:
        raise ValueError("Residual EC-3 evidence requires a documented DPIA reference and retention justification.")
    return "EC-3", add_calendar_months(delivery_closed_at, 24)


def deletion_block_reason(
    *,
    classification_status: str,
    accounting_document: bool,
    commercial_correspondence: bool,
    retention_expires_at: datetime | None,
    retention_dpo_reviewed_at: datetime | None,
    dpia_reference: str | None,
    dpo_deletion_suspended: bool,
    rights_review_status: str,
    active_hold: bool,
    active_policy: bool,
    now: datetime,
) -> str | None:
    """Return a fail-closed reason; statutory categories are never auto-deleted."""
    if active_hold:
        return "active_legal_hold"
    if dpo_deletion_suspended:
        return "dpo_deletion_suspension"
    if rights_review_status == "pending":
        return "pending_data_subject_rights_review"
    if accounting_document or commercial_correspondence:
        return "mandatory_ten_year_retention"
    if classification_status != "ordinary":
        return "unclassified_or_nonordinary_evidence"
    if retention_dpo_reviewed_at is None or not dpia_reference:
        return "missing_independent_dpo_or_dpia_review"
    if retention_expires_at is None or retention_expires_at > now:
        return "retention_period_not_expired"
    if not active_policy:
        return "retention_policy_not_active"
    return None
