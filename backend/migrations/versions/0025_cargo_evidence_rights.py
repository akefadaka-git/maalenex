# ruff: noqa: I001
"""Add data-subject rights request triage for cargo evidence.

Revision ID: 0025_cargo_evidence_rights
Revises: 0024_cargo_evidence_legal_retention
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0025_cargo_evidence_rights"
down_revision = "0024_cargo_evidence_legal_retention"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "cargo_delivery_evidence_rights_requests",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("evidence_id", uuid, sa.ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("request_type", sa.String(24), nullable=False),
        sa.Column("request_reference", sa.String(160), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("assessed_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("assessed_at", sa.DateTime(timezone=True)),
        sa.Column("assessment_note", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_cargo_evidence_rights_status",
        "cargo_delivery_evidence_rights_requests", ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_cargo_evidence_rights_status", table_name="cargo_delivery_evidence_rights_requests")
    op.drop_table("cargo_delivery_evidence_rights_requests")
