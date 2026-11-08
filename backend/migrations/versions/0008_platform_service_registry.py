"""Shared platform service registry and geographic availability policy.

Revision ID: 0008_platform_service_registry
Revises: 0007_operator_invites_support
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_platform_service_registry"
down_revision = "0007_operator_invites_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "platform_services",
        sa.Column("code", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(300), nullable=False),
        sa.Column("rollout_status", sa.String(24), nullable=False, server_default="planned"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "rollout_status IN ('planned', 'synthetic_test', 'pilot', 'active', 'suspended')",
            name="ck_platform_services_rollout_status",
        ),
    )
    op.create_table(
        "service_areas",
        sa.Column("code", sa.String(48), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False, server_default="ET"),
        sa.Column("administrative_area", sa.String(120), nullable=False),
        sa.Column("area_type", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "service_area_availability",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("service_code", sa.String(32), sa.ForeignKey("platform_services.code", ondelete="CASCADE"), nullable=False),
        sa.Column("area_code", sa.String(48), sa.ForeignKey("service_areas.code", ondelete="RESTRICT"), nullable=False),
        sa.Column("availability_status", sa.String(24), nullable=False, server_default="planned"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("valid_from", sa.DateTime(timezone=True)),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("service_code", "area_code", name="uq_service_area_availability"),
        sa.CheckConstraint(
            "availability_status IN ('planned', 'synthetic_test', 'pilot', 'active', 'suspended')",
            name="ck_service_area_availability_status",
        ),
        sa.CheckConstraint("valid_until IS NULL OR valid_from IS NULL OR valid_until > valid_from", name="ck_service_area_validity_window"),
    )
    op.create_index("ix_service_area_availability_area_code", "service_area_availability", ["area_code"])
    op.create_index("ix_service_area_availability_service_code", "service_area_availability", ["service_code"])


def downgrade() -> None:
    op.drop_index("ix_service_area_availability_service_code", table_name="service_area_availability")
    op.drop_index("ix_service_area_availability_area_code", table_name="service_area_availability")
    op.drop_table("service_area_availability")
    op.drop_table("service_areas")
    op.drop_table("platform_services")
