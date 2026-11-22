"""Authenticated carrier operations, delivery proof and exception APIs."""
# ruff: noqa: B008,I001
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.cargo.carrier_operations import CarrierOperationalProfile, CargoDeliveryProof, CargoExceptionCase
from app.domains.cargo.evidence_lifecycle import CargoDeliveryEvidence, PROVISIONAL_POLICY_VERSION, PROVISIONAL_RETENTION_MONTHS, add_calendar_months
from app.domains.cargo.carrier_service import (
    validate_carrier_status, validate_exception_code, validate_exception_transition, validate_resolution,
)
from app.domains.cargo.dispatch import CargoDispatch, CargoTrackingEvent
from app.domains.cargo.models import CargoConsignment
from app.domains.fleet.object_storage import (
    InvalidStoredObject, StorageNotConfigured,
    create_cargo_delivery_upload_intent, verify_cargo_delivery_object,
)
from app.domains.identity.authorization import has_permission
from app.domains.identity.service import StaffContext
from app.domains.organizations.models import Organization
from app.routers.auth import current_staff_context, require_csrf

router = APIRouter(prefix="/cargo", tags=["carrier operations and delivery proof"])


class CarrierOperationsUpdate(BaseModel):
    service_area: str | None = Field(default=None, max_length=240)
    operating_notes: str | None = Field(default=None, max_length=500)


class CarrierStatusUpdate(BaseModel):
    operational_status: str


class DeliveryProofUploadIntentCreate(BaseModel):
    content_type: Literal["application/pdf", "image/jpeg", "image/png"]
    content_length: int = Field(ge=1, le=10 * 1024 * 1024)


class DeliveryProofCreate(BaseModel):
    idempotency_key: str = Field(min_length=16, max_length=128)
    received_by_name: str = Field(min_length=1, max_length=160)
    evidence_reference: str = Field(min_length=8, max_length=255)
    delivery_notes: str | None = Field(default=None, max_length=500)
    occurred_at: datetime


class DeliveryProofReview(BaseModel):
    decision: str = Field(pattern="^(accepted|rejected)$")
    reason: str | None = Field(default=None, min_length=2, max_length=500)


class ExceptionCreate(BaseModel):
    idempotency_key: str = Field(min_length=16, max_length=128)
    exception_code: str
    description: str = Field(min_length=3, max_length=500)


class ExceptionUpdate(BaseModel):
    target_status: str = Field(pattern="^(investigating|open|resolved|closed)$")
    resolution_code: str | None = None
    resolution_notes: str | None = Field(default=None, max_length=500)


def _allowed(db: Session, context: StaffContext, permission: str, organization_id: UUID | None = None) -> bool:
    return has_permission(db, user_id=context.user.id, permission_code=permission, organization_id=organization_id)


def _carrier_access(db: Session, context: StaffContext, organization_id: UUID) -> bool:
    return (
        _allowed(db, context, "platform.carrier.operations.manage")
        or _allowed(db, context, "platform.dispatch.manage")
        or _allowed(db, context, "operator.cargo.dispatch.manage", organization_id)
    )


def _proof_json(item: CargoDeliveryProof) -> dict:
    return {
        "id": str(item.id), "dispatch_id": str(item.dispatch_id), "consignment_id": str(item.consignment_id),
        "received_by_name": item.received_by_name, "evidence_reference": item.evidence_reference,
        "delivery_notes": item.delivery_notes, "occurred_at": item.occurred_at.isoformat(),
        "status": item.status, "review_reason": item.review_reason,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
    }


def _exception_json(item: CargoExceptionCase) -> dict:
    return {
        "id": str(item.id), "dispatch_id": str(item.dispatch_id), "consignment_id": str(item.consignment_id),
        "carrier_organization_id": str(item.carrier_organization_id), "exception_code": item.exception_code,
        "description": item.description, "status": item.status, "resolution_code": item.resolution_code,
        "resolution_notes": item.resolution_notes, "resolved_at": item.resolved_at.isoformat() if item.resolved_at else None,
    }


