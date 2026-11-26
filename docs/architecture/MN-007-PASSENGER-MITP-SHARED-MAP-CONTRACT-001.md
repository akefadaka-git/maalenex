# MN-007 — Passenger/MITP Shared Map Contract Reconciliation

**Artifact:** MN-007-PASSENGER-MITP-SHARED-MAP-CONTRACT-001  
**Version:** 1.0.0  
**Assessment date:** 2026-11-26  
**Status:** MN-007 DELIVERED — READ-ONLY ARCHITECTURE RECONCILIATION; OWNER CONTRACT ACCEPTANCE PENDING  
**Canonical repository:** `akefadaka-git/maalenex`  
**Baseline:** `main` at `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` (MN-006 verified baseline)  
**Method:** Static inspection of PR #43 and PR #53 changed files, their source contents, the GIS candidate migration branch and MN-006 evidence. No code execution or database access.

## 1. Executive disposition

MN-007 reconciles the passenger journey map and MITP vehicle-tracking map into one proposed shared map contract.

**Recommendation:** standardize on a provider-neutral MapLibre renderer boundary with a self-hosted-first Martin/PostGIS vector-tile source. Passenger and MITP should share map presentation primitives and GeoJSON conventions, but they must not share authorization, data visibility, or publication rules.

The two current implementations are materially different:

- Passenger PR #43 uses a Google Maps JavaScript SDK component, public passenger catalog endpoints, and catalog-owned location/route geometry fields.
- MITP PR #53 uses MapLibre, a local Martin/PostGIS proof-of-concept tile service, and a staff-authorized latest-vehicle-position endpoint.

A separate GIS candidate branch contains a more complete canonical spatial schema, provenance/licensing controls, sanitized public views, and tenant RLS. The passenger catalog API has not yet been shown to consume those canonical public views. This is the central contract gap: **the passenger publication path must not bypass GIS source-verification, licensing, publication, or revocation controls.**

MN-007 is an architecture proposal and evidence record. It does not approve a renderer migration, provider activation, database changes, map-data publication, live tracking, merge, or deployment. Owner acceptance is pending. Current MN-series A2 remains OPEN / NOT CLOSED.

## 2. Scope and evidence baseline

### 2.1 Included evidence

| Evidence | Exact inspected ref / file | Finding |
|---|---|---|
| Passenger | PR #43, head `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | Google Maps component and passenger catalog map API |
| Passenger renderer | `frontend/src/PassengerGoogleMap.tsx`, blob `79f633b828544747eaefd4a56ce4df11969ea4ad` | Google Maps SDK loader, markers, route polyline, device geolocation |
| Passenger API contract | `frontend/src/passenger-api.ts`, blob `e01afb46229e11d148aad415783b7c279933db90` | Location/route DTOs, GeoJSON LineString coordinates |
| Passenger API implementation | `backend/app/routers/passenger_catalog.py`, blob `4be8a5bcf99e073aebabae3e886a29e2d5254fff` | Public published catalog routes and locations |
| Passenger map schema | `backend/app/domains/catalog/models.py`, blob `0674191323445f18a650fc232b6de67b0177d0c5` | Catalog-owned coordinates and route JSON geometry |
| Passenger map tests | `backend/tests/test_passenger_map_contract.py`, blob `a456d06187f2b3738408de9df7b9ef097bcb9491` | Coordinate/source and LineString validation |
| Koybe route-data record | `docs/operations/koybe-terminal-route-data.md`, blob `0079893012f87cd4974fd73240432a3e0bf873cd` | Confirmed terminal pin; route trace remains unverified |
| MITP | PR #53, head `6d6a2de592381cd751c52f40824a9da1dd17b07a` | Synthetic tracking foundation and local MapLibre POC |
| MITP renderer | `frontend/src/features/tracking/TrackingMap.tsx`, blob `ded6f30faac17285bea34f8b5477bae7f7d82390` | MapLibre map, local style, staff API polling every 15 seconds |
| MITP telemetry contract | `backend/app/domains/tracking/schemas.py`, blob `f6ea890867eaec6b36a95d48c1671b756e7a6836` | WGS84 bounds, timestamp, speed, heading, accuracy, synthetic flag |
| MITP tracking service | `backend/app/domains/tracking/service.py`, blob `eee8b3cebf9e1c668a47e9af03c06052afcd5d1b` | Signed telemetry, replay/rate controls, latest position |
| MITP tracking router | `backend/app/routers/tracking.py`, blob `fa9ed554b635ee34d5e2c1bd40dde0e3e7299f2f` | Staff context and tracking permission on latest-position endpoint |
| Local map stack | `infra/mitp-maps/README.md`, blob `27eaa3c69b8e5b327a760166420e5058ae46634f` | Loopback PostGIS/Martin and OSM PBF import instructions |
| Map style | `frontend/public/mitp-map/style.json`, blob `9cf91b0eefc89813394f03c7d64b2dfcdfd7bd71` | Local vector tiles, OSM attribution, road-only style |
| GIS canonical schema | branch `feat/a3-canonical-postgis-integration` | Canonical `geo.*` schema and publication controls |

