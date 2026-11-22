"""Private cargo delivery evidence lifecycle APIs.

This router is additive: the existing PR #48 upload and proof endpoints remain
available. Lifecycle-aware clients use the registration and attachment endpoints
below. No scheduled deletion or production policy activation is performed here.
"""
# ruff: noqa: B008,I001
from calendar import monthrange
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.cargo.carrier_operations import CargoDeliveryProof
from app.domains.cargo.dispatch import CargoDispatch
from app.domains.cargo.evidence_lifecycle import (
    CargoDeliveryEvidence, CargoDeliveryEvidenceAccessGrant,
    CargoDeliveryEvidenceDeletionRequest, CargoDeliveryEvidenceHold,
    CargoDeliveryEvidenceRetentionPolicy,
)
from app.domains.fleet.object_storage import (
    InvalidStoredObject, StorageNotConfigured, StorageOperationFailed,
    create_cargo_delivery_download_url, create_cargo_delivery_upload_intent,
    delete_cargo_delivery_object, verify_cargo_delivery_object,
)
from app.domains.identity.authorization import has_permission
from app.domains.identity.service import StaffContext
from app.routers.auth import current_staff_context, require_csrf

router = APIRouter(prefix="/cargo", tags=["cargo evidence lifecycle"])
UPLOAD_TTL_SECONDS = 300
DOWNLOAD_TTL_SECONDS = 60
PROVISIONAL_RETENTION_MONTHS = 24
PROVISIONAL_POLICY_VERSION = "owner-approved-provisional-24m-v1"


class EvidenceUploadIntentCreate(BaseModel):
    content_type: Literal["application/pdf", "image/jpeg", "image/png"]
    content_length: int = Field(ge=1, le=10 * 1024 * 1024)


class LifecycleDeliveryProofCreate(BaseModel):
    evidence_id: UUID
    idempotency_key: str = Field(min_length=16, max_length=128)
    received_by_name: str = Field(min_length=1, max_length=160)
    delivery_notes: str | None = Field(default=None, max_length=500)
    occurred_at: datetime


class EvidenceAttach(BaseModel):
    delivery_proof_id: UUID


class EvidenceHoldCreate(BaseModel):
    case_reference: str = Field(min_length=3, max_length=120)
    legal_basis: str = Field(min_length=10, max_length=500)
    review_due_at: datetime


class EvidenceHoldReview(BaseModel):
    outcome: Literal["reviewed", "release_recommended"]
    note: str = Field(min_length=3, max_length=500)


class EvidenceHoldRelease(BaseModel):
    note: str = Field(min_length=3, max_length=500)


class EvidenceDeletionRequestCreate(BaseModel):
    reason: str = Field(min_length=10, max_length=500)


class EvidenceDeletionApproval(BaseModel):
    confirmation: Literal["approve"]


class EvidenceRetentionClassify(BaseModel):
    classification: Literal["ordinary", "accounting_document", "extended_review"]
    legal_review_reference: str = Field(min_length=5, max_length=160)


class EvidenceRetentionReview(BaseModel):
    note: str = Field(min_length=5, max_length=500)


class EvidenceAccessGrantCreate(BaseModel):
    user_id: UUID
    reason: str = Field(min_length=10, max_length=500)
    expires_at: datetime


def _allowed(db: Session, context: StaffContext, code: str, organization_id: UUID | None = None) -> bool:
    return has_permission(
        db, user_id=context.user.id, permission_code=code, organization_id=organization_id,
    )


def _active_policy(db: Session, version: str | None) -> CargoDeliveryEvidenceRetentionPolicy | None:
    if version is None:
        return None
    return db.scalar(select(CargoDeliveryEvidenceRetentionPolicy).where(
        CargoDeliveryEvidenceRetentionPolicy.version == version,
        CargoDeliveryEvidenceRetentionPolicy.status == "active",
    ))


def _active_hold(db: Session, evidence_id: UUID) -> CargoDeliveryEvidenceHold | None:
    return db.scalar(select(CargoDeliveryEvidenceHold).where(
        CargoDeliveryEvidenceHold.evidence_id == evidence_id,
        CargoDeliveryEvidenceHold.released_at.is_(None),
    ).limit(1))


