"""Service-scoped organization role assignments.

Revision ID: 0009_service_roles
Revises: 0008_platform_service_registry
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_service_roles"
down_revision = "0008_platform_service_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "service_role_assignments",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("staff_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_code", sa.String(32), sa.ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False),
        sa.Column("role_id", uuid, sa.ForeignKey("access_roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assigned_by", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "uq_active_service_role_assignment", "service_role_assignments",
        ["user_id", "organization_id", "service_code", "role_id"],
        unique=True, postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_index(
        "ix_service_role_assignments_organization_service", "service_role_assignments",
        ["organization_id", "service_code"],
    )


def downgrade() -> None:
    op.drop_index("ix_service_role_assignments_organization_service", table_name="service_role_assignments")
    op.drop_index("uq_active_service_role_assignment", table_name="service_role_assignments")
    op.drop_table("service_role_assignments")
