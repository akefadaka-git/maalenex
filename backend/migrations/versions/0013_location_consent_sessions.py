"""Versioned location consent, scoped sessions and synthetic-only samples.

Revision ID: 0013_location_consent
Revises: 0012_challenge_resend
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0013_location_consent"
down_revision = "0012_challenge_resend"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "location_consents",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("service_code", sa.String(32), sa.ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False),
        sa.Column("resource_type", sa.String(32), nullable=False),
        sa.Column("resource_id", sa.String(80), nullable=False),
        sa.Column("purpose", sa.String(32), nullable=False),
        sa.Column("consent_version", sa.String(40), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("purpose IN ('active_job_tracking', 'safety_response')", name="ck_location_consent_purpose"),
        sa.CheckConstraint("resource_type IN ('move_ride', 'delivery_shipment', 'cargo_movement')", name="ck_location_consent_resource_type"),
        sa.CheckConstraint("length(consent_version) > 0", name="ck_location_consent_version"),
        sa.CheckConstraint("expires_at > granted_at", name="ck_location_consent_expiry"),
    )
    op.create_index(
        "ix_location_consents_subject_scope", "location_consents",
        ["account_id", "service_code", "resource_type", "resource_id", "purpose"],
    )
    op.create_table(
        "location_sessions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("consent_id", uuid, sa.ForeignKey("location_consents.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("service_code", sa.String(32), sa.ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False),
        sa.Column("resource_type", sa.String(32), nullable=False),
        sa.Column("resource_id", sa.String(80), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_sample_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("status IN ('active', 'completed', 'expired', 'revoked')", name="ck_location_session_status"),
        sa.CheckConstraint("resource_type IN ('move_ride', 'delivery_shipment', 'cargo_movement')", name="ck_location_session_resource_type"),
        sa.CheckConstraint("expires_at > started_at", name="ck_location_session_expiry"),
    )
    op.create_index("ix_location_sessions_account_status", "location_sessions", ["account_id", "status"])
    op.create_index("ix_location_sessions_resource_scope", "location_sessions", ["service_code", "resource_type", "resource_id"])
    op.create_index(
        "uq_active_location_session_per_consent", "location_sessions", ["consent_id"],
        unique=True, postgresql_where=sa.text("status = 'active'"),
    )
    op.create_table(
        "synthetic_location_samples",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("session_id", uuid, sa.ForeignKey("location_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("accuracy_meters", sa.Numeric(8, 2)),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("source", sa.String(32), nullable=False, server_default="synthetic_fixture"),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("is_synthetic IS TRUE", name="ck_location_sample_synthetic_only"),
        sa.CheckConstraint("source = 'synthetic_fixture'", name="ck_location_sample_source"),
        sa.CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_location_sample_latitude"),
        sa.CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_location_sample_longitude"),
        sa.CheckConstraint("accuracy_meters IS NULL OR accuracy_meters >= 0", name="ck_location_sample_accuracy"),
    )
    op.create_index(
        "ix_synthetic_location_samples_session_time", "synthetic_location_samples",
        ["session_id", "captured_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_synthetic_location_samples_session_time", table_name="synthetic_location_samples")
    op.drop_table("synthetic_location_samples")
    op.drop_index("uq_active_location_session_per_consent", table_name="location_sessions")
    op.drop_index("ix_location_sessions_resource_scope", table_name="location_sessions")
    op.drop_index("ix_location_sessions_account_status", table_name="location_sessions")
    op.drop_table("location_sessions")
    op.drop_index("ix_location_consents_subject_scope", table_name="location_consents")
    op.drop_table("location_consents")
