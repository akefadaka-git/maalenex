"""Create sanitized public spatial views and non-login reader roles.

Revision ID: 0022_geo_publication_views
Revises: 0021_mitp_tracking_to_geo

Public views expose only explicitly published, source-verified geography.
Internal tracking view is invoker-security and intentionally receives no
service-role grants until A3.5 tenant RLS and authorization are implemented.
"""
from alembic import op

revision = "0022_geo_publication_views"
down_revision = "0021_mitp_tracking_to_geo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS geo_public")
    op.execute("CREATE SCHEMA IF NOT EXISTS geo_internal")

    # Roles are NOLOGIN capability groups. Deployment-specific login/service
    # principals may be granted membership after their credentials are managed
    # outside migrations. Never grant these roles to PUBLIC.
    op.execute("""
DO $a34$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'maalenex_geo_public_reader') THEN
        CREATE ROLE maalenex_geo_public_reader NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'maalenex_geo_internal_reader') THEN
        CREATE ROLE maalenex_geo_internal_reader NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END;
$a34$
""")
    op.execute("REVOKE ALL ON SCHEMA geo_public FROM PUBLIC")
    op.execute("REVOKE ALL ON SCHEMA geo_internal FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA geo_public TO maalenex_geo_public_reader")

    # These views deliberately use owner permissions (PostgreSQL's default
    # security_invoker=false): the public role receives no privileges on geo
    # base tables, tracking tables, organizations, or staff identities.
    op.execute("""
CREATE OR REPLACE VIEW geo_public.locations
WITH (security_barrier = true)
AS
SELECT l.id, l.name, l.location_type, l.geom
FROM geo.locations l
JOIN geo.data_sources ds ON ds.id = l.source_id
JOIN geo.publications p
  ON p.entity_type = 'location'
 AND p.entity_id = l.id
 AND p.source_id = l.source_id
WHERE l.status = 'published'
  AND l.publication_eligible
  AND ds.verification_status = 'verified'
  AND ds.publication_eligible
  AND p.status = 'published'
  AND p.revoked_at IS NULL
""")
    op.execute("""
CREATE OR REPLACE VIEW geo_public.terminals
WITH (security_barrier = true)
AS
SELECT t.id, t.location_id, t.name, t.geom
FROM geo.terminals t
JOIN geo.data_sources ds ON ds.id = t.source_id
JOIN geo.publications p
  ON p.entity_type = 'terminal'
 AND p.entity_id = t.id
 AND p.source_id = t.source_id
WHERE t.status = 'published'
  AND t.publication_eligible
  AND ds.verification_status = 'verified'
  AND ds.publication_eligible
  AND p.status = 'published'
  AND p.revoked_at IS NULL
""")
    op.execute("""
CREATE OR REPLACE VIEW geo_public.routes
WITH (security_barrier = true)
AS
SELECT r.id, r.code, r.origin_location_id, r.destination_location_id, r.geom
FROM geo.routes r
JOIN geo.data_sources ds ON ds.id = r.source_id
JOIN geo.publications p
  ON p.entity_type = 'route'
 AND p.entity_id = r.id
 AND p.source_id = r.source_id
WHERE r.status = 'published'
  AND r.publication_eligible
  AND ds.verification_status = 'verified'
  AND ds.publication_eligible
  AND p.status = 'published'
  AND p.revoked_at IS NULL
""")
    op.execute("""
CREATE OR REPLACE VIEW geo_public.route_stops
WITH (security_barrier = true)
AS
SELECT s.id, s.route_id, s.location_id, s.terminal_id, s.sequence_number,
       s.geom, s.boarding_allowed, s.alighting_allowed
FROM geo.route_stops s
JOIN geo.data_sources ds ON ds.id = s.source_id
JOIN geo.publications sp
  ON sp.entity_type = 'route_stop'
 AND sp.entity_id = s.id
 AND sp.source_id = s.source_id
JOIN geo_public.routes pr ON pr.id = s.route_id
JOIN geo_public.locations pl ON pl.id = s.location_id
WHERE s.status = 'published'
  AND s.publication_eligible
  AND ds.verification_status = 'verified'
  AND ds.publication_eligible
  AND sp.status = 'published'
  AND sp.revoked_at IS NULL
""")
    op.execute("""
CREATE OR REPLACE VIEW geo_public.boundaries
WITH (security_barrier = true)
AS
SELECT b.id, b.code, b.name, b.boundary_type, b.geom
FROM geo.boundaries b
JOIN geo.data_sources ds ON ds.id = b.source_id
JOIN geo.publications p
  ON p.entity_type = 'boundary'
 AND p.entity_id = b.id
 AND p.source_id = b.source_id
WHERE b.status = 'published'
  AND b.publication_eligible
  AND ds.verification_status = 'verified'
  AND ds.publication_eligible
  AND p.status = 'published'
  AND p.revoked_at IS NULL
""")
    op.execute("""
CREATE OR REPLACE VIEW geo_public.roads
WITH (security_barrier = true)
AS
SELECT r.id, r.road_class, r.name, r.geom
FROM geo.roads r
JOIN geo.data_sources ds ON ds.id = r.source_id
WHERE r.status = 'active'
  AND r.publication_eligible
  AND ds.verification_status = 'verified'
  AND ds.publication_eligible
""")
    op.execute("""
GRANT SELECT ON
    geo_public.locations,
    geo_public.terminals,
    geo_public.routes,
    geo_public.route_stops,
    geo_public.boundaries,
    geo_public.roads
TO maalenex_geo_public_reader
""")

    # Internal view is explicitly invoker-security so later RLS policies apply
    # to the authenticated service principal, not the view owner. It is not
    # granted to any role in A3.4; A3.5 must add RLS and tenant checks first.
    op.execute("""
CREATE OR REPLACE VIEW geo_internal.vehicle_positions
WITH (security_barrier = true, security_invoker = true)
AS
SELECT id, organization_id, vehicle_id, sequence, recorded_at, received_at,
       geom, speed_kph, heading_degrees, accuracy_meters, is_synthetic, source_id
FROM geo.vehicle_positions
""")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA geo_internal FROM PUBLIC")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA geo_public FROM PUBLIC")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS geo_internal.vehicle_positions")
    op.execute("DROP VIEW IF EXISTS geo_public.route_stops")
    op.execute("DROP VIEW IF EXISTS geo_public.roads")
    op.execute("DROP VIEW IF EXISTS geo_public.boundaries")
    op.execute("DROP VIEW IF EXISTS geo_public.routes")
    op.execute("DROP VIEW IF EXISTS geo_public.terminals")
    op.execute("DROP VIEW IF EXISTS geo_public.locations")
    op.execute("REVOKE ALL ON SCHEMA geo_public FROM maalenex_geo_public_reader")
    op.execute("DROP SCHEMA IF EXISTS geo_internal")
    op.execute("DROP SCHEMA IF EXISTS geo_public")
    # Cluster roles are intentionally retained as NOLOGIN roles. They may
    # already be referenced by deployment-specific role memberships.
