from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
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


class PassengerAccount(Base):
    __tablename__ = "passenger_accounts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'suspended', 'closed')",
            name="ck_passenger_accounts_status",
        ),
        Index("ix_passenger_accounts_login_identifier", "login_identifier", unique=True),
        Index("ix_passenger_accounts_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    login_identifier: Mapped[str] = mapped_column(String(254))
    display_name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(24), server_default="active")
    contact_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PassengerCredential(Base):
    __tablename__ = "passenger_credentials"
    __table_args__ = (Index("ix_passenger_credentials_passenger_id", "passenger_id"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE")
    )
    credential_type: Mapped[str] = mapped_column(String(32))
    secret_hash: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(24), server_default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PassengerSession(Base):
    __tablename__ = "passenger_sessions"
    __table_args__ = (
        Index("ix_passenger_sessions_passenger_id", "passenger_id"),
        Index("ix_passenger_sessions_expires_at", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE")
    )
    secret_hash: Mapped[str] = mapped_column(String(64), unique=True)
    csrf_token_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PassengerLoginAttempt(Base):
    __tablename__ = "passenger_login_attempts"

    key_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    failed_count: Mapped[int] = mapped_column(Integer, server_default="0")
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PassengerSupportCase(Base):
    __tablename__ = "passenger_support_cases"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name="ck_passenger_support_cases_status",
        ),
        UniqueConstraint("case_reference", name="uq_passenger_support_cases_reference"),
        Index("ix_passenger_support_owner_created", "passenger_id", "created_at"),
        Index("ix_passenger_support_status_created", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    case_reference: Mapped[str] = mapped_column(String(32))
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE")
    )
    category: Mapped[str] = mapped_column(String(32))
    subject: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), server_default="open")
    assigned_to: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    resolution_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PassengerReport(Base):
    __tablename__ = "passenger_reports"
    __table_args__ = (
        CheckConstraint("report_type IN ('report', 'complaint')", name="ck_passenger_reports_type"),
        CheckConstraint(
            "status IN ('submitted', 'under_review', 'action_required', 'resolved', 'dismissed')",
            name="ck_passenger_reports_status",
        ),
        CheckConstraint(
            "severity IN ('low', 'normal', 'high', 'urgent')",
            name="ck_passenger_reports_severity",
        ),
        UniqueConstraint("report_reference", name="uq_passenger_reports_reference"),
        Index("ix_passenger_reports_owner_created", "passenger_id", "created_at"),
        Index("ix_passenger_reports_status_created", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_reference: Mapped[str] = mapped_column(String(32))
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE")
    )
    report_type: Mapped[str] = mapped_column(String(16))
    category: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(16), server_default="normal")
    subject: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), server_default="submitted")
    assigned_to: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    resolution_note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PassengerReportAttachment(Base):
    __tablename__ = "passenger_report_attachments"
    __table_args__ = (
        UniqueConstraint("storage_key", name="uq_passenger_report_attachments_storage_key"),
        Index("ix_passenger_report_attachments_report", "report_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_reports.id", ondelete="CASCADE")
    )
    original_filename: Mapped[str] = mapped_column(String(180))
    content_type: Mapped[str] = mapped_column(String(80))
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    storage_key: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PassengerNotification(Base):
    __tablename__ = "passenger_notifications"
    __table_args__ = (
        UniqueConstraint("dedupe_key", name="uq_passenger_notifications_dedupe_key"),
        Index("ix_passenger_notifications_owner_created", "passenger_id", "created_at"),
        Index("ix_passenger_notifications_owner_read", "passenger_id", "read_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE")
    )
    notification_type: Mapped[str] = mapped_column(String(48))
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    resource_type: Mapped[str | None] = mapped_column(String(48), nullable=True)
    resource_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dedupe_key: Mapped[str] = mapped_column(String(128))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PassengerNotificationPreference(Base):
    __tablename__ = "passenger_notification_preferences"
    __table_args__ = (
        UniqueConstraint("passenger_id", name="uq_passenger_notification_preferences_owner"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE")
    )
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, server_default="true")
    email_enabled: Mapped[bool] = mapped_column(Boolean, server_default="false")
    sms_enabled: Mapped[bool] = mapped_column(Boolean, server_default="false")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