def _add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def _audit(db: Session, *, context: StaffContext, evidence: CargoDeliveryEvidence,
           action: str, outcome: str, reason: str | None = None) -> None:
    record_event(
        db, event_type=f"cargo.delivery_evidence.{action}", actor_type="staff",
        actor_id=str(context.user.id), resource_type="cargo_delivery_evidence",
        resource_id=str(evidence.id), action=action, outcome=outcome,
        organization_id=evidence.carrier_organization_id, reason_code=reason[:100] if reason else None,
        metadata={"evidence_id": str(evidence.id), "dispatch_id": str(evidence.dispatch_id)},
    )


@router.post("/dispatches/{dispatch_id}/delivery-proof/evidence-upload-intents", status_code=201)
def create_lifecycle_upload_intent(
    dispatch_id: UUID, payload: EvidenceUploadIntentCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    dispatch = db.get(CargoDispatch, dispatch_id)
    if dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    if dispatch.status != "in_transit" or not _allowed(
        db, context, "operator.cargo.delivery_proof.submit", dispatch.carrier_organization_id,
    ):
        raise HTTPException(status_code=403, detail="Assigned carrier delivery-proof permission is required.")
    try:
        intent = create_cargo_delivery_upload_intent(
            carrier_organization_id=str(dispatch.carrier_organization_id),
            dispatch_id=str(dispatch.id), content_type=payload.content_type,
            content_length=payload.content_length,
        )
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail="Private evidence storage is not configured.") from exc
    except InvalidStoredObject as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    now = datetime.now(UTC)
    evidence = CargoDeliveryEvidence(
        carrier_organization_id=dispatch.carrier_organization_id,
        dispatch_id=dispatch.id, object_key=intent["object_key"],
        content_type=payload.content_type, content_length=payload.content_length,
        upload_intent_created_at=now,
        upload_intent_expires_at=now + timedelta(seconds=UPLOAD_TTL_SECONDS),
        lifecycle_state="pending", classification_status="unclassified",
    )
    db.add(evidence)
    db.flush()
    _audit(db, context=context, evidence=evidence, action="upload_intent_created", outcome="success")
    db.commit()
    return {
        "evidence_id": str(evidence.id), "upload_url": intent["upload_url"],
        "method": intent["method"], "content_type": intent["content_type"],
        "max_bytes": intent["max_bytes"], "expires_in_seconds": intent["expires_in_seconds"],
    }


