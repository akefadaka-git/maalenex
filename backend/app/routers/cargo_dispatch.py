"""Staff API for dispatch offers and append-only cargo tracking events."""
# ruff: noqa: B008,I001
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.cargo.carrier_operations import CarrierOperationalProfile, CargoDeliveryProof
from app.domains.cargo.dispatch import CargoDispatch, CargoTrackingEvent
from app.domains.cargo.dispatch_service import validate_dispatch_transition, validate_tracking_event
from app.domains.cargo.models import CargoConsignment
from app.domains.identity.authorization import has_permission
from app.domains.identity.service import StaffContext
from app.domains.fleet.models import Vehicle
from app.domains.organizations.models import Organization
from app.routers.auth import current_staff_context, require_csrf

router = APIRouter(prefix="/cargo", tags=["cargo dispatch and tracking"])


class DispatchCreate(BaseModel):
    consignment_id: UUID
    dispatch_reference: str = Field(min_length=2, max_length=80)
    idempotency_key: str = Field(min_length=16, max_length=128)
    carrier_organization_id: UUID
    vehicle_id: UUID | None = None


class DispatchTransition(BaseModel):
    target_status: str = Field(pattern="^(accepted|rejected|picked_up|in_transit|delivered|failed|cancelled)$")
    reason_code: str | None = Field(default=None, min_length=2, max_length=80)


