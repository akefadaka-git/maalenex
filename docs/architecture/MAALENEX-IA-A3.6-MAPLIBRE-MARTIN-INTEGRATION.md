# MAALENEX-IA-A3.6 — MapLibre / Martin Integration

**Disposition:** PARTIAL — PUBLIC MAP PATH IMPLEMENTED; INTERNAL TRACKING API/OVERLAY DEFERRED  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Architecture baseline:** MAALENEX-IA-A1-SPEC-001 v1.0.0; A2 canonical PostGIS decision  
**Database contract:** A3.4 `geo_public` views and A3.5 capability roles

## 1. Implemented

- Added MapLibre GL JS to the frontend and a dedicated public map at `/map`.
- Added a local MapLibre style using Martin TileJSON sources for approved roads, boundaries, routes, locations and terminals.
- Added Martin configuration that explicitly lists only the six A3.4 `geo_public` views, disables automatic source discovery and the web UI, disables CORS, and aborts startup if a configured source is invalid.
- Added explicit output-property allowlists for each public tile source.
- Added a local-only Compose service; it connects to the existing canonical application database using `MAALENEX_GEO_PUBLIC_DATABASE_URL`. No second PostGIS database is created.
- Added a Vite development proxy for the `/martin` route.
- Added contract tests that check the configured schema allowlist and the MapLibre style's source/layer references.

## 2. Security boundary and carry-forward

Martin is a public, read-only tile publisher. It must use a dedicated login principal with membership only in `maalenex_geo_public_reader`. It must not use the application DB login, migration role, database owner or table owner. The A3.4 views enforce publication eligibility, matching publication records and verified provenance; the public reader has no direct access to raw `geo` tables.

No internal tracking or vehicle-position tile source is configured. Martin cannot safely supply per-request tenant context for the A3.5 RLS model in this integration. Internal position access therefore remains outside Martin and must be served through an authenticated backend API that validates identity, active membership and permission before calling `authorize_geo_tenant_context`. That API integration and internal MapLibre overlay are not complete; they remain a controlled A3.6 carry-forward item, not an implied authorization bypass.

## 3. Data and licensing

The map displays only rows present in A3.4 public views. The style does not point to third-party basemaps, OSM public tile servers, Google Maps, satellite imagery or external API keys. If no verified, publication-eligible records have been published, the map remains empty. Koybe's boarding point remains a point and must not be represented as a verified route without authoritative route evidence.

OSM data is not imported by this package. Any later OSM-derived data must be loaded into the canonical `geo.roads` table with provenance and licensing evidence, and must pass publication controls before appearing in `geo_public.roads`.

## 4. Deployment and credential prerequisites

- Provision the Martin login and role membership out-of-band on the intended database.
- Store the dedicated connection string in `MAALENEX_GEO_PUBLIC_DATABASE_URL`; no secret is committed.
- Configure TLS and verify-full certificate validation for remote database connections.
- Configure a production reverse proxy, TLS, rate limiting, monitoring and capacity separately.
- The included Compose file binds Martin to loopback and is for local development only.
- Do not deploy to Plesk as part of A3.6.

## 5. Verification

- [ ] Frontend dependency installation and lockfile generation.
- [ ] Frontend TypeScript build and production bundle.
- [ ] Martin configuration validation against the selected Martin image.
- [ ] Disposable PostGIS smoke test: Martin catalog lists only the six configured views.
- [ ] Tile smoke tests for each public source.
- [ ] Negative privilege test: Martin login cannot SELECT from `geo.vehicle_positions`, `geo.devices`, `geo_internal` or `geo_audit`.
- [ ] Confirm no public endpoint or tile contains internal telemetry, device identifiers, tenant identifiers or staff personal data.
- [ ] Implement and verify the separate authenticated, tenant-scoped internal positions API/overlay before A3.6 closure.

No migration was added or executed. No live database was contacted. No credentials were created. No OSM data was imported. No merge, deployment or production change was performed.

**Status:** Public MapLibre/Martin integration committed to the integration branch. Internal tracking integration and all execution verification remain outstanding.