"""Durable lease and execution telemetry for scheduled maintenance jobs."""
# ruff: noqa: I001
from datetime import UTC, datetime, timedelta
from time import perf_counter

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.domains.operations.models import SchedulerLease, SchedulerRun
from app.jobs.booking_hold_expiry import expire_due_booking_holds


LEASE_NAME = "booking_hold_expiry"


def _utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace(" ", "T"))
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def run_scheduler_cycle(session_factory, *, worker_id: str, batch_size: int = 100,
                        lease_seconds: int = 90) -> dict:
    """Acquire a database lease, execute one bounded batch and persist telemetry."""
    started_clock = perf_counter()
    with session_factory() as db:
        now = _utc(db.scalar(select(func.now()))) or datetime.now(UTC)
        lease_values = {
            "lease_name": LEASE_NAME,
            "owner_id": worker_id,
            "lease_expires_at": now + timedelta(seconds=lease_seconds),
            "heartbeat_at": now,
        }
        claim = pg_insert(SchedulerLease).values(**lease_values).on_conflict_do_update(
            index_elements=[SchedulerLease.lease_name],
            set_={
                "owner_id": worker_id,
                "lease_expires_at": lease_values["lease_expires_at"],
                "heartbeat_at": now,
                "updated_at": now,
            },
            where=(
                (SchedulerLease.lease_expires_at <= now)
                | (SchedulerLease.owner_id == worker_id)
            ),
        ).returning(SchedulerLease.lease_name)
        acquired = db.scalar(claim)
        if acquired is not None:
            db.execute(update(SchedulerRun).where(
                SchedulerRun.job_name == LEASE_NAME,
                SchedulerRun.status == "running",
                SchedulerRun.worker_id != worker_id,
            ).values(status="abandoned", finished_at=now, error_code="worker_lease_expired"))
        db.commit()
        if acquired is None:
            return {"status": "lease_held_by_another_worker", "records_processed": 0}
        run = SchedulerRun(
            job_name=LEASE_NAME, worker_id=worker_id, status="running", started_at=now,
        )
        db.add(run)
        db.commit()
        run_id = run.id

    try:
        with session_factory() as db:
            processed = expire_due_booking_holds(db, batch_size=batch_size)
            db.commit()
        duration_ms = int((perf_counter() - started_clock) * 1000)
        with session_factory() as db:
            finished = _utc(db.scalar(select(func.now()))) or datetime.now(UTC)
            run = db.get(SchedulerRun, run_id)
            lease = db.get(SchedulerLease, LEASE_NAME)
            owns_lease = lease is not None and lease.owner_id == worker_id
            cycle_status = "succeeded" if owns_lease else "abandoned"
            if run is not None and run.status == "running":
                run.status = "succeeded" if owns_lease else "abandoned"
                run.finished_at = finished
                run.records_processed = processed
                run.duration_ms = duration_ms
                if not owns_lease:
                    run.error_code = "lease_lost_during_execution"
            if owns_lease:
                lease.heartbeat_at = finished
                lease.lease_expires_at = finished + timedelta(seconds=lease_seconds)
                lease.last_success_at = finished
                lease.last_error_code = None
                lease.consecutive_failures = 0
                lease.batches_completed += 1
                lease.records_processed += processed
                lease.last_duration_ms = duration_ms
            db.commit()
        return {"status": cycle_status, "records_processed": processed, "duration_ms": duration_ms}
    except Exception as exc:
        duration_ms = int((perf_counter() - started_clock) * 1000)
        error_code = type(exc).__name__[:80]
        with session_factory() as db:
            finished = _utc(db.scalar(select(func.now()))) or datetime.now(UTC)
            run = db.get(SchedulerRun, run_id)
            lease = db.get(SchedulerLease, LEASE_NAME)
            owns_lease = lease is not None and lease.owner_id == worker_id
            if run is not None and run.status == "running":
                run.status = "failed" if owns_lease else "abandoned"
                run.finished_at = finished
                run.duration_ms = duration_ms
                run.error_code = error_code if owns_lease else "lease_lost_during_execution"
            if owns_lease:
                lease.heartbeat_at = finished
                lease.lease_expires_at = finished + timedelta(seconds=lease_seconds)
                lease.last_failure_at = finished
                lease.last_error_code = error_code
                lease.consecutive_failures += 1
                lease.last_duration_ms = duration_ms
            db.commit()
        raise


def scheduler_snapshot(db, *, stale_after_seconds: int = 90, limit: int = 20) -> dict:
    now = _utc(db.scalar(select(func.now()))) or datetime.now(UTC)
    lease = db.get(SchedulerLease, LEASE_NAME)
    runs = list(db.scalars(
        select(SchedulerRun).where(SchedulerRun.job_name == LEASE_NAME)
        .order_by(SchedulerRun.started_at.desc()).limit(max(1, min(limit, 50)))
    ))
    if lease is None:
        health = "not_configured"
        heartbeat_age = None
        lease_active = False
        lease_remaining = None
    else:
        heartbeat = _utc(lease.heartbeat_at)
        heartbeat_age = max(0, int((now - heartbeat).total_seconds())) if heartbeat else None
        lease_expiry = _utc(lease.lease_expires_at)
        lease_remaining = max(0, int((lease_expiry - now).total_seconds())) if lease_expiry else None
        lease_active = bool(lease_expiry and lease_expiry > now)
        if heartbeat_age is None or heartbeat_age > stale_after_seconds or not lease_active:
            health = "stale"
        elif lease.consecutive_failures:
            health = "degraded"
        else:
            health = "healthy"
    return {
        "job_name": LEASE_NAME,
        "health": health,
        "worker_enabled_by_default": False,
        "worker_mode": "separate_process",
        "lease_active": lease_active,
        "lease_remaining_seconds": lease_remaining,
        "lease": None if lease is None else {
            "owner_id": lease.owner_id,
            "lease_expires_at": _utc(lease.lease_expires_at).isoformat(),
            "heartbeat_at": _utc(lease.heartbeat_at).isoformat(),
            "heartbeat_age_seconds": heartbeat_age,
            "last_success_at": _utc(lease.last_success_at).isoformat() if lease.last_success_at else None,
            "last_failure_at": _utc(lease.last_failure_at).isoformat() if lease.last_failure_at else None,
            "last_error_code": lease.last_error_code,
            "consecutive_failures": lease.consecutive_failures,
            "batches_completed": lease.batches_completed,
            "records_processed": lease.records_processed,
            "last_duration_ms": lease.last_duration_ms,
        },
        "runs": [{
            "id": str(run.id), "worker_id": run.worker_id, "status": run.status,
            "started_at": _utc(run.started_at).isoformat(),
            "finished_at": _utc(run.finished_at).isoformat() if run.finished_at else None,
            "records_processed": run.records_processed, "duration_ms": run.duration_ms,
            "error_code": run.error_code,
        } for run in runs],
    }