@router.post("/dispatches/{dispatch_id}/delivery-proof/lifecycle", status_code=201)
def submit_lifecycle_delivery_proof(
    dispatch_id: UUID, payload: LifecycleDeliveryProofCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    dispatch = db.scalar(select(CargoDispatch).where(
        CargoDispatch.id == dispatch_id,
    ).with_for_update())
    if dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    if dispatch.status != "in_transit" or not _allowed(
        db, context, "operator.cargo.delivery_proof.submit", dispatch.carrier_organization_id,
    ):
        raise HTTPException(status_code=403, detail="Assigned carrier delivery-proof permission is required.")
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == payload.evidence_id,
        CargoDeliveryEvidence.dispatch_id == dispatch.id,
        CargoDeliveryEvidence.carrier_organization_id == dispatch.carrier_organization_id,
    ).with_for_update())
    if evidence is None:
        raise HTTPException(status_code=404, detail="Dispatch-scoped evidence record not found.")
    if evidence.lifecycle_state != "pending" or datetime.now(UTC) > evidence.upload_intent_expires_at:
        raise HTTPException(status_code=409, detail="Upload intent is expired or no longer attachable.")
    if payload.occurred_at.tzinfo is None or payload.occurred_at.utcoffset() is None:
        raise HTTPException(status_code=422, detail="occurred_at must include an explicit timezone offset.")
    existing = db.scalar(select(CargoDeliveryProof).where(
        CargoDeliveryProof.dispatch_id == dispatch.id,
    ))
    if existing is not None:
        if (existing.idempotency_key != payload.idempotency_key
                or existing.evidence_reference != evidence.object_key):
            raise HTTPException(status_code=409, detail="A delivery proof already exists for this dispatch.")
        return {
            "id": str(existing.id), "dispatch_id": str(existing.dispatch_id),
            "consignment_id": str(existing.consignment_id), "status": existing.status,
            "evidence_id": str(evidence.id),
        }
    try:
        verified = verify_cargo_delivery_object(
            object_key=evidence.object_key,
            carrier_organization_id=str(dispatch.carrier_organization_id),
            dispatch_id=str(dispatch.id),
        )
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail="Private evidence storage is not configured.") from exc
    except StorageOperationFailed as exc:
        raise HTTPException(status_code=503, detail="Evidence storage is temporarily unavailable; retry safely.") from exc
    except InvalidStoredObject as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    proof = CargoDeliveryProof(
        dispatch_id=dispatch.id, consignment_id=dispatch.consignment_id,
        idempotency_key=payload.idempotency_key, received_by_name=payload.received_by_name,
        evidence_reference=evidence.object_key, delivery_notes=payload.delivery_notes,
        occurred_at=payload.occurred_at, submitted_by=context.user.id,
    )
    db.add(proof)
    db.flush()
    evidence.delivery_proof_id = proof.id
    evidence.verified_at = datetime.now(UTC)
    evidence.attached_at = evidence.verified_at
    evidence.content_type = verified["content_type"]
    evidence.content_length = verified["content_length"]
    evidence.lifecycle_state = "attached"
    record_event(
        db, event_type="cargo.delivery_proof.submitted", actor_type="staff",
        actor_id=str(context.user.id), resource_type="cargo_delivery_proof",
        resource_id=str(proof.id), action="submit", outcome="success",
        organization_id=dispatch.carrier_organization_id,
        metadata={"dispatch_id": str(dispatch.id), "evidence_id": str(evidence.id)},
    )
    _audit(db, context=context, evidence=evidence, action="attached", outcome="success")
    db.commit()
    return {
        "id": str(proof.id), "dispatch_id": str(proof.dispatch_id),
        "consignment_id": str(proof.consignment_id), "status": proof.status,
        "evidence_id": str(evidence.id),
    }


@router.post("/evidence/{evidence_id}/attach")
def attach_evidence_to_proof(
    evidence_id: UUID, payload: EvidenceAttach, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == evidence_id,
    ).with_for_update())
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    if not _allowed(db, context, "operator.cargo.delivery_proof.submit", evidence.carrier_organization_id):
        raise HTTPException(status_code=403, detail="Assigned carrier delivery-proof permission is required.")
    proof = db.get(CargoDeliveryProof, payload.delivery_proof_id)
    if proof is None or proof.dispatch_id != evidence.dispatch_id or proof.evidence_reference != evidence.object_key:
        raise HTTPException(status_code=422, detail="Delivery proof does not reference this dispatch evidence.")
    if evidence.delivery_proof_id not in {None, proof.id}:
        raise HTTPException(status_code=409, detail="Evidence is already attached to another delivery proof.")
    if evidence.lifecycle_state == "deleted":
        raise HTTPException(status_code=409, detail="Deleted evidence cannot be attached.")
    try:
        verified = verify_cargo_delivery_object(
            object_key=evidence.object_key,
            carrier_organization_id=str(evidence.carrier_organization_id),
            dispatch_id=str(evidence.dispatch_id),
        )
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail="Private evidence storage is not configured.") from exc
    except StorageOperationFailed as exc:
        raise HTTPException(status_code=503, detail="Evidence storage is temporarily unavailable; retry safely.") from exc
    except InvalidStoredObject as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    now = datetime.now(UTC)
    evidence.delivery_proof_id = proof.id
    evidence.verified_at = now
    evidence.attached_at = now
    evidence.content_type = verified["content_type"]
    evidence.content_length = verified["content_length"]
    evidence.lifecycle_state = "attached"
    if proof.status == "accepted":
        evidence.retention_policy_version = PROVISIONAL_POLICY_VERSION
        evidence.retention_started_at = now
        evidence.retention_expires_at = _add_months(now, PROVISIONAL_RETENTION_MONTHS)
        # Legal classification and policy activation are intentionally not inferred.
    _audit(db, context=context, evidence=evidence, action="attached", outcome="success")
    db.commit()
    return {
        "evidence_id": str(evidence.id), "delivery_proof_id": str(proof.id),
        "lifecycle_state": evidence.lifecycle_state,
        "retention_policy_version": evidence.retention_policy_version,
        "retention_expires_at": evidence.retention_expires_at.isoformat() if evidence.retention_expires_at else None,
        "classification_status": evidence.classification_status,
    }


