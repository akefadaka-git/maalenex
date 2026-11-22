"""Idempotent cleanup of expired, unattached cargo evidence uploads.
# ruff: noqa: I001

The caller must supply the separately approved orphan grace period. This module
is intentionally not scheduled or enabled by application startup.
"""
# ruff: noqa: I001
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.cargo.evidence_lifecycle import (
    CargoDeliveryEvidence, CargoDeliveryEvidenceHold, CargoDeliveryEvidenceRetentionPolicy,
)
from app.domains.fleet.object_storage import (
    StorageNotConfigured, StorageOperationFailed, delete_cargo_delivery_object,
)


def cleanup_expired_unattached_evidence(
    db: Session, *, now: datetime, grace_period: timedelta, batch_size: int = 100,
) -> dict[str, int]:
    """Delete only unattached uploads past intent expiry plus an approved grace period."""
    if now.tzinfo is None or grace_period.total_seconds() <= 0 or not 1 <= batch_size <= 1000:
        raise ValueError("A timezone-aware clock, positive grace period and bounded batch size are required.")
    cutoff = now - grace_period
    candidates = db.scalars(
        select(CargoDeliveryEvidence)
        .where(
            CargoDeliveryEvidence.delivery_proof_id.is_(None),
            CargoDeliveryEvidence.upload_intent_expires_at.is_not(None),
            CargoDeliveryEvidence.upload_intent_expires_at <= cutoff,
            CargoDeliveryEvidence.lifecycle_state.in_({"pending", "deletion_failed"}),
            CargoDeliveryEvidence.storage_deleted_at.is_(None),
        )
        .order_by(CargoDeliveryEvidence.upload_intent_expires_at)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    ).all()
    deleted = 0
    failed = 0
    held = 0
    for evidence in candidates:
        active_hold = db.scalar(select(CargoDeliveryEvidenceHold.id).where(
            CargoDeliveryEvidenceHold.evidence_id == evidence.id,
            CargoDeliveryEvidenceHold.released_at.is_(None),
        ).limit(1))
        if active_hold is not None:
            held += 1
            continue
        try:
            delete_cargo_delivery_object(
                object_key=evidence.object_key,
                carrier_organization_id=str(evidence.carrier_organization_id),
                dispatch_id=str(evidence.dispatch_id),
            )
        except (StorageOperationFailed, StorageNotConfigured):
            evidence.lifecycle_state = "deletion_failed"
            evidence.deletion_failure_code = "storage_unavailable"
            failed += 1
            outcome = "failure"
        else:
            evidence.lifecycle_state = "deleted"
            evidence.storage_deleted_at = now
            evidence.deletion_failure_code = None
            deleted += 1
            outcome = "success"
        record_event(
            db, event_type="cargo.delivery_evidence.orphan_cleanup",
            actor_type="system", actor_id=None,
            resource_type="cargo_delivery_evidence", resource_id=str(evidence.id),
            action="orphan_cleanup", outcome=outcome,
            organization_id=evidence.carrier_organization_id,
            metadata={"evidence_id": str(evidence.id), "dispatch_id": str(evidence.dispatch_id)},
        )
    db.commit()
    return {"examined": len(candidates), "deleted": deleted, "failed": failed, "held": held}



def process_expired_retention_evidence(
    db: Session, *, now: datetime, batch_size: int = 100,
) -> dict[str, int]:
    """Delete expired evidence only under a separately activated, legally reviewed policy."""
    if now.tzinfo is None or not 1 <= batch_size <= 1000:
        raise ValueError("A timezone-aware clock and bounded batch size are required.")
    candidates = db.scalars(
        select(CargoDeliveryEvidence)
        .where(
            CargoDeliveryEvidence.lifecycle_state.in_({"attached", "deletion_failed"}),
            CargoDeliveryEvidence.classification_status == "ordinary",
            CargoDeliveryEvidence.retention_dpo_reviewed_at.is_not(None),
            CargoDeliveryEvidence.retention_expires_at.is_not(None),
            CargoDeliveryEvidence.retention_expires_at <= now,
            CargoDeliveryEvidence.storage_deleted_at.is_(None),
        )
        .order_by(CargoDeliveryEvidence.retention_expires_at)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    ).all()
    deleted = 0
    failed = 0
    blocked = 0
    for evidence in candidates:
        policy = db.scalar(select(CargoDeliveryEvidenceRetentionPolicy.version).where(
            CargoDeliveryEvidenceRetentionPolicy.version == evidence.retention_policy_version,
            CargoDeliveryEvidenceRetentionPolicy.status == "active",
        ))
        active_hold = db.scalar(select(CargoDeliveryEvidenceHold.id).where(
            CargoDeliveryEvidenceHold.evidence_id == evidence.id,
            CargoDeliveryEvidenceHold.released_at.is_(None),
        ).limit(1))
        if policy is None or active_hold is not None:
            blocked += 1
            continue
        try:
            delete_cargo_delivery_object(
                object_key=evidence.object_key,
                carrier_organization_id=str(evidence.carrier_organization_id),
                dispatch_id=str(evidence.dispatch_id),
            )
        except (StorageOperationFailed, StorageNotConfigured):
            evidence.lifecycle_state = "deletion_failed"
            evidence.deletion_failure_code = "storage_unavailable"
            failed += 1
            outcome = "failure"
        else:
            evidence.lifecycle_state = "deleted"
            evidence.storage_deleted_at = now
            evidence.deletion_failure_code = None
            deleted += 1
            outcome = "success"
        record_event(
            db, event_type="cargo.delivery_evidence.retention_deletion",
            actor_type="system", actor_id=None,
            resource_type="cargo_delivery_evidence", resource_id=str(evidence.id),
            action="retention_delete", outcome=outcome,
            organization_id=evidence.carrier_organization_id,
            metadata={"evidence_id": str(evidence.id), "dispatch_id": str(evidence.dispatch_id)},
        )
    db.commit()
    return {"examined": len(candidates), "deleted": deleted, "failed": failed, "blocked": blocked}



def alert_due_legal_hold_reviews(db: Session, *, now: datetime, batch_size: int = 100) -> dict[str, int]:
    """Record one auditable escalation when a legal-hold review reaches its due time."""
    if now.tzinfo is None or not 1 <= batch_size <= 1000:
        raise ValueError("A timezone-aware clock and bounded batch size are required.")
    due_holds = db.scalars(
        select(CargoDeliveryEvidenceHold)
        .where(
            CargoDeliveryEvidenceHold.released_at.is_(None),
            CargoDeliveryEvidenceHold.review_due_at <= now,
            CargoDeliveryEvidenceHold.review_alerted_at.is_(None),
        )
        .order_by(CargoDeliveryEvidenceHold.review_due_at)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    ).all()
    for hold in due_holds:
        hold.review_alerted_at = now
        record_event(
            db, event_type="cargo.delivery_evidence.hold_review_due",
            actor_type="system", actor_id=None,
            resource_type="cargo_delivery_evidence_hold", resource_id=str(hold.id),
            action="hold_review_escalation", outcome="success",
            metadata={"hold_id": str(hold.id), "evidence_id": str(hold.evidence_id),
                      "review_due_at": hold.review_due_at.isoformat()},
        )
    db.commit()
    return {"review_due": len(due_holds)}
