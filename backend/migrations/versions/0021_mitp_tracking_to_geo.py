"""Backfill legacy MITP tracking records into canonical geo schema.

Revision ID: 0021_mitp_tracking_to_geo
Revises: 0020_canonical_postgis_schema

Legacy tables remain intact as rollback/evidence sources. Records whose tenant
cannot be inferred uniquely or whose telemetry has no unique matching
assignment are quarantined, never assigned by guesswork.
"""
from alembic import op

revision = "0021_mitp_tracking_to_geo"
down_revision = "0020_canonical_postgis_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE TABLE geo.legacy_tracking_quarantine (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_table varchar(80) NOT NULL,
    source_id uuid NOT NULL,
    reason varchar(120) NOT NULL,
    payload jsonb NOT NULL,
    quarantined_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_geo_legacy_tracking_quarantine UNIQUE(source_table, source_id)
)
""")
    op.execute("""
CREATE INDEX ix_geo_legacy_tracking_quarantine_source
ON geo.legacy_tracking_quarantine(source_table, source_id)
""")

    # Never overwrite canonical records or silently absorb identity collisions.
    op.execute("""
DO $
BEGIN
    IF EXISTS (
        SELECT 1 FROM public.tracking_devices legacy
        JOIN geo.devices canonical
          ON canonical.id = legacy.id
          OR canonical.device_identifier = legacy.device_identifier
    ) THEN
        RAISE EXCEPTION 'A3.3 device identity collision; reconcile before backfill';
    END IF;
    IF EXISTS (
        SELECT 1 FROM public.vehicle_device_assignments legacy
        JOIN geo.device_vehicle_assignments canonical
          ON canonical.id = legacy.id
    ) THEN
        RAISE EXCEPTION 'A3.3 assignment identity collision; reconcile before backfill';
    END IF;
    IF EXISTS (
        SELECT 1 FROM public.vehicle_telemetry legacy
        JOIN geo.vehicle_positions canonical
          ON canonical.id = legacy.id
          OR (canonical.device_id = legacy.device_id
              AND canonical.sequence = legacy.sequence)
    ) THEN
        RAISE EXCEPTION 'A3.3 telemetry identity collision; reconcile before backfill';
    END IF;
END;
$
""")

    # A device is tenant-owned only when every historical vehicle assignment
    # resolves to exactly one and the same organization.
    op.execute("""
CREATE TEMP TABLE _a33_device_tenant_map ON COMMIT DROP AS
SELECT
    d.id AS device_id,
    COUNT(DISTINCT v.organization_id) FILTER (
        WHERE v.organization_id IS NOT NULL
    ) AS organization_count,
    CASE
        WHEN COUNT(DISTINCT v.organization_id) FILTER (
            WHERE v.organization_id IS NOT NULL
        ) = 1
        THEN (ARRAY_AGG(DISTINCT v.organization_id) FILTER (
            WHERE v.organization_id IS NOT NULL
        ))[1]
        ELSE NULL
    END AS organization_id
FROM public.tracking_devices d
LEFT JOIN public.vehicle_device_assignments a ON a.device_id = d.id
LEFT JOIN public.vehicles v ON v.id = a.vehicle_id
GROUP BY d.id
""")
    op.execute("""
INSERT INTO geo.legacy_tracking_quarantine
    (source_table, source_id, reason, payload)
SELECT
    'tracking_devices',
    d.id,
    CASE
        WHEN m.organization_count = 0 THEN 'no_tenant_assignment_history'
        ELSE 'multiple_tenant_assignment_history'
    END,
    (to_jsonb(d) - 'credential_ciphertext') || jsonb_build_object(\n        'credential_ciphertext_redacted', true\n    )\nFROM public.tracking_devices d
JOIN _a33_device_tenant_map m ON m.device_id = d.id
WHERE m.organization_count <> 1
ON CONFLICT (source_table, source_id) DO NOTHING
""")
    op.execute("""
