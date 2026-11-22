# ruff: noqa: I001
"""Track one-time due-date escalation for legal-hold reviews.

Revision ID: 0023_cargo_evidence_hold_review_alert
Revises: 0022_cargo_evidence_lifecycle
"""
from alembic import op
import sqlalchemy as sa

revision = "0023_cargo_evidence_hold_review_alert"
down_revision = "0022_cargo_evidence_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cargo_delivery_evidence_holds",
        sa.Column("review_alerted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cargo_delivery_evidence_holds", "review_alerted_at")
