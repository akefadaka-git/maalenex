"""Passenger reports, complaints and private evidence metadata.

Revision ID: 0011_passenger_reports_complaints
Revises: 0010_passenger_support_cases
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0011_passenger_reports"
down_revision = "0010_passenger_support_cases"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "passenger_reports",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("report_reference", sa.String(32), nullable=False),
        sa.Column("passenger_id", uuid, sa.ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_type", sa.String(16), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False, server_default="normal"),
        sa.Column("subject", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="submitted"),
        sa.Column("assigned_to", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolution_note", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("report_type IN ('report', 'complaint')", name="ck_passenger_reports_type"),
        sa.CheckConstraint("status IN ('submitted', 'under_review', 'action_required', 'resolved', 'dismissed')", name="ck_passenger_reports_status"),
        sa.CheckConstraint("severity IN ('low', 'normal', 'high', 'urgent')", name="ck_passenger_reports_severity"),
        sa.UniqueConstraint("report_reference", name="uq_passenger_reports_reference"),
    )
    op.create_index("ix_passenger_reports_owner_created", "passenger_reports", ["passenger_id", "created_at"])
    op.create_index("ix_passenger_reports_status_created", "passenger_reports", ["status", "created_at"])
    op.create_table(
        "passenger_report_attachments",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("report_id", uuid, sa.ForeignKey("passenger_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(180), nullable=False),
        sa.Column("content_type", sa.String(80), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("storage_key", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("storage_key", name="uq_passenger_report_attachments_storage_key"),
    )
    op.create_index("ix_passenger_report_attachments_report", "passenger_report_attachments", ["report_id"])


def downgrade() -> None:
    op.drop_index("ix_passenger_report_attachments_report", table_name="passenger_report_attachments")
    op.drop_table("passenger_report_attachments")
    op.drop_index("ix_passenger_reports_status_created", table_name="passenger_reports")
    op.drop_index("ix_passenger_reports_owner_created", table_name="passenger_reports")
    op.drop_table("passenger_reports")
