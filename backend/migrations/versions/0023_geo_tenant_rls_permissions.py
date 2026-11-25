"""Enforce tenant-scoped RLS for canonical geo data and seed geo permissions.

Revision ID: 0023_geo_tenant_rls_permissions
Revises: 0022_geo_publication_views

Tenant context is transaction-local: app.current_organization_id. Missing or
malformed context resolves to NULL and all tenant policies fail closed.
"""
from uuid import NAMESPACE_URL, uuid5

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0023_geo_tenant_rls_permissions"
down_revision = "0022_geo_publication_views"
branch_labels = None
depends_on = None

PERMISSIONS = {
    "platform.geo.internal.read": "Read tenant-scoped internal geography and tracking",
    "platform.tracking.read": "Read vehicle tracking within an authorized organization",
    "platform.tracking.manage": "Manage tracking devices and assignments within an authorized organization",
    "platform.geo.manage": "Manage geographic records and provenance",
    "platform.geo.publish": "Publish approved geographic records",
    "platform.geo.audit.read": "Read geographic publication and privileged-access audit records",
}
ROLE_GRANTS = {
    "platform_operations_manager": [
        "platform.geo.internal.read", "platform.tracking.read",
    ],
    "platform_dispatch_manager": [
        "platform.geo.internal.read", "platform.tracking.read", "platform.tracking.manage",
    ],
    "platform_catalog_manager": [
        "platform.geo.manage", "platform.geo.publish",
    ],
    "platform_auditor": ["platform.geo.audit.read"],
    "operator_manager": ["platform.tracking.read", "platform.tracking.manage"],
    "operator_dispatcher": ["platform.tracking.read"],
    "operator_fleet_manager": ["platform.tracking.read", "platform.tracking.manage"],
}


def _id(kind: str, code: str):
    return uuid5(NAMESPACE_URL, f"maalenex:{kind}:{code}")


def upgrade() -> None:
    op.execute("""
CREATE OR REPLACE FUNCTION geo.current_organization_id()
RETURNS uuid
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = pg_catalog
AS $geo_tenant$
BEGIN
    RETURN NULLIF(pg_catalog.current_setting('app.current_organization_id', true), '')::uuid;
EXCEPTION WHEN invalid_text_representation THEN
    RETURN NULL;
END;
$geo_tenant$
""")

    # Direct tenant key policies. Nullable/global catalog rows deliberately
    # remain invisible to tenant-scoped application queries.
    tenant_tables = (
        "data_sources", "locations", "terminals", "routes", "route_stops",
        "boundaries", "devices", "device_vehicle_assignments",
        "vehicle_positions", "publications",
    )
    for table in tenant_tables:
        policy = f"p_{table}_tenant_isolation"
        op.execute(f"ALTER TABLE geo.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
CREATE POLICY {policy} ON geo.{table}
USING (organization_id = geo.current_organization_id())
WITH CHECK (organization_id = geo.current_organization_id())
""")

    # Restrictive relationship guards prevent cross-tenant foreign-key
    # references even when a caller knows another tenant's UUID. PostgreSQL
    # combines these with the permissive tenant-key policies using AND.
    relationship_guards = {
        "locations": """
EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = locations.source_id
      AND ds.organization_id = geo.current_organization_id()
)""",
        "terminals": """
EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = terminals.source_id
      AND ds.organization_id = geo.current_organization_id()
)
AND EXISTS (
    SELECT 1 FROM geo.locations l
    WHERE l.id = terminals.location_id
      AND l.organization_id = geo.current_organization_id()
)""",
        "routes": """
EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = routes.source_id
      AND ds.organization_id = geo.current_organization_id()
)
AND EXISTS (
    SELECT 1 FROM geo.locations l
    WHERE l.id = routes.origin_location_id
      AND l.organization_id = geo.current_organization_id()
)
AND EXISTS (
    SELECT 1 FROM geo.locations l
    WHERE l.id = routes.destination_location_id
      AND l.organization_id = geo.current_organization_id()
)""",
        "route_stops": """
EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = route_stops.source_id
      AND ds.organization_id = geo.current_organization_id()
)
AND EXISTS (
    SELECT 1 FROM geo.routes r
    WHERE r.id = route_stops.route_id
      AND r.organization_id = geo.current_organization_id()
)
AND EXISTS (
    SELECT 1 FROM geo.locations l
    WHERE l.id = route_stops.location_id
      AND l.organization_id = geo.current_organization_id()
)
AND (
    route_stops.terminal_id IS NULL
    OR EXISTS (
        SELECT 1 FROM geo.terminals t
        WHERE t.id = route_stops.terminal_id
          AND t.organization_id = geo.current_organization_id()
    )
)""",
        "boundaries": """
EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = boundaries.source_id
      AND ds.organization_id = geo.current_organization_id()
)""",
        "publications": """
EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = publications.source_id
      AND ds.organization_id = geo.current_organization_id()
)""",
    }
    for table, expression in relationship_guards.items():
        policy = f"p_{table}_tenant_relationship_guard"
        op.execute(f"""
CREATE POLICY {policy} ON geo.{table}
AS RESTRICTIVE
USING ({expression})
WITH CHECK ({expression})
""")

    # Route versions inherit tenant ownership through their parent route.
    op.execute("ALTER TABLE geo.route_versions ENABLE ROW LEVEL SECURITY")
    op.execute("""
CREATE POLICY p_route_versions_tenant_isolation ON geo.route_versions
USING (
    EXISTS (
        SELECT 1 FROM geo.routes r
        WHERE r.id = route_versions.route_id
          AND r.organization_id = geo.current_organization_id()
    )
    AND EXISTS (
        SELECT 1 FROM geo.data_sources ds
        WHERE ds.id = route_versions.source_id
          AND ds.organization_id = geo.current_organization_id()
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM geo.routes r
        WHERE r.id = route_versions.route_id
          AND r.organization_id = geo.current_organization_id()
    )
    AND EXISTS (
        SELECT 1 FROM geo.data_sources ds
        WHERE ds.id = route_versions.source_id
          AND ds.organization_id = geo.current_organization_id()
    )
)
""")

    # Road records inherit ownership from their provenance source. No tenant
    # context means the source lookup returns no visible row.
    op.execute("ALTER TABLE geo.roads ENABLE ROW LEVEL SECURITY")
    op.execute("""
CREATE POLICY p_roads_tenant_isolation ON geo.roads
USING (EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = roads.source_id
      AND ds.organization_id = geo.current_organization_id()
))
WITH CHECK (EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = roads.source_id
      AND ds.organization_id = geo.current_organization_id()
))
""")

    # Quarantine records have no independently trusted tenant key. Deny all
    # non-owner access until a separately reconciled tenant attribution exists.
    op.execute("ALTER TABLE geo.legacy_tracking_quarantine ENABLE ROW LEVEL SECURITY")

    # Append-only, tenant-scoped audit trail for protected geo operations.
    op.execute("CREATE SCHEMA IF NOT EXISTS geo_audit")
    op.execute("""
CREATE TABLE geo_audit.events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE RESTRICT,
    actor_user_id uuid REFERENCES public.staff_users(id) ON DELETE SET NULL,
    permission_code varchar(100) NOT NULL,
    action varchar(32) NOT NULL,
    outcome varchar(24) NOT NULL DEFAULT 'authorized',
    resource_type varchar(80),
    resource_id varchar(128),
    request_id varchar(80),
    occurred_at timestamptz NOT NULL DEFAULT now(),
    metadata_redacted jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT ck_geo_audit_action CHECK (
        action IN ('read', 'manage', 'publish', 'audit_read')
    ),
    CONSTRAINT ck_geo_audit_outcome CHECK (
        outcome IN ('authorized', 'denied', 'failed')
    )
)
""")
    op.execute("""
