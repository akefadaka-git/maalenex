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
    CargoDeliveryEvidenceRetentionPolicy, CargoDeliveryEvidenceRightsRequest,
)
from app.domains.cargo.legal_retention import deletion_block_reason, effective_retention_deadline
from app.domains.fleet.object_storage import (
    InvalidStoredObject, StorageNotConfigured, StorageOperationFailed,
    create_cargo_delivery_download_url, create_cargo_delivery_upload_intent,
    delete_cargo_delivery_object, verify_cargo_delivery_object,
)
from app.domains.identity.authorization import has_permission
from app.domains.identity.models import User
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
    is_accounting_document: bool = False
    is_commercial_correspondence: bool = False
    is_ordinary_operational_evidence: bool = False
    contains_personal_data: bool = True
    contains_sensitive_personal_data: bool = False
    personal_data_legal_basis: Literal["contract", "legal_obligation", "legitimate_interests", "consent", "vital_interests", "public_interest"] | None = None
    personal_data_processing_justification: str | None = Field(default=None, min_length=10, max_length=1000)
    privacy_notice_reference: str | None = Field(default=None, min_length=5, max_length=160)
    international_transfer_required: bool = False
    transfer_safeguard_reference: str | None = Field(default=None, min_length=5, max_length=160)
    sensitive_transfer_eca_approval_reference: str | None = Field(default=None, min_length=5, max_length=160)
    accounting_document_date: datetime | None = None
    commercial_correspondence_date: datetime | None = None
    operational_legal_basis: Literal["contract", "legal_obligation", "legitimate_interests", "consent", "vital_interests", "public_interest"] | None = None
    operational_retention_justification: str | None = Field(default=None, min_length=10, max_length=1000)
    sensitive_data_handling_review_reference: str | None = Field(default=None, min_length=5, max_length=160)
    legal_review_reference: str = Field(min_length=5, max_length=160)


class EvidenceRetentionReview(BaseModel):
    note: str = Field(min_length=5, max_length=500)
    operational_dpia_reference: str | None = Field(default=None, min_length=5, max_length=160)
    sensitive_data_handling_review_reference: str | None = Field(default=None, min_length=5, max_length=160)
    tombstone_retention_until: datetime | None = None
    audit_retention_until: datetime | None = None
    metadata_retention_justification: str | None = Field(default=None, min_length=10, max_length=1000)


class EvidenceHoldReleaseReview(BaseModel):
    note: str = Field(min_length=5, max_length=500)


class EvidenceRightsRequestCreate(BaseModel):
    request_type: Literal["access", "rectification", "erasure", "restriction"]
    request_reference: str = Field(min_length=5, max_length=160)


class EvidenceRightsRequestAssessment(BaseModel):
    outcome: Literal["under_review", "retained_by_legal_obligation", "eligible_for_erasure", "completed"]
    note: str = Field(min_length=10, max_length=1000)


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
    grantee = db.get(User, payload.user_id)
    if grantee is None or grantee.status != "active":
        raise HTTPException(status_code=404, detail="Active evidence-access grantee was not found.")
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


