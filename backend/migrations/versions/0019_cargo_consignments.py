"""Add organization-scoped cargo consignment lifecycle.

Revision ID: 0019_cargo_consignments
Revises: 0018_koybe_boarding_point
"""
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
    op.execute("""
        INSERT INTO access_permissions (id, code, description)
        SELECT gen_random_uuid(), 'platform.cargo.manage', 'Create and manage cargo consignments'
        WHERE NOT EXISTS (SELECT 1 FROM access_permissions WHERE code = 'platform.cargo.manage')
    """)
    op.execute("""
        INSERT INTO access_role_permissions (id, role_id, permission_id)
        SELECT gen_random_uuid(), rp.role_id, p.id
        FROM access_role_permissions rp
        JOIN access_permissions existing ON existing.id = rp.permission_id AND existing.code = 'platform.dashboard.read'
        JOIN access_permissions p ON p.code = 'platform.cargo.manage'
        WHERE NOT EXISTS (
            SELECT 1 FROM access_role_permissions current
            WHERE current.role_id = rp.role_id AND current.permission_id = p.id
        )
    """)


def downgrade() -> None:
    op.drop_index("ix_cargo_org_status_created", table_name="cargo_consignments")
    op.drop_index("ix_cargo_consignments_status", table_name="cargo_consignments")
    op.drop_table("cargo_consignments")
    op.execute("DELETE FROM access_role_permissions WHERE permission_id IN (SELECT id FROM access_permissions WHERE code = 'platform.cargo.manage')")
    op.execute("DELETE FROM access_permissions WHERE code = 'platform.cargo.manage'")