@router.get("/evidence/{evidence_id}/download")
def get_private_evidence_download(
    evidence_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    evidence = db.get(CargoDeliveryEvidence, evidence_id)
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    carrier_allowed = _allowed(
        db, context, "operator.cargo.delivery_proof.evidence.read", evidence.carrier_organization_id,
    )
    platform_permission = _allowed(db, context, "platform.cargo.delivery_proof.evidence.read")
    platform_grant = db.scalar(select(CargoDeliveryEvidenceAccessGrant).where(
        CargoDeliveryEvidenceAccessGrant.evidence_id == evidence.id,
        CargoDeliveryEvidenceAccessGrant.user_id == context.user.id,
        CargoDeliveryEvidenceAccessGrant.revoked_at.is_(None),
        CargoDeliveryEvidenceAccessGrant.expires_at > datetime.now(UTC),
    ))
    platform_allowed = platform_permission and platform_grant is not None
    if not (carrier_allowed or platform_allowed):
        _audit(db, context=context, evidence=evidence, action="access_denied", outcome="denied")
        db.commit()
        raise HTTPException(status_code=403, detail="Explicit evidence-read permission is required.")
    if evidence.lifecycle_state == "deleted" or evidence.storage_deleted_at is not None:
        raise HTTPException(status_code=410, detail="Evidence has been deleted.")
    if evidence.lifecycle_state != "attached":
        raise HTTPException(status_code=409, detail="Evidence is not attached to an accepted delivery record.")
    dispatch = db.get(CargoDispatch, evidence.dispatch_id)
    if dispatch is None or dispatch.carrier_organization_id != evidence.carrier_organization_id:
        raise HTTPException(status_code=409, detail="Evidence ownership relationship is inconsistent.")
    try:
        verify_cargo_delivery_object(
            object_key=evidence.object_key,
            carrier_organization_id=str(evidence.carrier_organization_id),
            dispatch_id=str(evidence.dispatch_id),
        )
        url = create_cargo_delivery_download_url(
            object_key=evidence.object_key,
            carrier_organization_id=str(evidence.carrier_organization_id),
            dispatch_id=str(evidence.dispatch_id),
            expires_in_seconds=DOWNLOAD_TTL_SECONDS,
        )
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail="Private evidence storage is not configured.") from exc
    except InvalidStoredObject as exc:
        raise HTTPException(status_code=410, detail="Evidence object is unavailable or invalid.") from exc
    except StorageOperationFailed as exc:
        raise HTTPException(status_code=503, detail="Private evidence storage is temporarily unavailable.") from exc
    _audit(db, context=context, evidence=evidence, action="access_granted", outcome="success")
    db.commit()
    return {"download_url": url, "expires_in_seconds": DOWNLOAD_TTL_SECONDS}