@router.post("/evidence/holds/{hold_id}/release-review")
def review_evidence_hold_release(
    hold_id: UUID, payload: EvidenceHoldReleaseReview, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.hold.review"):
        raise HTTPException(status_code=403, detail="Independent DPO hold-release review permission is required.")
    hold = db.scalar(select(CargoDeliveryEvidenceHold).where(
        CargoDeliveryEvidenceHold.id == hold_id,
    ).with_for_update())
    if hold is None or hold.released_at is not None:
        raise HTTPException(status_code=404, detail="Active legal hold not found.")
    if hold.issued_by == context.user.id:
        raise HTTPException(status_code=409, detail="Hold issuer cannot independently review hold release.")
    hold.release_reviewed_by = context.user.id
    hold.release_reviewed_at = datetime.now(UTC)
    hold.release_review_note = payload.note
    db.commit()
    return {"hold_id": str(hold.id), "release_reviewed": True}


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
    if hold.release_reviewed_at is None or hold.release_reviewed_by in {None, context.user.id, hold.issued_by}:
        raise HTTPException(status_code=409, detail="A distinct DPO release review is required before Legal/Compliance can release the hold.")
    hold.released_by = context.user.id
    hold.released_at = datetime.now(UTC)
    hold.release_note = payload.note
    evidence = db.get(CargoDeliveryEvidence, hold.evidence_id)
    evidence.lifecycle_state = (
        "attached" if evidence.delivery_proof_id
        else "verified" if evidence.verified_at is not None
        else "pending"
    )
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
    if not (payload.is_accounting_document or payload.is_commercial_correspondence or payload.is_ordinary_operational_evidence):
        raise HTTPException(status_code=422, detail="At least one legal evidence classification is required.")
    if payload.is_accounting_document and payload.accounting_document_date is None:
        raise HTTPException(status_code=422, detail="Accounting-document preparation/last-entry date is required.")
    if payload.is_commercial_correspondence and payload.commercial_correspondence_date is None:
        raise HTTPException(status_code=422, detail="Commercial correspondence date is required.")
    if payload.contains_sensitive_personal_data and not payload.contains_personal_data:
        raise HTTPException(status_code=422, detail="Sensitive personal data must also be marked as personal data.")
    if payload.contains_personal_data and (
        not payload.personal_data_legal_basis or not payload.personal_data_processing_justification
        or not payload.privacy_notice_reference
    ):
        raise HTTPException(status_code=422, detail="Personal-data processing requires a documented legal basis, necessity justification and privacy-notice reference.")
    if payload.international_transfer_required and not payload.transfer_safeguard_reference:
        raise HTTPException(status_code=422, detail="International transfers require documented adequacy or safeguard evidence.")
    if payload.contains_sensitive_personal_data and payload.international_transfer_required and not payload.sensitive_transfer_eca_approval_reference:
        raise HTTPException(status_code=422, detail="Sensitive personal-data transfers require prior ECA approval evidence.")
    if payload.is_ordinary_operational_evidence and (not payload.operational_legal_basis or not payload.operational_retention_justification):
        raise HTTPException(status_code=422, detail="Residual operational evidence requires a documented legal basis and retention justification.")
    for source_date in (payload.accounting_document_date, payload.commercial_correspondence_date):
        if source_date is not None and (source_date.tzinfo is None or source_date.utcoffset() is None):
            raise HTTPException(status_code=422, detail="Legal retention source dates must include a timezone offset.")
    evidence.is_accounting_document = payload.is_accounting_document
    evidence.is_commercial_correspondence = payload.is_commercial_correspondence
    evidence.is_ordinary_operational_evidence = payload.is_ordinary_operational_evidence
    evidence.contains_personal_data = payload.contains_personal_data
    evidence.contains_sensitive_personal_data = payload.contains_sensitive_personal_data
    evidence.personal_data_legal_basis = payload.personal_data_legal_basis
    evidence.personal_data_processing_justification = payload.personal_data_processing_justification
    evidence.privacy_notice_reference = payload.privacy_notice_reference
    evidence.international_transfer_required = payload.international_transfer_required
    evidence.transfer_safeguard_reference = payload.transfer_safeguard_reference
    evidence.sensitive_transfer_eca_approval_reference = payload.sensitive_transfer_eca_approval_reference
    evidence.accounting_document_date = payload.accounting_document_date
    evidence.commercial_correspondence_date = payload.commercial_correspondence_date
    evidence.operational_retention_started_at = evidence.retention_started_at or evidence.attached_at
    evidence.operational_legal_basis = payload.operational_legal_basis
    evidence.operational_retention_justification = payload.operational_retention_justification
    evidence.sensitive_data_handling_review_reference = payload.sensitive_data_handling_review_reference
    evidence.classification_complete = False
    evidence.classification_status = "multi_class_pending_dpo"
    evidence.legal_retention_until = None
    evidence.retention_expires_at = None
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
    if evidence.is_ordinary_operational_evidence and not payload.operational_dpia_reference:
        raise HTTPException(status_code=409, detail="A documented DPIA reference is required for the 24-month residual operational category.")
    if evidence.contains_sensitive_personal_data and not (payload.sensitive_data_handling_review_reference or evidence.sensitive_data_handling_review_reference):
        raise HTTPException(status_code=409, detail="Sensitive-data handling review evidence is required.")
    if payload.tombstone_retention_until is None or payload.audit_retention_until is None or payload.metadata_retention_justification is None:
        raise HTTPException(status_code=409, detail="Tombstone and audit-log retention periods require an independent documented justification.")
    now = datetime.now(UTC)
    for retention_date in (payload.tombstone_retention_until, payload.audit_retention_until):
        if retention_date.tzinfo is None or retention_date.utcoffset() is None:
            raise HTTPException(status_code=422, detail="Metadata retention dates must include timezone offsets.")
        if retention_date <= now:
            raise HTTPException(status_code=422, detail="Metadata retention deadlines must be in the future.")
    evidence.operational_dpia_reference = payload.operational_dpia_reference
    if payload.sensitive_data_handling_review_reference:
        evidence.sensitive_data_handling_review_reference = payload.sensitive_data_handling_review_reference
    evidence.tombstone_retention_until = payload.tombstone_retention_until
    evidence.audit_retention_until = payload.audit_retention_until
    evidence.retention_metadata_justification = payload.metadata_retention_justification
    evidence.classification_complete = True
    deadline = effective_retention_deadline(evidence)
    if deadline is None:
        evidence.classification_complete = False
        raise HTTPException(status_code=409, detail="A complete category-specific retention deadline could not be established.")
    evidence.legal_retention_until = deadline
    evidence.retention_expires_at = deadline
    evidence.classification_status = "classified"
    evidence.classification_complete = True
    evidence.retention_dpo_reviewed_by = context.user.id
    evidence.retention_dpo_reviewed_at = now
    _audit(db, context=context, evidence=evidence, action="retention_classification_dpo_reviewed",
           outcome="success", reason=f"multi_class:{payload.note}")
    db.commit()
    return {"evidence_id": str(evidence.id), "classification_status": evidence.classification_status,
            "dpo_reviewed": True}


@router.post("/evidence/{evidence_id}/rights-requests", status_code=201)
def register_evidence_rights_request(
    evidence_id: UUID, payload: EvidenceRightsRequestCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.retention.manage"):
        raise HTTPException(status_code=403, detail="Legal/Compliance rights-request triage permission is required.")
    evidence = db.get(CargoDeliveryEvidence, evidence_id)
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    item = CargoDeliveryEvidenceRightsRequest(
        evidence_id=evidence.id, request_type=payload.request_type,
        request_reference=payload.request_reference, status="pending",
    )
    db.add(item)
    evidence.rights_request_status = "pending"
    db.flush()
    _audit(db, context=context, evidence=evidence, action="rights_request_registered", outcome="success")
    db.commit()
    return {"rights_request_id": str(item.id), "status": item.status}


@router.post("/evidence/rights-requests/{request_id}/assessment")
def assess_evidence_rights_request(
    request_id: UUID, payload: EvidenceRightsRequestAssessment, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.evidence.retention.manage"):
        raise HTTPException(status_code=403, detail="Legal/Compliance rights-request triage permission is required.")
    item = db.scalar(select(CargoDeliveryEvidenceRightsRequest).where(
        CargoDeliveryEvidenceRightsRequest.id == request_id,
    ).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Rights request not found.")
    evidence = db.scalar(select(CargoDeliveryEvidence).where(
        CargoDeliveryEvidence.id == item.evidence_id,
    ).with_for_update())
    if payload.outcome == "completed" and item.request_type == "erasure":
        raise HTTPException(status_code=409, detail="An erasure request can be marked completed only after the controlled deletion workflow succeeds.")
    if payload.outcome == "eligible_for_erasure":
        if item.request_type != "erasure":
            raise HTTPException(status_code=422, detail="Only an erasure request can receive erasure eligibility.")
        if _active_hold(db, evidence.id) is not None:
            raise HTTPException(status_code=409, detail="An active legal hold prevents erasure eligibility.")
        prior_rights_status = evidence.rights_request_status
        evidence.rights_request_status = "eligible_for_erasure"
        block_reason = deletion_block_reason(evidence, now=datetime.now(UTC))
        if block_reason:
            evidence.rights_request_status = prior_rights_status
            raise HTTPException(status_code=409, detail=f"Erasure cannot be approved: {block_reason}.")
    item.status = payload.outcome
    item.assessed_by = context.user.id
    item.assessed_at = datetime.now(UTC)
    item.assessment_note = payload.note
    evidence.rights_request_status = (
        "pending" if payload.outcome == "under_review"
        else "eligible_for_erasure" if payload.outcome == "eligible_for_erasure"
        else "none"
    )
    _audit(db, context=context, evidence=evidence, action="rights_request_assessed", outcome="success")
    db.commit()
    return {"rights_request_id": str(item.id), "status": item.status}


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
    block_reason = deletion_block_reason(evidence, now=datetime.now(UTC))
    if block_reason:
        raise HTTPException(status_code=409, detail=f"Evidence deletion fails closed: {block_reason}.")
    if policy is None and evidence.rights_request_status != "eligible_for_erasure":
        raise HTTPException(status_code=409, detail="An independently validated and activated retention policy is required; deletion fails closed.")
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
    block_reason = deletion_block_reason(evidence, now=datetime.now(UTC))
    if block_reason:
        raise HTTPException(status_code=409, detail=f"Evidence deletion fails closed: {block_reason}.")
    if policy is None:
        raise HTTPException(status_code=409, detail="An independently validated and activated retention policy is required; deletion fails closed.")
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
    for rights_item in db.scalars(select(CargoDeliveryEvidenceRightsRequest).where(
        CargoDeliveryEvidenceRightsRequest.evidence_id == evidence.id,
        CargoDeliveryEvidenceRightsRequest.request_type == "erasure",
        CargoDeliveryEvidenceRightsRequest.status == "eligible_for_erasure",
    )).all():
        rights_item.status = "completed"
    evidence.rights_request_status = "none"
    _audit(db, context=context, evidence=evidence, action="deletion_completed", outcome="success")
    db.commit()
    return {"deletion_request_id": str(item.id), "status": "completed", "evidence_metadata_preserved": True}
