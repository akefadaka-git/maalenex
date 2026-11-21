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
    "platform_access_manager": ["platform.access.manage", "platform.dashboard.read", "platform.audit.read"],
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
    "platform_access_manager": "Platform access and role assignment administrator",
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
    connection = op.get_bind()
    role_ids = {}
    permission_ids = {}
    for code, description in PERMISSIONS.items():
        existing = connection.execute(sa.select(permissions.c.id).where(permissions.c.code == code)).scalar_one_or_none()
        permission_id = existing or _id("permission", code)
        if existing is None:
            connection.execute(permissions.insert().values(id=permission_id, code=code, description=description))
        permission_ids[code] = permission_id
    for code, description in ROLE_DESCRIPTIONS.items():
        existing = connection.execute(sa.select(roles.c.id).where(roles.c.code == code)).scalar_one_or_none()
        role_id = existing or _id("role", code)
        if existing is None:
            connection.execute(roles.insert().values(id=role_id, code=code, description=description))
        role_ids[code] = role_id
    for role_code, grants in ROLE_GRANTS.items():
        for permission_code in grants:
            role_id = role_ids[role_code]
            permission_id = permission_ids[permission_code]
            exists = connection.execute(sa.select(role_permissions.c.id).where(
                role_permissions.c.role_id == role_id,
                role_permissions.c.permission_id == permission_id,
            )).scalar_one_or_none()
            if exists is None:
                connection.execute(role_permissions.insert().values(
                    id=_id("role-permission", f"{role_code}:{permission_code}"),
                    role_id=role_id, permission_id=permission_id,
                ))


def downgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    role_codes = list(ROLE_DESCRIPTIONS)
    permission_codes = list(PERMISSIONS)
    role_ids = [_id("role", code) for code in role_codes]
    permission_ids = [_id("permission", code) for code in permission_codes]
    role_permissions = sa.table(
        "access_role_permissions", sa.column("id", uuid),
    )
    roles = sa.table("access_roles", sa.column("id", uuid))
    permissions = sa.table("access_permissions", sa.column("id", uuid))
    connection = op.get_bind()
    connection.execute(sa.delete(role_permissions).where(
        role_permissions.c.id.in_([
            _id("role-permission", f"{role}:{permission}")
            for role, grants in ROLE_GRANTS.items() for permission in grants
        ])
    ))
    connection.execute(sa.delete(roles).where(roles.c.id.in_(role_ids)))
    connection.execute(sa.delete(permissions).where(permissions.c.id.in_(permission_ids)))
    op.drop_table("scheduler_runs")
    op.drop_index("ix_scheduler_leases_lease_expires_at", table_name="scheduler_leases")
    op.drop_table("scheduler_leases")
