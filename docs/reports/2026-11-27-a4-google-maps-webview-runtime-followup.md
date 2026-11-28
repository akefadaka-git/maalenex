# A4 follow-up — Android, backend and Google Maps WebView evidence

**Date:** 2026-11-27  
**Repository:** `akefadaka-git/maalenex`  
**PR:** [#43](https://github.com/akefadaka-git/maalenex/pull/43)  
**Branch:** `feat/passenger-backend-connectivity-foundation`  
**Base:** `fix/passenger-password-minimum-six`  
**Exact verified head:** `fb2fa92a8fcc36fb03f23ed2de3248a667718eac`

## Governance and scope

- PR #43 remains OPEN / DRAFT / UNMERGED.
- This is A4 verification and evidence work only.
- No merge, deployment, production migration, credential rotation, payment activation or A5 action was performed.
- Independent external security review remains a mandatory pre-deployment gate only, not an A4 closure prerequisite.

## Changes included in this follow-up

- `638ee5078c85ae83797d192546069722c3ace6cd` — isolated CI-only map fixture. The fixture is enabled only by `VITE_MAP_RUNTIME_SMOKE=true`, uses a clearly labelled test coordinate, and is not used in ordinary builds or represented as a service location.
- `3cc6d68b606061e03440e4963e20a78b75d90d05` — native Android WebView runtime probe. It reports map status, Maps API presence, map DOM presence, script presence and tile-image count. It never logs the API key.
- `41f751795a29c82bc5515ffcfb20810d702f248a` — emulator smoke assertions for provider success versus explicit missing-key fallback.
- `cfce9969ddd9c7e5ca548bdf3bb9e5fa41955891` — enable the isolated map runtime fixture in the Android CI build.
- `bc48e3762430e7effc80b7f27b1171443d470eab` — make the Android feature branch PR-governed and avoid duplicate push + PR emulator runs.
- `43c90a5af6ada8463dc81f2192059522421c084f` — remove the same feature branch from duplicate backend push verification.
- `9fc8ae47b66ce436b8f3572a1e8d94a364c83fcb` — add explicit Maps API and Maps static resource hosts to the CSP, plus Google Fonts stylesheet host.
- `fb2fa92a8fcc36fb03f23ed2de3248a667718eac` — update the CSP verifier to require those exact origins.

The CSP continues to block inline scripts, script attributes and style attributes. `unsafe-inline` remains restricted to `style-src-elem` for Maps-generated style elements.

## Exact-head CI results

### Backend — PASS

[Run #45984865418](https://github.com/akefadaka-git/maalenex/actions/runs/45984865418)  
Head: `fb2fa92a8fcc36fb03f23ed2de3248a667718eac`

- 112 backend tests passed; 1 Starlette/httpx TestClient deprecation warning remains.
- Ruff passed.
- Production API container build passed.
- Ephemeral S3-compatible service smoke passed.
- Empty-database baseline migration passed.
- HTTPS passenger session, CORS and CSRF checks passed.
- Alembic metadata parity passed.
- Full migration downgrade and clean re-upgrade passed.

### Android and dependency security — PASS

[Run #45984865920](https://github.com/akefadaka-git/maalenex/actions/runs/45984865920)  
Head: `fb2fa92a8fcc36fb03f23ed2de3248a667718eac`

- Frontend: 20 tests passed; typecheck and production build passed.
- Packaged WebView CSP contract passed, including explicit Maps and Google Fonts origins.
- HTTPS API-origin validation passed; insecure remote API origin was rejected.
- Gradle dependency verification metadata bootstrap passed.
- Four categorized CycloneDX SBOMs validated.
- Android unit tests: 12 passed, 0 failures, 0 errors, 0 skipped.
- APK assembly and Android lint passed.
- APK installed and launched on Android 15 emulator.
- WebView packaged document loaded; React root probe passed.
- OSV scanned 27 runtime, 19 compile, 29 test, 112 build-tool and 161 frontend packages. Scanner output: **No issues found**.

## Android WebView map runtime evidence

Artifact: `maalenex-android-webview-smoke-evidence` (run #45984865920).

Captured on Android 15 emulator, package `com.maalenex.moto`, app PID `2194`, at `2026-11-27T10:51:26Z`.

Packaged document probe:

```json
{"schemaVersion":1,"readyState":"complete","title":"MaaleNex — Mobility and Digital Services","rootPresent":true,"rootTextLength":817}
```

Map runtime probe:

```json
{"schemaVersion":1,"status":"missing-key","mapsApiLoaded":false,"mapDomPresent":false,"googleMapsScriptPresent":false,"mapTileImageCount":0}
```

Observed:
- `WEBVIEW_PAGE_FINISHED` for `https://appassets.androidplatform.net/assets/www/index.html`.
- The real Android WebView mounted the passenger map component and exposed the explicit missing-key fallback.
- No `WEBVIEW_CSP_VIOLATION`, main-frame load error, renderer loss or fatal Android exception was detected.
- App process remained alive and `MainActivity` remained the resumed foreground activity.

**Provider runtime disposition: NOT RUN.** The workflow has no `VITE_GOOGLE_MAPS_API_KEY` repository variable configured. Therefore the Maps JavaScript API was not requested, no Google map DOM or tiles were created, and this run does not prove successful Google Maps provider compatibility. The captured result is real WebView evidence for the safe missing-key path only.

## S1 — Google Maps CSP and provider compatibility

**Disposition: PARTIALLY MITIGATED / OPEN.**

Completed:
- Added explicit `maps.googleapis.com` and `maps.gstatic.com` entries for map connections and image resources.
- Added `fonts.googleapis.com` for Maps-injected stylesheet resources.
- Preserved the restrictive CSP rules for scripts and style attributes.
- Added an Android WebView runtime probe and a non-production fixture so a provider test can run without live passenger catalog data.
- Verified the safe missing-key path in the real Android 15 WebView.

Remaining:
- A valid, appropriately restricted Maps JavaScript API key is required to test Google-hosted script loading, authorization, map DOM initialization, tiles, fonts and runtime CSP behavior.
- The key must be configured as the repository Actions variable `VITE_GOOGLE_MAPS_API_KEY`. It is a client-side key embedded in the test APK, so it must be restricted to the Maps JavaScript API and the authorized application referrer.
- Google Maps Platform requires a valid API key and an enabled billing account for Maps JavaScript API use. No payment or top-up was made or requested.
- Google security guidance warns that hybrid applications loading local WebView resources may omit the HTTP Referer header. The runtime test must establish whether the HTTPS WebViewAssetLoader origin `https://appassets.androidplatform.net` is accepted by the key's HTTP-referrer restriction. If not, use a controlled HTTPS-hosted test origin or revise the integration architecture; do not weaken key restrictions blindly.

S1 closure criteria:
1. Run the Android 15 WebView smoke with a valid restricted key.
2. Require `data-map-status=ready`, `mapsApiLoaded=true`, `mapDomPresent=true`, and the Maps JavaScript script present.
3. Capture map rendering evidence and verify no Maps authorization errors, CSP violations, main-frame errors or renderer loss.
4. Run the no-key fallback test and verify it remains explicit and safe.
5. Reassess whether the `style-src-elem 'unsafe-inline'` exception is required after observing the real provider runtime.

## Other A4 findings

| Finding | Disposition | Remaining action |
|---|---|---|
| S2 — PostgreSQL TLS | REMEDIATED IN CONFIGURATION | Production provider CA, hostname identity and live TLS handshake remain deployment-time verification inputs |
| Warning 1 — TestClient deprecation | ACCEPTED TEMPORARILY | Migrate to a supported Starlette/FastAPI/httpx2 test-client combination |
| Warnings 2–3 — per-request TestClient cookies | RESOLVED | Prior cookie deprecation remediation remains in place |
| S3 — operations fixture guard coverage | DOCUMENTED LIMITATION | Dedicated endpoint mutation/CSRF tests remain evidence; fixture itself does not prove the mutation guard |

## Stage decision

- Backend exact-head CI: PASS.
- Android exact-head CI and OSV scan: PASS.
- Android WebView safe missing-key fallback: PASS.
- Real Google Maps provider runtime: NOT RUN — key absent.
- S1: PARTIALLY MITIGATED / OPEN.
- A4: PARTIAL / NOT CLOSED.
- A5: NOT STARTED; separate explicit Owner authorization remains required.
