# MaaleNex Moto map-provider architecture

## Current state

The ride planner currently renders a local SVG schematic. It is deliberately not a geographic map, navigation system, verified road graph, or live routing service. Do not add fabricated coordinates or turn the existing sample kilometre/fare values into operational claims.

A provider-neutral TypeScript contract lives at `frontend/src/maps/map-provider.ts`. It defines provider metadata, mandatory attribution, capability declarations, explicit route profiles, route geometry provenance, and resource disposal. The active mode remains `schematic`.

## Candidate technical direction

- **Renderer:** MapLibre GL JS is a suitable open-source WebGL renderer for browser/WebView vector maps. It does not supply map data, routing, geocoding, hosting, or offline rights by itself.
- **Data:** OpenStreetMap-derived data is a viable candidate for local road/place coverage, subject to an ODbL attribution and share-alike compliance review and validation of actual local completeness.
- **Routing:** A separate routing engine/service is required. Motorcycle routing must not be inferred from a generic driving profile; provider support and legal/road restrictions need field validation.
- **Offline:** Use a self-hosted or explicitly offline-licensed vector-tile package/provider. The standard OpenStreetMap raster tile service must not be used for bulk downloads, pre-seeding, or offline area packs.
- **Fallback:** Keep the local schematic available when map assets, network, style metadata, or route service are unavailable.

## OpenStreetMap service constraints

The standard `tile.openstreetmap.org` service is best-effort and has no service-level guarantee. Its policy requires visible attribution, proper caching, and prohibits bulk downloading and offline tile packs. It is not an acceptable tile source for a commercial offline-first deployment.

OpenStreetMap data can be obtained separately from tile services. Geofabrik publishes an Ethiopia extract in PBF and other formats. The existence of a country extract does not prove road coverage or routing suitability in Koybe, Maale Woreda, or the pilot corridors. Validate roads, access restrictions, names, bridges, seasonal conditions, and route continuity against local field evidence before launch.

## Required gates before enabling a real provider

1. Select the map renderer, tile/data host, routing engine, geocoder and offline packaging approach as separate decisions.
2. Record each provider's licence, commercial-use terms, attribution text, caching rules, offline rights, rate limits, SLA, data residency and privacy implications.
3. Obtain and version a bounded South Omo pilot-area dataset from a source whose licence permits the intended use. Record source timestamp, extract bounds, checksum and update process.
4. Verify place identity and coordinates for Koybe, Jinka, Maale Woreda and each pilot stop using authoritative/local evidence. No coordinate is accepted solely from a generic geocoder result.
5. Have local operators validate road access, motorcycle suitability, seasonal passability, bridges, and route alternatives. Mark unverified segments as unavailable.
6. Build routing tests for disconnected roads, one-way/access restrictions, no-route cases, stale data, offline mode and profile mismatch.
7. Keep device location opt-in. Do not send device coordinates to a provider unless the user action, privacy notice, provider terms and backend policy explicitly authorize it.
8. Show provider/data attribution persistently on the map, with a working licence link.
9. Verify offline packs are legally permitted, bounded, versioned, integrity-checked and updated without violating provider terms.
10. Only after these gates, replace the schematic renderer behind the adapter. Preserve the schematic fallback and never imply turn-by-turn navigation until separately verified.

## Explicit non-goals in this stage

- No live map tile endpoint or API key.
- No third-party map SDK dependency.
- No geocoding or route requests.
- No guessed geographic coordinates.
- No tile prefetching or offline map download.
- No production navigation, dispatch, ETA or fare calculation.

## Evidence references

- MapLibre GL JS documentation: https://github.com/maplibre/maplibre-gl-js
- OpenStreetMap standard tile usage policy: https://operations.osmfoundation.org/policies/tiles/
- OpenStreetMap vector tile usage policy: https://operations.osmfoundation.org/policies/vector/
- Geofabrik Ethiopia extract: https://download.geofabrik.de/africa/ethiopia.html
