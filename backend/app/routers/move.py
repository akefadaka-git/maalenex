"""Authenticated Move ride endpoints; synthetic-only until a separate rollout approval."""
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.identity.authorization import has_permission
from app.domains.identity.service import StaffContext
from app.domains.move.models import MoveRide
from app.domains.move.service import assign_move_driver, request_move_ride, transition_move_ride
from app.routers.auth import current_staff_context, require_csrf
from app.routers.identity import _current_account, _require_csrf

router = APIRouter(prefix="/move", tags=["move-rides"])


class MoveRideRequest(BaseModel):
    pickup_area_code: str = Field(min_length=1, max_length=48)
    dropoff_area_code: str = Field(min_length=1, max_length=48)


class DriverAssignmentRequest(BaseModel):
    driver_account_id: UUID


class RideTransitionRequest(BaseModel):
    next_status: Literal["accepted", "arrived", "in_progress", "completed", "cancelled"]
    cancellation_reason_code: str | None = Field(default=None, min_length=1, max_length=80)


def _require_synthetic_move() -> None:
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Move API is restricted to synthetic development/test mode.",
        )


def _ride_payload(ride: MoveRide) -> dict:
    return {
        "ride_id": str(ride.id),
        "service_code": ride.service_code,
        "passenger_account_id": str(ride.passenger_account_id),
        "driver_account_id": str(ride.driver_account_id) if ride.driver_account_id else None,
        "pickup_area_code": ride.pickup_area_code,
        "dropoff_area_code": ride.dropoff_area_code,
        "status": ride.status,
        "requested_at": ride.requested_at.isoformat() if ride.requested_at else None,
        "matched_at": ride.matched_at.isoformat() if ride.matched_at else None,
        "accepted_at": ride.accepted_at.isoformat() if ride.accepted_at else None,
        "arrived_at": ride.arrived_at.isoformat() if ride.arrived_at else None,
        "started_at": ride.started_at.isoformat() if ride.started_at else None,
        "completed_at": ride.completed_at.isoformat() if ride.completed_at else None,
        "cancelled_at": ride.cancelled_at.isoformat() if ride.cancelled_at else None,
    }


@router.post("/rides", status_code=status.HTTP_201_CREATED)
def create_move_ride(
    payload: MoveRideRequest,
    request: Request,
    context=Depends(_current_account),
    db: Session = Depends(get_db),
) -> dict:
    _require_synthetic_move()
    account, session = context
    _require_csrf(request, session)
    ride = request_move_ride(
        db, passenger_account_id=account.id,
        pickup_area_code=payload.pickup_area_code,
        dropoff_area_code=payload.dropoff_area_code,
    )
    db.commit()
    return _ride_payload(ride)


@router.get("/rides/{ride_id}")
def read_move_ride(
    ride_id: UUID,
    context=Depends(_current_account),
    db: Session = Depends(get_db),
) -> dict:
    _require_synthetic_move()
    account, _session = context
    ride = db.get(MoveRide, ride_id)
    if ride is None or account.id not in {ride.passenger_account_id, ride.driver_account_id}:
        raise HTTPException(status_code=404, detail="Move ride not found.")
    return _ride_payload(ride)


@router.post("/rides/{ride_id}/transitions")
def transition_ride(
    ride_id: UUID,
    payload: RideTransitionRequest,
    request: Request,
    context=Depends(_current_account),
    db: Session = Depends(get_db),
) -> dict:
    _require_synthetic_move()
    account, session = context
    _require_csrf(request, session)
    ride = db.get(MoveRide, ride_id)
    if ride is None:
        raise HTTPException(status_code=404, detail="Move ride not found.")
    if account.id not in {ride.passenger_account_id, ride.driver_account_id}:
        raise HTTPException(status_code=404, detail="Move ride not found.")
    try:
        ride = transition_move_ride(
            db,
            ride_id=ride_id,
            actor_account_id=account.id,
            next_status=payload.next_status,
            cancellation_reason_code=payload.cancellation_reason_code,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _ride_payload(ride)


@router.post("/rides/{ride_id}/dispatch")
def dispatch_ride(
    ride_id: UUID,
    payload: DriverAssignmentRequest,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_synthetic_move()
    require_csrf(request, context)
    if not has_permission(
        db,
        user_id=context.user.id,
        permission_code="platform.move.dispatch",
        organization_id=None,
    ):
        raise HTTPException(status_code=403, detail="Move dispatch permission is required.")
    try:
        ride = assign_move_driver(
            db,
            ride_id=ride_id,
            driver_account_id=payload.driver_account_id,
            dispatcher_user_id=context.user.id,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _ride_payload(ride)
