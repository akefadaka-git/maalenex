"""Add independent audit and tombstone retention review metadata.

Revision ID: 0025_audit_tombstone_review
Revises: 0024_cargo_legal_retention
"""
from alembic import op
import sqlalchemy as sa

revision = "0025_audit_tombstone_review"
down_revision = "0024_cargo_legal_retention"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name in ("audit_retention_classified_by", "audit_retention_reviewed_by",
                 "tombstone_retention_classified_by", "tombstone_retention_reviewed_by"):
        op.add_column("cargo_delivery_evidence", sa.Column(
            name, sa.Uuid(), sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True,
        ))
    for name in ("audit_retention_reviewed_at", "tombstone_retention_reviewed_at"):
        op.add_column("cargo_delivery_evidence", sa.Column(
            name, sa.DateTime(timezone=True), nullable=True,
        ))


def downgrade() -> None:
    for name in (
        "tombstone_retention_reviewed_at", "audit_retention_reviewed_at",
        "tombstone_retention_reviewed_by", "tombstone_retention_classified_by",
        "audit_retention_reviewed_by", "audit_retention_classified_by",
    ):
        op.drop_column("cargo_delivery_evidence", name)
