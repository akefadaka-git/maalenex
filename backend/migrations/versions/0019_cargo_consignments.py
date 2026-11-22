# ruff: noqa: I001
"""Add organization-scoped cargo consignment lifecycle.

Revision ID: 0019_cargo_consignments
Revises: 0018_koybe_boarding_point
"""
from uuid import NAMESPACE_URL, uuid5

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0019_cargo_consignments"
down_revision = "0018_koybe_boarding_point"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "cargo_consignments",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("consignment_reference", sa.String(80), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("sender_name", sa.String(160), nullable=False),
        sa.Column("recipient_name", sa.String(160), nullable=False),
        sa.Column("destination", sa.String(240), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("weight_grams", sa.Integer()),
        sa.Column("status", sa.String(24), nullable=False, server_default="draft"),
        sa.Column("assigned_organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="RESTRICT")),
        sa.Column("created_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("organization_id", "consignment_reference", name="uq_cargo_org_reference"),
        sa.UniqueConstraint("organization_id", "idempotency_key", name="uq_cargo_org_idempotency"),
        sa.CheckConstraint("weight_grams IS NULL OR weight_grams > 0", name="ck_cargo_weight_positive"),
        sa.CheckConstraint("status IN ('draft','accepted','assigned','in_transit','delivered','cancelled','exception')", name="ck_cargo_status"),
    )
    op.create_index("ix_cargo_consignments_status", "cargo_consignments", ["status"])
    op.create_index("ix_cargo_org_status_created", "cargo_consignments", ["organization_id", "status", "created_at"])
    permission_id = uuid5(NAMESPACE_URL, "maalenex:permission:platform.cargo.manage")
    role_permission_id = uuid5(NAMESPACE_URL, "maalenex:role-permission:platform_operations_manager:platform.cargo.manage")
    admin_role_permission_id = uuid5(NAMESPACE_URL, "maalenex:role-permission:synthetic_platform_admin:platform.cargo.manage")
    connection = op.get_bind()
    permission_exists = connection.execute(sa.text(
        "SELECT id FROM access_permissions WHERE code = 'platform.cargo.manage'"
    )).scalar_one_or_none()
    if permission_exists is None:
        connection.execute(sa.text(
            "INSERT INTO access_permissions (id, code, description) "
            "VALUES (:id, 'platform.cargo.manage', 'Create and manage cargo consignments')"
        ), {"id": permission_id})
    permission_id = permission_exists or permission_id
    for role_code, grant_id in (
        ("platform_operations_manager", role_permission_id),
        ("synthetic_platform_admin", admin_role_permission_id),
    ):
        role_id = connection.execute(sa.text(
            "SELECT id FROM access_roles WHERE code = :code"
        ), {"code": role_code}).scalar_one_or_none()
        if role_id is not None:
            connection.execute(sa.text(
                "INSERT INTO access_role_permissions (id, role_id, permission_id) "
                "SELECT :id, :role_id, :permission_id "
                "WHERE NOT EXISTS (SELECT 1 FROM access_role_permissions "
                "WHERE role_id = :role_id AND permission_id = :permission_id)"
            ), {"id": grant_id, "role_id": role_id, "permission_id": permission_id})



def downgrade() -> None:
    op.drop_index("ix_cargo_org_status_created", table_name="cargo_consignments")
    op.drop_index("ix_cargo_consignments_status", table_name="cargo_consignments")
    op.drop_table("cargo_consignments")
    op.execute("DELETE FROM access_role_permissions WHERE permission_id IN (SELECT id FROM access_permissions WHERE code = 'platform.cargo.manage')")
    op.execute("DELETE FROM access_permissions WHERE code = 'platform.cargo.manage'")
