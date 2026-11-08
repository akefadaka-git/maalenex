"""General platform accounts and auditable trust verification.

Revision ID: 0010_accounts_trust
Revises: 0009_service_roles
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_accounts_trust"
down_revision = "0009_service_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "platform_accounts",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("preferred_locale", sa.String(16), nullable=False, server_default="am-ET"),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'suspended', 'closed')",
            name="ck_platform_accounts_status",
        ),
    )
    op.create_table(
        "account_identifiers",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("identifier_type", sa.String(16), nullable=False),
        sa.Column("lookup_digest", sa.String(64), nullable=False),
        sa.Column("encrypted_value", sa.LargeBinary(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("identifier_type IN ('email', 'phone')", name="ck_account_identifier_type"),
    )
    op.create_index(
        "uq_active_account_identifier_digest", "account_identifiers",
        ["identifier_type", "lookup_digest"], unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_index("ix_account_identifiers_account_id", "account_identifiers", ["account_id"])
    op.create_table(
        "account_credentials",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("credential_type", sa.String(24), nullable=False),
        sa.Column("verifier", sa.String(1024), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("credential_type IN ('password', 'passkey')", name="ck_account_credential_type"),
        sa.CheckConstraint("status IN ('active', 'revoked')", name="ck_account_credential_status"),
    )
    op.create_index("ix_account_credentials_account_id", "account_credentials", ["account_id"])
    op.create_table(
        "account_service_role_assignments",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_code", sa.String(32), sa.ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False),
        sa.Column("role_id", uuid, sa.ForeignKey("access_roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assigned_by", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "uq_active_account_service_role", "account_service_role_assignments",
        ["account_id", "organization_id", "service_code", "role_id"], unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_index(
        "ix_account_service_roles_org_service", "account_service_role_assignments",
        ["organization_id", "service_code"],
    )
    op.create_table(
        "trust_verification_cases",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("subject_type", sa.String(20), nullable=False),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="CASCADE")),
        sa.Column("organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("verification_level", sa.String(32), nullable=False, server_default="basic"),
        sa.Column("status", sa.String(24), nullable=False, server_default="draft"),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("reviewed_by", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("decision_reason_code", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "(subject_type = 'individual' AND account_id IS NOT NULL AND organization_id IS NULL) "
            "OR (subject_type = 'organization' AND organization_id IS NOT NULL AND account_id IS NULL)",
            name="ck_trust_case_exactly_one_subject",
        ),
        sa.CheckConstraint(
            "subject_type IN ('individual', 'organization')", name="ck_trust_case_subject_type"
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'submitted', 'in_review', 'approved', 'rejected', 'expired', 'revoked')",
            name="ck_trust_case_status",
        ),
    )
    op.create_index(
        "uq_open_individual_trust_case", "trust_verification_cases", ["account_id"],
        unique=True, postgresql_where=sa.text(
            "account_id IS NOT NULL AND status IN ('submitted', 'in_review')"
        ),
    )
    op.create_index(
        "uq_open_organization_trust_case", "trust_verification_cases", ["organization_id"],
        unique=True, postgresql_where=sa.text(
            "organization_id IS NOT NULL AND status IN ('submitted', 'in_review')"
        ),
    )
    op.create_table(
        "trust_evidence",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("case_id", uuid, sa.ForeignKey("trust_verification_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_type", sa.String(48), nullable=False),
        sa.Column("issuer_code", sa.String(80)),
        sa.Column("document_digest", sa.String(64), nullable=False),
        sa.Column("private_object_key", sa.String(512), nullable=False),
        sa.Column("media_type", sa.String(120), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="submitted"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('submitted', 'accepted', 'rejected', 'expired')",
            name="ck_trust_evidence_status",
        ),
    )
    op.create_index("ix_trust_evidence_case_id", "trust_evidence", ["case_id"])
    op.create_table(
        "trust_review_events",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("case_id", uuid, sa.ForeignKey("trust_verification_cases.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("actor_staff_user_id", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("from_status", sa.String(24), nullable=False),
        sa.Column("to_status", sa.String(24), nullable=False),
        sa.Column("reason_code", sa.String(80)),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("case_id", "sequence_number", name="uq_trust_review_case_sequence"),
    )
    op.create_index("ix_trust_review_events_case_id", "trust_review_events", ["case_id"])
    op.execute("""
        CREATE OR REPLACE FUNCTION reject_trust_review_event_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $trust$
        BEGIN
            RAISE EXCEPTION 'trust_review_events are append-only';
        END;
        $trust$
    """)
    op.execute("""
        CREATE TRIGGER trust_review_events_append_only
        BEFORE UPDATE OR DELETE ON trust_review_events
        FOR EACH ROW EXECUTE FUNCTION reject_trust_review_event_mutation()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trust_review_events_append_only ON trust_review_events")
    op.execute("DROP FUNCTION IF EXISTS reject_trust_review_event_mutation()")
    op.drop_index("ix_trust_review_events_case_id", table_name="trust_review_events")
    op.drop_table("trust_review_events")
    op.drop_index("ix_trust_evidence_case_id", table_name="trust_evidence")
    op.drop_table("trust_evidence")
    op.drop_index("uq_open_organization_trust_case", table_name="trust_verification_cases")
    op.drop_index("uq_open_individual_trust_case", table_name="trust_verification_cases")
    op.drop_table("trust_verification_cases")
    op.drop_index("ix_account_service_roles_org_service", table_name="account_service_role_assignments")
    op.drop_index("uq_active_account_service_role", table_name="account_service_role_assignments")
    op.drop_table("account_service_role_assignments")
    op.drop_index("ix_account_credentials_account_id", table_name="account_credentials")
    op.drop_table("account_credentials")
    op.drop_index("ix_account_identifiers_account_id", table_name="account_identifiers")
    op.drop_index("uq_active_account_identifier_digest", table_name="account_identifiers")
    op.drop_table("account_identifiers")
    op.drop_table("platform_accounts")