### 2.2 Boundaries

- Repository scope is only `akefadaka-git/maalenex`.
- PR #43 and PR #53 remain separate, open, unmerged workstreams.
- The GIS candidate branch is architecture/implementation evidence, not proof of a merged or deployed canonical spatial service.
- MN-006's historical governance distinction remains intact. MN-007 does not reopen or amend the historical MaaleNex–IROKA A2 disposition.
- No tests were run in this assessment. Existing test and workflow results are cited only as previously recorded evidence in MN-006.

## 3. Current interface comparison

### 3.1 Passenger map

PR #43 defines `PassengerLocation` with an optional coordinate object containing latitude, longitude and a source string. `PassengerRoute` includes origin, destination, ordered stops, optional GeoJSON LineString geometry and a geometry publication status.

The passenger catalog API:
- returns locations where `Location.status == "published"`;
- returns routes where the route, origin and destination are published;
- returns only published route stops;
- validates coordinate bounds and requires a non-empty coordinate source;
- validates route geometry as a LineString with at least two coordinate pairs and valid geographic bounds.

The renderer:
- loads the Google Maps JavaScript API from `maps.googleapis.com`;
- requires `VITE_GOOGLE_MAPS_API_KEY`;
- draws location markers and route polylines;
- provides a device-location action using browser/WebView geolocation;
- shows explicit missing-key, missing-data, offline and error states.

**Limit:** the passenger API's publication predicate is based on catalog status and basic source/geometry validation. The inspected endpoint does not demonstrate enforcement of canonical GIS source verification, licence approval, a matching publication record, or publication revocation. A non-empty `coordinate_source` / `geometry_source` string is not equivalent to reviewed provenance or reuse permission.

### 3.2 MITP map

PR #53 defines a separate MapLibre renderer using a local style and relative `/mitp-tiles` vector-tile URLs. The local compose documentation binds PostGIS and Martin to loopback interfaces and uses a separate read-only tile-reader role.

The tracking view:
- reads a vehicle UUID from the query string;
- calls `/api/v1/tracking/vehicles/{vehicle_id}/latest` with session credentials;
- polls every 15 seconds;
- renders a GeoJSON Point using [longitude, latitude];
- labels a position stale when its recorded timestamp is more than 90 seconds old;
- displays source, synthetic/live indicator, speed, accuracy and recorded time.

The backend latest-position endpoint requires a staff session and `platform.tracking.read`. Telemetry ingestion validates coordinate bounds, timezone-aware timestamps, speed, heading and accuracy, and applies device-signature, replay, age and rate checks. The PR #53 scope and configuration keep the current baseline synthetic-only.

**Limit:** the renderer and API are a proof of concept, not a verified production tracking service. The inspected endpoint's authorization helper is called with `organization_id=None`, and the latest-position query is by vehicle ID. The GIS candidate has tenant RLS design, but that does not prove the PR #53 endpoint is already executing under that RLS/tenant context. This must be reconciled before any live or multi-tenant tracking acceptance.

### 3.3 Canonical GIS candidate

The GIS candidate branch provides a separate `geo` schema with source records, locations, terminals, routes, route stops, device/vehicle positions, publication records and spatial geometries.

