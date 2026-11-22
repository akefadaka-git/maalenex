"""Add category-aware legal retention and privacy governance fields.

Revision ID: 0024_cargo_evidence_legal_retention
Revises: 0023_evidence_hold_review
"""
from alembic import op
import sqlalchemy as sa

revision = "0024_cargo_evidence_legal_retention"
down_revision = "0023_evidence_hold_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = [
        sa.Column("classification_complete", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_accounting_document", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_commercial_correspondence", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_ordinary_operational_evidence", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("contains_personal_data", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("contains_sensitive_personal_data", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("accounting_document_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("commercial_correspondence_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("operational_retention_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("operational_legal_basis", sa.String(40), nullable=True),
        sa.Column("operational_retention_justification", sa.String(1000), nullable=True),
        sa.Column("operational_dpia_reference", sa.String(160), nullable=True),
        sa.Column("sensitive_data_handling_review_reference", sa.String(160), nullable=True),
        sa.Column("legal_retention_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rights_request_status", sa.String(24), nullable=False, server_default="none"),
        sa.Column("tombstone_retention_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("audit_retention_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retention_metadata_justification", sa.String(1000), nullable=True),
    ]
    for column in columns:
        op.add_column("cargo_delivery_evidence", column)

    op.add_column("cargo_delivery_evidence_holds", sa.Column("release_reviewed_by", sa.Uuid(), nullable=True))
    op.add_column("cargo_delivery_evidence_holds", sa.Column("release_reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("cargo_delivery_evidence_holds", sa.Column("release_review_note", sa.String(500), nullable=True))
    op.create_foreign_key(
        "fk_cargo_evidence_hold_release_reviewer",
        "cargo_delivery_evidence_holds", "staff_users",
        ["release_reviewed_by"], ["id"], ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_cargo_evidence_hold_release_reviewer", "cargo_delivery_evidence_holds", type_="foreignkey")
    op.drop_column("cargo_delivery_evidence_holds", "release_review_note")
    op.drop_column("cargo_delivery_evidence_holds", "release_reviewed_at")
    op.drop_column("cargo_delivery_evidence_holds", "release_reviewed_by")
    for name in [
        "retention_metadata_justification", "audit_retention_until", "tombstone_retention_until",
        "rights_request_status", "legal_retention_until", "sensitive_data_handling_review_reference",
        "operational_dpia_reference", "operational_retention_justification", "operational_legal_basis",
        "operational_retention_started_at", "commercial_correspondence_date", "accounting_document_date",
        "contains_sensitive_personal_data", "contains_personal_data", "is_ordinary_operational_evidence",
        "is_commercial_correspondence", "is_accounting_document", "classification_complete",
    ]:
        op.drop_column("cargo_delivery_evidence", name)
