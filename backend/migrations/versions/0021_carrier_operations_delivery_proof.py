# ruff: noqa: I001
"""Add carrier operations, delivery proof and exception resolution.

Revision ID: 0021_carrier_ops_delivery
Revises: 0020_cargo_dispatch_tracking
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0021_carrier_ops_delivery"
down_revision = "0020_cargo_dispatch_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "carrier_operational_profiles",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("operational_status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("service_area", sa.String(240)),
        sa.Column("operating_notes", sa.String(500)),
        sa.Column("updated_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("organization_id", name="uq_carrier_operation_org"),
        sa.CheckConstraint("operational_status IN ('pending','active','restricted','suspended')", name="ck_carrier_operation_status"),
    )
    op.create_index("ix_carrier_operation_status", "carrier_operational_profiles", ["operational_status"])
    op.create_table(
        "cargo_delivery_proofs",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("dispatch_id", uuid, sa.ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("consignment_id", uuid, sa.ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("received_by_name", sa.String(160), nullable=False),
        sa.Column("evidence_reference", sa.String(255), nullable=False),
        sa.Column("delivery_notes", sa.String(500)),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="submitted"),
        sa.Column("submitted_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reviewed_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("review_reason", sa.String(500)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("dispatch_id", name="uq_cargo_delivery_proof_dispatch"),
        sa.UniqueConstraint("idempotency_key", name="uq_cargo_delivery_proof_idempotency"),
        sa.CheckConstraint("status IN ('submitted','accepted','rejected')", name="ck_cargo_delivery_proof_status"),
    )
    op.create_table(
        "cargo_exception_cases",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("dispatch_id", uuid, sa.ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("consignment_id", uuid, sa.ForeignKey("cargo_consignments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("carrier_organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("exception_code", sa.String(48), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="open"),
        sa.Column("resolution_code", sa.String(48)),
        sa.Column("resolution_notes", sa.String(500)),
        sa.Column("reported_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("resolved_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("dispatch_id", "idempotency_key", name="uq_cargo_exception_idempotency"),
        sa.CheckConstraint("status IN ('open','investigating','resolved','closed')", name="ck_cargo_exception_status"),
    )
    op.create_index("ix_cargo_exception_carrier_status", "cargo_exception_cases", ["carrier_organization_id", "status"])
    connection = op.get_bind()
    permissions = {
        "platform.carrier.operations.manage": "Manage carrier operational eligibility",
        "platform.cargo.delivery_proof.review": "Review cargo delivery proof",
        "operator.cargo.delivery_proof.submit": "Submit delivery proof for assigned carrier dispatches",
        "operator.cargo.exception.manage": "Report and manage cargo delivery exceptions for assigned carrier dispatches",
    }
    from uuid import NAMESPACE_URL, uuid5
    permission_ids = {}
    for code, description in permissions.items():
        existing = connection.execute(sa.text("SELECT id FROM access_permissions WHERE code=:code"), {"code": code}).scalar_one_or_none()
        permission_id = existing or uuid5(NAMESPACE_URL, f"maalenex:permission:{code}")
        if existing is None:
            connection.execute(sa.text("INSERT INTO access_permissions (id,code,description) VALUES (:id,:code,:description)"),
                               {"id": permission_id, "code": code, "description": description})
        permission_ids[code] = permission_id
    grants = {
        "platform_operations_manager": ["platform.carrier.operations.manage", "platform.cargo.delivery_proof.review"],
        "synthetic_platform_admin": list(permissions),
        "operator_manager": ["operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage"],
        "operator_dispatcher": ["operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage"],
        "synthetic_operator_manager": ["operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage"],
    }
    for role_code, codes in grants.items():
        role_id = connection.execute(sa.text("SELECT id FROM access_roles WHERE code=:code"), {"code": role_code}).scalar_one_or_none()
        if role_id is None:
            continue
        for code in codes:
            permission_id = permission_ids[code]
            exists = connection.execute(sa.text("SELECT id FROM access_role_permissions WHERE role_id=:role AND permission_id=:permission"),
                                        {"role": role_id, "permission": permission_id}).scalar_one_or_none()
            if exists is None:
                grant_id = uuid5(NAMESPACE_URL, f"maalenex:role-permission:{role_code}:{code}")
                connection.execute(sa.text("INSERT INTO access_role_permissions (id,role_id,permission_id) VALUES (:id,:role,:permission)"),
                                   {"id": grant_id, "role": role_id, "permission": permission_id})


def downgrade() -> None:
    from uuid import NAMESPACE_URL, uuid5
    connection = op.get_bind()
    grants = {
        "platform_operations_manager": ["platform.carrier.operations.manage", "platform.cargo.delivery_proof.review"],
        "synthetic_platform_admin": [
            "platform.carrier.operations.manage", "platform.cargo.delivery_proof.review",
            "operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage",
        ],
        "operator_manager": ["operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage"],
        "operator_dispatcher": ["operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage"],
        "synthetic_operator_manager": ["operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage"],
    }
    for role_code, codes in grants.items():
        role_id = connection.execute(sa.text("SELECT id FROM access_roles WHERE code=:code"), {"code": role_code}).scalar_one_or_none()
        if role_id is None:
            continue
        for code in codes:
            grant_id = uuid5(NAMESPACE_URL, f"maalenex:role-permission:{role_code}:{code}")
            connection.execute(sa.text("DELETE FROM access_role_permissions WHERE id=:id"), {"id": grant_id})
    for code in (
        "platform.carrier.operations.manage", "platform.cargo.delivery_proof.review",
        "operator.cargo.delivery_proof.submit", "operator.cargo.exception.manage",
    ):
        generated_id = uuid5(NAMESPACE_URL, f"maalenex:permission:{code}")
        connection.execute(sa.text("DELETE FROM access_permissions WHERE id=:id"), {"id": generated_id})
    op.drop_index("ix_cargo_exception_carrier_status", table_name="cargo_exception_cases")
    op.drop_table("cargo_exception_cases")
    op.drop_table("cargo_delivery_proofs")
    op.drop_index("ix_carrier_operation_status", table_name="carrier_operational_profiles")
    op.drop_table("carrier_operational_profiles")