Its inspected migration sequence includes:
- `0020_canonical_postgis_schema`: creates PostGIS structures and source/provenance fields;
- `0021_mitp_tracking_to_geo`: migrates eligible legacy tracking rows and quarantines ambiguous tenant/assignment records rather than guessing;
- `0022_geo_publication_views`: creates sanitized `geo_public` views for explicitly published, source-verified and publication-eligible geography; keeps vehicle positions in a separate internal view;
- `0023_geo_tenant_rls_permissions`: adds tenant-scoped row-level security and geo/tracking permissions;
- `0024_geo_provenance_licensing`: requires verified source provenance and approved licence review before source publication eligibility, and records append-only source evidence.

This is materially stronger than the catalog-only publication gate in PR #43. However, it is still a branch candidate; no database migration or runtime wiring was verified in MN-007.

## 4. Proposed shared map contract

### 4.1 Renderer boundary

**Proposed standard:** one provider-neutral map component/API boundary, with MapLibre as the initial renderer implementation and self-hosted vector tiles as the default map source.

The shared renderer should accept typed, presentation-ready inputs and emit user interactions. It must not own domain authorization or decide whether a record is publishable.

Conceptual interface:

- `MapView`: viewport, zoom, locale, accessible controls and explicit loading/error/offline state.
- `MapFeatureCollection`: GeoJSON features for permitted public or internal layers.
- `MapLayerDescriptor`: layer identity, layer class, visibility, attribution and interaction policy.
- `MapSelection`: selected feature identifier and feature type; never a raw credential or private telemetry payload.
- `MapSourceStatus`: source identity/version, freshness, availability and attribution text.

Renderer adapter requirements:
1. Renderer implementation is replaceable behind a stable interface.
2. Domain services supply already-authorized features; renderer does not call privileged endpoints on its own.
3. Map style and tile URLs are configuration, not hard-coded provider credentials.
4. The renderer does not infer, fabricate, route or publish geometry.
5. The renderer supports keyboard/touch interaction, accessible labels, reduced-motion behavior and Amharic/English labels.
6. If map tiles are unavailable, the application retains usable text/list alternatives and does not imply that the map is current.

Google Maps is not the recommended default. PR #43's Google Maps SDK/API key and possible billing dependency are not approved by this reconciliation. No key, billing account or paid map service may be activated under MN-007.

### 4.2 Coordinate and geometry contract

- Canonical interchange format: GeoJSON compatible with RFC 7946.
- Coordinate reference system: WGS 84 longitude/latitude (EPSG:4326).
- Coordinate order: `[longitude, latitude]` for GeoJSON positions.
- Point: exactly one valid position.
- LineString: at least two valid positions; no invalid, non-finite, boolean or out-of-range ordinates.
- Geometry must carry a stable feature ID and a resolvable source/provenance reference in the domain contract.
- Transformations into projected coordinates for spatial indexing/rendering must be explicit and reversible to the published interchange contract.
- Accuracy, capture method, source timestamp, verification timestamp and data freshness must not be discarded where relevant.

Passenger's current DTO uses named latitude/longitude fields for points and GeoJSON [longitude, latitude] arrays for route geometry. MITP uses named latitude/longitude fields in telemetry and emits [longitude, latitude] GeoJSON in the renderer. A shared adapter can normalize these at the boundary without changing domain-owned storage or API contracts prematurely.

### 4.3 Domain ownership and access

| Layer / data | Owning domain | Intended consumer | Access rule |
|---|---|---|---|
| Public locations and terminals | Catalog / canonical Geo | Passenger web and Android | Explicit publication eligibility only |
| Public routes and ordered stops | Catalog / canonical Geo | Passenger web and Android | Source verified, licence approved, publication active and not revoked |
| Road basemap/vector tiles | Geo infrastructure | Shared renderer | Read-only tile access; source/licence attribution preserved |
| Vehicle/device registry | MITP / tracking | Authorized operations staff | Staff session, tenant scope and tracking permissions |
| Latest vehicle position | MITP / tracking | Authorized dispatcher/operations views | Tenant-scoped, purpose-bound permission; no public passenger endpoint |
| Device/user current location | Client device | Current user interaction | Explicit runtime permission and user action; no default persistence or telemetry upload |
| Route trace/source evidence | Geo data governance | Authorized catalog/geo reviewers | Controlled review and append-only evidence |

Passenger and MITP may use the same renderer and base-map infrastructure. They must not share the same feature-visibility policy. Passenger must never receive raw tracking tables, device identifiers, staff-only metadata, or internal vehicle positions through a public map endpoint.