CREATE INDEX ix_geo_audit_events_org_time
ON geo_audit.events(organization_id, occurred_at DESC)
""")
    op.execute("""
CREATE INDEX ix_geo_audit_events_actor_time
ON geo_audit.events(actor_user_id, occurred_at DESC)
""")
    op.execute("ALTER TABLE geo_audit.events ENABLE ROW LEVEL SECURITY")
    op.execute("""
CREATE POLICY p_geo_audit_events_tenant_isolation ON geo_audit.events
USING (organization_id = geo.current_organization_id())
WITH CHECK (organization_id = geo.current_organization_id())
""")
    op.execute("""
CREATE OR REPLACE FUNCTION geo_audit.reject_event_mutation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $geo_audit$
BEGIN
    RAISE EXCEPTION 'geo_audit.events are append-only';
END;
$geo_audit$
""")
    op.execute("""
CREATE TRIGGER geo_audit_events_append_only
BEFORE UPDATE OR DELETE ON geo_audit.events
FOR EACH ROW EXECUTE FUNCTION geo_audit.reject_event_mutation()
""")
    op.execute("""
CREATE OR REPLACE FUNCTION geo_audit.record_access_event(
    p_actor_user_id uuid,
    p_permission_code text,
    p_action text
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, geo_audit
AS $geo_audit_record$
DECLARE
    v_organization_id uuid;
BEGIN
    v_organization_id := geo.current_organization_id();
    IF v_organization_id IS NULL THEN
        RAISE EXCEPTION 'geo audit requires an authorized tenant context';
    END IF;
    INSERT INTO geo_audit.events (
        organization_id, actor_user_id, permission_code, action, outcome
    ) VALUES (
        v_organization_id, p_actor_user_id, p_permission_code, p_action, 'authorized'
    );
END;
$geo_audit_record$
""")
    op.execute("""
REVOKE ALL ON geo_audit.events FROM PUBLIC
""")
    op.execute("""
REVOKE ALL ON FUNCTION geo_audit.record_access_event(uuid, text, text) FROM PUBLIC
""")

    op.execute("""
DO $geo_roles$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'maalenex_geo_tenant_manager') THEN
        CREATE ROLE maalenex_geo_tenant_manager NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'maalenex_geo_catalog_manager') THEN
        CREATE ROLE maalenex_geo_catalog_manager NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END;
$geo_roles$
""")
    op.execute("""
ALTER ROLE maalenex_geo_internal_reader
    NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT
""")
    op.execute("""
ALTER ROLE maalenex_geo_public_reader
    NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT
""")
    op.execute("""
ALTER ROLE maalenex_geo_public_reader
    NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT
""")
    op.execute("""
ALTER ROLE maalenex_geo_tenant_manager
    NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT
""")
    op.execute("""
ALTER ROLE maalenex_geo_catalog_manager
    NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT
""")

    op.execute("""
DO $geo_audit_role$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'maalenex_geo_audit_reader') THEN
        CREATE ROLE maalenex_geo_audit_reader NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END;
$geo_audit_role$
""")
    op.execute("""
ALTER ROLE maalenex_geo_audit_reader
    NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT
""")

    # The internal reader receives only SELECT on the position relation/view.
    # Invoker-security view means its SELECT is filtered by the same RLS policy.
    op.execute("GRANT USAGE ON SCHEMA geo, geo_internal TO maalenex_geo_internal_reader")
    op.execute("GRANT SELECT ON geo.vehicle_positions TO maalenex_geo_internal_reader")
    op.execute("GRANT SELECT ON geo_internal.vehicle_positions TO maalenex_geo_internal_reader")
    op.execute("GRANT EXECUTE ON FUNCTION geo.current_organization_id() TO maalenex_geo_internal_reader")

    op.execute("""
GRANT USAGE ON SCHEMA geo TO maalenex_geo_tenant_manager
""")
    op.execute("""
