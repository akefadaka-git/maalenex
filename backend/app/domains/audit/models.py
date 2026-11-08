from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    actor_type: Mapped[str] = mapped_column(String(24))
    actor_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    actor_role_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
    organization_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80))
    outcome: Mapped[str] = mapped_column(String(24))
    reason_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    metadata_redacted: Mapped[dict] = mapped_column(JSON, default=dict)
