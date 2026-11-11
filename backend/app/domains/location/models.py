from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String,
    Uuid, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LocationConsent(Base):
    __tablename__ = "location_consents"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ('active_job_tracking', 'safety_response')",
            name="ck_location_consent_purpose",
        ),
        CheckConstraint(
            "resource_type IN ('move_ride', 'delivery_shipment', 'cargo_movement')",
            name="ck_location_consent_resource_type",
        ),
        CheckConstraint("length(consent_version) > 0", name="ck_location_consent_version"),
        CheckConstraint("expires_at > granted_at", name="ck_location_consent_expiry"),
        Index(
            "ix_location_consents_subject_scope",
            "account_id", "service_code", "resource_type", "resource_id", "purpose",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="RESTRICT"), nullable=False
    )
    service_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False
    )
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(80), nullable=False)
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    consent_version: Mapped[str] = mapped_column(String(40), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LocationSession(Base):
    __tablename__ = "location_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'expired', 'revoked')",
            name="ck_location_session_status",
        ),
        CheckConstraint(
            "resource_type IN ('move_ride', 'delivery_shipment', 'cargo_movement')",
            name="ck_location_session_resource_type",
        ),
        CheckConstraint("expires_at > started_at", name="ck_location_session_expiry"),
        Index("ix_location_sessions_account_status", "account_id", "status"),
        Index("ix_location_sessions_resource_scope", "service_code", "resource_type", "resource_id"),
        Index(
            "uq_active_location_session_per_consent", "consent_id", unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    consent_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("location_consents.id", ondelete="RESTRICT"), nullable=False
    )
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="RESTRICT"), nullable=False
    )
    service_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False
    )
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_sample_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SyntheticLocationSample(Base):
    __tablename__ = "synthetic_location_samples"
    __table_args__ = (
        CheckConstraint("is_synthetic IS TRUE", name="ck_location_sample_synthetic_only"),
        CheckConstraint("source = 'synthetic_fixture'", name="ck_location_sample_source"),
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_location_sample_latitude"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_location_sample_longitude"),
        CheckConstraint("accuracy_meters IS NULL OR accuracy_meters >= 0", name="ck_location_sample_accuracy"),
        Index("ix_synthetic_location_samples_session_time", "session_id", "captured_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("location_sessions.id", ondelete="CASCADE"), nullable=False
    )
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    accuracy_meters: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="synthetic_fixture")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
