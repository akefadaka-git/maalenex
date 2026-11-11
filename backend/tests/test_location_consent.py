import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.domains.identity.accounts import PlatformAccount
from app.domains.location.models import SyntheticLocationSample
from app.domains.location.service import (
    expire_location_sessions, get_location_freshness, grant_location_consent,
    open_location_session, record_synthetic_location_sample, revoke_location_consent,
)
from app.domains.move.service import assign_move_driver, request_move_ride, transition_move_ride
from scripts.seed_platform_services import seed

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def _account(db, status="active"):
    account = PlatformAccount(display_name="Synthetic location subject", status=status)
    db.add(account)
    db.flush()
    return account


def _ride(db, passenger, driver=None, status="requested"):
    ride = request_move_ride(db, passenger_account_id=passenger.id)
    if driver is not None:
        assign_move_driver(db, ride_id=ride.id, driver_account_id=driver.id)
        steps = ["accepted", "arrived", "in_progress", "completed"]
        for step in steps:
            if step == status:
                break
            transition_move_ride(db, ride_id=ride.id, actor_account_id=driver.id, next_status=step)
        if status == "completed" and ride.status != "completed":
            transition_move_ride(db, ride_id=ride.id, actor_account_id=driver.id, next_status="completed")
    return ride


def _consent(db, account, ride, *, expires=None):
    return grant_location_consent(
        db, account_id=account.id, service_code="move", resource_type="move_ride",
        resource_id=str(ride.id), purpose="active_job_tracking",
        consent_version="location-v1",
        expires_at=expires or datetime.now(timezone.utc) + timedelta(hours=1),
    )


def _open(db, account, consent, ride, *, expires=None):
    return open_location_session(
        db, consent_id=consent.id, account_id=account.id, service_code="move",
        resource_type="move_ride", resource_id=str(ride.id),
        expires_at=expires or min(consent.expires_at, datetime.now(timezone.utc) + timedelta(minutes=30)),
    )


def test_move_ride_lifecycle_is_actor_bound_and_monotonic():
    seed()
    with SessionLocal.begin() as db:
        passenger, driver, stranger = _account(db), _account(db), _account(db)
        ride = _ride(db, passenger)
        assign_move_driver(db, ride_id=ride.id, driver_account_id=driver.id)
        with pytest.raises(ValueError, match="not permitted"):
            transition_move_ride(db, ride_id=ride.id, actor_account_id=stranger.id, next_status="accepted")
        for step in ("accepted", "arrived", "in_progress", "completed"):
            transition_move_ride(db, ride_id=ride.id, actor_account_id=driver.id, next_status=step)
        assert ride.status == "completed"
        assert ride.completed_at is not None


def test_location_session_resolves_authoritative_ride_and_participant():
    seed()
    with SessionLocal.begin() as db:
        passenger, driver, stranger = _account(db), _account(db), _account(db)
        ride = _ride(db, passenger, driver, "in_progress")
        consent = _consent(db, passenger, ride)
        assert _open(db, passenger, consent, ride).status == "active"
        driver_consent = _consent(db, driver, ride)
        assert _open(db, driver, driver_consent, ride).status == "active"
        stranger_consent = _consent(db, stranger, ride)
        with pytest.raises(ValueError, match="authoritative active ride"):
            _open(db, stranger, stranger_consent, ride)



def test_ride_completion_terminates_all_active_location_sessions():
    seed()
    with SessionLocal.begin() as db:
        passenger, driver = _account(db), _account(db)
        ride = _ride(db, passenger, driver, "in_progress")
        passenger_session = _open(db, passenger, _consent(db, passenger, ride), ride)
        driver_session = _open(db, driver, _consent(db, driver, ride), ride)
        transition_move_ride(
            db, ride_id=ride.id, actor_account_id=driver.id, next_status="completed"
        )
        assert passenger_session.status == "completed"
        assert passenger_session.ended_at is not None
        assert driver_session.status == "completed"
        assert driver_session.ended_at is not None


def test_location_session_rejects_requested_and_completed_rides():
    seed()
    with SessionLocal.begin() as db:
        passenger, driver = _account(db), _account(db)
        requested = _ride(db, passenger)
        with pytest.raises(ValueError, match="authoritative active ride"):
            _open(db, passenger, _consent(db, passenger, requested), requested)
        completed = _ride(db, passenger, driver, "completed")
        with pytest.raises(ValueError, match="authoritative active ride"):
            _open(db, passenger, _consent(db, passenger, completed), completed)


def test_location_consent_requires_active_account_and_matching_service_scope():
    seed()
    with SessionLocal.begin() as db:
        pending = _account(db, "pending")
        ride = _ride(db, pending)
        with pytest.raises(ValueError, match="active platform account"):
            _consent(db, pending, ride)
        active = _account(db)
        active_ride = _ride(db, active)
        with pytest.raises(ValueError, match="do not match"):
            grant_location_consent(
                db, account_id=active.id, service_code="move", resource_type="cargo_movement",
                resource_id="cargo-1", purpose="active_job_tracking", consent_version="v1",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        _consent(db, active, active_ride)
        with pytest.raises(ValueError, match="already exists"):
            _consent(db, active, active_ride)


def test_revocation_terminates_session_and_blocks_further_samples():
    seed()
    with SessionLocal.begin() as db:
        passenger, driver = _account(db), _account(db)
        ride = _ride(db, passenger, driver, "in_progress")
        consent = _consent(db, passenger, ride)
        session = _open(db, passenger, consent, ride)
        revoke_location_consent(db, consent_id=consent.id, account_id=passenger.id)
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
        passenger, driver = _account(db), _account(db)
        ride = _ride(db, passenger, driver, "in_progress")
        consent = _consent(db, passenger, ride)
        session = _open(db, passenger, consent, ride)
        assert get_location_freshness(db, session_id=session.id, max_age=timedelta(minutes=2)) == "no_sample"
        sample_time = db.scalar(select(func.now()))
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


def test_expired_sessions_are_closed_and_cannot_accept_samples(monkeypatch):
    seed()
    with SessionLocal.begin() as db:
        passenger, driver = _account(db), _account(db)
        ride = _ride(db, passenger, driver, "in_progress")
        consent = _consent(db, passenger, ride, expires=datetime.now(timezone.utc) + timedelta(minutes=10))
        session = _open(db, passenger, consent, ride, expires=consent.expires_at)
        monkeypatch.setattr(
            "app.domains.location.service._database_now",
            lambda _db: session.expires_at + timedelta(seconds=1),
        )
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
        passenger, driver = _account(db), _account(db)
        ride = _ride(db, passenger, driver, "in_progress")
        consent = _consent(db, passenger, ride)
        session = _open(db, passenger, consent, ride)
        sample = SyntheticLocationSample(
            session_id=session.id, latitude=Decimal("6.2"), longitude=Decimal("36.9"),
            captured_at=datetime.now(timezone.utc), source="device_gps", is_synthetic=False,
        )
        db.add(sample)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()
