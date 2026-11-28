# A4 continuation — keyless MapLibre/OpenFreeMap passenger maps

**Date:** 2026-11-28  
**Repository:** `akefadaka-git/maalenex`  
**PR:** [#43](https://github.com/akefadaka-git/maalenex/pull/43)  
**Branch:** `feat/passenger-backend-connectivity-foundation`  
**Base:** `fix/passenger-password-minimum-six`  
**Application-code candidate SHA:** `819a83d6f3bc0b2b3a087b311cfc803fdd81f94a`

## Governance

- PR #43 remains OPEN / DRAFT / UNMERGED.
- This is A3/A4 implementation and verification only.
- No merge, deployment, production migration, production credential use, payment activation or A5 action was performed.
- Independent external security review remains a mandatory pre-deployment gate only, not an A4 closure prerequisite.
- No Google billing account, API key, payment method, paid mapping provider or top-up is required by this implementation.

## Implementation

- Replaced the Google Maps passenger renderer with MapLibre GL JS pinned to 6.11.2, loaded as a version-pinned ESM module from UNPKG.
- Uses the OpenFreeMap Liberty style at `https://tiles.openfreemap.org/styles/liberty`.
- Removed the Google Maps API-key variable from the Android build workflow.
- Removed the Google-specific passenger component and API-key tests.
- Preserved passenger location coordinates as WGS84 `[longitude, latitude]`, validation of coordinate bounds, marker selection, GPS centering, route selection, and the rule that only published route geometry may be drawn.
- Retained explicit missing-data, offline and provider-error states. No route is inferred from endpoints.
- Added test-only map fixtures around Addis Ababa, Hawassa, Jinka and the Owner-confirmed Koybe terminal coordinate. These are labelled CI fixtures and are not passenger service records.
- Added frontend tests for the Liberty style, coordinate ordering, vector source detection, published route geometry, markers, marker selection and zoom interaction.
- Updated Android WebView runtime probing to require MapLibre initialization, loaded style, OpenFreeMap vector source and tiles, four markers, marker selection and map interaction.
- Preserved visible OpenStreetMap/OpenFreeMap attribution.

## Content Security Policy

The packaged WebView CSP now permits only:
- `https://unpkg.com` for the pinned MapLibre ESM and stylesheet.
- `https://tiles.openfreemap.org` for Liberty style, vector tiles, glyphs and sprite resources.
- `blob:` for MapLibre's CDN worker and generated map image resources.
- The configured API origin, when supplied, subject to existing HTTPS-origin validation.

Google Maps domains, broad wildcard hosts, `unsafe-inline` and `unsafe-eval` are removed. Inline scripts and style attributes remain blocked. The CSP verifier enforces the exact allow-list.

## Exact-SHA verification

### Backend — PASS

[Run #46128261717](https://github.com/akefadaka-git/maalenex/actions/runs/46128261717)  
Candidate SHA: `819a83d6f3bc0b2b3a087b311cfc803fdd81f94a`

- 112 backend tests passed; 1 existing Starlette/httpx TestClient deprecation warning.
- Ruff passed.
- Production API image build passed.
- Local S3-compatible service smoke passed.
- Empty-database migration and PostgreSQL integration passed.
- HTTPS passenger registration/session, exact-origin CORS and CSRF smoke passed.
- Alembic metadata parity passed.
- Full migration downgrade and clean re-upgrade passed.

### Android — PENDING / NOT VERIFIED

[Run #46128261842](https://github.com/akefadaka-git/maalenex/actions/runs/46128261842)  
Candidate SHA: `819a83d6f3bc0b2b3a087b311cfc803fdd81f94a`

At report time the exact-head Android workflow is still pending and has no job result. An earlier Android workflow run #234 at an earlier commit remains reported in progress but exposes no completed steps. Do not treat either state as a pass.

## S1 — Map provider, WebView runtime and CSP

**Disposition: PARTIALLY MITIGATED / OPEN.**

Completed in source and static/component coverage:
- Removed Google Maps and its billing/API-key dependency.
- Replaced Google-specific CSP origins with the exact MapLibre/OpenFreeMap resources.
- Added a real Android WebView probe and a CI-only Ethiopian location fixture.
- Added deterministic component tests for map setup, vector source recognition, markers, coordinate order, route geometry and interaction.

Still required before S1 closure:
1. Exact-head Android workflow success.
2. Android 15 WebView evidence that the MapLibre module and Liberty style load.
3. Evidence that OpenFreeMap vector tiles reach the loaded/idle state.
4. Evidence that Ethiopian markers render and marker selection plus zoom interaction complete.
5. No CSP violations, map-provider console errors, main-frame errors or renderer loss.
6. Inspect runtime CSP diagnostics and retain only necessary resource permissions.

No live Android provider evidence is claimed in this report. A passing component mock or a successful APK build alone does not close S1.

## Stage disposition

- Backend exact-head CI: PASS.
- Android exact-head CI: PENDING.
- MapLibre/OpenFreeMap Android WebView runtime: NOT YET VERIFIED.
- S1: PARTIALLY MITIGATED / OPEN.
- A4: PARTIAL / NOT CLOSED.
- A5: NOT STARTED; separate explicit Owner authorization remains required.
