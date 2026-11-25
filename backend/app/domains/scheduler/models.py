from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SchedulerLease(Base):
    __tablename__ = "scheduler_leases"
    __table_args__ = (Index("ix_scheduler_leases_lease_expires_at", "lease_expires_at"),)

    lease_name: Mapped[str] = mapped_column(String(80), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(80))
    lease_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, server_default="0")
    batches_completed: Mapped[int] = mapped_column(Integer, server_default="0")
    records_processed: Mapped[int] = mapped_column(Integer, server_default="0")
    last_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SchedulerRun(Base):
    __tablename__ = "scheduler_runs"
    __table_args__ = (
        Index("ix_scheduler_runs_job_name", "job_name"),
        Index("ix_scheduler_runs_worker_id", "worker_id"),
        Index("ix_scheduler_runs_status", "status"),
        Index("ix_scheduler_runs_started_at", "started_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    job_name: Mapped[str] = mapped_column(String(80))
    worker_id: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(24))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    records_processed: Mapped[int] = mapped_column(Integer, server_default="0")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
