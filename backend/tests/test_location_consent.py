import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.domains.identity.accounts import PlatformAccount
from app.domains.location.models import SyntheticLocationSample
from app.domains.location.service import (
    expire_location_sessions, get_location_freshness, grant_location_consent,
    open_location_session, record_synthetic_location_sample, revoke_location_consent,
)
from scripts.seed_platform_services import seed

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def _account(db):
    account = PlatformAccount(display_name="Synthetic location subject", status="active")
    db.add(account)
    db.flush()
    return account


def _consent(db, account, *, expires=None):
    return grant_location_consent(
        db, account_id=account.id, service_code="move", resource_type="move_ride",
        resource_id=f"ride-{uuid4().hex}", purpose="active_job_tracking",
        consent_version="location-v1", expires_at=expires or datetime.now(timezone.utc) + timedelta(hours=1),
    )


def test_location_consent_requires_active_account_and_matching_service_scope():
    seed()
    with SessionLocal.begin() as db:
        account = PlatformAccount(display_name="Pending synthetic account", status="pending")
        db.add(account)
        db.flush()
        with pytest.raises(ValueError, match="active platform account"):
            _consent(db, account)
        active = _account(db)
        with pytest.raises(ValueError, match="do not match"):
            grant_location_consent(
                db, account_id=active.id, service_code="move", resource_type="cargo_movement",
                resource_id="cargo-1", purpose="active_job_tracking", consent_version="v1",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        consent = _consent(db, active)
        with pytest.raises(ValueError, match="already exists"):
            grant_location_consent(
                db, account_id=active.id, service_code="move", resource_type="move_ride",
                resource_id=consent.resource_id, purpose="active_job_tracking",
                consent_version="location-v1", expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )


def test_location_session_is_bound_to_exact_consent_and_active_job():
    seed()
    with SessionLocal.begin() as db:
        account = _account(db)
        consent = _consent(db, account)
        expiry = min(consent.expires_at, datetime.now(timezone.utc) + timedelta(minutes=30))
        with pytest.raises(ValueError, match="active job"):
            open_location_session(
                db, consent_id=consent.id, account_id=account.id, service_code="move",
                resource_type="move_ride", resource_id=consent.resource_id,
                resource_account_id=account.id, resource_status="requested", expires_at=expiry,
            )
        with pytest.raises(ValueError, match="scope"):
            open_location_session(
                db, consent_id=consent.id, account_id=account.id, service_code="move",
                resource_type="move_ride", resource_id="different-ride",
                resource_account_id=account.id, resource_status="in_progress", expires_at=expiry,
            )
        session = open_location_session(
            db, consent_id=consent.id, account_id=account.id, service_code="move",
            resource_type="move_ride", resource_id=consent.resource_id,
            resource_account_id=account.id, resource_status="in_progress", expires_at=expiry,
        )
        assert session.status == "active"
        with pytest.raises(ValueError, match="already exists"):
            open_location_session(
                db, consent_id=consent.id, account_id=account.id, service_code="move",
                resource_type="move_ride", resource_id=consent.resource_id,
                resource_account_id=account.id, resource_status="in_progress", expires_at=expiry,
            )


def test_revocation_terminates_session_and_blocks_further_samples():
    seed()
    with SessionLocal.begin() as db:
        account = _account(db)
        consent = _consent(db, account)
        expiry = min(consent.expires_at, datetime.now(timezone.utc) + timedelta(minutes=30))
        session = open_location_session(
            db, consent_id=consent.id, account_id=account.id, service_code="move",
            resource_type="move_ride", resource_id=consent.resource_id,
            resource_account_id=account.id, resource_status="matched", expires_at=expiry,
        )
        revoke_location_consent(db, consent_id=consent.id, account_id=account.id)
        assert consent.status == "revoked"
        assert consent.revoked_at is not None
        assert session.status == "revoked"
        with pytest.raises(ValueError, match="active, unexpired"):
            record_synthetic_location_sample(
                db, session_id=session.id, latitude=Decimal("6.250000"),
                longitude=Decimal("36.900000"), captured_at=datetime.now(timezone.utc),
            )


def test_synthetic_samples_are_scoped_and_freshness_is_explicit():
    seed()
    with SessionLocal.begin() as db:
        account = _account(db)
        consent = _consent(db, account)
        expiry = min(consent.expires_at, datetime.now(timezone.utc) + timedelta(minutes=30))
        session = open_location_session(
            db, consent_id=consent.id, account_id=account.id, service_code="move",
            resource_type="move_ride", resource_id=consent.resource_id,
            resource_account_id=account.id, resource_status="accepted", expires_at=expiry,
        )
        assert get_location_freshness(db, session_id=session.id, max_age=timedelta(minutes=2)) == "no_sample"
        sample_time = datetime.now(timezone.utc)
        sample = record_synthetic_location_sample(
            db, session_id=session.id, latitude=Decimal("6.250000"),
            longitude=Decimal("36.900000"), accuracy_meters=Decimal("25.00"),
            captured_at=sample_time,
        )
        assert sample.is_synthetic is True
        assert sample.source == "synthetic_fixture"
        assert get_location_freshness(db, session_id=session.id, max_age=timedelta(minutes=2)) == "fresh"
        sample.captured_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        db.flush()
        assert get_location_freshness(db, session_id=session.id, max_age=timedelta(minutes=2)) == "stale"


def test_expired_sessions_are_closed_and_cannot_accept_samples():
    seed()
    with SessionLocal.begin() as db:
        account = _account(db)
        consent = _consent(db, account, expires=datetime.now(timezone.utc) + timedelta(minutes=10))
        session = open_location_session(
            db, consent_id=consent.id, account_id=account.id, service_code="move",
            resource_type="move_ride", resource_id=consent.resource_id,
            resource_account_id=account.id, resource_status="in_progress", expires_at=consent.expires_at,
        )
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.flush()
        assert expire_location_sessions(db) == 1
        assert session.status == "expired"
        with pytest.raises(ValueError, match="active, unexpired"):
            record_synthetic_location_sample(
                db, session_id=session.id, latitude=Decimal("6.250000"),
                longitude=Decimal("36.900000"), captured_at=datetime.now(timezone.utc),
            )


def test_location_sample_database_scope_is_synthetic_only():
    seed()
    with SessionLocal.begin() as db:
        account = _account(db)
        consent = _consent(db, account)
        expiry = min(consent.expires_at, datetime.now(timezone.utc) + timedelta(minutes=30))
        session = open_location_session(
            db, consent_id=consent.id, account_id=account.id, service_code="move",
            resource_type="move_ride", resource_id=consent.resource_id,
            resource_account_id=account.id, resource_status="matched", expires_at=expiry,
        )
        sample = SyntheticLocationSample(
            session_id=session.id, latitude=Decimal("6.2"), longitude=Decimal("36.9"),
            captured_at=datetime.now(timezone.utc), source="device_gps", is_synthetic=False,
        )
        db.add(sample)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()