@router.post("/evidence/{evidence_id}/access-grants", status_code=201)
def grant_case_scoped_evidence_access(
    evidence_id: UUID, payload: EvidenceAccessGrantCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.access.manage"):
        raise HTTPException(status_code=403, detail="Evidence access-grant administration permission is required.")
    evidence = db.get(CargoDeliveryEvidence, evidence_id)
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    if payload.expires_at.tzinfo is None or payload.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=422, detail="Access grant expiry must be timezone-aware and in the future.")
    grant = CargoDeliveryEvidenceAccessGrant(
        evidence_id=evidence.id, user_id=payload.user_id, granted_by=context.user.id,
        reason=payload.reason, expires_at=payload.expires_at,
    )
    db.add(grant)
    db.flush()
    record_event(
        db, event_type="cargo.delivery_evidence.access_granted", actor_type="staff",
        actor_id=str(context.user.id), resource_type="cargo_delivery_evidence_access_grant",
        resource_id=str(grant.id), action="grant_access", outcome="success",
        organization_id=evidence.carrier_organization_id,
        metadata={"evidence_id": str(evidence.id), "grantee_user_id": str(payload.user_id)},
    )
    db.commit()
    return {"grant_id": str(grant.id), "evidence_id": str(evidence.id), "expires_at": grant.expires_at.isoformat()}


@router.delete("/evidence/{evidence_id}/access-grants/{grant_id}")
def revoke_case_scoped_evidence_access(
    evidence_id: UUID, grant_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.access.manage"):
        raise HTTPException(status_code=403, detail="Evidence access-grant administration permission is required.")
    grant = db.scalar(select(CargoDeliveryEvidenceAccessGrant).where(
        CargoDeliveryEvidenceAccessGrant.id == grant_id,
        CargoDeliveryEvidenceAccessGrant.evidence_id == evidence_id,
    ).with_for_update())
    if grant is None:
        raise HTTPException(status_code=404, detail="Evidence access grant not found.")
    if grant.revoked_at is None:
        grant.revoked_at = datetime.now(UTC)
        record_event(
            db, event_type="cargo.delivery_evidence.access_revoked", actor_type="staff",
            actor_id=str(context.user.id), resource_type="cargo_delivery_evidence_access_grant",
            resource_id=str(grant.id), action="revoke_access", outcome="success",
            metadata={"evidence_id": str(evidence_id), "grantee_user_id": str(grant.user_id)},
        )
        db.commit()
    return {"grant_id": str(grant.id), "status": "revoked"}


@router.post("/evidence/{evidence_id}/holds", status_code=201)
def create_evidence_hold(
    evidence_id: UUID, payload: EvidenceHoldCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.hold.manage"):
        raise HTTPException(status_code=403, detail="Legal/Compliance evidence-hold permission is required.")
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == evidence_id,
    ).with_for_update())
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    if evidence.storage_deleted_at is not None or evidence.lifecycle_state == "deleted":
        raise HTTPException(status_code=410, detail="Deleted evidence cannot be placed on legal hold.")
    if payload.review_due_at.tzinfo is None or payload.review_due_at <= datetime.now(UTC):
        raise HTTPException(status_code=422, detail="A future timezone-aware hold review date is required.")
    if _active_hold(db, evidence.id):
        raise HTTPException(status_code=409, detail="An active legal hold already exists.")
    hold = CargoDeliveryEvidenceHold(
        evidence_id=evidence.id, case_reference=payload.case_reference,
        legal_basis=payload.legal_basis, issued_by=context.user.id,
        issued_at=datetime.now(UTC), review_due_at=payload.review_due_at,
    )
    db.add(hold)
    evidence.lifecycle_state = "held"
    db.flush()
    _audit(db, context=context, evidence=evidence, action="hold_created", outcome="success")
    db.commit()
    return {"hold_id": str(hold.id), "evidence_id": str(evidence.id), "status": "active"}


