"""Authenticated passenger inbox and notification preferences."""
# FastAPI dependency injection requires Depends instances in endpoint defaults.
# ruff: noqa: B008
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.identity.passenger_service import PassengerContext, verify_passenger_csrf
from app.domains.notifications.service import (
    get_preferences,
    list_notifications,
    mark_notification_read,
    notification_payload,
)
from app.routers.passenger_auth import current_passenger_context

router = APIRouter(prefix="/passenger/notifications", tags=["passenger-notifications"])


def _check_mutation(request: Request, context: PassengerContext) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")
    if not verify_passenger_csrf(
        context, cookie_token=request.cookies.get("mnm_passenger_csrf"),
        header_token=request.headers.get("X-CSRF-Token"),
    ):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")


class PreferenceUpdate(BaseModel):
    in_app_enabled: bool
    email_enabled: bool
    sms_enabled: bool


@router.get("")
def inbox(context: PassengerContext = Depends(current_passenger_context), db: Session = Depends(get_db)) -> dict:
    return list_notifications(db, context.passenger.id)


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: UUID, request: Request,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    _check_mutation(request, context)
    item = mark_notification_read(db, context.passenger.id, notification_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Notification not found.")
    db.commit()
    db.refresh(item)
    return notification_payload(item)


@router.get("/preferences")
def read_preferences(
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    prefs = get_preferences(db, context.passenger.id)
    db.commit()
    return {
        "in_app_enabled": prefs.in_app_enabled,
        "email_enabled": prefs.email_enabled,
        "sms_enabled": prefs.sms_enabled,
        "email_delivery_available": False,
        "sms_delivery_available": False,
    }


@router.patch("/preferences")
def update_preferences(
    payload: PreferenceUpdate, request: Request,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    _check_mutation(request, context)
    prefs = get_preferences(db, context.passenger.id)
    prefs.in_app_enabled = payload.in_app_enabled
    # Channels remain off until delivery providers and consent workflows are reviewed.
    prefs.email_enabled = False
    prefs.sms_enabled = False
    db.commit()
    db.refresh(prefs)
    return {
        "in_app_enabled": prefs.in_app_enabled,
        "email_enabled": prefs.email_enabled,
        "sms_enabled": prefs.sms_enabled,
        "email_delivery_available": False,
        "sms_delivery_available": False,
    }
