# A4 evidence and findings disposition — 2026-11-27

## Scope and governance

- Repository: `akefadaka-git/maalenex`
- PR: #43 — passenger backend connectivity foundation
- Working branch: `feat/passenger-backend-connectivity-foundation`
- Base branch: `fix/passenger-password-minimum-six`
- This record covers A4 development verification only.
- PR remains draft and unmerged. No deployment, production migration, production credential use, payment activation or A5 action is authorized.
- Independent external security review remains a mandatory pre-deployment gate only; it is not an A4 closure prerequisite.

## Exact-head CI evidence

At PR head `4609b11ff40953138967401f2070e074bac1440f`:

- Backend run [#45974821581](https://github.com/akefadaka-git/maalenex/actions/runs/45974821581): SUCCESS. PostgreSQL migration baseline, Ruff, backend tests, HTTPS passenger session/CORS/CSRF smoke, Alembic metadata parity, and full migration downgrade/re-upgrade all passed. Pytest reported 112 passed, 1 warning.
- Android run [#45974822194](https://github.com/akefadaka-git/maalenex/actions/runs/45974822194): SUCCESS. Frontend tests/build, CSP contract verifier, API-origin validation, Android assemble/lint, trusted-navigation tests, Android 15 emulator install/launch/WebView probe, SBOM validation and OSV scan passed.
- The Android emulator probe verified the packaged document and React root. It did not navigate to the passenger map or establish live Google Maps rendering.

## Google Maps / CSP finding S1

**Disposition: PARTIALLY MITIGATED — OPEN.**

Evidence and remediation in this A4 continuation:

1. The packaged CSP blocks inline style attributes (`style-src-attr 'none'`) and inline scripts (`script-src-attr 'none'`).
2. The CSP retains `style-src-elem 'unsafe-inline'` for possible Google Maps-generated style elements. This is a narrowly scoped compatibility exception, not a verified necessity.
3. `PassengerGoogleMap` now exposes a non-sensitive `data-map-status` state for runtime evidence collection.
4. The frontend component test now covers:
   - safe explicit missing-key state (no fabricated map);
   - initialization against a controlled Maps API fixture;
   - marker creation for supplied coordinates;
   - drawing published route geometry only; and
   - map bounds initialization.
5. The existing CSP verifier continues to enforce that `unsafe-inline` is permitted only for `style-src-elem`, not script or style attributes.

**Real provider runtime: NOT RUN / UNRESOLVED.** The latest recorded Android emulator run did not enter the map screen. The GitHub integration used for this reconciliation does not expose Actions variable values, so the presence and validity of `VITE_GOOGLE_MAPS_API_KEY` cannot be asserted here. A real Google Maps runtime test also needs a key restricted to the packaged WebView origin and Maps JavaScript API, plus a test fixture containing source-valid coordinates. A mocked Maps API unit test is not evidence of Google-hosted script, tile, font, CSP or API-key compatibility.

**Closure criteria:** run the passenger map in Android WebView with a restricted, valid key; capture `data-map-status=ready`, Google Maps DOM/runtime evidence, and zero CSP violations or main-frame errors; repeat a negative test with no key and confirm the explicit safe fallback. Review the generated network/CSP diagnostics. Only then decide whether the style-element exception can be removed or must remain with a documented provider requirement.

## S2 — PostgreSQL TLS

**Disposition: REMEDIATED IN PRODUCTION CONFIGURATION; DEPLOYMENT-TIME VERIFICATION OPEN.**

Production configuration requires `sslmode=verify-full` and an explicit `sslrootcert` provider CA path; weaker TLS modes and missing CA configuration are rejected. The template and runtime documentation align. Actual provider CA material, production hostname identity, and a live managed-database connection have not been verified because no production database/provider has been provisioned in this A4 scope. Do not represent this as a completed live TLS handshake.

## Warning 1 — FastAPI / Starlette TestClient deprecation

**Disposition: ACCEPTED TEMPORARILY; FOLLOW-UP OPEN.**

The exact-head backend log records:

`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

The backend suite passed 112 tests with this one warning. Do not suppress the warning or change test-client dependencies speculatively. Follow up by validating the supported httpx2/Starlette/FastAPI test-client combination, then migrate the test harness and rerun the complete backend suite.

The same workflow log also contains upstream Node.js deprecation notices (`punycode`, legacy `url.parse()`) and GitHub action Node 20 compatibility notices. These are toolchain/dependency warnings, not failed application tests; track action/runtime upgrades separately and keep actions pinned/verified.

## S3 — Operations integration fixture isolation / mutation guard

**Disposition: DOCUMENTED TEST-COVERAGE LIMITATION; NOT A PRODUCTION BYPASS.**

The operations integration fixture uses a direct fixture path that bypasses the mutation guard. Dedicated endpoint-level tests remain the evidence for mutation and CSRF enforcement. Keep the limitation explicit; do not claim the fixture itself verifies mutation-guard behavior. A future improvement may exercise the guarded API path end-to-end in the integration fixture, but this is not silently treated as completed.

## A4 disposition summary

| Finding / control | Status | Evidence / remaining action |
|---|---|---|
| S1 — Google Maps CSP/runtime | PARTIALLY MITIGATED / OPEN | CSP contract and component tests; real Android WebView provider runtime not run |
| S2 — PostgreSQL TLS | REMEDIATED IN CONFIGURATION | verify-full and explicit CA required; live provider handshake remains A5 input |
| Warning 1 — TestClient deprecation | ACCEPTED TEMPORARILY | 112 tests pass; migrate to supported client stack |
| Warnings 2–3 — per-request TestClient cookies | RESOLVED | prior remediation removed deprecated cookie arguments |
| S3 — operations fixture guard coverage | DOCUMENTED LIMITATION | dedicated mutation/CSRF endpoint tests; fixture does not prove guard behavior |
| Backend exact-head CI | PASS | run #45974821581 |
| Android exact-head CI | PASS | run #45974822194 |

## Current stage decision

A4 remains **PARTIAL / NOT CLOSED**. The new map unit tests improve deterministic component coverage but do not close S1. No merge or deployment is performed by this record. Continue with real Google Maps WebView runtime evidence when the restricted test key and source-valid map fixture are available. A5 remains separate and requires explicit Owner authorization.


## A4 continuation implementation and verification

- Commit `2604a2af7d354bb52f0a3d7a4693fcf5e52568c0`: expose the map component's current state through a non-sensitive `data-map-status` attribute for automated evidence.
- Commit `0247625eebdff478aff8ad89bcb2ccced44beae7`: add controlled Maps API component coverage for missing-key fallback and map/marker/published-geometry initialization.
- Commit `830f5f3a5542fd35f9e6fa640c3dfe42c2a73387`: correct the test fixture's JavaScript constructor semantics after CI exposed that arrow-function mocks cannot be called with `new`.
- Commit `28dfade3b6f562444a9a5a56adeb4945595d4d58`: final test-fixture correction using constructable function mocks.
- Exact-head frontend verification run [#45980451633](https://github.com/akefadaka-git/maalenex/actions/runs/45980451633): SUCCESS at `28dfade3b6f562444a9a5a56adeb4945595d4d58`; 20 frontend tests passed, TypeScript typecheck passed, production build passed, and Android resource validation passed.
- Exact-head Android run [#45980452198](https://github.com/akefadaka-git/maalenex/actions/runs/45980452198): frontend tests, packaged CSP verifier and API-origin validation passed at the time of this record; Android SDK/emulator stages were still in progress.

The initial map fixture attempt failed because its mocked constructors were not constructable. That failure was corrected in commit `28dfade3b6f562444a9a5a56adeb4945595d4d58`; the final frontend test suite then passed. This is test-harness remediation, not a production Google Maps runtime result.
