"""Add governed lifecycle metadata for cargo delivery evidence.

Revision ID: 0022_cargo_evidence_lifecycle
Revises: 0021_carrier_ops_delivery
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0022_cargo_evidence_lifecycle"
down_revision = "0021_carrier_ops_delivery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "cargo_delivery_evidence",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("carrier_organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("dispatch_id", uuid, sa.ForeignKey("cargo_dispatches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("delivery_proof_id", uuid, sa.ForeignKey("cargo_delivery_proofs.id", ondelete="RESTRICT")),
        sa.Column("object_key", sa.String(512), nullable=False),
        sa.Column("content_type", sa.String(120)),
        sa.Column("content_length", sa.Integer()),
        sa.Column("upload_intent_created_at", sa.DateTime(timezone=True)),
        sa.Column("upload_intent_expires_at", sa.DateTime(timezone=True)),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("attached_at", sa.DateTime(timezone=True)),
        sa.Column("lifecycle_state", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("retention_policy_version", sa.String(40)),
        sa.Column("retention_started_at", sa.DateTime(timezone=True)),
        sa.Column("retention_expires_at", sa.DateTime(timezone=True)),
        sa.Column("classification_status", sa.String(24), nullable=False, server_default="unclassified"),
        sa.Column("retention_legal_review_reference", sa.String(160)),
        sa.Column("retention_classified_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("retention_classified_at", sa.DateTime(timezone=True)),
        sa.Column("retention_dpo_reviewed_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("retention_dpo_reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("storage_deleted_at", sa.DateTime(timezone=True)),
        sa.Column("deletion_failure_code", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("object_key", name="uq_cargo_delivery_evidence_object_key"),
    )
    op.create_index("ix_cargo_delivery_evidence_dispatch_state", "cargo_delivery_evidence", ["dispatch_id", "lifecycle_state"])
    op.create_index("ix_cargo_delivery_evidence_retention", "cargo_delivery_evidence", ["retention_expires_at", "lifecycle_state"])
    op.create_table(
        "cargo_delivery_evidence_holds",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("evidence_id", uuid, sa.ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("case_reference", sa.String(120), nullable=False),
        sa.Column("legal_basis", sa.String(500), nullable=False),
        sa.Column("issued_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dpo_reviewed_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("dpo_reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("review_due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("released_at", sa.DateTime(timezone=True)),
        sa.Column("release_note", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cargo_evidence_hold_evidence_active", "cargo_delivery_evidence_holds", ["evidence_id", "released_at"])
    op.create_table(
        "cargo_delivery_evidence_deletion_requests",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("evidence_id", uuid, sa.ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("requested_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("approved_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("executed_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="requested"),
        sa.Column("failure_code", sa.String(80)),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cargo_evidence_deletion_status", "cargo_delivery_evidence_deletion_requests", ["status", "created_at"])
    op.create_table(
        "cargo_delivery_evidence_access_grants",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("evidence_id", uuid, sa.ForeignKey("cargo_delivery_evidence.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("user_id", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("granted_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cargo_evidence_access_user_active", "cargo_delivery_evidence_access_grants", ["user_id", "revoked_at", "expires_at"])
    op.create_table(
        "cargo_delivery_evidence_retention_policies",
        sa.Column("version", sa.String(40), primary_key=True),
        sa.Column("retention_months", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="provisional"),
        sa.Column("legal_validation_reference", sa.String(160)),
        sa.Column("validated_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("dpo_reviewed_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("activated_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT")),
        sa.Column("activated_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    connection = op.get_bind()
    connection.execute(sa.text(
        "INSERT INTO cargo_delivery_evidence_retention_policies "
        "(version, retention_months, status) VALUES "
        "('owner-approved-provisional-24m-v1', 24, 'provisional')"
    ))
    # Preserve legacy proof rows without inventing historical upload/verification times.
    legacy_rows = connection.execute(sa.text(
        "SELECT p.id, p.dispatch_id, d.carrier_organization_id, p.evidence_reference "
        "FROM cargo_delivery_proofs p JOIN cargo_dispatches d ON d.id = p.dispatch_id"
    )).mappings().all()
    from uuid import NAMESPACE_URL, uuid5
    for row in legacy_rows:
        evidence_id = uuid5(NAMESPACE_URL, f"maalenex:cargo-delivery-evidence:legacy:{row['id']}")
        connection.execute(sa.text(
            "INSERT INTO cargo_delivery_evidence "
            "(id, carrier_organization_id, dispatch_id, delivery_proof_id, object_key, "
            "lifecycle_state, classification_status, created_at, updated_at) "
            "VALUES (:id, :carrier, :dispatch, :proof, :object_key, 'attached', 'unclassified', "
            "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (object_key) DO NOTHING"
        ), {"id": evidence_id, "carrier": row["carrier_organization_id"],
            "dispatch": row["dispatch_id"], "proof": row["id"], "object_key": row["evidence_reference"]})

    permissions = {
        "operator.cargo.delivery_proof.evidence.read": "Read private delivery evidence for own carrier dispatches",
        "platform.cargo.delivery_proof.evidence.read": "Read private delivery evidence for explicitly authorized cases",
        "platform.cargo.delivery_proof.evidence.hold.manage": "Initiate and release legal holds on cargo delivery evidence",
        "platform.cargo.delivery_proof.evidence.hold.review": "Provide independent DPO oversight of cargo evidence legal holds",
        "platform.cargo.delivery_proof.evidence.delete": "Approve and execute controlled cargo delivery evidence deletion",
        "platform.cargo.delivery_proof.evidence.access.manage": "Grant and revoke case-scoped cargo evidence access",
        "platform.cargo.delivery_proof.evidence.retention.manage": "Classify cargo evidence under legally validated retention rules",
        "platform.cargo.delivery_proof.evidence.retention.review": "Provide independent DPO review of cargo evidence retention classification",
    }
    permission_ids = {}
    for code, description in permissions.items():
        existing = connection.execute(sa.text("SELECT id FROM access_permissions WHERE code=:code"), {"code": code}).scalar_one_or_none()
        permission_id = existing or uuid5(NAMESPACE_URL, f"maalenex:permission:{code}")
        if existing is None:
            connection.execute(
                sa.text("INSERT INTO access_permissions (id,code,description) VALUES (:id,:code,:description)"),
                {"id": permission_id, "code": code, "description": description},
            )
        permission_ids[code] = permission_id

    roles = {
        "platform_evidence_reviewer": ("Platform reviewer with case-granted evidence read access", [
            "platform.cargo.delivery_proof.evidence.read",
        ]),
        "platform_evidence_custodian": ("Evidence custody and controlled deletion administration", [
            "platform.cargo.delivery_proof.evidence.access.manage",
            "platform.cargo.delivery_proof.evidence.delete",
        ]),
        "platform_legal_compliance_officer": ("Legal and compliance authority for evidence holds and classification", [
            "platform.cargo.delivery_proof.evidence.hold.manage",
            "platform.cargo.delivery_proof.evidence.retention.manage",
        ]),
        "platform_data_protection_officer": ("Independent DPO oversight for evidence holds and retention", [
            "platform.cargo.delivery_proof.evidence.hold.review",
            "platform.cargo.delivery_proof.evidence.retention.review",
        ]),
        "operator_manager": ("Organization-scoped operator manager", [
            "operator.cargo.delivery_proof.evidence.read",
        ]),
        "operator_dispatcher": ("Organization-scoped operator dispatcher", [
            "operator.cargo.delivery_proof.evidence.read",
        ]),
        "synthetic_operator_manager": ("Synthetic-only organization-scoped operator manager", [
            "operator.cargo.delivery_proof.evidence.read",
        ]),
    }
    for role_code, (description, codes) in roles.items():
        role_id = connection.execute(
            sa.text("SELECT id FROM access_roles WHERE code=:code"), {"code": role_code},
        ).scalar_one_or_none()
        if role_id is None:
            role_id = uuid5(NAMESPACE_URL, f"maalenex:role:{role_code}")
            connection.execute(
                sa.text("INSERT INTO access_roles (id,code,description) VALUES (:id,:code,:description)"),
                {"id": role_id, "code": role_code, "description": description},
            )
        for code in codes:
            exists = connection.execute(sa.text(
                "SELECT id FROM access_role_permissions WHERE role_id=:role AND permission_id=:permission"
            ), {"role": role_id, "permission": permission_ids[code]}).scalar_one_or_none()
            if exists is None:
                grant_id = uuid5(NAMESPACE_URL, f"maalenex:role-permission:{role_code}:{code}")
                connection.execute(sa.text(
                    "INSERT INTO access_role_permissions (id,role_id,permission_id) VALUES (:id,:role,:permission)"
                ), {"id": grant_id, "role": role_id, "permission": permission_ids[code]})


def downgrade() -> None:
    # Preserve evidence bytes and business/audit records. Schema downgrade is intentionally blocked
    # when lifecycle rows exist; operators must export/reconcile records before a controlled rollback.
    connection = op.get_bind()
    count = connection.execute(sa.text("SELECT count(*) FROM cargo_delivery_evidence")).scalar_one()
    if count:
        raise RuntimeError("Refusing to drop cargo evidence lifecycle records during downgrade.")
    op.drop_table("cargo_delivery_evidence_retention_policies")
    op.drop_index("ix_cargo_evidence_access_user_active", table_name="cargo_delivery_evidence_access_grants")
    op.drop_table("cargo_delivery_evidence_access_grants")
    op.drop_index("ix_cargo_evidence_deletion_status", table_name="cargo_delivery_evidence_deletion_requests")
    op.drop_table("cargo_delivery_evidence_deletion_requests")
    op.drop_index("ix_cargo_evidence_hold_evidence_active", table_name="cargo_delivery_evidence_holds")
    op.drop_table("cargo_delivery_evidence_holds")
    op.drop_index("ix_cargo_delivery_evidence_retention", table_name="cargo_delivery_evidence")
    op.drop_index("ix_cargo_delivery_evidence_dispatch_state", table_name="cargo_delivery_evidence")
    op.drop_table("cargo_delivery_evidence")