class TrackingEventCreate(BaseModel):
    idempotency_key: str = Field(min_length=16, max_length=128)
    event_type: str = Field(min_length=3, max_length=32)
    description: str | None = Field(default=None, max_length=300)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    occurred_at: datetime | None = None

    @model_validator(mode="after")
    def validate_tracking_payload(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Latitude and longitude must be supplied together.")
        if self.occurred_at is not None and (
            self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None
        ):
            raise ValueError("occurred_at must include an explicit timezone offset.")
        return self


def _allowed(db: Session, context: StaffContext, permission: str, organization_id: UUID | None = None) -> bool:
    return has_permission(db, user_id=context.user.id, permission_code=permission, organization_id=organization_id)


def _dispatch_json(item: CargoDispatch) -> dict:
    return {
        "id": str(item.id),
        "consignment_id": str(item.consignment_id),
        "dispatch_reference": item.dispatch_reference,
        "carrier_organization_id": str(item.carrier_organization_id),
        "vehicle_id": str(item.vehicle_id) if item.vehicle_id else None,
        "status": item.status,
        "version": item.version,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def _tracking_json(item: CargoTrackingEvent) -> dict:
    return {
        "id": str(item.id),
        "dispatch_id": str(item.dispatch_id),
        "consignment_id": str(item.consignment_id),
        "sequence_number": item.sequence_number,
        "event_type": item.event_type,
        "description": item.description,
        "latitude": item.latitude,
        "longitude": item.longitude,
        "occurred_at": item.occurred_at.isoformat(),
        "recorded_at": item.recorded_at.isoformat() if item.recorded_at else None,
    }


@router.post("/dispatches", status_code=201)
def create_dispatch(
    payload: DispatchCreate,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if not _allowed(db, context, "platform.dispatch.manage"):
        raise HTTPException(status_code=403, detail="Platform dispatch permission is required.")
    cargo = db.scalar(select(CargoConsignment).where(CargoConsignment.id == payload.consignment_id).with_for_update())
    if cargo is None:
        raise HTTPException(status_code=404, detail="Consignment not found.")
    if cargo.status != "accepted":
        raise HTTPException(status_code=409, detail="Only accepted consignments can be offered for dispatch.")
    carrier = db.get(Organization, payload.carrier_organization_id)
    if carrier is None or carrier.status != "approved" or carrier.organization_type != "operator":
        raise HTTPException(status_code=409, detail="Carrier must be an approved operator organization.")
    carrier_profile = db.scalar(select(CarrierOperationalProfile).where(
        CarrierOperationalProfile.organization_id == carrier.id
    ))
    if carrier_profile is None or carrier_profile.operational_status != "active":
        raise HTTPException(status_code=409, detail="Carrier must have an active operational profile before dispatch.")
    if payload.vehicle_id is not None:
        vehicle = db.get(Vehicle, payload.vehicle_id)
        if (
            vehicle is None
            or vehicle.organization_id != carrier.id
            or vehicle.status != "active"
            or vehicle.review_status != "approved"
        ):
            raise HTTPException(status_code=409, detail="Vehicle must be approved and active under the selected carrier.")
    existing = db.scalar(
        select(CargoDispatch).where(
            CargoDispatch.consignment_id == cargo.id,
            CargoDispatch.idempotency_key == payload.idempotency_key,
        )
    )
    if existing is not None:
        if (
            existing.carrier_organization_id != payload.carrier_organization_id
            or existing.dispatch_reference != payload.dispatch_reference
            or existing.vehicle_id != payload.vehicle_id
        ):
            raise HTTPException(status_code=409, detail="Dispatch idempotency key conflicts with an earlier request.")
        return _dispatch_json(existing)
    item = CargoDispatch(
        consignment_id=cargo.id,
        dispatch_reference=payload.dispatch_reference,
        idempotency_key=payload.idempotency_key,
        carrier_organization_id=carrier.id,
        vehicle_id=payload.vehicle_id,
        offered_by=context.user.id,
    )
    db.add(item)
    db.flush()
    db.add(
        CargoTrackingEvent(
            dispatch_id=item.id,
            consignment_id=cargo.id,
            sequence_number=1,
            idempotency_key=f"dispatch-created:{item.id}",
            event_type="offered",
            description="Dispatch offer created",
            occurred_at=datetime.now(UTC),
            recorded_by=context.user.id,
        )
    )
    record_event(
        db,
        event_type="cargo.dispatch.offered",
        actor_type="staff",
        actor_id=str(context.user.id),
        resource_type="cargo_dispatch",
        resource_id=str(item.id),
        action="offer",
        outcome="success",
        organization_id=cargo.organization_id,
        metadata={"carrier_organization_id": str(carrier.id), "consignment_id": str(cargo.id)},
    )
    db.commit()
    db.refresh(item)
    return _dispatch_json(item)


@router.post("/dispatches/{dispatch_id}/transition")
def transition_dispatch(
    dispatch_id: UUID,
    payload: DispatchTransition,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    item = db.scalar(select(CargoDispatch).where(CargoDispatch.id == dispatch_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    platform = _allowed(db, context, "platform.dispatch.manage")
    carrier_user = _allowed(db, context, "operator.cargo.dispatch.manage", item.carrier_organization_id)
    if not (platform or carrier_user):
        raise HTTPException(status_code=403, detail="Dispatch is restricted to the platform dispatcher or assigned carrier.")
    validate_dispatch_transition(item.status, payload.target_status)
    cargo = db.scalar(select(CargoConsignment).where(CargoConsignment.id == item.consignment_id).with_for_update())
    if cargo is None:
        raise HTTPException(status_code=409, detail="Linked consignment is unavailable.")
    if payload.target_status == "accepted":
        if cargo.status != "accepted":
            raise HTTPException(status_code=409, detail="Consignment is no longer dispatchable.")
        cargo.status = "assigned"
        cargo.assigned_organization_id = item.carrier_organization_id
        item.responded_by = context.user.id
    elif payload.target_status == "picked_up":
        if cargo.status != "assigned":
            raise HTTPException(status_code=409, detail="Consignment must be assigned before pickup.")
        cargo.status = "in_transit"
    elif payload.target_status == "delivered":
        if cargo.status != "in_transit":
            raise HTTPException(status_code=409, detail="Consignment must be in transit before delivery.")
        accepted_proof = db.scalar(select(CargoDeliveryProof).where(
            CargoDeliveryProof.dispatch_id == item.id,
            CargoDeliveryProof.status == "accepted",
        ))
        if accepted_proof is None:
            raise HTTPException(status_code=409, detail="An accepted delivery proof is required before dispatch completion.")
        cargo.status = "delivered"
        cargo.delivered_at = datetime.now(UTC)
    elif payload.target_status in {"failed", "rejected"}:
        if cargo.status not in {"accepted", "assigned", "in_transit"}:
            raise HTTPException(status_code=409, detail="Consignment cannot enter an exception from its current state.")
        cargo.status = "exception"
    elif payload.target_status == "cancelled":
        if cargo.status not in {"accepted", "assigned"}:
            raise HTTPException(status_code=409, detail="Only unstarted consignments can be cancelled.")
        cargo.status = "cancelled"
    item.status = payload.target_status
    item.version += 1
    event_type = "departed" if payload.target_status == "in_transit" else payload.target_status
    sequence = (
        db.scalar(select(func.max(CargoTrackingEvent.sequence_number)).where(CargoTrackingEvent.dispatch_id == item.id))
        or 0
    ) + 1
    db.add(
        CargoTrackingEvent(
            dispatch_id=item.id,
            consignment_id=cargo.id,
            sequence_number=sequence,
            idempotency_key=f"dispatch-transition:{item.id}:{item.version}",
            event_type=event_type,
            description=payload.reason_code,
            occurred_at=datetime.now(UTC),
            recorded_by=context.user.id,
        )
    )
    record_event(
        db,
        event_type=f"cargo.dispatch.{payload.target_status}",
        actor_type="staff",
        actor_id=str(context.user.id),
        resource_type="cargo_dispatch",
        resource_id=str(item.id),
        action="transition",
        outcome="success",
        organization_id=cargo.organization_id,
        reason_code=payload.reason_code,
        metadata={
            "consignment_id": str(cargo.id),
            "carrier_organization_id": str(item.carrier_organization_id),
            "version": item.version,
        },
    )
    db.commit()
    db.refresh(item)
    return _dispatch_json(item)


@router.post("/dispatches/{dispatch_id}/tracking-events", status_code=201)
def append_tracking_event(
    dispatch_id: UUID,
    payload: TrackingEventCreate,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    item = db.scalar(select(CargoDispatch).where(CargoDispatch.id == dispatch_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    if not (
        _allowed(db, context, "platform.dispatch.manage")
        or _allowed(db, context, "operator.cargo.dispatch.manage", item.carrier_organization_id)
    ):
        raise HTTPException(status_code=403, detail="Tracking updates are restricted to the assigned carrier and platform dispatchers.")
    existing = db.scalar(
        select(CargoTrackingEvent).where(
            CargoTrackingEvent.dispatch_id == item.id,
            CargoTrackingEvent.idempotency_key == payload.idempotency_key,
        )
    )
    if existing is not None:
        if (
            existing.event_type != payload.event_type
            or existing.description != payload.description
            or existing.latitude != payload.latitude
            or existing.longitude != payload.longitude
            or existing.occurred_at != (payload.occurred_at or existing.occurred_at)
        ):
            raise HTTPException(status_code=409, detail="Tracking idempotency key conflicts with an earlier event.")
        return _tracking_json(existing)
    validate_tracking_event(payload.event_type)
    occurred = payload.occurred_at or datetime.now(UTC)
    now = datetime.now(UTC)
    if occurred > now + timedelta(minutes=5) or occurred < now - timedelta(days=30):
        raise HTTPException(status_code=422, detail="Tracking event time must be within the previous 30 days and not materially in the future.")
    sequence = (
        db.scalar(select(func.max(CargoTrackingEvent.sequence_number)).where(CargoTrackingEvent.dispatch_id == item.id))
        or 0
    ) + 1
    event = CargoTrackingEvent(
        dispatch_id=item.id,
        consignment_id=item.consignment_id,
        sequence_number=sequence,
        idempotency_key=payload.idempotency_key,
        event_type=payload.event_type,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        occurred_at=occurred,
        recorded_by=context.user.id,
    )
    db.add(event)
    db.flush()
    record_event(
        db,
        event_type=f"cargo.tracking.{payload.event_type}",
        actor_type="staff",
        actor_id=str(context.user.id),
        resource_type="cargo_dispatch",
        resource_id=str(item.id),
        action="tracking_event",
        outcome="success",
        metadata={"sequence_number": sequence, "event_id": str(event.id)},
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Duplicate tracking event or concurrent sequence conflict.")
    db.refresh(event)
    return _tracking_json(event)


@router.get("/dispatches/{dispatch_id}/tracking-events")
def list_tracking_events(
    dispatch_id: UUID,
    limit: int = 100,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    item = db.get(CargoDispatch, dispatch_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Dispatch not found.")
    if not (
        _allowed(db, context, "platform.dispatch.manage")
        or _allowed(db, context, "operator.cargo.dispatch.manage", item.carrier_organization_id)
    ):
        raise HTTPException(status_code=403, detail="Tracking history is restricted to dispatch participants.")
    rows = db.scalars(
        select(CargoTrackingEvent)
        .where(CargoTrackingEvent.dispatch_id == item.id)
        .order_by(CargoTrackingEvent.sequence_number)
        .limit(max(1, min(limit, 250)))
    )
    return {"items": [_tracking_json(row) for row in rows]}
