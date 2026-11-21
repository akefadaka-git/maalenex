from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, settings
from app.db.base import Base
from app.domains.operations.models import SchedulerLease, SchedulerRun
from app.jobs.scheduler_service import scheduler_snapshot
from app.main import app


def test_scheduler_settings_are_disabled_and_synthetic_only_by_default():
    assert settings.scheduler_enabled is False
    assert settings.synthetic_data_only is True


def test_production_environment_remains_rejected():
    try:
        Settings(app_env="production")
    except ValueError as error:
        assert "Only development/test" in str(error)
    else:
        raise AssertionError("Production configuration must remain disabled in this baseline.")


def test_scheduler_snapshot_reports_unconfigured_and_healthy_states():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=[SchedulerLease.__table__, SchedulerRun.__table__])
    with Session(engine) as db:
        initial = scheduler_snapshot(db)
        assert initial["health"] == "not_configured"
        now = datetime.now(UTC)
        db.add(SchedulerLease(
            lease_name="booking_hold_expiry", owner_id="synthetic-worker",
            lease_expires_at=now + timedelta(seconds=90), heartbeat_at=now,
            last_success_at=now, consecutive_failures=0, batches_completed=2,
            records_processed=3,
        ))
        db.add(SchedulerRun(
            job_name="booking_hold_expiry", worker_id="synthetic-worker",
            status="succeeded", started_at=now, finished_at=now,
            records_processed=3, duration_ms=12,
        ))
        db.commit()
        snapshot = scheduler_snapshot(db)
        assert snapshot["health"] == "healthy"
        assert snapshot["lease"]["records_processed"] == 3
        assert snapshot["runs"][0]["status"] == "succeeded"
    engine.dispose()


def test_staff_operations_routes_are_registered_and_protected():
    paths = app.openapi()["paths"]
    assert {
        "/api/v1/admin/dashboard",
        "/api/v1/admin/access/roles",
        "/api/v1/admin/access/users",
        "/api/v1/admin/access/organizations",
        "/api/v1/admin/access/invitations",
        "/api/v1/admin/access/users/{user_id}/roles",
        "/api/v1/admin/access/role-assignments/{assignment_id}",
        "/api/v1/admin/operations/scheduler",
        "/api/v1/admin/operations/scheduler/run-once",
    }.issubset(paths)
    client = TestClient(app)
    assert client.get("/api/v1/admin/dashboard").status_code == 401
    assert client.get("/api/v1/admin/operations/scheduler").status_code == 401