INSERT INTO geo.devices (
    id, organization_id, device_identifier, credential_ciphertext,
    credential_version, status, last_sequence, created_by, created_at, last_seen_at
)
SELECT
    d.id, m.organization_id, d.device_identifier, d.credential_ciphertext,
    d.credential_version, d.status, d.last_sequence, d.created_by,
    d.created_at, d.last_seen_at
FROM public.tracking_devices d
JOIN _a33_device_tenant_map m ON m.device_id = d.id
WHERE m.organization_count = 1
""")

    op.execute("""
INSERT INTO geo.legacy_tracking_quarantine
    (source_table, source_id, reason, payload)
SELECT
    'vehicle_device_assignments',
    a.id,
    CASE
        WHEN m.device_id IS NULL THEN 'device_tenant_unresolved'
        ELSE 'device_vehicle_tenant_mismatch'
    END,
    to_jsonb(a)
FROM public.vehicle_device_assignments a
JOIN public.vehicles v ON v.id = a.vehicle_id
LEFT JOIN _a33_device_tenant_map m ON m.device_id = a.device_id
WHERE m.organization_count IS DISTINCT FROM 1
   OR m.organization_id IS DISTINCT FROM v.organization_id
ON CONFLICT (source_table, source_id) DO NOTHING
""")
    op.execute("""
INSERT INTO geo.device_vehicle_assignments (
    id, organization_id, device_id, vehicle_id, assigned_by,
    assigned_at, unassigned_by, unassigned_at
)
SELECT
    a.id, v.organization_id, a.device_id, a.vehicle_id, a.assigned_by,
    a.assigned_at, a.unassigned_by, a.unassigned_at
FROM public.vehicle_device_assignments a
JOIN public.vehicles v ON v.id = a.vehicle_id
JOIN _a33_device_tenant_map m
  ON m.device_id = a.device_id
 AND m.organization_count = 1
 AND m.organization_id = v.organization_id
""")

    # Only telemetry with one matching device+vehicle assignment active at
    # recorded_at is eligible for canonical migration.
    op.execute("""
CREATE TEMP TABLE _a33_eligible_telemetry ON COMMIT DROP AS
SELECT
    t.id AS telemetry_id,
    t.device_id,
    t.vehicle_id,
    v.organization_id,
    t.sequence,
    t.recorded_at,
    t.received_at,
    t.latitude,
    t.longitude,
    t.speed_kph,
    t.heading_degrees,
    t.accuracy_meters,
    t.is_synthetic,
    (
        SELECT COUNT(*)
        FROM public.vehicle_device_assignments a
        WHERE a.device_id = t.device_id
          AND a.vehicle_id = t.vehicle_id
          AND t.recorded_at >= a.assigned_at
          AND (a.unassigned_at IS NULL OR t.recorded_at <= a.unassigned_at)
    ) AS matching_assignment_count
FROM public.vehicle_telemetry t
JOIN public.vehicles v ON v.id = t.vehicle_id
LEFT JOIN _a33_device_tenant_map m ON m.device_id = t.device_id
WHERE m.organization_count = 1
  AND m.organization_id = v.organization_id
""")
    op.execute("""
INSERT INTO geo.legacy_tracking_quarantine
    (source_table, source_id, reason, payload)
SELECT
    'vehicle_telemetry',
    t.id,
    CASE
        WHEN m.device_id IS NULL OR m.organization_count <> 1
            THEN 'device_tenant_unresolved'
        WHEN m.organization_id IS DISTINCT FROM v.organization_id
            THEN 'device_vehicle_tenant_mismatch'
        WHEN (
            SELECT COUNT(*)
            FROM public.vehicle_device_assignments a
            WHERE a.device_id = t.device_id
              AND a.vehicle_id = t.vehicle_id
              AND t.recorded_at >= a.assigned_at
              AND (a.unassigned_at IS NULL OR t.recorded_at <= a.unassigned_at)
        ) = 0 THEN 'no_assignment_at_recorded_time'
        ELSE 'multiple_assignments_at_recorded_time'
    END,
    to_jsonb(t)
