"""Add category-aware retention, privacy review and rights-request records.

Revision ID: 0024_cargo_legal_retention
Revises: 0023_evidence_hold_review
"""
from alembic import op
import sqlalchemy as sa

revision = "0024_cargo_legal_retention"
down_revision = "0023_evidence_hold_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cargo_delivery_evidence", sa.Column(
        "accounting_document", sa.Boolean(), nullable=False, server_default=sa.false(),
    ))
    op.add_column("cargo_delivery_evidence", sa.Column(
        "commercial_correspondence", sa.Boolean(), nullable=False, server_default=sa.false(),
    ))
    op.add_column("cargo_delivery_evidence", sa.Column(
        "personal_data_present", sa.Boolean(), nullable=False, server_default=sa.true(),
    ))
    op.add_column("cargo_delivery_evidence", sa.Column(
        "sensitive_personal_data_present", sa.Boolean(), nullable=False, server_default=sa.false(),
    ))
    for name in ("accounting_record_date", "correspondence_date",
                 "audit_retention_expires_at", "tombstone_retention_expires_at"):
        op.add_column("cargo_delivery_evidence", sa.Column(name, sa.DateTime(timezone=True), nullable=True))
    for name, length in (
        ("privacy_processing_basis", 40), ("retention_justification", 500),
        ("dpia_reference", 160), ("audit_retention_justification", 500),
        ("tombstone_retention_justification", 500),
    ):
        op.add_column("cargo_delivery_evidence", sa.Column(name, sa.String(length), nullable=True))
    op.add_column("cargo_delivery_evidence", sa.Column(
        "rights_review_status", sa.String(24), nullable=False, server_default="not_reviewed",
    ))
    op.add_column("cargo_delivery_evidence", sa.Column(
        "dpo_deletion_suspended", sa.Boolean(), nullable=False, server_default=sa.false(),
    ))
    op.add_column("cargo_delivery_evidence_holds", sa.Column(
        "release_conclusion_reference", sa.String(160), nullable=True,
    ))
    op.add_column("cargo_delivery_evidence_holds", sa.Column(
        "release_confirmed_by", sa.Uuid(),
        sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True,
    ))
    op.create_table(
        "cargo_delivery_evidence_rights_requests",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("request_type", sa.String(24), nullable=False),
        sa.Column("requested_by_reference", sa.String(160), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("decision", sa.String(24), nullable=True),
        sa.Column("decision_reason", sa.String(500), nullable=True),
        sa.Column("reviewed_by", sa.Uuid(), sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_cargo_evidence_rights_status",
        "cargo_delivery_evidence_rights_requests", ["status", "created_at"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    rights_count = bind.execute(sa.text(
        "SELECT count(*) FROM cargo_delivery_evidence_rights_requests"
    )).scalar_one()
    classified_count = bind.execute(sa.text(
        "SELECT count(*) FROM cargo_delivery_evidence "
        "WHERE accounting_document OR commercial_correspondence "
        "OR sensitive_personal_data_present OR dpo_deletion_suspended "
        "OR classification_status <> 'unclassified' "
        "OR privacy_processing_basis IS NOT NULL OR dpia_reference IS NOT NULL "
        "OR audit_retention_justification IS NOT NULL "
        "OR tombstone_retention_justification IS NOT NULL"
    )).scalar_one()
    released_holds = bind.execute(sa.text(
        "SELECT count(*) FROM cargo_delivery_evidence_holds "
        "WHERE release_conclusion_reference IS NOT NULL OR release_confirmed_by IS NOT NULL"
    )).scalar_one()
    if rights_count or classified_count or released_holds:
        raise RuntimeError(
            "Refusing to downgrade populated legal-retention or rights-governance records."
        )
    op.drop_index("ix_cargo_evidence_rights_status", table_name="cargo_delivery_evidence_rights_requests")
    op.drop_table("cargo_delivery_evidence_rights_requests")
    op.drop_column("cargo_delivery_evidence_holds", "release_confirmed_by")
    op.drop_column("cargo_delivery_evidence_holds", "release_conclusion_reference")
    for name in (
        "dpo_deletion_suspended", "rights_review_status",
        "tombstone_retention_justification", "audit_retention_justification",
        "dpia_reference", "retention_justification", "privacy_processing_basis",
        "tombstone_retention_expires_at", "audit_retention_expires_at",
        "correspondence_date", "accounting_record_date",
        "sensitive_personal_data_present", "personal_data_present",
        "commercial_correspondence", "accounting_document",
    ):
        op.drop_column("cargo_delivery_evidence", name)
