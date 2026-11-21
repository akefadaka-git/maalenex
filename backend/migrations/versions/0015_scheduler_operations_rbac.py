"""Durable scheduler telemetry and role catalogue.

Revision ID: 0015_scheduler_operations_rbac
Revises: 0014_verified_booking_ownership
"""
from uuid import NAMESPACE_URL, uuid5

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0015_scheduler_operations_rbac"
down_revision = "0014_verified_booking_ownership"
branch_labels = None
depends_on = None


PERMISSIONS = {
    "platform.access.manage": "Manage staff access and role assignments",
    "platform.audit.read": "Read redacted audit events",
    "platform.operator.create": "Create candidate operator organizations",
    "platform.operator.review": "Review operator organizations",
    "platform.catalog.manage": "Manage catalog drafts",
    "platform.catalog.publish": "Publish approved catalog records",
    "platform.trip.approve": "Approve operator trips",
    "platform.trip.publish": "Publish approved trips",
    "platform.fare.approve": "Approve fare proposals",
    "platform.fare.publish": "Publish approved fares",
    "platform.fleet.review": "Review operator fleet and seat layouts",
    "platform.support.manage": "Manage support cases and passenger reports",
    "platform.scheduler.read": "Read scheduler health and execution history",
    "platform.scheduler.manage": "Manage scheduler operations controls",
    "platform.dashboard.read": "Read platform operations dashboard",
    "operator.fleet.manage": "Manage fleet within assigned operator organization",
    "operator.trip.manage": "Manage trips within assigned operator organization",
    "operator.fare.propose": "Propose fares within assigned operator organization",
    "operator.trip.manifest.read": "Read trip manifests within assigned operator organization",
    "organization.members.manage": "Manage members within assigned operator organization",
}

ROLE_GRANTS = {
    "synthetic_platform_admin": [code for code in PERMISSIONS if code.startswith("platform.")],
    "synthetic_operator_manager": [code for code in PERMISSIONS if code.startswith("operator.") or code == "organization.members.manage"],
    "platform_operations_manager": [
        "platform.dashboard.read", "platform.operator.create", "platform.operator.review",
        "platform.catalog.manage", "platform.catalog.publish", "platform.trip.approve",
        "platform.trip.publish", "platform.fare.approve", "platform.fare.publish",
        "platform.fleet.review", "platform.support.manage", "platform.scheduler.read",
    ],
    "platform_support_agent": ["platform.dashboard.read", "platform.support.manage"],
    "platform_safety_moderator": ["platform.dashboard.read", "platform.support.manage", "platform.audit.read"],
    "platform_auditor": ["platform.dashboard.read", "platform.audit.read", "platform.scheduler.read"],
    "platform_scheduler_operator": ["platform.dashboard.read", "platform.scheduler.read", "platform.scheduler.manage"],
    "platform_catalog_manager": ["platform.dashboard.read", "platform.catalog.manage", "platform.catalog.publish"],
    "platform_dispatch_manager": ["platform.dashboard.read", "platform.trip.approve", "platform.trip.publish"],
    "platform_fleet_reviewer": ["platform.dashboard.read", "platform.fleet.review"],
    "platform_fare_manager": ["platform.dashboard.read", "platform.fare.approve", "platform.fare.publish"],
    "operator_manager": ["operator.fleet.manage", "operator.trip.manage", "operator.fare.propose", "operator.trip.manifest.read", "organization.members.manage"],
    "operator_dispatcher": ["operator.trip.manage", "operator.trip.manifest.read"],
    "operator_fleet_manager": ["operator.fleet.manage"],
    "operator_fare_manager": ["operator.fare.propose"],
}

