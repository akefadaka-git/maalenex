# MN-008 — Passenger Web and Android API Flow Reconciliation

**Artifact:** MN-008-PASSENGER-WEB-ANDROID-API-FLOW-RECONCILIATION-001  
**Version:** 1.0.0  
**Assessment date:** 2026-11-26  
**Status:** DELIVERED — READ-ONLY CONTRACT RECONCILIATION; END-TO-END ACCEPTANCE PARTIAL  
**Repository:** `akefadaka-git/maalenex`  
**Main baseline:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Method:** Static inspection of PR #38, #42, #43 and #54 descriptions, changed-file inventories, selected source files, workflow records and the MN-006/MN-007 records. No workflow was dispatched and no application or database was executed.

## 1. Executive disposition

MN-008 reconciles the passenger web/PWA and packaged Android client API boundaries. The repository contains a provider-neutral API-origin resolver in PR #54, a broader Android/WebView and backend runtime candidate in PR #43, and an earlier Android connectivity baseline in PR #42.

The principal result is that **the client API-origin contract is specified, but a fully connected passenger web/Android journey against one verified backend is not yet accepted**.

PR #54's successful Android debug APK is a UI/package artifact. Its own instructions state that when `MAALENEX_TEST_API_BASE_URL` is unset, the APK is a UI preview and same-origin requests cannot reach a separately hosted FastAPI service. The PR records that this variable was not configured, cross-origin CORS/cookie/CSRF and end-to-end Android connectivity were not verified, and physical-device acceptance was not run.

PR #43 provides a broader candidate for WebView cookie handling, HTTPS API-origin validation, CORS/CSRF and production-capable runtime configuration. Its exact-head push workflows are recorded as successful in MN-006, but PR-event trigger coverage and several security/lifecycle requirements remain unresolved. A passing push workflow is not a substitute for PR-event coverage or end-to-end runtime acceptance.

## 2. Evidence baseline

| Evidence | Exact reference | Reconciled finding |
|---|---|---|
| Canonical main | `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | Frozen current assessment baseline |
| PR #42 | `d3011e288c7487ebdca824d8c4dcd998ad3cfc7b` | Earlier Android API-connectivity foundation; exact-head Android/backend checks recorded PASS |
| PR #43 | `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | Broader Android/WebView and backend runtime candidate; open/draft/unmerged |
| PR #43 exact-head push runs | Android #45033264442; backend #45033264304 | PASS on the stated head; PR-event coverage not established |
| PR #38 | `046da5e6cb435f2c9baeb2228fc9918287bd584e` | Passenger identity-adjacent notification/inbox and booking-claim client flows; separate unmerged stack |
| PR #54 | `34e4aab8d84561828fb0a1bc8bdce9f914bc32ca` | API-origin resolver, Capacitor Android shell and debug APK workflow |
| PR #54 Android run | #45765359628 | PASS on exact PR #54 head; APK build/artifact evidence only |
| PR #54 frontend/Pages workflow | #45765359641 | Frontend tests/typecheck/build PASS; deployment steps skipped |

PRs #42 and #43 are sibling branches on the same parent. PR #54 is based directly on current main, not on PR #43. These are not one integrated commit and their results must not be combined into a single release-readiness claim.

## 3. Canonical API-origin contract

PR #54's `frontend/src/api.ts` implements the following rules:

1. API paths must begin with `/api/`.
2. An empty configured origin uses same-origin paths, suitable for local development or a reverse-proxy arrangement.
3. A configured origin must be an absolute URL.
4. HTTPS is required except HTTP on `localhost` or `127.0.0.1` for local development.
5. Credentials, non-root paths, query strings and fragments are rejected.
6. The client constructs API URLs from the validated origin; it does not embed a guessed hostname.

PR #43 adds a related Android build-time origin validation contract and credentialed request/session handling. The final integrated client must have one shared API-origin resolver and one shared API client rather than independently constructed fetch paths in each feature.

**Acceptance requirement:** one approved HTTPS test origin must be configured outside source control. It must be confirmed to identify the intended non-production API service. No secret may be placed in a public frontend build variable or APK.

## 4. End-to-end journey contract

The following is the required acceptance sequence, not a claim that the complete sequence has passed:

