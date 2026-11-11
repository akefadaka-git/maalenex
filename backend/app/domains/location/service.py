"""Location-consent lifecycle. No HTTP ingestion route or live GPS adapter is provided."""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.identity.accounts import PlatformAccount
from app.domains.location.models import LocationConsent, LocationSession, SyntheticLocationSample
from app.domains.platform.models import PlatformService
from app.domains.move.models import MoveRide

_RESOURCE_SERVICE = {
    "move_ride": "move",
    "delivery_shipment": "delivery",
    "cargo_movement": "cargo",
}
_ACTIVE_RESOURCE_STATUSES = {"matched", "accepted", "arrived", "in_progress"}


def _database_now(db: Session) -> datetime:
    return db.scalar(select(func.now()))


def _validate_scope(service_code: str, resource_type: str, purpose: str) -> None:
    if _RESOURCE_SERVICE.get(resource_type) != service_code:
        raise ValueError("Location consent service and resource scope do not match.")
    if purpose not in {"active_job_tracking", "safety_response"}:
        raise ValueError("Location consent purpose is not supported.")


def grant_location_consent(
    db: Session, *, account_id: UUID, service_code: str, resource_type: str,
    resource_id: str, purpose: str, consent_version: str, expires_at: datetime,
) -> LocationConsent:
    """Record explicit, versioned consent for one account and one service resource."""
    _validate_scope(service_code, resource_type, purpose)
    if not resource_id or len(resource_id) > 80 or not consent_version.strip():
        raise ValueError("A resource reference and consent version are required.")
    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("Location consent expiry must be timezone-aware.")
    account = db.scalar(select(PlatformAccount).where(PlatformAccount.id == account_id).with_for_update())
    if account is None or account.status != "active":
        raise ValueError("An active platform account is required for location consent.")
    if db.get(PlatformService, service_code) is None:
        raise ValueError("The requested platform service does not exist.")
    now = _database_now(db)
    if expires_at <= now:
        raise ValueError("Location consent expiry must be in the future.")
    existing = db.scalar(
        select(LocationConsent).where(
            LocationConsent.account_id == account_id,
            LocationConsent.service_code == service_code,
            LocationConsent.resource_type == resource_type,
            LocationConsent.resource_id == resource_id,
            LocationConsent.purpose == purpose,
            LocationConsent.status == "active",
        ).with_for_update()
    )
    if existing is not None:
        if existing.expires_at <= now:
            existing.status = "expired"
        else:
            raise ValueError("An active consent already exists for this resource and purpose.")
    consent = LocationConsent(
        account_id=account_id, service_code=service_code, resource_type=resource_type,
        resource_id=resource_id, purpose=purpose, consent_version=consent_version.strip(),
        expires_at=expires_at,
    )
    db.add(consent)
    db.flush()
    record_event(
        db, event_type="location.consent.granted", actor_type="account",
        actor_id=str(account_id), resource_type="location_consent", resource_id=str(consent.id),
        action="grant", outcome="success",
        metadata={"service_code": service_code, "resource_type": resource_type,
                  "purpose": purpose, "consent_version": consent.consent_version},
    )
    return consent


def open_location_session(
    db: Session, *, consent_id: UUID, account_id: UUID, service_code: str,
    resource_type: str, resource_id: str, expires_at: datetime,
) -> LocationSession:
    """Resolve the authoritative Move ride and verify participant and lifecycle state."""

    consent = db.scalar(
        select(LocationConsent).where(LocationConsent.id == consent_id).with_for_update()
    )
    now = _database_now(db)
    if consent is None or consent.account_id != account_id:
        raise ValueError("Location consent does not belong to this account.")
    if consent.status != "active" or consent.revoked_at is not None or consent.expires_at <= now:
        raise ValueError("Location consent is revoked or expired.")
    if (consent.service_code, consent.resource_type, consent.resource_id) != (
        service_code, resource_type, resource_id
    ):
        raise ValueError("Location session does not match the consented resource scope.")
    if service_code != "move" or resource_type != "move_ride":
        raise ValueError("This location-session adapter currently supports Move rides only.")
    try:
        ride_id = UUID(resource_id)
    except ValueError as exc:
        raise ValueError("Move ride resource reference is invalid.") from exc
    ride = db.scalar(select(MoveRide).where(MoveRide.id == ride_id).with_for_update())
    if (
        ride is None or ride.service_code != service_code
        or account_id not in {ride.passenger_account_id, ride.driver_account_id}
        or ride.status not in _ACTIVE_RESOURCE_STATUSES
    ):
        raise ValueError("Location sharing requires the consenting participant's authoritative active ride.")
    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("Location session expiry must be timezone-aware.")
    if expires_at <= now or expires_at > consent.expires_at:
        raise ValueError("Location session expiry must be within the consent window.")
    active = db.scalar(
        select(LocationSession.id).where(
            LocationSession.consent_id == consent.id, LocationSession.status == "active"
        ).with_for_update()
    )
    if active is not None:
        raise ValueError("An active location session already exists for this consent.")
    session = LocationSession(
        consent_id=consent.id, account_id=account_id, service_code=service_code,
        resource_type=resource_type, resource_id=resource_id, status="active", expires_at=expires_at,
    )
    db.add(session)
    db.flush()
    record_event(
        db, event_type="location.session.opened", actor_type="account",
        actor_id=str(account_id), resource_type="location_session", resource_id=str(session.id),
        action="open", outcome="success",
        metadata={"service_code": service_code, "resource_type": resource_type,
                  "resource_id": resource_id},
    )
    return session


