"""Identity, audit and operator organization foundation.

Revision ID: 0002_identity_audit_orgs
Revises: 0001_g1_foundation
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_identity_audit_orgs"
down_revision = "0001_g1_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table("staff_users",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("login_identifier", sa.String(254), nullable=False, unique=True),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_staff_users_status", "staff_users", ["status"])
    op.create_table("staff_credentials",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("staff_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("credential_type", sa.String(32), nullable=False),
        sa.Column("secret_hash", sa.String(512), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)))
    op.create_index("ix_staff_credentials_user_id", "staff_credentials", ["user_id"])
    op.create_table("staff_sessions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("staff_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("secret_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)))
    op.create_index("ix_staff_sessions_user_id", "staff_sessions", ["user_id"])
    op.create_index("ix_staff_sessions_expires_at", "staff_sessions", ["expires_at"])
    op.create_table("access_roles",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("code", sa.String(80), nullable=False, unique=True),
        sa.Column("description", sa.String(240), nullable=False))
    op.create_table("access_permissions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(240), nullable=False))
    op.create_table("access_role_permissions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("role_id", uuid, sa.ForeignKey("access_roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", uuid, sa.ForeignKey("access_permissions.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"))
    op.create_table("access_role_assignments",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("staff_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", uuid, sa.ForeignKey("access_roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("organization_id", uuid),
        sa.Column("assigned_by", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)))
    op.create_index("ix_access_role_assignments_user_id", "access_role_assignments", ["user_id"])
    op.create_index("ix_access_role_assignments_organization_id", "access_role_assignments", ["organization_id"])
    op.create_table("organizations",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("organization_type", sa.String(32), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_organizations_status", "organizations", ["status"])
    op.create_table("organization_memberships",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", uuid, sa.ForeignKey("staff_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("membership_status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)))
    op.create_index("ix_organization_memberships_organization_id", "organization_memberships", ["organization_id"])
    op.create_index("ix_organization_memberships_user_id", "organization_memberships", ["user_id"])
    op.create_table("audit_events",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_type", sa.String(24), nullable=False),
        sa.Column("actor_id", sa.String(80)),
        sa.Column("actor_role_snapshot", sa.String(120)),
        sa.Column("organization_id", uuid),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(80)),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("outcome", sa.String(24), nullable=False),
        sa.Column("reason_code", sa.String(100)),
        sa.Column("request_id", sa.String(80)),
        sa.Column("correlation_id", sa.String(80)),
        sa.Column("metadata_redacted", sa.JSON(), nullable=False))
    for column in ("event_type", "occurred_at", "actor_id", "organization_id", "resource_id", "request_id", "correlation_id"):
        op.create_index("ix_audit_events_" + column, "audit_events", [column])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("organization_memberships")
    op.drop_table("organizations")
    op.drop_table("access_role_assignments")
    op.drop_table("access_role_permissions")
    op.drop_table("access_permissions")
    op.drop_table("access_roles")
    op.drop_table("staff_sessions")
    op.drop_table("staff_credentials")
    op.drop_table("staff_users")