### 4.4 API boundary

Proposed logical read contracts:

**Public passenger geography**
- Published locations and terminals.
- Published routes and ordered stops.
- Only source-verified and licence-approved geometries with an active publication record.
- Minimal fields required for passenger journey discovery.
- No internal source payloads, reviewer identity, private notes, staff identifiers or tracking data.

**Internal MITP geography and tracking**
- Vehicle position only through an authenticated, authorized endpoint.
- Explicit organization/tenant scope enforced in the query and database policy, not inferred from a globally checked permission alone.
- Return recorded time, received time, accuracy and source/synthetic status so clients can show staleness and provenance.
- No public/customer tracking endpoint unless a separate privacy, consent, security and product decision explicitly defines it.

**Tile service**
- Read-only, bounded access to approved tile layers.
- Public road basemap separated from tenant-private operational overlays.
- No direct access from the browser to PostGIS credentials or database ports.
- Public tiles must not expose unpublished routes, private boundaries or tracking positions.

These are proposed logical boundaries, not a claim that the routes or services are already implemented.

## 5. Provenance, licensing and publication controls

### 5.1 Required source record

Every published spatial feature must be traceable to a source record containing, as applicable:

- provider / source name and source URI;
- source version or extract date;
- checksum or immutable source reference;
- licence identifier, licence name, licence URI and required attribution;
- source CRS and collection method;
- collection timestamp and responsible actor;
- verification status, verifier and verification timestamp;
- licence-review status, reviewer and review timestamp;
- publication eligibility and publication/revocation history.

A free-text source label alone is insufficient evidence. Source records and supporting evidence must remain reviewable and auditable.

### 5.2 Publication gate

A location, terminal, route, stop or other public spatial feature may be exposed only when all applicable conditions pass:

1. Geometry and attributes pass structural validation.
2. Source is identified and evidence is recorded.
3. Source verification is approved by an authorized reviewer.
4. Licence/reuse review is approved and required attribution is present.
5. Feature is explicitly publication-eligible.
6. A publication record exists for the exact feature and source.
7. Publication is active and has not been revoked.
8. Public projection removes internal-only attributes.
9. Review and publication actions are auditable.

A failure or missing field must fail closed: omit the feature from public map responses and explain the unavailable state without inventing a substitute.

### 5.3 OpenStreetMap / ODbL

The MITP POC documentation identifies OpenStreetMap-derived vector tiles and ODbL obligations, with attribution to OpenStreetMap contributors. This is acceptable as a development proof-of-concept direction, not blanket commercial-use clearance.

Before public or commercial use, the Owner must obtain a documented review of:
- exact OSM extract/provider, date, geographic coverage and checksum;
- ODbL attribution placement and any applicable database/public-distribution obligations;
- whether derived/combined datasets trigger share-alike or other obligations;
- tile hosting, caching, update cadence and source notices;
- compatibility with other map data sources and contractual terms.

Do not assume all public map data is open for reuse, and do not mix incompatible sources without recorded licence review.

## 6. Koybe and route-publication disposition

The Koybe passenger boarding-point pin is recorded as Owner/operator-confirmed:

- Latitude: `5.7678630`
- Longitude: `36.7985890`
- Provenance: `operator_confirmed_terminal_pin`

This establishes the boarding-point coordinate only. It does not establish the road route, destination terminal, intermediate stops, operating corridor, distance or travel time.

The current Koybe route-data record says route geometry is **NOT VERIFIED** and must remain unpublished. Do not generate a passenger route line from a public routing engine, locality-centre/hospital candidate pins, or guessed roads.

Required evidence before route publication:
- operator-sourced route trace or field-verified waypoints;
- destination terminal identity and confirmed coordinates;
- ordered stops and boarding/alighting permissions;
- responsible operator confirmation and date;
- source/licence review and publication approval;
- topology and coordinate-order validation;
- reviewable change history when the route is corrected.

## 7. Privacy, consent and security requirements

### 7.1 Passenger map and device geolocation

The passenger renderer offers a user-triggered geolocation action. Keep device geolocation separate from operator/vehicle tracking.