FROM public.vehicle_telemetry t
JOIN public.vehicles v ON v.id = t.vehicle_id
LEFT JOIN _a33_device_tenant_map m ON m.device_id = t.device_id
WHERE m.organization_count IS DISTINCT FROM 1
   OR m.organization_id IS DISTINCT FROM v.organization_id
   OR (
       SELECT COUNT(*)
       FROM public.vehicle_device_assignments a
       WHERE a.device_id = t.device_id
         AND a.vehicle_id = t.vehicle_id
         AND t.recorded_at >= a.assigned_at
         AND (a.unassigned_at IS NULL OR t.recorded_at <= a.unassigned_at)
   ) <> 1
ON CONFLICT (source_table, source_id) DO NOTHING
""")

    # One internal-data provenance record per tenant receiving migrated fixes.
    op.execute("""
CREATE TEMP TABLE _a33_source_map ON COMMIT DROP AS
WITH tenant_sources AS (
    SELECT organization_id, MIN(recorded_at) AS collected_at
    FROM _a33_eligible_telemetry
    WHERE matching_assignment_count = 1
    GROUP BY organization_id
), inserted AS (
    INSERT INTO geo.data_sources (
        id, organization_id, provider, source_name, source_version,
        license_identifier, license_name, attribution_text, source_srid,
        collected_at, verification_status, responsible_actor_type,
        responsible_actor_id, publication_eligible
    )
    SELECT
        gen_random_uuid(),
        organization_id,
        'MaaleNex MITP',
        'Legacy internal vehicle telemetry (backfill)',
        '0021_mitp_tracking_to_geo',
        'INTERNAL_OPERATIONAL_DATA',
        'Internal operational data; no third-party map license asserted',
        'Backfilled from MaaleNex MITP device telemetry; source records retained',
        4326,
        collected_at,
        'unverified',
        'system',
        'migration:0021_mitp_tracking_to_geo',
        false
    FROM tenant_sources
    RETURNING id, organization_id
)
SELECT id AS source_id, organization_id FROM inserted
""")
    op.execute("""
INSERT INTO geo.vehicle_positions (
    id, organization_id, device_id, vehicle_id, source_id, sequence,
    recorded_at, received_at, geom, speed_kph, heading_degrees,
    accuracy_meters, is_synthetic
)
SELECT
    t.telemetry_id,
    t.organization_id,
    t.device_id,
    t.vehicle_id,
    s.source_id,
    t.sequence,
    t.recorded_at,
    t.received_at,
    ST_SetSRID(ST_MakePoint(t.longitude, t.latitude), 4326),
    t.speed_kph,
    t.heading_degrees,
    t.accuracy_meters,
    t.is_synthetic
FROM _a33_eligible_telemetry t
JOIN _a33_source_map s ON s.organization_id = t.organization_id
WHERE t.matching_assignment_count = 1
""")

    op.execute("""
CREATE INDEX ix_geo_legacy_tracking_quarantine_reason
ON geo.legacy_tracking_quarantine(reason)
""")


def downgrade() -> None:
    # Source tables are retained and never modified by upgrade. Remove only
    # canonical rows whose primary keys came from those legacy source rows.
    op.execute("""
DELETE FROM geo.vehicle_positions p
USING public.vehicle_telemetry t
WHERE p.id = t.id
""")
    op.execute("""
DELETE FROM geo.device_vehicle_assignments a
USING public.vehicle_device_assignments legacy
WHERE a.id = legacy.id
""")
    op.execute("""
DELETE FROM geo.devices d
USING public.tracking_devices legacy
WHERE d.id = legacy.id
""")
    op.execute("""
DELETE FROM geo.data_sources
WHERE responsible_actor_id = 'migration:0021_mitp_tracking_to_geo'
  AND source_name = 'Legacy internal vehicle telemetry (backfill)'
""")
    op.execute("DROP TABLE IF EXISTS geo.legacy_tracking_quarantine")