@router.post("/evidence/holds/{hold_id}/dpo-review")
def review_evidence_hold(
    hold_id: UUID, payload: EvidenceHoldReview, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.hold.review"):
        raise HTTPException(status_code=403, detail="Independent DPO hold-oversight permission is required.")
    hold = db.scalar(select(CargoDeliveryEvidenceHold).where(
        CargoDeliveryEvidenceHold.id == hold_id,
    ).with_for_update())
    if hold is None or hold.released_at is not None:
        raise HTTPException(status_code=404, detail="Active legal hold not found.")
    if hold.issued_by == context.user.id:
        raise HTTPException(status_code=409, detail="Hold issuer cannot provide the independent DPO oversight record.")
    hold.dpo_reviewed_by = context.user.id
    hold.dpo_reviewed_at = datetime.now(UTC)
    evidence = db.get(CargoDeliveryEvidence, hold.evidence_id)
    _audit(db, context=context, evidence=evidence, action="hold_dpo_reviewed", outcome="success", reason=f"{payload.outcome}:{payload.note}")
    db.commit()
    return {"hold_id": str(hold.id), "oversight_recorded": True, "outcome": payload.outcome}


@router.post("/evidence/holds/{hold_id}/release")
def release_evidence_hold(
    hold_id: UUID, payload: EvidenceHoldRelease, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.hold.manage"):
        raise HTTPException(status_code=403, detail="Legal/Compliance evidence-hold permission is required.")
    hold = db.scalar(select(CargoDeliveryEvidenceHold).where(
        CargoDeliveryEvidenceHold.id == hold_id,
    ).with_for_update())
    if hold is None or hold.released_at is not None:
        raise HTTPException(status_code=404, detail="Active legal hold not found.")
    if hold.dpo_reviewed_at is None:
        raise HTTPException(status_code=409, detail="DPO oversight must be recorded before hold release.")
    hold.released_by = context.user.id
    hold.released_at = datetime.now(UTC)
    hold.release_note = payload.note
    evidence = db.get(CargoDeliveryEvidence, hold.evidence_id)
    evidence.lifecycle_state = "attached" if evidence.delivery_proof_id else "verified"
    _audit(db, context=context, evidence=evidence, action="hold_released", outcome="success", reason=payload.note)
    db.commit()
    return {"hold_id": str(hold.id), "status": "released"}


@router.post("/evidence/{evidence_id}/retention-classification")
def classify_evidence_retention(
    evidence_id: UUID, payload: EvidenceRetentionClassify, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.retention.manage"):
        raise HTTPException(status_code=403, detail="Legal/Compliance retention-classification permission is required.")
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == evidence_id,
    ).with_for_update())
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    if evidence.lifecycle_state not in {"attached", "held"} or evidence.retention_started_at is None:
        raise HTTPException(status_code=409, detail="Evidence must be attached to a closed delivery before classification.")
    evidence.classification_status = f"{payload.classification}_pending_dpo"
    evidence.retention_legal_review_reference = payload.legal_review_reference
    evidence.retention_classified_by = context.user.id
    evidence.retention_classified_at = datetime.now(UTC)
    evidence.retention_dpo_reviewed_by = None
    evidence.retention_dpo_reviewed_at = None
    _audit(db, context=context, evidence=evidence, action="retention_classification_submitted", outcome="success")
    db.commit()
    return {"evidence_id": str(evidence.id), "classification_status": evidence.classification_status}


@router.post("/evidence/{evidence_id}/retention-classification/dpo-review")
def review_evidence_retention_classification(
    evidence_id: UUID, payload: EvidenceRetentionReview, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.retention.review"):
        raise HTTPException(status_code=403, detail="Independent DPO retention-review permission is required.")
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == evidence_id,
    ).with_for_update())
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    if not evidence.classification_status.endswith("_pending_dpo"):
        raise HTTPException(status_code=409, detail="No pending Legal/Compliance classification requires DPO review.")
    if evidence.retention_classified_by == context.user.id:
        raise HTTPException(status_code=409, detail="The Legal/Compliance classifier cannot provide independent DPO review.")
    classification = evidence.classification_status.removesuffix("_pending_dpo")
    evidence.classification_status = classification
    evidence.retention_dpo_reviewed_by = context.user.id
    evidence.retention_dpo_reviewed_at = datetime.now(UTC)
    _audit(db, context=context, evidence=evidence, action="retention_classification_dpo_reviewed",
           outcome="success", reason=f"{classification}:{payload.note}")
    db.commit()
    return {"evidence_id": str(evidence.id), "classification_status": evidence.classification_status,
            "dpo_reviewed": True}


