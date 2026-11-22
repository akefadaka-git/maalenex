"""Authenticated staff API for cargo consignments; no frontend coupling."""
# ruff: noqa: B008
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.cargo.models import CargoConsignment
from app.domains.cargo.service import validate_transition
from app.domains.identity.authorization import has_permission
from app.domains.identity.service import StaffContext
from app.domains.organizations.models import Organization
from app.routers.auth import current_staff_context, require_csrf

router = APIRouter(prefix="/cargo", tags=["cargo"])


class ConsignmentCreate(BaseModel):
    organization_id: UUID
    consignment_reference: str = Field(min_length=2, max_length=80)
    idempotency_key: str = Field(min_length=16, max_length=128)
    sender_name: str = Field(min_length=1, max_length=160)
    recipient_name: str = Field(min_length=1, max_length=160)
    destination: str = Field(min_length=2, max_length=240)
    description: str = Field(min_length=1, max_length=500)
    weight_grams: int | None = Field(default=None, gt=0, le=1_000_000_000)


class ConsignmentTransition(BaseModel):
    target_status: str = Field(pattern="^(accepted|assigned|in_transit|delivered|cancelled|exception)$")
    assigned_organization_id: UUID | None = None
    reason_code: str | None = Field(default=None, min_length=2, max_length=80)


def _authorize(db: Session, context: StaffContext, organization_id: UUID | None = None) -> None:
    if not has_permission(db, user_id=context.user.id, permission_code="platform.cargo.manage", organization_id=organization_id):
        raise HTTPException(status_code=403, detail="Cargo management permission is required.")


def _serialize(item: CargoConsignment) -> dict:
    return {
        "id": str(item.id), "organization_id": str(item.organization_id),
        "consignment_reference": item.consignment_reference,
        "sender_name": item.sender_name, "recipient_name": item.recipient_name,
        "destination": item.destination, "description": item.description,
        "weight_grams": item.weight_grams, "status": item.status,
        "assigned_organization_id": str(item.assigned_organization_id) if item.assigned_organization_id else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "delivered_at": item.delivered_at.isoformat() if item.delivered_at else None,
    }


@router.post("/consignments", status_code=201)
def create_consignment(payload: ConsignmentCreate, request: Request,
                       context: StaffContext = Depends(current_staff_context),
                       db: Session = Depends(get_db)) -> dict:
    require_csrf(request, context)
    _authorize(db, context, payload.organization_id)
    organization = db.get(Organization, payload.organization_id)
    if organization is None or organization.status != "approved":
        raise HTTPException(status_code=409, detail="An approved organization is required.")
    existing = db.scalar(select(CargoConsignment).where(
        CargoConsignment.organization_id == payload.organization_id,
        CargoConsignment.idempotency_key == payload.idempotency_key,
    ))
    if existing is not None:
        if existing.consignment_reference != payload.consignment_reference or existing.description != payload.description:
            raise HTTPException(status_code=409, detail="Idempotency key was already used for a different consignment.")
        return _serialize(existing)
    item = CargoConsignment(**payload.model_dump(), created_by=context.user.id)
    db.add(item)
    record_event(db, event_type="cargo.consignment.created", actor_type="staff", actor_id=str(context.user.id),
                 resource_type="cargo_consignment", resource_id=str(item.id), action="create", outcome="success",
                 organization_id=payload.organization_id, metadata={"reference": payload.consignment_reference, "status": "draft"})
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Consignment reference or idempotency key already exists.")
    db.refresh(item)
    return _serialize(item)


@router.get("/consignments")
def list_consignments(organization_id: UUID, limit: int = 50,
                      context: StaffContext = Depends(current_staff_context),
                      db: Session = Depends(get_db)) -> dict:
    _authorize(db, context, organization_id)
    rows = db.scalars(select(CargoConsignment).where(
        CargoConsignment.organization_id == organization_id
    ).order_by(CargoConsignment.created_at.desc()).limit(max(1, min(limit, 100))))
    return {"items": [_serialize(item) for item in rows]}


@router.post("/consignments/{consignment_id}/transition")
def transition_consignment(consignment_id: UUID, payload: ConsignmentTransition, request: Request,
                           context: StaffContext = Depends(current_staff_context),
                           db: Session = Depends(get_db)) -> dict:
    require_csrf(request, context)
    item = db.scalar(select(CargoConsignment).where(CargoConsignment.id == consignment_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Consignment not found.")
    _authorize(db, context, item.organization_id)
    validate_transition(item.status, payload.target_status)
    if payload.target_status == "assigned":
        if payload.assigned_organization_id is None:
            raise HTTPException(status_code=422, detail="An approved carrier organization is required for assignment.")
        carrier = db.get(Organization, payload.assigned_organization_id)
        if carrier is None or carrier.status != "approved" or carrier.organization_type != "operator":
            raise HTTPException(status_code=409, detail="Carrier must be an approved operator organization.")
        item.assigned_organization_id = carrier.id
    elif payload.assigned_organization_id is not None:
        raise HTTPException(status_code=422, detail="Carrier assignment is only accepted during assignment transition.")
    previous = item.status
    item.status = payload.target_status
    if payload.target_status == "delivered":
        item.delivered_at = datetime.now(UTC)
    record_event(db, event_type="cargo.consignment.transitioned", actor_type="staff", actor_id=str(context.user.id),
                 resource_type="cargo_consignment", resource_id=str(item.id), action="transition", outcome="success",
                 organization_id=item.organization_id, reason_code=payload.reason_code,
                 metadata={"from_status": previous, "to_status": item.status,
                           "assigned_organization_id": str(item.assigned_organization_id) if item.assigned_organization_id else None})
    db.commit()
    db.refresh(item)
    return _serialize(item)