GRANT SELECT ON geo.vehicle_positions TO maalenex_geo_tenant_manager
""")
    op.execute("""
GRANT SELECT, INSERT, UPDATE ON
    geo.devices, geo.device_vehicle_assignments
TO maalenex_geo_tenant_manager
""")
    op.execute("""
GRANT USAGE ON SCHEMA geo TO maalenex_geo_catalog_manager
""")
    op.execute("""
GRANT SELECT, INSERT, UPDATE ON
    geo.data_sources, geo.locations, geo.terminals, geo.routes,
    geo.route_stops, geo.route_versions, geo.boundaries, geo.roads,
    geo.publications
TO maalenex_geo_catalog_manager
""")
    op.execute("""
GRANT EXECUTE ON FUNCTION geo.current_organization_id()
TO maalenex_geo_tenant_manager, maalenex_geo_catalog_manager
""")

    op.execute("""
GRANT USAGE ON SCHEMA geo_audit
TO maalenex_geo_internal_reader, maalenex_geo_tenant_manager,
   maalenex_geo_catalog_manager, maalenex_geo_audit_reader
""")
    op.execute("""
GRANT SELECT ON geo_audit.events TO maalenex_geo_audit_reader
""")
    op.execute("""
GRANT EXECUTE ON FUNCTION geo_audit.record_access_event(uuid, text, text)
TO maalenex_geo_internal_reader, maalenex_geo_tenant_manager,
   maalenex_geo_catalog_manager, maalenex_geo_audit_reader