def revoke_location_consent(db: Session, *, consent_id: UUID, account_id: UUID) -> LocationConsent:
    """Revoke consent and terminate every active session in the same transaction."""
    consent = db.scalar(
        select(LocationConsent).where(LocationConsent.id == consent_id).with_for_update()
    )
    if consent is None or consent.account_id != account_id:
        raise ValueError("Location consent does not belong to this account.")
    if consent.status == "revoked":
        return consent
    now = _database_now(db)
    consent.status = "revoked"
    consent.revoked_at = now
    sessions = db.scalars(
        select(LocationSession).where(
            LocationSession.consent_id == consent.id, LocationSession.status == "active"
        ).with_for_update()
    ).all()
    for session in sessions:
        session.status = "revoked"
        session.ended_at = now
    record_event(
        db, event_type="location.consent.revoked", actor_type="account",
        actor_id=str(account_id), resource_type="location_consent", resource_id=str(consent.id),
        action="revoke", outcome="success", metadata={"sessions_terminated": len(sessions)},
    )
    db.flush()
    return consent


def record_synthetic_location_sample(
    db: Session, *, session_id: UUID, latitude: Decimal, longitude: Decimal,
    captured_at: datetime, accuracy_meters: Decimal | None = None,
) -> SyntheticLocationSample:
    """Persist only synthetic fixture samples; no production/live ingestion path exists."""
    session = db.scalar(
        select(LocationSession).where(LocationSession.id == session_id).with_for_update()
    )
    now = _database_now(db)
    if session is None or session.status != "active" or session.expires_at <= now:
        raise ValueError("An active, unexpired location session is required.")
    if captured_at.tzinfo is None or captured_at.utcoffset() is None:
        raise ValueError("Synthetic sample timestamp must be timezone-aware.")
    if captured_at > now or captured_at < session.started_at or captured_at > session.expires_at:
        raise ValueError("Synthetic sample timestamp must fall within the active session window.")
    sample = SyntheticLocationSample(
        session_id=session.id, latitude=latitude, longitude=longitude,
        accuracy_meters=accuracy_meters, captured_at=captured_at,
        source="synthetic_fixture", is_synthetic=True,
    )
    db.add(sample)
    session.last_sample_at = captured_at
    db.flush()
    return sample


def get_location_freshness(
    db: Session, *, session_id: UUID, max_age: timedelta,
) -> str:
    """Return a freshness classification without exposing coordinates."""
    if max_age <= timedelta(0):
        raise ValueError("Freshness window must be positive.")
    session = db.get(LocationSession, session_id)
    if session is None:
        return "session_missing"
    now = _database_now(db)
    if session.status != "active" or session.expires_at <= now:
        return "session_inactive"
    latest = db.scalar(
        select(SyntheticLocationSample).where(
            SyntheticLocationSample.session_id == session_id
        ).order_by(SyntheticLocationSample.captured_at.desc()).limit(1)
    )
    if latest is None:
        return "no_sample"
    return "fresh" if now - latest.captured_at <= max_age else "stale"


def expire_location_sessions(db: Session) -> int:
    """Close expired sessions and consents using database time; safe to call repeatedly."""
    now = _database_now(db)
    consents = db.scalars(
        select(LocationConsent).where(
            LocationConsent.status == "active", LocationConsent.expires_at <= now
        ).with_for_update()
    ).all()
    for consent in consents:
        consent.status = "expired"
    sessions = db.scalars(
        select(LocationSession).where(
            LocationSession.status == "active", LocationSession.expires_at <= now
        ).with_for_update()
    ).all()
    for session in sessions:
        session.status = "expired"
        session.ended_at = now
    db.flush()
    return len(sessions)
