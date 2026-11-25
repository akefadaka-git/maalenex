# MAALENEX-IA-A3.3 — MITP Tracking Backfill into Canonical Geo

**Status:** Backfill migration and synthetic CI verification path implemented; execution evidence pending  
**A1 baseline:** MAALENEX-IA-A1-SPEC-001 v1.0.0 (preserved)  
**A2 resolution:** Canonical PostGIS schema and tenant-scoped public/internal access contract  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Migration:** `0021_mitp_tracking_to_geo`  
**Parent:** `0020_canonical_postgis_schema`

## 1. Scope and source evidence

The MITP branch stores device registry, vehicle assignment history and telemetry in the primary application's PostgreSQL database through the legacy public tables:

- `tracking_devices`
- `vehicle_device_assignments`
- `vehicle_telemetry`

The MITP proof-of-concept also defines a separate, local-only `mitp_maps` PostGIS database for OpenStreetMap vector-tile source data. Its README explicitly says the OSM PBF import is a manual prerequisite; the repository contains only a synthetic OSM SQL fixture, not an authoritative Maale Woreda extract. No live `mitp_maps` database or imported OSM dataset was available to this repository migration. That separate map-data transfer is therefore not represented as completed.

## 2. Controlled backfill

Migration `0021_mitp_tracking_to_geo` copies legacy operational tracking rows into the canonical `geo` schema:

| Legacy source | Canonical target |
|---|---|
| `tracking_devices` | `geo.devices` |
| `vehicle_device_assignments` | `geo.device_vehicle_assignments` |
| `vehicle_telemetry` | `geo.vehicle_positions` |

The original UUIDs, credential ciphertext, credential version, device status, sequence counters, assignment timestamps, telemetry timestamps, measurements and synthetic flags are preserved. Latitude/longitude become EPSG:4326 PostGIS points using longitude as X and latitude as Y.

A per-tenant internal provenance source is created for migrated telemetry. It is marked `unverified` and is not publication-eligible; this migration does not assert that legacy GPS records are verified or suitable for public release.

## 3. Tenant inference and quarantine

The legacy device table has no organization key. Tenant ownership is inferred only from the complete historical assignment set:

- Exactly one distinct vehicle organization across all assignment history: device may be migrated.
- No organization history: device is quarantined.
- More than one organization across history: device is quarantined as ambiguous.

An assignment is migrated only if the device's uniquely inferred organization equals the assigned vehicle's organization.

A telemetry row is migrated only if:
1. The device has one unambiguous organization.
2. The vehicle belongs to that same organization.
3. Exactly one matching device/vehicle assignment was active at the telemetry `recorded_at` time.

Unresolved devices, assignments and telemetry are copied into `geo.legacy_tracking_quarantine` with the complete original row as JSONB and a reason code. They are not discarded, assigned to a guessed tenant, or made publicly accessible.

The migration also fails closed if canonical IDs, device identifiers or device-sequence identities already collide with the legacy rows. It does not silently overwrite or skip existing canonical data.

## 4. Rollback and preservation

- Legacy public tables are retained unchanged.
- Upgrade copies rows; it does not delete or rewrite source rows.
- Downgrade removes only canonical rows matching the retained legacy source IDs and the provenance rows created by this migration, then drops the quarantine table.
- Existing canonical data is protected by preflight collision checks.
- No production or external database was accessed or changed.

## 5. CI verification

The backend PostgreSQL workflow now:
1. Migrates a disposable PostGIS database through `0020_canonical_postgis_schema`.
2. Seeds deterministic synthetic legacy records for a valid tenant, an unassigned device and a cross-tenant device.
3. Applies the `0021` backfill.
4. Asserts valid rows migrate with preserved IDs, tenant ownership, EPSG:4326 coordinates and provenance.
5. Asserts unassigned, cross-tenant and invalid telemetry rows are quarantined.
6. Runs canonical schema checks, Alembic metadata checks, and full downgrade/re-upgrade.

The workflow has been updated in source, but no successful workflow run or local database execution has yet been observed. Therefore A3.3 is **IMPLEMENTED — VERIFICATION PENDING**, not verified-closed.

## 6. Explicit carry-forward items

- **CF- A3.3-01:** The separate `mitp_maps` OSM database has not been copied into `geo.roads`. No PBF import exists in the repository evidence; authoritative Maale Woreda road data, source checksum, collection date and ODbL attribution must be verified before importing or publishing road features.
- **CF- A3.3-02:** Tracking API/model/service code still references legacy public tables. Application cutover must follow the tenant-scoped authorization, RLS and restricted-role work in A3.4/A3.5; the legacy tables remain the rollback source until that cutover is verified.
- **CF- A3.3-03:** Existing deployed database Alembic histories and row counts have not been inspected. The migration must not be run against an existing deployment until its history and source/target row inventory are reconciled.

**Disposition:** Migration and seeded integration-test path committed to the A3 integration branch. Execution and data-transfer verification remain pending. No merge, deployment or external database mutation occurred.