Required contract:
- request permission only after an explicit user action and only when needed for a stated feature;
- use the minimum location precision needed;
- do not upload, persist, or use device location for analytics by default;
- do not equate user-device location with vehicle location;
- provide manual location selection if permission is denied or unavailable;
- do not block passenger trip discovery because location permission is denied;
- make the purpose and permission state clear in Amharic and English;
- test denial, revocation, repeated prompts, navigation, lifecycle and stale callback behavior.

PR #43's existing helper tests establish trusted app origin and coarse/fine permission logic, but MN-006 recorded missing concurrency, navigation, denial/revocation and device-lifecycle acceptance. Those gaps remain.

### 7.2 MITP tracking

- Device telemetry credentials remain device-specific, encrypted at rest, rotated/revocable and never exposed in map responses.
- Device identity and vehicle assignment history must be auditable.
- Enforce signature, replay, sequence, timestamp, accuracy and rate controls at ingestion.
- Latest-position access must require both an authorized staff session and the correct organization/tenant scope.
- Use least-privilege database roles and RLS; test missing, malformed and cross-tenant context as deny-by-default.
- Separate raw telemetry retention from map rendering/cache lifetime.
- Define purpose, retention, access logging, incident handling and authorized disclosure before any live device data.
- No customer-facing live tracking is implied by the staff-only POC.

### 7.3 Map provider and browser security

- No paid provider, key, billing, satellite imagery or third-party tile service is authorized by MN-007.
- Review CSP, external script loading, referrer restrictions and API key exposure if a third-party provider is ever proposed.
- Prefer same-origin/self-hosted tile delivery and a read-only tile role.
- Restrict CORS and tile endpoints to documented application origins and intended audiences.
- Never put database credentials, device credentials or privileged tokens in frontend configuration.

## 8. Freshness, availability and client behavior

The shared contract must distinguish:
- static geography source version and verification date;
- route publication version and effective date;
- vehicle position recorded time and received time;
- tile-source update time;
- current device geolocation timestamp.

Client behavior:
- stale vehicle positions are visibly stale and never represented as current;
- map/tile failure falls back to textual locations, stops and route details;
- offline mode does not imply that routes, schedules or vehicle positions are current;
- unavailable/unverified geometry is not replaced with a guessed line;
- no-data, permission-denied, unauthorized, stale, offline and provider-error states are distinct;
- Amharic and English labels are supported consistently.

The MITP POC already labels positions stale after 90 seconds and polls every 15 seconds. Those values are prototype behavior, not an approved operational service-level objective. The production freshness threshold, polling cadence, cache headers and rate limits require Owner/domain approval and capacity review.

## 9. Candidate shared architecture

The proposed logical flow is:

1. **Authoritative domain stores** own passenger catalog records, canonical Geo features, provenance/publication records, and MITP device/position records.
2. **Geo governance/publication layer** verifies source, licence, tenant, publication and revocation rules.
3. **Public geography API/view** exposes only sanitized, explicitly published locations, terminals, routes and stops.
4. **Internal tracking API** exposes only authorized, tenant-scoped current/latest positions.
5. **Self-hosted tile service** serves approved road/base layers read-only from PostGIS via Martin.
6. **Shared MapLibre renderer adapter** renders public and internal layers with separate permissions and layer descriptors.
7. **Passenger and staff experiences** compose only the layers their domain and role are allowed to see.

This is a target architecture proposal. The current PR branches are not yet wired into one verified runtime path.

## 10. Gaps and required closure evidence

