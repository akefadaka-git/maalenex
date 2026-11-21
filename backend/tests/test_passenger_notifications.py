from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.domains.audit.models import AuditEvent
from app.domains.identity.passenger_models import PassengerAccount
from app.domains.identity.passenger_service import token_digest
from app.domains.notifications.models import PassengerNotification, PassengerNotificationPreference
from app.domains.notifications.service import create_notification
from app.routers.passenger_auth import current_passenger_context
from app.routers.passenger_notifications import router


def _client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        PassengerAccount.__table__, PassengerNotification.__table__,
        PassengerNotificationPreference.__table__, AuditEvent.__table__,
    ])
    db = Session(engine)
    passenger = PassengerAccount(
        id=uuid4(), login_identifier="notice-rider@example.test",
        display_name="Notification Rider", status="active",
    )
    other = PassengerAccount(
        id=uuid4(), login_identifier="other-rider@example.test",
        display_name="Other Rider", status="active",
    )
    db.add_all([passenger, other])
    db.commit()
    csrf = "notification-csrf-test"
    context = SimpleNamespace(passenger=passenger, session=SimpleNamespace(csrf_token_hash=token_digest(csrf)))
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[current_passenger_context] = lambda: context
    return TestClient(app), db, passenger, other, engine, csrf


def test_notification_inbox_is_owner_scoped_and_counts_unread():
    client, db, passenger, other, engine, csrf = _client()
    try:
        create_notification(
            db, passenger_id=passenger.id, notification_type="report_created",
            title="Report received", body="Your report was received.",
            dedupe_key="report-created:one", resource_type="report",
            resource_reference="MN-RPT-0001",
        )
        create_notification(
            db, passenger_id=other.id, notification_type="report_created",
            title="Private other", body="Not yours.",
            dedupe_key="report-created:other",
        )
        db.commit()
        response = client.get("/api/v1/passenger/notifications")
        assert response.status_code == 200
        assert response.json()["unread_count"] == 1
        assert len(response.json()["items"]) == 1
        assert response.json()["items"][0]["resource_reference"] == "MN-RPT-0001"
    finally:
        db.close()
        engine.dispose()


def test_mark_read_is_csrf_protected_and_audited():
    client, db, passenger, other, engine, csrf = _client()
    try:
        item = create_notification(
            db, passenger_id=passenger.id, notification_type="support_case_created",
            title="Support received", body="Your support request was received.",
            dedupe_key="support-created:one",
        )
        db.commit()
        response = client.post(
            f"/api/v1/passenger/notifications/{item.id}/read",
            cookies={"mnm_passenger_csrf": csrf},
            headers={"X-CSRF-Token": csrf},
        )
        assert response.status_code == 200
        assert response.json()["read"] is True
        assert db.query(AuditEvent).filter_by(event_type="passenger.notification.read").count() == 1
        assert client.post(f"/api/v1/passenger/notifications/{item.id}/read").status_code == 403
    finally:
        db.close()
        engine.dispose()


def test_notification_dedupe_and_disabled_in_app_preference():
    client, db, passenger, other, engine, csrf = _client()
    try:
        first = create_notification(
            db, passenger_id=passenger.id, notification_type="report_created",
            title="One", body="Body", dedupe_key="same-event",
        )
        duplicate = create_notification(
            db, passenger_id=passenger.id, notification_type="report_created",
            title="Duplicate", body="Duplicate body", dedupe_key="same-event",
        )
        assert first.id == duplicate.id
        prefs = PassengerNotificationPreference(passenger_id=passenger.id, in_app_enabled=False)
        db.add(prefs)
        db.flush()
        suppressed = create_notification(
            db, passenger_id=passenger.id, notification_type="report_created",
            title="Suppressed", body="Body", dedupe_key="suppressed-event",
        )
        assert suppressed is None
    finally:
        db.close()
        engine.dispose()


def test_notification_preferences_never_enable_unconfigured_email_or_sms():
    client, db, passenger, other, engine, csrf = _client()
    try:
        response = client.patch(
            "/api/v1/passenger/notifications/preferences",
            json={"in_app_enabled": True, "email_enabled": True, "sms_enabled": True},
            cookies={"mnm_passenger_csrf": csrf},
            headers={"X-CSRF-Token": csrf},
        )
        assert response.status_code == 200
        assert response.json()["in_app_enabled"] is True
        assert response.json()["email_enabled"] is False
        assert response.json()["sms_enabled"] is False
        assert response.json()["email_delivery_available"] is False
        assert response.json()["sms_delivery_available"] is False
    finally:
        db.close()
        engine.dispose()
