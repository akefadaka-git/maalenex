"""Passenger-owned support cases independent of booking records.

Revision ID: 0010_passenger_support_cases
Revises: 0009_passenger_identity
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0010_passenger_support_cases"
down_revision = "0009_passenger_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "passenger_support_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_reference", sa.String(32), nullable=False),
        sa.Column(
            "passenger_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("passenger_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("subject", sa.String(160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="open"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolution_code", sa.String(80), nullable=True),
        sa.Column("resolution_note", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name="ck_passenger_support_cases_status",
        ),
        sa.UniqueConstraint("case_reference", name="uq_passenger_support_cases_reference"),
    )
    op.create_index(
        "ix_passenger_support_owner_created",
        "passenger_support_cases",
        ["passenger_id", "created_at"],
    )
    op.create_index(
        "ix_passenger_support_status_created",
        "passenger_support_cases",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_passenger_support_status_created", table_name="passenger_support_cases")
    op.drop_index("ix_passenger_support_owner_created", table_name="passenger_support_cases")
    op.drop_table("passenger_support_cases")