| Step | Client/API boundary | Required evidence |
|---:|---|---|
| 1 | Launch web/PWA or Android WebView | Correct shell, language, offline and startup-error state |
| 2 | Resolve API origin | Valid HTTPS origin; invalid origin fails closed; no credentials/path/query/fragment |
| 3 | Establish anonymous/guest context | Public catalogue discovery does not require staff or passenger privileges |
| 4 | Passenger registration/login | Credential validation, one-time challenge, session cookie and CSRF behavior verified |
| 5 | Search published trips | API responses use only authorized, published catalogue data |
| 6 | Seat selection and synthetic hold | Server-side availability and concurrency rules; no client-only entitlement |
| 7 | Contact challenge and booking claim | One-time challenge bound to the exact booking and passenger; competing claims fail closed |
| 8 | Reservation recovery and support | Ownership and guest-access boundaries preserved |
| 9 | Logout/session revocation | Session invalidation, cookie behavior and subsequent request rejection verified |
| 10 | Network interruption/recovery | Clear offline state, bounded retries and no duplicate booking/claim mutation |
| 11 | Android geolocation, if requested | Explicit permission, origin restriction, denial/revocation and lifecycle handling |
| 12 | Return to normal service | No synthetic preview is presented as a live booking or operating route |

## 5. Web, PWA and Android security boundary

The integrated acceptance plan must verify all of the following on the same exact candidate SHA:

- Exact HTTPS API origin and exact allowed CORS origins; no wildcard credentialed CORS.
- Secure, HttpOnly session cookie attributes and correct WebView cookie persistence behavior.
- CSRF token acquisition, transmission, origin validation and rejection of invalid requests.
- Android cleartext traffic remains prohibited; only approved API origin is allowed by CSP.
- WebView navigation and geolocation origin policy are tested together.
- Android INTERNET/network permissions are declared without weakening navigation restrictions.
- Geolocation prompts are denied for untrusted origins; denial, retry, cancellation, revocation and navigation while pending are tested.
- Concurrent geolocation prompts cannot overwrite an earlier pending callback. MN-006 identified the current single-pending-callback implementation as a lifecycle/concurrency gap.
- No API key, session token, device credential or server secret is bundled in client assets or APK.
- Guest passenger access is not accidentally converted into staff access or a mandatory account requirement.

## 6. Acceptance and verification gaps

| Item | Status | Evidence still required |
|---|---|---|
| API-origin validation in PR #54 | PASS — source-level contract | Revalidate on final integrated SHA |
| Android debug APK build PR #54 | PASS — CI scope only | Physical-device install and acceptance |
| PR #43 exact-head push workflows | PASS — push CI only | PR-event checks on actual target branch |
| API origin configured for standalone APK | MISSING | Approved test API origin and redacted configuration evidence |
| Cross-origin CORS/cookie/CSRF | NOT VERIFIED | End-to-end test against approved hosted test API |
| Passenger search/booking against connected Android API | NOT RUN | End-to-end synthetic journey on physical device |
| Geolocation lifecycle/concurrency | PARTIAL | Complete Android permission lifecycle test matrix |
| Unified API client across passenger and staff features | PARTIAL | Source-level reconciliation and integration tests |
| Offline retry/idempotency | PARTIAL | Interruption/recovery and duplicate-submit tests |
| Accessibility and physical-device usability | NOT RUN | Amharic/English, text scaling, keyboard, screen reader and device record |

## 7. Required acceptance matrix for A4

A4 must record, per device and exact build:

- Device manufacturer/model, Android version and app build SHA.
- APK SHA-256 and installation/launch result.
- Language, text scaling, screen rotation, keyboard/focus and accessibility results.
- API origin identifier (redacted host label only), TLS result and CORS origin.
- Login/session/CSRF/logout results.
- Search, seat availability, synthetic hold, challenge, claim, recovery and support results.
- Offline transition, recovery, retry and idempotency results.
- Geolocation permission grant/deny/revoke and origin-boundary results.
- Screenshots/log references with tokens, identifiers and personal data redacted.

No real passenger information may be used for this acceptance.

## 8. MN-008 disposition and governance

**MN-008: DELIVERED — CONTRACT AND ACCEPTANCE PLAN RECORDED.**  
**End-to-end passenger web/Android acceptance: PARTIAL / NOT VERIFIED-CLOSED.**

This record does not configure an API host, change a workflow, dispatch CI, modify source, create credentials, provision a provider, run migrations, merge PRs, or deploy. It does not authorize real passenger data, payments, ticket issuance, boarding or commercial operations.

The next step for this workstream is a separately authorized A3 integration followed by A4 execution against an exact integrated candidate.