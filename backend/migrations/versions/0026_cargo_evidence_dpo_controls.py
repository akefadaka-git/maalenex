# ruff: noqa: I001
"""Add DPO deletion suspension control.

Revision ID: 0026_evidence_dpo_controls
Revises: 0025_cargo_evidence_rights
"""
from alembic import op
import sqlalchemy as sa

revision = "0026_evidence_dpo_controls"
down_revision = "0025_cargo_evidence_rights"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cargo_delivery_evidence", sa.Column(
        "deletion_suspended", sa.Boolean(), nullable=False, server_default=sa.false(),
    ))
    op.add_column("cargo_delivery_evidence", sa.Column("deletion_suspension_reason", sa.String(500), nullable=True))
    op.add_column("cargo_delivery_evidence", sa.Column("deletion_suspended_by", sa.Uuid(), nullable=True))
    op.add_column("cargo_delivery_evidence", sa.Column("deletion_suspended_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_cargo_evidence_deletion_suspended_by", "cargo_delivery_evidence", "staff_users",
        ["deletion_suspended_by"], ["id"], ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_cargo_evidence_deletion_suspended_by", "cargo_delivery_evidence", type_="foreignkey")
    op.drop_column("cargo_delivery_evidence", "deletion_suspended_at")
    op.drop_column("cargo_delivery_evidence", "deletion_suspended_by")
    op.drop_column("cargo_delivery_evidence", "deletion_suspension_reason")
    op.drop_column("cargo_delivery_evidence", "deletion_suspended")
