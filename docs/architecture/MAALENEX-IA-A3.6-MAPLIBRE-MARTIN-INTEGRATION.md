# MAALENEX-IA-A3.6 — MapLibre / Martin Integration

**Disposition:** VERIFIED-CLOSED — A3.6 CODE AND CI ACCEPTANCE; RUNTIME PROVISIONING DEFERRED  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Architecture baseline:** MAALENEX-IA-A1-SPEC-001 v1.0.0; A2 canonical PostGIS decision  
**Database contract:** A3.4 `geo_public` views and A3.5 capability roles

## 1. Public map and Martin

- Added MapLibre GL JS and the public map at `/map`.
- The public style requests only the Martin sources for approved roads, boundaries, routes, locations and terminals.
- Martin explicitly lists six A3.4 `geo_public` views, disables automatic source discovery and the web UI, disables CORS, and aborts startup if a configured source is invalid.
- Each table source has an explicit output-property allowlist.
- The local-only Compose service connects to the canonical application database using `MAALENEX_GEO_PUBLIC_DATABASE_URL`; no second spatial database is created.
- The Vite development proxy forwards `/martin` to the local Martin service.

Martin table sources can publish PostgreSQL views, and its configuration supports explicit source allowlists; this is the basis of the public-reader boundary.

## 2. Internal positions API and MapLibre overlay

- Added `GET /api/v1/geo/internal/vehicles/positions`.
- Requires the existing staff session cookie through `current_staff_context`.
- Requires an explicit `organization_id`; optional `vehicle_id`, `max_age_minutes` (1–1440, default 30), and `limit` (1–500, default 200) are bounded query parameters.
- Calls A3.5 `authorize_geo_tenant_context` with `platform.tracking.read` before querying the database. This enforces active organization membership plus scoped permission, or an explicit platform-wide grant, then sets the transaction-local tenant context and assumes the mapped NOLOGIN capability role.
- SQL additionally filters by the requested organization and selects only the latest recent position per vehicle.
- Response allowlist contains vehicle ID, coordinates, recorded/received timestamps, speed, heading, accuracy and synthetic flag. It excludes device identifiers, credential material, source internals and staff identity.
- Responses set `Cache-Control: no-store, private` and vary on Cookie. Missing authorization fails closed; an unconfigured database capability returns 503 rather than falling back to an owner connection.
- Added restricted frontend route `/map/internal`. Staff sign in using the existing session endpoint, enter an organization ID, and receive positions through the authenticated API. The overlay refreshes every 30 seconds and excludes positions older than 30 minutes by default.
- The internal map does not use Martin for internal tracking. It clears displayed positions when the session expires, tenant permission is denied, the service fails, the tenant changes or the user signs out.

The public Martin service remains incapable of serving internal tracking. Its dedicated database login must be granted membership only in `maalenex_geo_public_reader`, never the application or migration role.

## 3. Tests and CI verification added

- `backend/tests/test_geo_internal_positions_api.py`: staff authentication dependency, permission-before-query behavior, tenant filter, response privacy and no-store header.
- Existing A3.5 PostGIS RLS integration tests cover missing/malformed tenant context and two-tenant isolation of `geo.vehicle_positions` and `geo_internal.vehicle_positions`.
- Existing Martin contract test checks the explicit public-schema allowlist and MapLibre style source/layer contract.
- Updated `.github/workflows/g1-backend-verification.yml` to run on integration-branch pushes and PRs. It runs frontend TypeScript/Vite build and UI tests, backend tests, PostGIS migrations/RLS tests, Martin catalog and TileJSON smoke checks, and negative privilege checks for the Martin login.
- CI uses disposable PostgreSQL/PostGIS 3.5 and a throwaway reader credential; no production credentials are used.

## 4. Data, privacy and licensing boundary

The public map displays only rows in the A3.4 publication-eligible views. No third-party basemap, public OSM tile endpoint, Google Maps, satellite imagery or external API key is configured. If no verified and published records exist, the map remains without those features. Koybe's boarding point remains a point, not a verified route.

OSM data is not imported by this package. Any later OSM-derived data must be loaded into canonical `geo.roads` with provenance and licensing evidence, then pass publication controls before appearing in `geo_public.roads`.

## 5. Operational prerequisites and limitations

- The actual runtime application DB login must be granted SET membership in the required A3.5 capability roles out-of-band. The login is not yet identified or provisioned by this repository change.
- The Martin login must be provisioned out-of-band and granted only the public-reader capability.
- Production database host, TLS, secrets, reverse proxy, rate limiting, monitoring and capacity remain deployment decisions.
- The included Martin Compose service binds to loopback and is local-development only.
- No internal tracking credentials, database secrets or production endpoints are committed.
- No migration, production database change, Plesk deployment, merge or PR mutation is part of A3.6.

## 6. Verification results

**GitHub Actions run:** [G1 backend foundation verification #748](https://github.com/akefadaka-git/maalenex/actions/runs/45569701583)  
**Verified commit:** `da93d345ab576bcb187ae9c2daa712a596875636`  
**Branch:** `feat/a3-canonical-postgis-integration`

A3.6 acceptance checks completed successfully:

- [x] Ruff check for the new internal API and authorization tests.
- [x] Backend pytest suite, including the authenticated internal positions API tests.
- [x] Canonical PostGIS migration and A3.3 backfill integration tests on disposable PostGIS.
- [x] A3.4 public/internal view privilege tests.
- [x] A3.5 tenant RLS and cross-tenant isolation tests.
- [x] Frontend TypeScript/Vite production build.
- [x] Internal MapLibre overlay UI tests: authenticated session path requests the selected organization; unauthenticated path does not request positions.
- [x] Martin 2.0.0-beta.7 starts against the disposable canonical PostGIS database using the dedicated public-reader login.
- [x] Martin catalog and all six configured public TileJSON endpoints respond.
- [x] Negative privilege checks confirm the Martin login cannot read `geo.vehicle_positions` or `geo.devices`.

**Important broader workflow qualification:** the overall backend job is marked failed after the A3.6 checks, at the separate `alembic check` metadata-parity step. That check reports reflected public/extension tables absent from the SQLAlchemy metadata, including TIGER tables and existing passenger-account metadata. This is not a failure of the A3.6 API, frontend, Martin or RLS acceptance checks, but remains an unresolved repository-wide migration-baseline issue. Do not describe the entire workflow as green.

**Verification limits:** the internal frontend component test mocks the map renderer and API response; no live staff account or production application DB login was used. Martin TileJSON discovery was verified, but no populated production MVT tile payload was tested. The actual runtime application DB login is still unidentified, so its out-of-band membership in the A3.5 capability roles remains a deployment prerequisite.

**Disposition:** A3.6 implementation and CI-level acceptance are VERIFIED-CLOSED. Runtime DB role provisioning, production infrastructure and live-user acceptance remain deferred; no live DB, credentials, merge or deployment were changed.