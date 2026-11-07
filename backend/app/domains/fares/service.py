from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domains.audit.service import record_event
from app.domains.fares.models import Fare, FareApproval, FareVersion


class FareConflict(Exception):
    pass


def propose_fare(
    db: Session, *, organization_id: UUID, route_id: UUID,
    proposed_by: UUID, amount_minor_units: int, effective_from: datetime,
    trip_id: UUID | None = None,
) -> FareVersion:
    if amount_minor_units < 0:
        raise ValueError("Fare amount must be a non-negative integer.")
    if effective_from.tzinfo is None:
        raise ValueError("Fare effective_from must be timezone-aware.")
    fare = db.scalar(select(Fare).where(
        Fare.organization_id == organization_id, Fare.route_id == route_id,
        Fare.trip_id == trip_id,
    ).with_for_update())
    if fare is None:
        fare = Fare(id=uuid4(), organization_id=organization_id,
                    route_id=route_id, trip_id=trip_id, status="draft")
        db.add(fare)
        db.flush()
    latest = db.scalar(select(FareVersion.version_number).where(
        FareVersion.fare_id == fare.id
    ).order_by(FareVersion.version_number.desc()).limit(1))
    version = FareVersion(
        fare_id=fare.id, version_number=(latest or 0) + 1,
        amount_minor_units=amount_minor_units, currency_code="ETB",
        effective_from=effective_from, status="draft", proposed_by=proposed_by,
    )
    db.add(version)
    record_event(db, event_type="fare.version.proposed", actor_type="staff",
                 actor_id=str(proposed_by), resource_type="fare_version",
                 resource_id=str(version.id), action="propose", outcome="success",
                 organization_id=organization_id,
                 metadata={"amount_minor_units": amount_minor_units, "currency_code": "ETB"})
    db.flush()
    return version



def submit_fare(db: Session, *, fare_version_id: UUID, proposer_id: UUID) -> FareVersion:
    version = db.scalar(select(FareVersion).where(
        FareVersion.id == fare_version_id
    ).with_for_update())
    if version is None or version.proposed_by != proposer_id or version.status != "draft":
        raise FareConflict("Only the proposer may submit their draft fare version.")
    if version.amount_minor_units < 0 or version.currency_code != "ETB":
        raise FareConflict("Fare amount or currency is invalid.")
    version.status = "submitted"
    record_event(db, event_type="fare.version.submitted", actor_type="staff",
                 actor_id=str(proposer_id), resource_type="fare_version",
                 resource_id=str(version.id), action="submit", outcome="success")
    db.flush()
    return version

def decide_fare(
    db: Session, *, fare_version_id: UUID, reviewer_id: UUID,
    decision: str, reason: str,
) -> FareApproval:
    if decision not in {"approved", "rejected"}:
        raise ValueError("Decision must be approved or rejected.")
    version = db.scalar(select(FareVersion).where(
        FareVersion.id == fare_version_id
    ).with_for_update())
    if version is None or version.status != "submitted":
        raise FareConflict("Only a submitted fare version can be reviewed.")
    if version.proposed_by == reviewer_id:
        raise FareConflict("The proposer cannot approve their own fare version.")
    if not reason.strip():
        raise ValueError("A decision reason is required.")
    approval = FareApproval(
        fare_version_id=version.id, decision=decision,
        reviewer_user_id=reviewer_id, reason=reason.strip()[:500],
    )
    version.status = decision
    version.approved_by = reviewer_id if decision == "approved" else None
    version.approved_at = db.scalar(select(func.now()))
    db.add(approval)
    record_event(db, event_type="fare.version.reviewed", actor_type="staff",
                 actor_id=str(reviewer_id), resource_type="fare_version",
                 resource_id=str(version.id), action="review", outcome=decision,
                 reason_code="review_decision")
    db.flush()
    return approval


def publish_fare(db: Session, *, fare_version_id: UUID, publisher_id: UUID) -> FareVersion:
    now = db.scalar(select(func.now()))
    version = db.scalar(select(FareVersion).where(
        FareVersion.id == fare_version_id
    ).with_for_update())
    if version is None or version.status != "approved":
        raise FareConflict("Only an approved fare version can be published.")
    if version.approved_by == publisher_id:
        raise FareConflict("The publisher must be separate from the approver.")
    if version.effective_from > now or (version.effective_to is not None and version.effective_to <= now):
        raise FareConflict("Fare effective period does not include publication time.")
    if version.effective_to is not None and version.effective_to <= version.effective_from:
        raise FareConflict("Fare effective_to must be later than effective_from.")
    overlapping = db.scalar(select(FareVersion.id).where(
        FareVersion.fare_id == version.fare_id,
        FareVersion.id != version.id,
        FareVersion.status == "published",
        FareVersion.effective_from < (version.effective_to if version.effective_to is not None else datetime.max.replace(tzinfo=version.effective_from.tzinfo)),
        (FareVersion.effective_to.is_(None)) | (FareVersion.effective_to > version.effective_from),
    ).limit(1))
    if overlapping is not None:
        raise FareConflict("Published fare effective periods may not overlap.")
    version.status = "published"
    version.published_by = publisher_id
    version.published_at = now
    record_event(db, event_type="fare.version.published", actor_type="staff",
                 actor_id=str(publisher_id), resource_type="fare_version",
                 resource_id=str(version.id), action="publish", outcome="success")
    db.flush()
    return version
