# ruff: noqa: I001
"""Add dispatch assignments and append-only cargo tracking events.

Revision ID: 0020_cargo_dispatch_tracking
Revises: 0019_cargo_consignments
"""
from uuid import NAMESPACE_URL, uuid5

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0020_cargo_dispatch_tracking"
down_revision = "0019_cargo_consignments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "cargo_dispatches",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("consignment_id", uuid, sa.ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("dispatch_reference", sa.String(80), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("carrier_organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vehicle_id", uuid, sa.ForeignKey("vehicles.id", ondelete="RESTRICT")),
        sa.Column("status", sa.String(24), nullable=False, server_default="offered"),
        sa.Column("offered_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("responded_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("consignment_id", "dispatch_reference", name="uq_cargo_dispatch_reference"),
        sa.UniqueConstraint("consignment_id", "idempotency_key", name="uq_cargo_dispatch_idempotency"),
        sa.CheckConstraint("status IN ('offered','accepted','rejected','picked_up','in_transit','delivered','failed','cancelled')", name="ck_cargo_dispatch_status"),
    )
    op.create_index("ix_cargo_dispatch_carrier_status", "cargo_dispatches", ["carrier_organization_id", "status"])
    op.create_table(
        "cargo_tracking_events",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("dispatch_id", uuid, sa.ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("consignment_id", uuid, sa.ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("description", sa.String(300)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("recorded_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("dispatch_id", "idempotency_key", name="uq_cargo_tracking_idempotency"),
        sa.UniqueConstraint("dispatch_id", "sequence_number", name="uq_cargo_tracking_sequence"),
        sa.CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="ck_cargo_tracking_latitude"),
        sa.CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="ck_cargo_tracking_longitude"),
    )
    op.create_index("ix_cargo_tracking_consignment_occurred", "cargo_tracking_events", ["consignment_id", "occurred_at"])
    connection = op.get_bind()
    permissions = {
        "platform.dispatch.manage": "Offer and manage cargo dispatch assignments",
        "operator.cargo.dispatch.manage": "Accept and update cargo dispatches for assigned operator organization",
    }
    ids = {}
    for code, description in permissions.items():
        existing = connection.execute(sa.text("SELECT id FROM access_permissions WHERE code = :code"), {"code": code}).scalar_one_or_none()
        permission_id = existing or uuid5(NAMESPACE_URL, f"maalenex:permission:{code}")
        if existing is None:
            connection.execute(sa.text("INSERT INTO access_permissions (id, code, description) VALUES (:id, :code, :description)"),
                               {"id": permission_id, "code": code, "description": description})
        ids[code] = permission_id
    grants = {
        "platform_dispatch_manager": "platform.dispatch.manage",
        "platform_operations_manager": "platform.dispatch.manage",
        "synthetic_platform_admin": "platform.dispatch.manage",
        "operator_dispatcher": "operator.cargo.dispatch.manage",
        "operator_manager": "operator.cargo.dispatch.manage",
        "synthetic_operator_manager": "operator.cargo.dispatch.manage",
    }
    for role_code, permission_code in grants.items():
        role_id = connection.execute(sa.text("SELECT id FROM access_roles WHERE code = :code"), {"code": role_code}).scalar_one_or_none()
        if role_id is None:
            continue
        permission_id = ids[permission_code]
        exists = connection.execute(sa.text("SELECT id FROM access_role_permissions WHERE role_id = :role_id AND permission_id = :permission_id"),
                                    {"role_id": role_id, "permission_id": permission_id}).scalar_one_or_none()
        if exists is None:
            grant_id = uuid5(NAMESPACE_URL, f"maalenex:role-permission:{role_code}:{permission_code}")
            connection.execute(sa.text("INSERT INTO access_role_permissions (id, role_id, permission_id) VALUES (:id, :role_id, :permission_id)"),
                               {"id": grant_id, "role_id": role_id, "permission_id": permission_id})


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM access_role_permissions WHERE permission_id IN (SELECT id FROM access_permissions WHERE code IN ('platform.dispatch.manage','operator.cargo.dispatch.manage'))"))
    connection.execute(sa.text("DELETE FROM access_permissions WHERE code IN ('platform.dispatch.manage','operator.cargo.dispatch.manage')"))
    op.drop_index("ix_cargo_tracking_consignment_occurred", table_name="cargo_tracking_events")
    op.drop_table("cargo_tracking_events")
    op.drop_index("ix_cargo_dispatch_carrier_status", table_name="cargo_dispatches")
    op.drop_table("cargo_dispatches")
