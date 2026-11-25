# MAALENEX-IA-A3.7 — Cross-Tenant and Public Leakage Verification

**Disposition:** VERIFIED-CLOSED — A3.7 CI ACCEPTANCE; REPOSITORY-WIDE ALEMBIC PARITY UNRESOLVED  
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

- [x] New two-tenant catalog RLS tests pass under the catalog capability role.
- [x] Missing and malformed tenant context tests pass.
- [x] Public reader sees verified/published eligible feature only.
- [x] Public reader direct access to internal/base/audit relations is denied.
- [x] Actual Martin MVT tile contains approved feature and excludes unverified private marker.
- [x] Existing backend, frontend, migration, RLS and Martin acceptance checks remain passing.
- [x] Full workflow outcome and unrelated Alembic metadata failure are separately recorded.

## 6. CI evidence and final disposition

**GitHub Actions run:** [G1 backend foundation verification #756](https://github.com/akefadaka-git/maalenex/actions/runs/45571126186)  
**Verified commit:** `e75a8b07dba166ca6ad9b862cf8017106d96fb74`  
**Branch:** `feat/a3-canonical-postgis-integration`

The backend job completed with failure only at the separate repository-wide Alembic metadata-parity step. The following A3.7 and preceding package checks all completed successfully:

- Ruff for the established A3.6 scope.
- Full backend pytest suite.
- Canonical PostGIS baseline, MITP backfill and migration integration tests.
- A3.4 public/internal view privilege tests.
- A3.5 tenant RLS and cross-tenant isolation tests.
- **A3.7 two-tenant catalog RLS and missing/malformed context tests.**
- **A3.7 public-reader publication-eligibility and direct privilege-denial tests.**
- Disposable Martin startup, catalog and all six public TileJSON sources.
- **Actual Martin MVT tile check: approved marker present; unverified private marker absent.**
- Martin reader denied direct access to internal positions and device tables.
- Frontend TypeScript/Vite build and internal map UI tests.

The metadata-parity failure remains a separate repository-wide issue. The check reports unmodeled PostGIS TIGER/extension objects and existing passenger-account, ledger, notification, report and other application schema differences. The full backend workflow is therefore **not green**; the A3.7 acceptance steps themselves are green. No waiver or baseline suppression was introduced.

**Final disposition:** A3.7 cross-tenant and public leakage verification is **VERIFIED-CLOSED at disposable CI acceptance level**. This does not establish production runtime provisioning or external reverse-proxy behavior. No production DB, merge, deployment or PR state was changed.
