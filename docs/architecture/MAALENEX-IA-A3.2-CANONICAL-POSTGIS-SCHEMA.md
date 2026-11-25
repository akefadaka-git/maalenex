# MAALENEX-IA-A3.2 — Canonical PostGIS Schema

**Status:** Implemented on integration branch; execution and database verification pending  
**A1 baseline:** MAALENEX-IA-A1-SPEC-001 v1.0.0 (preserved)  
**A2 resolution:** Owner-approved canonical PostGIS and tenant-scoped access-control contract  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Predecessor:** `0019_merge_passenger_mitp`  
**Migration:** `0020_canonical_postgis_schema`

## 1. Purpose

Establish one canonical spatial schema, `geo`, inside the primary MaaleNex PostgreSQL database. This is the target data model for catalog geography, route geometry, provenance, device identity, vehicle telemetry and publication records. It replaces the separate MITP spatial database as the intended architecture; data migration is a later A3.3 increment.

## 2. Canonical tables

| Table | Responsibility |
|---|---|
| `geo.data_sources` | Provider, source URI/version/checksum, license, attribution, source CRS, collection/verification dates, verification state, responsible actor and publication eligibility |
| `geo.locations` | Canonical location identity and optional point geometry |
| `geo.terminals` | Terminal identity and optional point geometry linked to a location |
| `geo.routes` | Route identity, endpoints and optional MultiLineString geometry |
| `geo.route_stops` | Ordered route stops, terminal/location links and boarding/alighting flags |
| `geo.route_versions` | Immutable route-geometry version history |
| `geo.boundaries` | Administrative or service-area MultiPolygon geometry |
| `geo.roads` | Licensed/provenanced road-network MultiLineString geometry |
| `geo.devices` | Tenant-owned tracking-device identity and encrypted credential metadata |
| `geo.device_vehicle_assignments` | Tenant-bound device/vehicle assignment history |
| `geo.vehicle_positions` | Tenant-bound position/telemetry records |
| `geo.publications` | Versioned publication/revocation history for public spatial records |

## 3. Spatial conventions

- EPSG:4326 is the canonical interchange CRS.
- Point geometry is used for locations, terminals, route stops and vehicle positions.
- MultiLineString geometry is used for routes and roads.
- MultiPolygon geometry is used for administrative/service boundaries.
- Geometry columns have PostGIS typmods, validity checks and GiST indexes.
- Geometry may remain null for an unverified location or route. The Koybe operator-confirmed boarding pin remains a point only; it does not imply a verified road route.

## 4. Provenance and publication controls

Spatial feature records require a `source_id`. The source record captures provider, source name, license identifier/name, attribution, source CRS, collection date, verification state, responsible actor and publication eligibility. Publication history is explicit and versioned; publication is not inferred from the existence of geometry.

No authoritative Maale Woreda boundary or road-network source is introduced by this migration. Those datasets remain pending source/licensing verification.

## 5. Tenant integrity

Tracking devices and vehicle positions require an organization. Composite foreign keys bind each device and vehicle reference to the same organization, preventing cross-tenant device/vehicle assignment and position rows at the database constraint layer. Each position also requires a provenance source record. Vehicle composite identity is represented in ORM metadata so public-schema Alembic metadata checks can account for the supporting unique index.

API authorization, tenant-aware queries, RLS, restricted database roles and sanitized public views remain separate A3.4/A3.5 deliverables; this schema alone is not an authorization boundary.

## 6. Compatibility and migration sequence

- Revision `0020_canonical_postgis_schema` follows the graph-only merge `0019_merge_passenger_mitp`.
- The migration creates the PostGIS extension if absent and creates the canonical `geo` schema.
- It does not copy or delete rows from legacy `locations`, `routes`, `tracking_devices`, `vehicle_device_assignments`, `vehicle_telemetry` or the separate `mitp_maps` database.
- It does not create public views, roles, RLS policies, or public tile endpoints.
- Downgrade removes the new `geo` tables/schema and supporting vehicle index but deliberately retains the PostGIS extension because it may be shared.

## 7. Verification evidence required

The backend verification workflow now uses `postgis/postgis:16-3.4` and includes a post-upgrade schema test for the expected tables, EPSG:4326 geometry types, mandatory position provenance and tenant-bound tracking foreign keys. Alembic's environment excludes the PostGIS-owned `spatial_ref_sys` reference table from application metadata comparison.

Still required:
- [ ] Exact-head CI run on this branch/PR.
- [ ] Empty-database `alembic upgrade head`.
- [ ] PostGIS schema integration tests.
- [ ] `alembic check` metadata parity.
- [ ] Full downgrade and clean re-upgrade.
- [ ] Review on a copy of any deployed database before applying migrations there.

**Disposition:** A3.2 schema and verification code are committed to the integration branch. Database migration execution and tests remain NOT RUN. No production database was changed; no merge or deployment occurred.