ROLE_DESCRIPTIONS = {
    "synthetic_platform_admin": "Synthetic-only local platform administrator; never provisioned automatically",
    "synthetic_operator_manager": "Legacy synthetic operator manager, organization-scoped",
    "platform_operations_manager": "Platform-wide operations coordination",
    "platform_support_agent": "Passenger and operator support case handling",
    "platform_safety_moderator": "Safety, fraud and complaint moderation",
    "platform_auditor": "Read-only audit and scheduler oversight",
    "platform_scheduler_operator": "Scheduler health and operations oversight",
    "platform_catalog_manager": "Location, terminal and route catalogue management",
    "platform_dispatch_manager": "Trip approval and publication",
    "platform_fleet_reviewer": "Fleet and seat-layout review",
    "platform_fare_manager": "Fare approval and publication",
    "operator_manager": "Organization-scoped operator manager",
    "operator_dispatcher": "Organization-scoped trip operations and manifest access",
    "operator_fleet_manager": "Organization-scoped fleet manager",
    "operator_fare_manager": "Organization-scoped fare proposer",
}


def _id(kind: str, code: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"maalenex:{kind}:{code}"))


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "scheduler_leases",
        sa.Column("lease_name", sa.String(80), primary_key=True),
        sa.Column("owner_id", sa.String(80), nullable=False),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True)),
        sa.Column("last_failure_at", sa.DateTime(timezone=True)),
        sa.Column("last_error_code", sa.String(80)),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("batches_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_duration_ms", sa.Integer()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_scheduler_leases_lease_expires_at", "scheduler_leases", ["lease_expires_at"])
    op.create_table(
        "scheduler_runs",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("job_name", sa.String(80), nullable=False),
        sa.Column("worker_id", sa.String(80), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("records_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.Integer()),
    )
    for column in ("job_name", "worker_id", "status", "started_at"):
        op.create_index(f"ix_scheduler_runs_{column}", "scheduler_runs", [column])

    roles = sa.table("access_roles",
        sa.column("id", uuid), sa.column("code", sa.String), sa.column("description", sa.String))
    permissions = sa.table("access_permissions",
        sa.column("id", uuid), sa.column("code", sa.String), sa.column("description", sa.String))
    role_permissions = sa.table("access_role_permissions",
        sa.column("id", uuid), sa.column("role_id", uuid), sa.column("permission_id", uuid))

    op.bulk_insert(permissions, [
        {"id": _id("permission", code), "code": code, "description": description}
        for code, description in PERMISSIONS.items()
    ])
    op.bulk_insert(roles, [
        {"id": _id("role", code), "code": code, "description": description}
        for code, description in ROLE_DESCRIPTIONS.items()
    ])
    op.bulk_insert(role_permissions, [
        {"id": _id("role-permission", f"{role}:{permission}"),
         "role_id": _id("role", role), "permission_id": _id("permission", permission)}
        for role, grants in ROLE_GRANTS.items() for permission in grants
    ])


def downgrade() -> None:
    role_codes = list(ROLE_DESCRIPTIONS)
    permission_codes = list(PERMISSIONS)
    role_ids = [_id("role", code) for code in role_codes]
    permission_ids = [_id("permission", code) for code in permission_codes]
    op.execute(sa.text("DELETE FROM access_role_permissions WHERE role_id = ANY(:role_ids) OR permission_id = ANY(:permission_ids)").bindparams(
        sa.bindparam("role_ids", value=role_ids, type_=postgresql.ARRAY(uuid_type := postgresql.UUID(as_uuid=True))),
        sa.bindparam("permission_ids", value=permission_ids, type_=postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
    ))
    op.execute(sa.text("DELETE FROM access_roles WHERE id = ANY(:role_ids)").bindparams(
        sa.bindparam("role_ids", value=role_ids, type_=postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
    ))
    op.execute(sa.text("DELETE FROM access_permissions WHERE id = ANY(:permission_ids)").bindparams(
        sa.bindparam("permission_ids", value=permission_ids, type_=postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
    ))
    op.drop_table("scheduler_runs")
    op.drop_index("ix_scheduler_leases_lease_expires_at", table_name="scheduler_leases")
    op.drop_table("scheduler_leases")