@router.post("/evidence/{evidence_id}/deletion-requests", status_code=201)
def request_evidence_deletion(
    evidence_id: UUID, payload: EvidenceDeletionRequestCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.delete"):
        raise HTTPException(status_code=403, detail="Platform evidence-deletion permission is required.")
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == evidence_id,
    ).with_for_update())
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    if evidence.storage_deleted_at is not None:
        raise HTTPException(status_code=410, detail="Evidence has already been deleted.")
    if _active_hold(db, evidence.id):
        raise HTTPException(status_code=409, detail="Active legal hold prevents deletion.")
    policy = _active_policy(db, evidence.retention_policy_version)
    if (evidence.classification_status != "ordinary" or evidence.retention_dpo_reviewed_at is None
            or evidence.retention_expires_at is None or policy is None):
        raise HTTPException(status_code=409, detail="Legal classification, independent DPO review or activated retention policy is missing; deletion fails closed.")
    if evidence.retention_expires_at > datetime.now(UTC):
        raise HTTPException(status_code=409, detail="Evidence is still within its retention period.")
    item = CargoDeliveryEvidenceDeletionRequest(
        evidence_id=evidence.id, requested_by=context.user.id,
        reason=payload.reason, status="requested",
    )
    db.add(item)
    db.flush()
    _audit(db, context=context, evidence=evidence, action="deletion_requested", outcome="success", reason=payload.reason)
    db.commit()
    return {"deletion_request_id": str(item.id), "status": item.status}


@router.post("/evidence/deletion-requests/{request_id}/approve")
def approve_and_execute_evidence_deletion(
    request_id: UUID, payload: EvidenceDeletionApproval, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.delete"):
        raise HTTPException(status_code=403, detail="Platform evidence-deletion permission is required.")
    item = db.scalar(select(CargoDeliveryEvidenceDeletionRequest).where(
        CargoDeliveryEvidenceDeletionRequest.id == request_id,
    ).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Deletion request not found.")
    if item.status == "completed":
        return {"deletion_request_id": str(item.id), "status": "completed"}
    if item.status not in {"requested", "failed"} or item.requested_by == context.user.id:
        raise HTTPException(status_code=409, detail="Approval requires a distinct authorized second person and a pending or retryable request.")
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == item.evidence_id,
    ).with_for_update())
    if _active_hold(db, evidence.id):
        raise HTTPException(status_code=409, detail="Active legal hold prevents deletion.")
    policy = _active_policy(db, evidence.retention_policy_version)
    if (evidence.classification_status != "ordinary" or evidence.retention_dpo_reviewed_at is None
            or policy is None or evidence.retention_expires_at is None
            or evidence.retention_expires_at > datetime.now(UTC)):
        raise HTTPException(status_code=409, detail="Legal classification, independent DPO review, activated policy or expiry eligibility is missing; deletion fails closed.")
    item.approved_by = context.user.id
    item.approved_at = datetime.now(UTC)
    item.executed_by = context.user.id
    try:
        delete_cargo_delivery_object(
            object_key=evidence.object_key,
            carrier_organization_id=str(evidence.carrier_organization_id),
            dispatch_id=str(evidence.dispatch_id),
        )
    except (StorageOperationFailed, StorageNotConfigured) as exc:
        item.status = "failed"
        item.failure_code = "storage_unavailable"
        evidence.deletion_failure_code = item.failure_code
        _audit(db, context=context, evidence=evidence, action="deletion_failed", outcome="failure")
        db.commit()
        raise HTTPException(status_code=503, detail="Storage deletion failed; the request remains retryable.") from exc
    item.status = "completed"
    item.completed_at = datetime.now(UTC)
    evidence.storage_deleted_at = item.completed_at
    evidence.lifecycle_state = "deleted"
    evidence.deletion_failure_code = None
    _audit(db, context=context, evidence=evidence, action="deletion_completed", outcome="success")
    db.commit()
    return {"deletion_request_id": str(item.id), "status": "completed", "evidence_metadata_preserved": True}
