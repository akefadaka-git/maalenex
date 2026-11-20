"""Passenger-owned reports and complaints with private evidence attachments."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PassengerReport(Base):
    __tablename__ = "passenger_reports"
    __table_args__ = (
        CheckConstraint("report_type IN ('report', 'complaint')", name="ck_passenger_reports_type"),
        CheckConstraint("status IN ('submitted', 'under_review', 'action_required', 'resolved', 'dismissed')", name="ck_passenger_reports_status"),
        CheckConstraint("severity IN ('low', 'normal', 'high', 'urgent')", name="ck_passenger_reports_severity"),
        Index("ix_passenger_reports_owner_created", "passenger_id", "created_at"),
        Index("ix_passenger_reports_status_created", "status", "created_at"),
        UniqueConstraint("report_reference", name="uq_passenger_reports_reference"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_reference: Mapped[str] = mapped_column(String(32), nullable=False)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False
    )
    report_type: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="normal", server_default="normal")
    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="submitted", server_default="submitted")
    assigned_to: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    resolution_note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PassengerReportAttachment(Base):
    __tablename__ = "passenger_report_attachments"
    __table_args__ = (
        Index("ix_passenger_report_attachments_report", "report_id"),
        UniqueConstraint("storage_key", name="uq_passenger_report_attachments_storage_key"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_reports.id", ondelete="CASCADE"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(180), nullable=False)
    content_type: Mapped[str] = mapped_column(String(80), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
