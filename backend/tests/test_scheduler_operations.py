# ruff: noqa: I001
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, settings
from app.db.base import Base
from app.domains.bookings.models import Booking
from app.domains.identity.authorization import has_permission
from app.domains.identity.models import Permission, Role, RoleAssignment, RolePermission, User
from app.domains.operations.models import SchedulerLease, SchedulerRun
from app.domains.organizations.models import Organization
from app.jobs.scheduler_service import scheduler_snapshot
from app.routers.staff_admin import _access
from app.main import app


def test_scheduler_settings_are_disabled_and_synthetic_only_by_default():
    assert settings.scheduler_enabled is False
    assert settings.synthetic_data_only is True


def test_production_environment_remains_rejected():
    try:
        Settings(app_env="production")
    except ValueError as error:
        assert "Production must explicitly disable synthetic-only mode" in str(error)
    else:
        raise AssertionError("Production configuration must remain disabled in this baseline.")


def test_scheduler_snapshot_reports_unconfigured_and_healthy_states():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=[Booking.__table__, SchedulerLease.__table__, SchedulerRun.__table__])
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


def test_staff_access_profile_resolves_only_active_role_permissions():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=[
        User.__table__, Role.__table__, Permission.__table__, Organization.__table__,
        RolePermission.__table__, RoleAssignment.__table__,
    ])
    with Session(engine) as db:
        user = User(login_identifier="rbac@example.test", display_name="RBAC Tester", status="active")
        role = Role(code="platform_scheduler_operator", description="Scheduler operator")
        permission = Permission(code="platform.scheduler.read", description="Read scheduler")
        db.add_all([user, role, permission])
        db.flush()
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))
        assignment = RoleAssignment(user_id=user.id, role_id=role.id, organization_id=None, assigned_by=user.id)
        db.add(assignment)
        db.flush()
        access = _access(db, user.id)
        assert access["permissions"] == ["platform.scheduler.read"]
        assert access["roles"][0]["role_code"] == "platform_scheduler_operator"
        assert has_permission(db, user_id=user.id, permission_code="platform.scheduler.read", organization_id=None)
        assignment.revoked_at = datetime.now(UTC)
        db.flush()
        assert _access(db, user.id)["permissions"] == []
        assert not has_permission(db, user_id=user.id, permission_code="platform.scheduler.read", organization_id=None)
    engine.dispose()


def test_scheduler_configuration_rejects_remote_database_and_non_synthetic_data():
    for overrides, expected in [
        (
            {"database_url": "postgresql+psycopg://user:pass@example.com:5432/maalenex_dev"},
            "host must be local",
        ),
        ({"synthetic_data_only": False}, "Synthetic-only mode is mandatory"),
        ({"database_url": "postgresql+psycopg://localhost:5432/production"}, "database name must be maalenex_dev"),
    ]:
        try:
            Settings(**overrides)
        except ValueError as error:
            assert expected in str(error)
        else:
            raise AssertionError(f"Unsafe scheduler configuration was accepted: {overrides}")


def test_scheduler_timing_configuration_enforces_lease_and_batch_bounds():
    invalid_settings = [
        ({"scheduler_interval_seconds": 4}, "interval must be between"),
        ({"scheduler_interval_seconds": 60, "scheduler_lease_seconds": 90}, "at least twice"),
        ({"scheduler_batch_size": 0}, "batch size must be between"),
        ({"scheduler_batch_size": 1001}, "batch size must be between"),
    ]
    for overrides, expected in invalid_settings:
        try:
            Settings(**overrides)
        except ValueError as error:
            assert expected in str(error)
        else:
            raise AssertionError(f"Invalid scheduler timing was accepted: {overrides}")


def test_staff_admin_sensitive_read_routes_fail_closed_without_staff_session():
    client = TestClient(app)
    protected_gets = [
        "/api/v1/admin/dashboard",
        "/api/v1/admin/access/roles",
        "/api/v1/admin/access/users",
        "/api/v1/admin/access/organizations",
        "/api/v1/admin/access/invitations",
        "/api/v1/admin/operations/scheduler",
        "/api/v1/audit/events",
        "/api/v1/support/cases",
        "/api/v1/reports/passenger",
    ]
    for path in protected_gets:
        response = client.get(path)
        assert response.status_code == 401, (path, response.status_code)



def test_cargo_evidence_orphan_cleanup_is_disabled_without_explicit_grace():
    assert settings.cargo_evidence_orphan_grace_hours == 0
    try:
        Settings(cargo_evidence_orphan_grace_hours=-1)
    except ValueError as error:
        assert "cannot be negative" in str(error)
    else:
        raise AssertionError("Negative orphan cleanup grace was accepted.")


def test_cargo_evidence_scheduler_is_visible_in_operations_snapshot():
    from app.jobs.scheduler_service import CARGO_EVIDENCE_LEASE_NAME

    assert CARGO_EVIDENCE_LEASE_NAME == "cargo_evidence_lifecycle"
    paths = app.openapi()["paths"]
    assert "/api/v1/cargo/evidence/{evidence_id}/download" in paths
    assert "/api/v1/cargo/evidence/{evidence_id}/holds" in paths
    assert "/api/v1/cargo/evidence/{evidence_id}/deletion-requests" in paths
