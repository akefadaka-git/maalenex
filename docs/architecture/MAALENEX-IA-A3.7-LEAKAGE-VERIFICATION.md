# MAALENEX-IA-A3.7 — Cross-Tenant and Public Leakage Verification

**Disposition:** IMPLEMENTED — CI VERIFICATION PENDING  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Scope:** Disposable PostGIS and Martin verification only; no production database access or deployment.

## 1. Tenant isolation coverage

Added `backend/tests/test_geo_publication_leakage.py` to exercise A3.5 capability roles under actual PostgreSQL `SET LOCAL ROLE` behavior.

- A synthetic two-tenant catalog fixture creates tenant-owned provenance, locations, routes and publication records.
- `maalenex_geo_catalog_manager` with tenant A context can see tenant A locations, routes and publications but not tenant B records.
- Missing and malformed tenant context return zero rows for locations, routes and publications.
- Assertions run through the capability role, not the database owner role.
- Existing A3.5 RLS tests continue to cover vehicle positions, devices, audit isolation, and denied quarantine access.

## 2. Public publication boundary

The new public-reader test creates:
- A globally published point whose provenance is verified and publication-eligible.
- A similarly located private point whose provenance is unverified and not publication-eligible, even though the entity and publication row are marked published.

The public reader must see only the approved point through `geo_public.locations`. It must not read base catalog tables, routes/publications, device or position tables, or the audit schema. Expected privilege denials use savepoints so each negative assertion is independent.

## 3. Martin vector-tile verification

The backend workflow now seeds two synthetic tile features into the disposable PostGIS database:
- `A37_APPROVED_TILE_FEATURE`: verified, publication-eligible, published.
- `A37_PRIVATE_MUST_NOT_LEAK`: unverified and ineligible.

After Martin starts with the dedicated least-privilege public-reader login, CI requests the actual `locations` MVT tile at z0/x0/y0. It requires a non-empty tile containing the approved feature and fails if the private marker appears. The existing catalog/TileJSON checks and direct denials for `geo.vehicle_positions` and `geo.devices` remain.

## 4. Verification boundaries

- All fixtures are synthetic and are inserted only into the GitHub Actions disposable PostGIS service.
- The workflow still includes the repository-wide `alembic check` metadata-parity step. Its previously observed TIGER extension and passenger-account metadata mismatch remains unresolved and must not be waived or represented as a green full workflow.
- This package does not prove production reverse-proxy behavior, live credentials, production role memberships, actual external-user session authorization, or populated production tile correctness.
- No production data, secrets, DB roles, merge state, deployment or PR state is changed.

## 5. Acceptance criteria

- [ ] New two-tenant catalog RLS tests pass under the catalog capability role.
- [ ] Missing and malformed tenant context tests pass.
- [ ] Public reader sees verified/published eligible feature only.
- [ ] Public reader direct access to internal/base/audit relations is denied.
- [ ] Actual Martin MVT tile contains approved feature and excludes unverified private marker.
- [ ] Existing backend, frontend, migration, RLS and Martin acceptance checks remain passing.
- [ ] Full workflow outcome and any unrelated Alembic metadata failure are separately recorded.

**Current status:** Code and CI workflow changes committed; awaiting the corresponding GitHub Actions run before A3.7 can be marked VERIFIED-CLOSED.