@router.put("/carriers/{organization_id}/operations")
def update_carrier_operations(
    organization_id: UUID, payload: CarrierOperationsUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _carrier_access(db, context, organization_id):
        raise HTTPException(status_code=403, detail="Carrier operational access is required.")
    organization = db.get(Organization, organization_id)
    if organization is None or organization.organization_type != "operator" or organization.status != "approved":
        raise HTTPException(status_code=409, detail="An approved operator organization is required.")
    item = db.scalar(select(CarrierOperationalProfile).where(
        CarrierOperationalProfile.organization_id == organization_id
    ).with_for_update())
    if item is None:
        item = CarrierOperationalProfile(organization_id=organization_id, updated_by=context.user.id)
        db.add(item)
    item.service_area = payload.service_area
    item.operating_notes = payload.operating_notes
    item.updated_by = context.user.id
    db.flush()
    record_event(db, event_type="cargo.carrier.operations.updated", actor_type="staff",
                 actor_id=str(context.user.id), resource_type="carrier_operational_profile",
                 resource_id=str(item.id), action="update", outcome="success",
                 organization_id=organization_id, metadata={"service_area": payload.service_area})
    db.commit()
    db.refresh(item)
    return {"id": str(item.id), "organization_id": str(item.organization_id),
            "operational_status": item.operational_status, "service_area": item.service_area}


@router.patch("/carriers/{organization_id}/operations/status")
def set_carrier_status(
    organization_id: UUID, payload: CarrierStatusUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.carrier.operations.manage"):
        raise HTTPException(status_code=403, detail="Platform carrier-operations permission is required.")
    validate_carrier_status(payload.operational_status)
    organization = db.get(Organization, organization_id)
    if organization is None or organization.organization_type != "operator" or organization.status != "approved":
        raise HTTPException(status_code=409, detail="An approved operator organization is required.")
    item = db.scalar(select(CarrierOperationalProfile).where(
        CarrierOperationalProfile.organization_id == organization_id
    ).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Carrier operational profile not found.")
    previous = item.operational_status
    item.operational_status = payload.operational_status
    item.updated_by = context.user.id
    record_event(db, event_type="cargo.carrier.operations.status_changed", actor_type="staff",
                 actor_id=str(context.user.id), resource_type="carrier_operational_profile",
                 resource_id=str(item.id), action="status_change", outcome="success",
                 organization_id=organization_id, metadata={"from": previous, "to": item.operational_status})
    db.commit()
    return {"organization_id": str(organization_id), "operational_status": item.operational_status}


@router.post("/dispatches/{dispatch_id}/delivery-proof/upload-intents", status_code=201)
def create_delivery_proof_upload_intent(
    dispatch_id: UUID, payload: DeliveryProofUploadIntentCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    dispatch = db.scalar(select(CargoDispatch).where(CargoDispatch.id == dispatch_id).with_for_update())
    if dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    if not _allowed(db, context, "operator.cargo.delivery_proof.submit", dispatch.carrier_organization_id):
        raise HTTPException(status_code=403, detail="Assigned carrier delivery-proof permission is required.")
    if dispatch.status != "in_transit":
        raise HTTPException(status_code=409, detail="Delivery evidence can only be uploaded for an in-transit dispatch.")
    try:
        intent = create_cargo_delivery_upload_intent(
            carrier_organization_id=str(dispatch.carrier_organization_id),
            dispatch_id=str(dispatch.id),
            content_type=payload.content_type,
            content_length=payload.content_length,
        )
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail="Private evidence storage is not configured.") from exc
    except InvalidStoredObject as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    record_event(
        db, event_type="cargo.delivery_proof.upload_intent_created", actor_type="staff",
        actor_id=str(context.user.id), resource_type="cargo_dispatch",
        resource_id=str(dispatch.id), action="upload_intent", outcome="success",
        organization_id=dispatch.carrier_organization_id,
        metadata={"content_type": payload.content_type, "content_length": payload.content_length},
    )
    db.commit()
    return intent


@router.post("/dispatches/{dispatch_id}/delivery-proof", status_code=201)
def submit_delivery_proof(
    dispatch_id: UUID, payload: DeliveryProofCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    dispatch = db.scalar(select(CargoDispatch).where(CargoDispatch.id == dispatch_id).with_for_update())
    if dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    if not _allowed(db, context, "operator.cargo.delivery_proof.submit", dispatch.carrier_organization_id):
        raise HTTPException(status_code=403, detail="Assigned carrier delivery-proof permission is required.")
    if payload.occurred_at.tzinfo is None or payload.occurred_at.utcoffset() is None:
        raise HTTPException(status_code=422, detail="occurred_at must include an explicit timezone offset.")
    if dispatch.status != "in_transit":
        raise HTTPException(status_code=409, detail="Delivery proof can only be submitted for an in-transit dispatch.")
    try:
        verify_cargo_delivery_object(
            object_key=payload.evidence_reference,
            carrier_organization_id=str(dispatch.carrier_organization_id),
            dispatch_id=str(dispatch.id),
        )
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail="Private evidence storage is not configured.") from exc
    except InvalidStoredObject as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    existing = db.scalar(select(CargoDeliveryProof).where(
        CargoDeliveryProof.dispatch_id == dispatch.id
    ))
    if existing is not None:
        same = (
            existing.idempotency_key == payload.idempotency_key
            and existing.received_by_name == payload.received_by_name
            and existing.evidence_reference == payload.evidence_reference
            and existing.delivery_notes == payload.delivery_notes
            and existing.occurred_at == payload.occurred_at
        )
        if not same:
            raise HTTPException(status_code=409, detail="A delivery proof already exists for this dispatch.")
        return _proof_json(existing)
    proof = CargoDeliveryProof(
        dispatch_id=dispatch.id, consignment_id=dispatch.consignment_id,
        idempotency_key=payload.idempotency_key, received_by_name=payload.received_by_name,
        evidence_reference=payload.evidence_reference, delivery_notes=payload.delivery_notes,
        occurred_at=payload.occurred_at, submitted_by=context.user.id,
    )
    db.add(proof)
    db.flush()
    record_event(db, event_type="cargo.delivery_proof.submitted", actor_type="staff",
                 actor_id=str(context.user.id), resource_type="cargo_delivery_proof",
                 resource_id=str(proof.id), action="submit", outcome="success",
                 organization_id=dispatch.carrier_organization_id,
                 metadata={"dispatch_id": str(dispatch.id), "evidence_reference": payload.evidence_reference})
    db.commit()
    db.refresh(proof)
    return _proof_json(proof)


@router.patch("/dispatches/{dispatch_id}/delivery-proof/review")
def review_delivery_proof(
    dispatch_id: UUID, payload: DeliveryProofReview, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.cargo.delivery_proof.review"):
        raise HTTPException(status_code=403, detail="Platform delivery-proof review permission is required.")
    proof = db.scalar(select(CargoDeliveryProof).where(
        CargoDeliveryProof.dispatch_id == dispatch_id
    ).with_for_update())
    if proof is None:
        raise HTTPException(status_code=404, detail="Delivery proof not found.")
    if proof.status != "submitted":
        raise HTTPException(status_code=409, detail="Only submitted delivery proof can be reviewed.")
    dispatch = db.scalar(select(CargoDispatch).where(CargoDispatch.id == dispatch_id).with_for_update())
    cargo = db.scalar(select(CargoConsignment).where(
        CargoConsignment.id == proof.consignment_id
    ).with_for_update())
    proof.status = payload.decision
    proof.review_reason = payload.reason
    if payload.decision == "accepted":
        evidence = db.scalar(select(CargoDeliveryEvidence).where(
            CargoDeliveryEvidence.delivery_proof_id == proof.id
        ).with_for_update())
        if evidence is not None and evidence.retention_started_at is None:
            retention_start = datetime.now(UTC)
            evidence.retention_policy_version = PROVISIONAL_POLICY_VERSION
            evidence.retention_started_at = retention_start
            evidence.retention_expires_at = add_calendar_months(
                retention_start, PROVISIONAL_RETENTION_MONTHS,
            )
    proof.reviewed_by = context.user.id
    proof.reviewed_at = datetime.now(UTC)
    if payload.decision == "accepted":
        if dispatch.status != "in_transit" or cargo.status != "in_transit":
            raise HTTPException(status_code=409, detail="Dispatch and consignment must both be in transit.")
        dispatch.status = "delivered"
        dispatch.version += 1
        cargo.status = "delivered"
        cargo.delivered_at = datetime.now(UTC)
        db.add(CargoTrackingEvent(
            dispatch_id=dispatch.id, consignment_id=cargo.id,
            sequence_number=(db.scalar(select(func.max(CargoTrackingEvent.sequence_number)).where(
                CargoTrackingEvent.dispatch_id == dispatch.id
            )) or 0) + 1,
            idempotency_key=f"delivery-proof-accepted:{proof.id}",
            event_type="delivered", description="Delivery proof accepted",
            occurred_at=proof.occurred_at, recorded_by=context.user.id,
        ))
    record_event(db, event_type=f"cargo.delivery_proof.{payload.decision}", actor_type="staff",
                 actor_id=str(context.user.id), resource_type="cargo_delivery_proof",
                 resource_id=str(proof.id), action="review", outcome="success",
                 organization_id=dispatch.carrier_organization_id, reason_code=payload.reason,
                 metadata={"dispatch_id": str(dispatch.id), "consignment_id": str(cargo.id)})
    db.commit()
    db.refresh(proof)
    return _proof_json(proof)


@router.post("/dispatches/{dispatch_id}/exceptions", status_code=201)
def create_cargo_exception(
    dispatch_id: UUID, payload: ExceptionCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    dispatch = db.scalar(select(CargoDispatch).where(CargoDispatch.id == dispatch_id).with_for_update())
    if dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    if not _allowed(db, context, "operator.cargo.exception.manage", dispatch.carrier_organization_id):
        raise HTTPException(status_code=403, detail="Assigned carrier exception permission is required.")
    validate_exception_code(payload.exception_code)
    existing = db.scalar(select(CargoExceptionCase).where(
        CargoExceptionCase.dispatch_id == dispatch.id,
        CargoExceptionCase.idempotency_key == payload.idempotency_key,
    ))
    if existing is not None:
        if existing.exception_code != payload.exception_code or existing.description != payload.description:
            raise HTTPException(status_code=409, detail="Exception idempotency key conflicts with an earlier request.")
        return _exception_json(existing)
    item = CargoExceptionCase(
        dispatch_id=dispatch.id, consignment_id=dispatch.consignment_id,
        carrier_organization_id=dispatch.carrier_organization_id,
        idempotency_key=payload.idempotency_key, exception_code=payload.exception_code,
        description=payload.description, reported_by=context.user.id,
    )
    db.add(item)
    db.flush()
    record_event(db, event_type="cargo.exception.opened", actor_type="staff",
                 actor_id=str(context.user.id), resource_type="cargo_exception_case",
                 resource_id=str(item.id), action="open", outcome="success",
                 organization_id=dispatch.carrier_organization_id,
                 metadata={"dispatch_id": str(dispatch.id), "exception_code": payload.exception_code})
    db.commit()
    db.refresh(item)
    return _exception_json(item)


@router.patch("/exceptions/{exception_id}")
def update_cargo_exception(
    exception_id: UUID, payload: ExceptionUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    item = db.scalar(select(CargoExceptionCase).where(
        CargoExceptionCase.id == exception_id
    ).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Cargo exception not found.")
    if not (
        _allowed(db, context, "platform.dispatch.manage")
        or _allowed(db, context, "operator.cargo.exception.manage", item.carrier_organization_id)
    ):
        raise HTTPException(status_code=403, detail="Exception management permission is required.")
    validate_exception_transition(item.status, payload.target_status)
    if payload.target_status == "resolved":
        if payload.resolution_code is None:
            raise HTTPException(status_code=422, detail="A resolution code is required.")
        validate_resolution(payload.resolution_code)
        item.resolution_code = payload.resolution_code
        item.resolution_notes = payload.resolution_notes
        item.resolved_by = context.user.id
        item.resolved_at = datetime.now(UTC)
    elif payload.resolution_code is not None or payload.resolution_notes is not None:
        raise HTTPException(status_code=422, detail="Resolution details are accepted only when resolving an exception.")
    previous = item.status
    item.status = payload.target_status
    record_event(db, event_type="cargo.exception.status_changed", actor_type="staff",
                 actor_id=str(context.user.id), resource_type="cargo_exception_case",
                 resource_id=str(item.id), action="transition", outcome="success",
                 organization_id=item.carrier_organization_id,
                 metadata={"from": previous, "to": item.status, "resolution_code": item.resolution_code})
    db.commit()
    db.refresh(item)
    return _exception_json(item)
