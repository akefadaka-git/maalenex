"""Staff-governed trust-case state transitions; caller owns transaction commit."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.identity.accounts import TrustReviewEvent, TrustVerificationCase
from app.domains.identity.models import User

_ALLOWED_TRANSITIONS = {
    "submitted": {"in_review"},
    "in_review": {"approved", "rejected"},
    "approved": {"revoked"},
}


def transition_trust_case(
    db: Session, *, case_id, reviewer_user_id, target_status: str,
    reason_code: str | None = None,
) -> TrustVerificationCase:
    """Apply one legal review transition under a row lock and append immutable evidence."""
    case = db.scalar(
        select(TrustVerificationCase)
        .where(TrustVerificationCase.id == case_id)
        .with_for_update()
    )
    if case is None:
        raise ValueError("Trust verification case does not exist.")
    if target_status not in _ALLOWED_TRANSITIONS.get(case.status, set()):
        raise ValueError("Trust verification status transition is not permitted.")
    if target_status in {"rejected", "revoked"} and not reason_code:
        raise ValueError("A reason code is required for rejection or revocation.")
    reviewer = db.get(User, reviewer_user_id)
    if reviewer is None or reviewer.status != "active":
        raise ValueError("An active staff reviewer is required.")

    previous_status = case.status
    now = db.scalar(select(func.now()))
    case.status = target_status
    case.reviewed_by = reviewer.id
    case.reviewed_at = now
    case.decision_reason_code = reason_code
    sequence = db.scalar(
        select(func.coalesce(func.max(TrustReviewEvent.sequence_number), 0) + 1)
        .where(TrustReviewEvent.case_id == case.id)
    )
    db.add(TrustReviewEvent(
        case_id=case.id, sequence_number=sequence, actor_staff_user_id=reviewer.id,
        action=target_status, from_status=previous_status, to_status=target_status,
        reason_code=reason_code,
    ))
    record_event(
        db, event_type="trust.verification.transitioned", actor_type="staff",
        actor_id=str(reviewer.id), resource_type="trust_verification_case",
        resource_id=str(case.id), action=target_status, outcome="success",
        reason_code=reason_code,
        metadata={"subject_type": case.subject_type, "from_status": previous_status,
                  "to_status": target_status, "sequence": sequence},
    )
    db.flush()
    return case