""")

    # Add stable permission identifiers and least-privilege role mappings.
    uuid = postgresql.UUID(as_uuid=True)
    permissions = sa.table(
        "access_permissions",
        sa.column("id", uuid), sa.column("code", sa.String),
        sa.column("description", sa.String),
    )
    roles = sa.table("access_roles", sa.column("id", uuid), sa.column("code", sa.String))
    links = sa.table(
        "access_role_permissions",
        sa.column("id", uuid), sa.column("role_id", uuid), sa.column("permission_id", uuid),
    )
    connection = op.get_bind()
    permission_ids = {}
    for code, description in PERMISSIONS.items():
        existing = connection.execute(
            sa.select(permissions.c.id).where(permissions.c.code == code)
        ).scalar_one_or_none()
        permission_id = existing or _id("permission", code)
        if existing is None:
            connection.execute(permissions.insert().values(
                id=permission_id, code=code, description=description,
            ))
        permission_ids[code] = permission_id

    for role_code, grants in ROLE_GRANTS.items():
        role_id = connection.execute(
            sa.select(roles.c.id).where(roles.c.code == role_code)
        ).scalar_one_or_none()
        if role_id is None:
            raise RuntimeError(f"Required A3.5 RBAC role is missing: {role_code}")
        for permission_code in grants:
            permission_id = permission_ids[permission_code]
            existing = connection.execute(sa.select(links.c.id).where(
                links.c.role_id == role_id,
                links.c.permission_id == permission_id,
            )).scalar_one_or_none()
            if existing is None:
                connection.execute(links.insert().values(
                    id=_id("role-permission", f"{role_code}:{permission_code}"),
                    role_id=role_id, permission_id=permission_id,
                ))


def downgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    permissions = sa.table(
        "access_permissions", sa.column("id", uuid), sa.column("code", sa.String),
    )
    links = sa.table(
        "access_role_permissions",
        sa.column("id", uuid), sa.column("role_id", uuid), sa.column("permission_id", uuid),
    )
    connection = op.get_bind()
    permission_ids = [_id("permission", code) for code in PERMISSIONS]
    link_ids = [
        _id("role-permission", f"{role}:{permission}")
        for role, grants in ROLE_GRANTS.items() for permission in grants
    ]
    connection.execute(links.delete().where(links.c.id.in_(link_ids)))
    connection.execute(permissions.delete().where(permissions.c.id.in_(permission_ids)))

    policy_tables = {
        "data_sources": "p_data_sources_tenant_isolation",
        "locations": "p_locations_tenant_isolation",
        "terminals": "p_terminals_tenant_isolation",
        "routes": "p_routes_tenant_isolation",
        "route_stops": "p_route_stops_tenant_isolation",
        "boundaries": "p_boundaries_tenant_isolation",
        "devices": "p_devices_tenant_isolation",
        "device_vehicle_assignments": "p_device_vehicle_assignments_tenant_isolation",
        "vehicle_positions": "p_vehicle_positions_tenant_isolation",
        "publications": "p_publications_tenant_isolation",
        "route_versions": "p_route_versions_tenant_isolation",
        "roads": "p_roads_tenant_isolation",
    }
    for table, policy in policy_tables.items():
        op.execute(f"DROP POLICY IF EXISTS {policy} ON geo.{table}")
    for table in ("locations", "terminals", "routes", "route_stops", "boundaries", "publications"):
        op.execute(
            f"DROP POLICY IF EXISTS p_{table}_tenant_relationship_guard ON geo.{table}"
        )
    op.execute(
        "ALTER TABLE geo.legacy_tracking_quarantine DISABLE ROW LEVEL SECURITY"
    )
    op.execute("DROP POLICY IF EXISTS p_geo_audit_events_tenant_isolation ON geo_audit.events")
    op.execute("ALTER TABLE geo_audit.events DISABLE ROW LEVEL SECURITY")
    op.execute("DROP TRIGGER IF EXISTS geo_audit_events_append_only ON geo_audit.events")
    op.execute("DROP FUNCTION IF EXISTS geo_audit.record_access_event(uuid, text, text)")
    op.execute("DROP FUNCTION IF EXISTS geo_audit.reject_event_mutation()")
    op.execute("DROP TABLE IF EXISTS geo_audit.events")
    op.execute("DROP SCHEMA IF EXISTS geo_audit")
    for table in policy_tables:
        op.execute(f"ALTER TABLE geo.{table} DISABLE ROW LEVEL SECURITY")
    op.execute("REVOKE EXECUTE ON FUNCTION geo.current_organization_id() FROM maalenex_geo_internal_reader, maalenex_geo_tenant_manager, maalenex_geo_catalog_manager")
    op.execute("REVOKE EXECUTE ON FUNCTION geo_audit.record_access_event(uuid, text, text) FROM maalenex_geo_internal_reader, maalenex_geo_tenant_manager, maalenex_geo_catalog_manager, maalenex_geo_audit_reader")
    op.execute("REVOKE ALL ON geo_audit.events FROM maalenex_geo_audit_reader")
    op.execute("REVOKE USAGE ON SCHEMA geo_audit FROM maalenex_geo_internal_reader, maalenex_geo_tenant_manager, maalenex_geo_catalog_manager, maalenex_geo_audit_reader")
    op.execute("REVOKE ALL ON geo.vehicle_positions FROM maalenex_geo_internal_reader")
    op.execute("REVOKE ALL ON geo_internal.vehicle_positions FROM maalenex_geo_internal_reader")
    op.execute("REVOKE USAGE ON SCHEMA geo, geo_internal FROM maalenex_geo_internal_reader")
    op.execute("REVOKE ALL ON geo.vehicle_positions, geo.devices, geo.device_vehicle_assignments FROM maalenex_geo_tenant_manager")
    op.execute("REVOKE ALL ON geo.data_sources, geo.locations, geo.terminals, geo.routes, geo.route_stops, geo.route_versions, geo.boundaries, geo.roads, geo.publications FROM maalenex_geo_catalog_manager")
    op.execute("REVOKE USAGE ON SCHEMA geo FROM maalenex_geo_tenant_manager, maalenex_geo_catalog_manager")
    op.execute("DROP FUNCTION IF EXISTS geo.current_organization_id()")
