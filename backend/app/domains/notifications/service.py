"""Passenger-owned in-app inbox and preference operations."""
from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.notifications.models import PassengerNotification, PassengerNotificationPreference


def create_notification(
    db: Session, *, passenger_id: UUID, notification_type: str,
    title: str, body: str, dedupe_key: str,
    resource_type: str | None = None, resource_reference: str | None = None,
) -> PassengerNotification | None:
    prefs = db.scalar(
        select(PassengerNotificationPreference).where(
            PassengerNotificationPreference.passenger_id == passenger_id
        )
    )
    if prefs is not None and not prefs.in_app_enabled:
        return None
    existing = db.scalar(
        select(PassengerNotification).where(PassengerNotification.dedupe_key == dedupe_key)
    )
    if existing is not None:
        return existing
    item = PassengerNotification(
        passenger_id=passenger_id,
        notification_type=notification_type,
        title=title[:160],
        body=body,
        resource_type=resource_type,
        resource_reference=resource_reference,
        dedupe_key=dedupe_key[:128],
    )
    db.add(item)
    return item

def notification_payload(item: PassengerNotification) -> dict:
    return {
        "id": str(item.id),
        "notification_type": item.notification_type,
        "title": item.title,
        "body": item.body,
        "resource_type": item.resource_type,
        "resource_reference": item.resource_reference,
        "read": item.read_at is not None,
        "created_at": item.created_at.isoformat(),
    }


def list_notifications(db: Session, passenger_id: UUID) -> dict:
    rows = db.scalars(
        select(PassengerNotification)
        .where(PassengerNotification.passenger_id == passenger_id)
        .order_by(PassengerNotification.created_at.desc(), PassengerNotification.id.desc())
        .limit(50)
    ).all()
    unread = db.scalar(
        select(func.count()).select_from(PassengerNotification).where(
            PassengerNotification.passenger_id == passenger_id,
            PassengerNotification.read_at.is_(None),
        )
    ) or 0
    return {"items": [notification_payload(row) for row in rows], "unread_count": int(unread)}


def mark_notification_read(db: Session, passenger_id: UUID, notification_id: UUID) -> PassengerNotification | None:
    item = db.scalar(
        select(PassengerNotification).where(
            PassengerNotification.id == notification_id,
            PassengerNotification.passenger_id == passenger_id,
        ).with_for_update()
    )
    if item is None:
        return None
    if item.read_at is None:
        item.read_at = datetime.now(UTC)
        record_event(
            db,
            event_type="passenger.notification.read",
            actor_type="passenger",
            actor_id=str(passenger_id),
            resource_type="passenger_notification",
            resource_id=str(item.id),
            action="mark_read",
            outcome="success",
            metadata={"notification_type": item.notification_type},
        )
    return item


def get_preferences(db: Session, passenger_id: UUID) -> PassengerNotificationPreference:
    prefs = db.scalar(
        select(PassengerNotificationPreference).where(
            PassengerNotificationPreference.passenger_id == passenger_id
        )
    )
    if prefs is None:
        prefs = PassengerNotificationPreference(passenger_id=passenger_id)
        db.add(prefs)
        db.flush()
    return prefs
