"""Create the canonical PostGIS geography and tracking schema.

Revision ID: 0020_canonical_postgis_schema
Revises: 0019_merge_passenger_mitp

This migration establishes the canonical spatial data model in the primary
application database. Data transfer from legacy catalog/MITP stores, public
views, RLS and service roles are separate A3 increments.
"""
from alembic import op

revision = "0020_canonical_postgis_schema"
down_revision = "0019_merge_passenger_mitp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE SCHEMA IF NOT EXISTS geo")

    op.execute("""
        CREATE TABLE geo.data_sources (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id uuid REFERENCES public.organizations(id) ON DELETE RESTRICT,
            provider varchar(160) NOT NULL,
            source_name varchar(200) NOT NULL,
            source_uri text,
            source_version varchar(120),
            source_checksum varchar(128),
            license_identifier varchar(120) NOT NULL,
            license_name varchar(200) NOT NULL,
            license_uri text,
            attribution_text text NOT NULL,
            source_srid integer NOT NULL,
            collected_at timestamptz NOT NULL,
            verified_at timestamptz,
            verification_status varchar(24) NOT NULL DEFAULT 'unverified',
            responsible_actor_type varchar(32) NOT NULL,
            responsible_actor_id varchar(128) NOT NULL,
            verified_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            publication_eligible boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT ck_geo_data_sources_srid CHECK (source_srid > 0),
            CONSTRAINT ck_geo_data_sources_verification CHECK (
                verification_status IN ('unverified', 'pending', 'verified', 'rejected')
            ),
            CONSTRAINT ck_geo_data_sources_verified_at CHECK (
                verification_status <> 'verified' OR verified_at IS NOT NULL
            )
        )
    """)
    op.execute("""
        CREATE INDEX ix_geo_data_sources_organization_id
        ON geo.data_sources(organization_id)
    """)
    op.execute("""
        CREATE INDEX ix_geo_data_sources_verification_status
        ON geo.data_sources(verification_status)
    """)

    op.execute("""
        CREATE TABLE geo.locations (
            id uuid PRIMARY KEY,
            organization_id uuid REFERENCES public.organizations(id) ON DELETE RESTRICT,
            name varchar(160) NOT NULL,
            location_type varchar(32) NOT NULL,
            status varchar(24) NOT NULL DEFAULT 'draft',
            geom geometry(Point, 4326),
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            publication_eligible boolean NOT NULL DEFAULT false,
            created_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            updated_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT ck_geo_locations_geom_valid CHECK (geom IS NULL OR ST_IsValid(geom))
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_locations_organization_id ON geo.locations(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_locations_status ON geo.locations(status)
""")
    op.execute("""
CREATE INDEX ix_geo_locations_geom_gix ON geo.locations USING GIST(geom)
""")

    op.execute("""
        CREATE TABLE geo.terminals (
            id uuid PRIMARY KEY,
            organization_id uuid REFERENCES public.organizations(id) ON DELETE RESTRICT,
            location_id uuid NOT NULL REFERENCES geo.locations(id) ON DELETE RESTRICT,
            name varchar(160) NOT NULL,
            status varchar(24) NOT NULL DEFAULT 'draft',
            geom geometry(Point, 4326),
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            publication_eligible boolean NOT NULL DEFAULT false,
            created_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            updated_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT ck_geo_terminals_geom_valid CHECK (geom IS NULL OR ST_IsValid(geom))
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_terminals_organization_id ON geo.terminals(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_terminals_location_id ON geo.terminals(location_id)
""")
    op.execute("""
CREATE INDEX ix_geo_terminals_status ON geo.terminals(status)
""")
    op.execute("""
CREATE INDEX ix_geo_terminals_geom_gix ON geo.terminals USING GIST(geom)
""")

    op.execute("""
        CREATE TABLE geo.routes (
            id uuid PRIMARY KEY,
            organization_id uuid REFERENCES public.organizations(id) ON DELETE RESTRICT,
            code varchar(60) NOT NULL UNIQUE,
            origin_location_id uuid NOT NULL REFERENCES geo.locations(id) ON DELETE RESTRICT,
            destination_location_id uuid NOT NULL REFERENCES geo.locations(id) ON DELETE RESTRICT,
            geom geometry(MultiLineString, 4326),
            status varchar(24) NOT NULL DEFAULT 'draft',
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            publication_eligible boolean NOT NULL DEFAULT false,
            created_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            updated_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT ck_geo_routes_distinct_endpoints CHECK (
                origin_location_id <> destination_location_id
            ),
            CONSTRAINT ck_geo_routes_geom_valid CHECK (geom IS NULL OR ST_IsValid(geom))
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_routes_organization_id ON geo.routes(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_routes_status ON geo.routes(status)
""")
    op.execute("""
CREATE INDEX ix_geo_routes_geom_gix ON geo.routes USING GIST(geom)
""")

    op.execute("""
        CREATE TABLE geo.route_stops (
            id uuid PRIMARY KEY,
            organization_id uuid REFERENCES public.organizations(id) ON DELETE RESTRICT,
            route_id uuid NOT NULL REFERENCES geo.routes(id) ON DELETE CASCADE,
            location_id uuid NOT NULL REFERENCES geo.locations(id) ON DELETE RESTRICT,
            terminal_id uuid REFERENCES geo.terminals(id) ON DELETE RESTRICT,
            sequence_number integer NOT NULL,
            geom geometry(Point, 4326),
            boarding_allowed boolean NOT NULL DEFAULT false,
            alighting_allowed boolean NOT NULL DEFAULT false,
            status varchar(24) NOT NULL DEFAULT 'draft',
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            publication_eligible boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_geo_route_stop_sequence UNIQUE(route_id, sequence_number),
            CONSTRAINT ck_geo_route_stop_sequence CHECK (sequence_number > 0),
            CONSTRAINT ck_geo_route_stops_geom_valid CHECK (geom IS NULL OR ST_IsValid(geom))
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_route_stops_organization_id ON geo.route_stops(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_route_stops_route_id ON geo.route_stops(route_id)
""")
    op.execute("""
CREATE INDEX ix_geo_route_stops_geom_gix ON geo.route_stops USING GIST(geom)
""")

    op.execute("""
        CREATE TABLE geo.route_versions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            route_id uuid NOT NULL REFERENCES geo.routes(id) ON DELETE RESTRICT,
            version_number integer NOT NULL,
            geom geometry(MultiLineString, 4326),
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            status varchar(24) NOT NULL DEFAULT 'draft',
            change_reason varchar(500),
            effective_from timestamptz,
            effective_to timestamptz,
            created_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_geo_route_version UNIQUE(route_id, version_number),
            CONSTRAINT ck_geo_route_version_number CHECK (version_number > 0),
            CONSTRAINT ck_geo_route_version_dates CHECK (
                effective_to IS NULL OR effective_from IS NULL OR effective_to > effective_from
            ),
            CONSTRAINT ck_geo_route_versions_geom_valid CHECK (geom IS NULL OR ST_IsValid(geom))
        )
    """)
    op.execute("""
        CREATE INDEX ix_geo_route_versions_geom_gix
        ON geo.route_versions USING GIST(geom)
    """)

    op.execute("""
        CREATE TABLE geo.boundaries (
            id uuid PRIMARY KEY,
            organization_id uuid REFERENCES public.organizations(id) ON DELETE RESTRICT,
            code varchar(80) NOT NULL,
            name varchar(200) NOT NULL,
            boundary_type varchar(40) NOT NULL,
            geom geometry(MultiPolygon, 4326) NOT NULL,
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            status varchar(24) NOT NULL DEFAULT 'draft',
            publication_eligible boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT ck_geo_boundaries_geom_valid CHECK (ST_IsValid(geom))
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_boundaries_organization_id ON geo.boundaries(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_boundaries_type ON geo.boundaries(boundary_type)
""")
    op.execute("""
CREATE INDEX ix_geo_boundaries_geom_gix ON geo.boundaries USING GIST(geom)
""")

    op.execute("""
        CREATE TABLE geo.roads (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            road_class varchar(40) NOT NULL,
            name varchar(200),
            geom geometry(MultiLineString, 4326) NOT NULL,
            attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
            status varchar(24) NOT NULL DEFAULT 'active',
            publication_eligible boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT ck_geo_roads_geom_valid CHECK (ST_IsValid(geom))
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_roads_source_id ON geo.roads(source_id)
""")
    op.execute("""
CREATE INDEX ix_geo_roads_class ON geo.roads(road_class)
""")
    op.execute("""
CREATE INDEX ix_geo_roads_geom_gix ON geo.roads USING GIST(geom)
""")

    # A composite unique key enables database-enforced tenant matching for
    # devices, assignments and position records referencing an existing vehicle.
    op.execute("""
        CREATE UNIQUE INDEX uq_geo_vehicle_tenant_identity
        ON public.vehicles(id, organization_id)
    """)

    op.execute("""
        CREATE TABLE geo.devices (
            id uuid PRIMARY KEY,
            organization_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE RESTRICT,
            device_identifier varchar(80) NOT NULL UNIQUE,
            credential_ciphertext varchar(512) NOT NULL,
            credential_version integer NOT NULL DEFAULT 1,
            status varchar(24) NOT NULL DEFAULT 'pending',
            last_sequence integer NOT NULL DEFAULT 0,
            created_by uuid REFERENCES public.staff_users(id) ON DELETE SET NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            last_seen_at timestamptz,
            CONSTRAINT uq_geo_device_tenant_identity UNIQUE(id, organization_id),
            CONSTRAINT ck_geo_device_credential_version CHECK (credential_version > 0),
            CONSTRAINT ck_geo_device_last_sequence CHECK (last_sequence >= 0),
            CONSTRAINT ck_geo_device_status CHECK (
                status IN ('pending', 'active', 'suspended', 'revoked')
            )
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_devices_organization_id ON geo.devices(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_devices_status ON geo.devices(status)
""")

    op.execute("""
        CREATE TABLE geo.device_vehicle_assignments (
            id uuid PRIMARY KEY,
            organization_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE RESTRICT,
            device_id uuid NOT NULL,
            vehicle_id uuid NOT NULL,
            assigned_by uuid REFERENCES public.staff_users(id) ON DELETE SET NULL,
            assigned_at timestamptz NOT NULL DEFAULT now(),
            unassigned_by uuid REFERENCES public.staff_users(id) ON DELETE SET NULL,
            unassigned_at timestamptz,
            CONSTRAINT fk_geo_assignment_device_tenant
                FOREIGN KEY(device_id, organization_id)
                REFERENCES geo.devices(id, organization_id) ON DELETE RESTRICT,
            CONSTRAINT fk_geo_assignment_vehicle_tenant
                FOREIGN KEY(vehicle_id, organization_id)
                REFERENCES public.vehicles(id, organization_id) ON DELETE RESTRICT,
            CONSTRAINT ck_geo_assignment_dates CHECK (
                unassigned_at IS NULL OR unassigned_at >= assigned_at
            )
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_device_assignments_organization_id
        ON geo.device_vehicle_assignments(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_device_assignments_device_id
        ON geo.device_vehicle_assignments(device_id)
""")
    op.execute("""
CREATE INDEX ix_geo_device_assignments_vehicle_id
        ON geo.device_vehicle_assignments(vehicle_id)
""")
    op.execute("""
CREATE UNIQUE INDEX uq_geo_active_device_assignment_device
        ON geo.device_vehicle_assignments(device_id) WHERE unassigned_at IS NULL
""")
    op.execute("""
CREATE UNIQUE INDEX uq_geo_active_device_assignment_vehicle
        ON geo.device_vehicle_assignments(vehicle_id) WHERE unassigned_at IS NULL
""")

    op.execute("""
        CREATE TABLE geo.vehicle_positions (
            id uuid PRIMARY KEY,
            organization_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE RESTRICT,
            device_id uuid NOT NULL,
            vehicle_id uuid NOT NULL,
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            sequence integer NOT NULL,
            recorded_at timestamptz NOT NULL,
            received_at timestamptz NOT NULL DEFAULT now(),
            geom geometry(Point, 4326) NOT NULL,
            speed_kph numeric(6,2) NOT NULL,
            heading_degrees numeric(6,2) NOT NULL,
            accuracy_meters numeric(7,2) NOT NULL,
            is_synthetic boolean NOT NULL DEFAULT true,
            CONSTRAINT fk_geo_position_device_tenant
                FOREIGN KEY(device_id, organization_id)
                REFERENCES geo.devices(id, organization_id) ON DELETE RESTRICT,
            CONSTRAINT fk_geo_position_vehicle_tenant
                FOREIGN KEY(vehicle_id, organization_id)
                REFERENCES public.vehicles(id, organization_id) ON DELETE RESTRICT,
            CONSTRAINT uq_geo_vehicle_position_sequence UNIQUE(device_id, sequence),
            CONSTRAINT ck_geo_position_sequence CHECK (sequence > 0),
            CONSTRAINT ck_geo_position_speed CHECK (speed_kph >= 0),
            CONSTRAINT ck_geo_position_heading CHECK (
                heading_degrees >= 0 AND heading_degrees < 360
            ),
            CONSTRAINT ck_geo_position_accuracy CHECK (accuracy_meters >= 0),
            CONSTRAINT ck_geo_position_geom_valid CHECK (ST_IsValid(geom))
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_vehicle_positions_organization_id
        ON geo.vehicle_positions(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_vehicle_positions_vehicle_recorded
        ON geo.vehicle_positions(vehicle_id, recorded_at DESC)
""")
    op.execute("""
CREATE INDEX ix_geo_vehicle_positions_device_recorded
        ON geo.vehicle_positions(device_id, recorded_at DESC)
""")
    op.execute("""
CREATE INDEX ix_geo_vehicle_positions_geom_gix
        ON geo.vehicle_positions USING GIST(geom)
""")

    op.execute("""
        CREATE TABLE geo.publications (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id uuid REFERENCES public.organizations(id) ON DELETE RESTRICT,
            entity_type varchar(48) NOT NULL,
            entity_id uuid NOT NULL,
            entity_version integer NOT NULL DEFAULT 1,
            source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
            status varchar(24) NOT NULL DEFAULT 'published',
            published_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            published_at timestamptz NOT NULL DEFAULT now(),
            revoked_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
            revoked_at timestamptz,
            audit_reference varchar(128),
            CONSTRAINT uq_geo_publication_entity_version
                UNIQUE(entity_type, entity_id, entity_version),
            CONSTRAINT ck_geo_publication_version CHECK (entity_version > 0),
            CONSTRAINT ck_geo_publication_status CHECK (
                status IN ('published', 'revoked', 'superseded')
            ),
            CONSTRAINT ck_geo_publication_revocation CHECK (
                (status = 'revoked' AND revoked_at IS NOT NULL)
                OR (status <> 'revoked')
            )
        )
    """)
    op.execute("""
CREATE INDEX ix_geo_publications_organization_id
        ON geo.publications(organization_id)
""")
    op.execute("""
CREATE INDEX ix_geo_publications_status_time
        ON geo.publications(status, published_at DESC)
""")
    op.execute("""
CREATE INDEX ix_geo_publications_entity
        ON geo.publications(entity_type, entity_id)
""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS geo.publications")
    op.execute("DROP TABLE IF EXISTS geo.vehicle_positions")
    op.execute("DROP TABLE IF EXISTS geo.device_vehicle_assignments")
    op.execute("DROP TABLE IF EXISTS geo.devices")
    op.execute("DROP INDEX IF EXISTS public.uq_geo_vehicle_tenant_identity")
    op.execute("DROP TABLE IF EXISTS geo.roads")
    op.execute("DROP TABLE IF EXISTS geo.boundaries")
    op.execute("DROP TABLE IF EXISTS geo.route_versions")
    op.execute("DROP TABLE IF EXISTS geo.route_stops")
    op.execute("DROP TABLE IF EXISTS geo.routes")
    op.execute("DROP TABLE IF EXISTS geo.terminals")
    op.execute("DROP TABLE IF EXISTS geo.locations")
    op.execute("DROP TABLE IF EXISTS geo.data_sources")
    op.execute("DROP SCHEMA IF EXISTS geo")
    # PostGIS is intentionally retained: other application schemas may use it.