| ID | Gap | Status | Closure evidence required |
|---|---|---|---|
| MN-007-01 | Passenger and MITP use different renderer stacks | **CONFIRMED** | Owner accepts shared renderer direction; later A3 adapter plan |
| MN-007-02 | Passenger API bypasses canonical GIS publication gates | **BLOCKER** | API/view contract mapped to source verification, licence, publication and revocation |
| MN-007-03 | Duplicate catalog and canonical `geo.*` spatial models | **UNRESOLVED** | Explicit system-of-record and migration/read-model ownership map |
| MN-007-04 | MITP latest-position tenant enforcement not demonstrated in PR #53 endpoint | **BLOCKER FOR LIVE / MULTI-TENANT ACCEPTANCE** | Tenant-scoped query, RLS context and cross-tenant negative tests |
| MN-007-05 | OSM source/licence/attribution evidence is procedural, not an approved dataset record | **PARTIAL** | Exact extract metadata/checksum and licence review |
| MN-007-06 | Passenger route trace and destination evidence absent | **BLOCKER FOR ROUTE PUBLICATION** | Operator/field-verified route and destination package |
| MN-007-07 | Koybe terminal pin only | **VERIFIED — LIMITED SCOPE** | Preserve exact pin; do not infer route geometry |
| MN-007-08 | Passenger geolocation lifecycle acceptance incomplete | **PARTIAL** | Permission/lifecycle/concurrency/revocation test plan and evidence |
| MN-007-09 | Production tile hosting, capacity, backups and security unverified | **NOT RUN / NOT VERIFIED** | Separate infrastructure/security review |
| MN-007-10 | Shared API DTO, renderer adapter and layer policy not approved | **PROPOSED ONLY** | Owner decision and later A3 design approval |
| MN-007-11 | Operational freshness, polling and cache SLOs undefined | **MISSING** | Owner/domain-approved service objectives |
| MN-007-12 | Integrated browser/device acceptance not run | **NOT RUN** | Later A4 evidence on a single approved integration candidate |

### 10.1 Immediate A2 closure conditions from MN-007

1. Owner approves or rejects the shared MapLibre/self-hosted-first renderer direction.
2. Record the canonical spatial system-of-record and transition/read-model relationship between catalog tables and `geo.*`.
3. Define the passenger public geography API's dependency on canonical GIS publication eligibility and revocation.
4. Define tenant-scoped MITP access and require negative cross-tenant tests before live/multi-tenant acceptance.
5. Keep Koybe route geometry unpublished until operator/field evidence is accepted.
6. Record OSM data-source and licence evidence before external publication or commercial use.
7. Carry geolocation lifecycle, accessibility, Amharic/English, freshness and offline behavior into MN-008/MN-011 and the eventual acceptance matrix.

## 11. Proposed decision record for Owner review

| Decision | Proposed direction | Approval state |
|---|---|---|
| MN-007-D01 renderer | Shared provider-neutral renderer boundary; MapLibre initial renderer | **PENDING OWNER** |
| MN-007-D02 base map | Self-hosted-first Martin/PostGIS vector tiles; no paid provider activation | **PENDING OWNER** |
| MN-007-D03 public geography | Passenger API consumes only sanitized canonical published geography with source/licence/publication/revocation gates | **PENDING OWNER** |
| MN-007-D04 tracking separation | MITP positions remain internal, staff-authorized and tenant-scoped; no public tracking endpoint | **PENDING OWNER** |
| MN-007-D05 device geolocation | User-triggered, purpose-limited, non-persistent by default; manual fallback | **PENDING OWNER** |
| MN-007-D06 route evidence | Koybe pin preserved; route geometry remains unpublished until operator/field verification | **PENDING OWNER** |
| MN-007-D07 OSM licensing | No public/commercial OSM-derived map release until source-specific ODbL review and attribution evidence | **PENDING OWNER** |

These are recommendations, not recorded Owner approvals. No A3 authorization is implied.

## 12. Final disposition

- **MN-007:** DELIVERED as a read-only architecture reconciliation artifact.
- **Shared map contract:** PROPOSED; Owner acceptance pending.
- **Passenger renderer:** Google Maps implementation evidenced in PR #43; not accepted as the shared target.
- **MITP renderer:** MapLibre/local Martin/PostGIS POC evidenced in PR #53; not production-ready.
- **Canonical GIS publication model:** stronger candidate controls identified; runtime/API integration not verified.
- **Koybe terminal pin:** VERIFIED as an Owner/operator-confirmed point only.
- **Koybe route geometry:** NOT VERIFIED; keep unpublished.
- **Live tracking / public tracking:** NOT AUTHORIZED by this record.
- **Paid provider / billing / satellite imagery:** NOT AUTHORIZED.
- **Implementation, migrations, merge, workflow dispatch and deployment:** NOT PERFORMED / NOT AUTHORIZED.
- **Current MN-series A2:** OPEN / NOT CLOSED.
- **Next package:** MN-008 — reconcile web/Android API flows into a passenger end-to-end acceptance plan, still read-only unless separately authorized.

No application source, migration, model, workflow, configuration, secret, database or production service was changed or accessed.
