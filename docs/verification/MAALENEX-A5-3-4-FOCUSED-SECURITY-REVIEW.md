# MaaleNex A5.3.4 Focused Security Review

**Review date:** 2026-11-09  
**Reviewed implementation HEAD:** `973660973bcdd328d725bf22ef7f3b154eab8d18`  
**Branch:** `a5/a5-3-4-edge-security-hardening`  
**PR:** #11 — open, draft, unmerged  
**Verification evidence:** [A5.3.4 exact-HEAD workflow #42568620218](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42568620218), success on the reviewed HEAD  
**Review type:** focused static security review of application source, router mutation inventory, security tests and approved A5.3.3 contract. This is not a penetration test or a live edge/TLS assessment.

## Executive disposition

**A5.3.4 implementation: PARTIAL — automated verification PASS; focused security review found remediation items.**

Positive findings:
- All 26 operator, catalog, fleet, trip, fare and support mutation routes in `backend/app/routers/admin.py` use `_require_mutation()`, which delegates to staff `require_csrf()`. That helper enforces strict allowed-Origin validation and the session-bound double-submit CSRF token.
- Staff logout and all three account-session revocation routes also enforce Origin and session-bound CSRF.
- CORS configuration uses explicit origins, rejects wildcard/null origins and non-loopback HTTP, rejects duplicate normalized origins, and normalizes scheme/host/default ports before constructing the allowlist.
- The trusted-proxy middleware trusts only the immediate peer address, rejects duplicate/comma-separated or downgrade forwarded-proto values when present, validates forwarded hosts against the configured canonical-host allowlist, and strips the common forwarding headers before routing.
- Session cookies are host-only, HttpOnly, SameSite=Lax; the CSRF cookie is intentionally script-readable and checked against a server-side digest.

Findings requiring remediation before any production-bound deployment:
1. A trusted proxy request with no `X-Forwarded-Proto` is accepted as HTTP instead of rejected. This can cause session cookies to be issued without Secure.
2. Rate limiting uses `request.client.host`, while the proxy middleware removes `X-Forwarded-For` and leaves the ASGI client address as the proxy. Behind a shared reverse proxy, users share one rate-limit identity.
3. Staff/account login and guest-booking challenge verification accept a missing Origin header, contrary to the strict Origin contract. This is a contract gap and login/session-bootstrap hardening issue; this review did not establish a working account-takeover exploit.
4. The response-header middleware does not add HSTS or CSP, both of which remain absent from the implemented baseline and must be addressed/verified at the production edge before release.

Production remains **NOT READY**. Runtime settings still prohibit production mode, non-synthetic data and remote databases. No production infrastructure or public edge was tested.

## Findings

### F-01 — Trusted proxy accepts missing HTTPS scheme metadata

**Severity:** P1 — deployment blocker  
**Status:** CONFIRMED

Evidence:
- `backend/app/core/proxy.py`: the trusted-peer scheme check is guarded by `if trusted and forwarded_proto`; it validates the value only when the header exists.
- The ASGI scheme is upgraded only under `if trusted and forwarded_proto`; when the trusted peer omits the header, the request proceeds with the original scheme (normally HTTP from a TLS-terminating proxy).
- `backend/tests/test_edge_security_config.py` contains `test_trusted_proxy_without_https_metadata_does_not_upgrade_scheme`, which explicitly expects HTTP 204 and an HTTP scope when a trusted peer omits the header.
- `backend/app/routers/auth.py` and `backend/app/routers/identity.py` derive the Secure cookie attribute from `request.url.scheme` (or the explicit `SECURE_COOKIES` setting). The default is false.

Impact:
- A misconfigured trusted proxy can silently downgrade the application’s request scheme and cause staff/account session cookies to be emitted without Secure.
- This contradicts the A5.3.3 contract that a trusted TLS-terminating proxy must provide exactly one canonical `X-Forwarded-Proto: https` value and malformed/missing proxy metadata must fail closed.

Required remediation:
- For a request whose immediate peer is in the trusted-proxy allowlist, require exactly one `X-Forwarded-Proto` header with the value `https`; reject missing, duplicate, comma-separated, empty or non-HTTPS values.
- Keep direct untrusted development requests governed by the existing development policy; do not trust arbitrary client-supplied forwarding headers.
- Replace the current “missing metadata is accepted as HTTP” test with fail-closed tests, including duplicate headers, comma-joined values, empty value and HTTP downgrade.

### F-02 — Rate-limit identity collapses to the reverse-proxy address

**Severity:** P2 — availability and abuse-control defect  
**Status:** CONFIRMED

Evidence:
- `backend/app/core/proxy.py` removes `X-Forwarded-For` from the request headers and does not place a separately validated client address into ASGI scope.
- `backend/app/routers/auth.py` and `backend/app/routers/identity.py` derive the login rate-limit client IP from `request.client.host`.
- `backend/app/routers/bookings.py` uses the same `request.client.host` approach for guest booking and challenge rate limits.

Impact:
- Behind a shared proxy, `request.client.host` identifies the proxy, not the end user. Unrelated users can share one login/challenge rate-limit bucket. One client can consume or lock the shared bucket, causing denial of service or false lockouts for other users.

Required remediation:
- Define a trusted-proxy client-address contract: the edge must overwrite/normalize the client-IP metadata, and the application must accept it only from a trusted immediate peer with strict single-value/chain validation.
- Preserve the immediate peer separately for trust decisions; never accept client-supplied `X-Forwarded-For` from an untrusted peer.
- Add tests proving spoofed client IPs from untrusted peers are ignored and distinct clients behind a trusted proxy receive distinct rate-limit identities.

### F-03 — Missing Origin is accepted by login and guest challenge bootstrap

**Severity:** P2 — browser-request policy gap  
**Status:** CONFIRMED policy gap; exploitability not demonstrated

Evidence:
- `backend/app/routers/auth.py`, `create_staff_session`: rejects an Origin only when one is present and not allowed; absent Origin continues to authentication and issues session cookies.
- `backend/app/routers/identity.py`, `create_account_session`: uses the same optional-Origin pattern and issues account session cookies.
- `backend/app/routers/bookings.py`, `_require_origin`: rejects a present disallowed Origin but accepts a missing Origin. It is called by booking challenge verification and the cookie-authenticated booking mutation handlers.
- By contrast, `backend/app/core/request_security.py` `require_allowed_origin()` correctly rejects both missing and unapproved Origin values.
- The guest reservation/support/revoke mutation handlers additionally verify the booking CSRF cookie/header against the grant’s server-side digest. The staff and account session revocation routes likewise use strict Origin and CSRF checks.

Impact:
- The login/session-bootstrap and booking challenge-bootstrap endpoints do not uniformly enforce the approved strict Origin contract. This weakens login-CSRF and session-bootstrap defenses and makes policy behavior inconsistent.
- The existing double-submit CSRF checks on guest booking mutations materially reduce their exposure; this finding is not a claim that those endpoints currently permit a cross-site attacker to bypass the CSRF token.

Required remediation:
- Reuse strict `require_allowed_origin()` on browser login/session-creation and booking challenge-verification endpoints.
- Replace the optional booking `_require_origin()` helper with the shared strict helper for cookie-authenticated mutations.
- Add HTTP-level tests for missing, null, duplicate, malformed, disallowed and allowed Origin values on each browser session/bootstrap and mutation family.
- Keep non-browser/service-to-service flows explicit and separately authenticated; do not weaken browser checks to accommodate them.

### F-04 — HSTS and CSP are not emitted by application edge middleware

**Severity:** P2 — production hardening gap  
**Status:** CONFIRMED

Evidence:
- `backend/app/core/proxy.py` adds `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options` and `Permissions-Policy`.
- It does not add `Strict-Transport-Security` or `Content-Security-Policy`.
- No public TLS endpoint, ingress configuration or external TLS/header scan exists in this repository evidence.

Impact:
- The application itself does not provide HSTS/CSP evidence. A future edge may supply these, but that has not been configured or verified.

Required remediation:
- Define ownership for HSTS and CSP (application or ingress) and ensure there is exactly one effective policy.
- Enable HSTS only after HTTPS is universal for the intended host/subdomain scope and certificate/redirect behavior is verified. Do not enable `includeSubDomains` or preload without explicit domain-wide readiness.
- Define and test a CSP compatible with the actual frontend asset/API architecture; avoid an unreviewed permissive policy.
- Verify final response headers through the deployed edge before any production gate.

## Browser mutation and session-route inventory

| Route family | Inventory | Review result |
|---|---:|---|
| Admin/operator/catalog/fleet/trip/fare/support POST mutations | 26 routes | **PASS** — every handler calls `_require_mutation()`; helper delegates to strict Origin + session-bound CSRF |
| Staff session revocation | 1 route | **PASS** — strict Origin + CSRF |
| Account session revocation | 3 routes | **PASS** — strict Origin + session-bound CSRF |
| Staff login | 1 route | **PARTIAL** — disallowed Origin rejected, missing Origin accepted |
| Account login | 1 route | **PARTIAL** — disallowed Origin rejected, missing Origin accepted |
| Guest booking reservation/support/access-revoke | 3 routes | **PARTIAL** — booking CSRF checked, but Origin helper accepts missing Origin |
| Guest booking challenge verification (sets access/CSRF cookies) | 1 route | **PARTIAL** — missing Origin accepted during cookie bootstrap |
| Guest booking cancellation | 1 route | **DISABLED** — returns 409; no cancellation mutation |
| Ticket issue / boarding validation | 2 routes | **DISABLED** — return 409 |
| Public hold/challenge, registration/recovery and token-based verification | Public/token workflows | Not cookie-authenticated mutation routes; separate abuse/rate-limit and token lifecycle review remains necessary |

This inventory is based on the registered FastAPI routers at the reviewed HEAD. The 26 admin handlers were individually checked for the shared helper call; this corrects the preliminary scan that initially overlooked the helper indirection.

## Proxy and CORS assessment

### Trusted-proxy controls that passed static review
- Trust is based on the immediate socket peer, not on an untrusted forwarded header.
- CIDR configuration is validated and broad networks are rejected by the settings validator.
- Forwarded host values, when present, must match the canonical-host allowlist.
- Duplicate or comma-separated forwarded-proto values and explicit HTTP downgrade values are rejected.
- Common forwarding headers are stripped before request handlers execute.
- Trusted-proxy middleware is installed outside CORS middleware so proxy metadata is normalized before CORS and routing.

### Remaining proxy gaps
- Missing HTTPS proto metadata is accepted (F-01).
- The client IP is not safely propagated for per-client rate limiting (F-02).
- No real proxy/ingress was available for an end-to-end trust-boundary test.
- The exact proxy must be configured to remove inbound client-supplied forwarding headers and write its own single canonical values. Application allowlisting alone cannot prove the proxy performs that overwrite.

### CORS controls that passed static review
- Exact origin list; no wildcard or `null`.
- Non-loopback HTTP origins rejected.
- Raw and normalized duplicate origins rejected.
- Scheme/host case and default ports normalized.
- Credentialed CORS uses explicit origins, explicit methods (`GET`, `POST`, `DELETE`) and explicit request headers.
- The current router inventory uses POST/DELETE for mutations; no PUT/PATCH route was found in the reviewed router modules.

### CORS test/assurance limitations
- The CORS middleware test is an isolated FastAPI probe, not a full application integration test across all browser mutation routes.
- No live browser, public origin, ingress, TLS or subdomain integration test was performed.
- CORS is not a substitute for server-side Origin and CSRF validation.

## Cookie and CSRF assessment

- Staff/account session cookies are HttpOnly, SameSite=Lax, host-only and have bounded lifetimes.
- CSRF cookies are intentionally readable by the frontend and paired with a request header; server-side digest checks prevent arbitrary cookie/header values from passing.
- Staff admin mutations and staff/account session revocation enforce strict Origin plus CSRF.
- Secure is derived from the ASGI request scheme or explicit `SECURE_COOKIES`; therefore F-01 directly affects cookie security when trusted proxy metadata is missing.
- Guest booking access/CSRF cookies are also scheme-derived. Guest access-cookie deletion currently omits the Secure attribute on the deletion Set-Cookie headers; this is a consistency issue to correct and test alongside cookie lifecycle work, not a demonstrated authentication bypass.
- Login/session creation and guest challenge verification need strict Origin enforcement (F-03).

## Verification evidence and limits

- Reviewed exact source HEAD: `973660973bcdd328d725bf22ef7f3b154eab8d18`.
- Exact-HEAD GitHub Actions run #42568620218 passed all three jobs: backend/PostgreSQL/migrations, frontend/typecheck/build/npm audit, and Python dependency/Bandit checks.
- Backend suite: 70 passed, 1 warning; Ruff, migration, registry seed, Alembic parity and downgrade/re-upgrade steps passed.
- The CI pass establishes build/test success, not security closure. Existing edge tests include a test that codifies the missing-proto acceptance behavior; it must be changed when F-01 is remediated.
- No independent penetration test, external SAST/DAST assessment, live TLS scan, production ingress test or production secret/identity lifecycle exercise was performed.

## Required remediation order

1. **F-01:** require HTTPS forwarding metadata from trusted peers and fail closed; update middleware tests.
2. **F-03:** enforce strict Origin on login and guest challenge/session-bootstrap routes; add route-level regression tests.
3. **F-02:** define trusted client-IP propagation for rate limiting and test spoofing/isolation.
4. **F-04:** finalize HSTS/CSP ownership and validate them at a real edge before production.
5. Align guest booking cookie deletion attributes and add full cookie lifecycle assertions.

## Governance disposition

- Focused review: **COMPLETED — FINDINGS OPEN**.
- A5.3.4 implementation: **NOT SECURITY-CLOSED** until F-01 through F-03 are remediated and exact-HEAD tests pass.
- A5 production readiness: **NOT READY**.
- PR #11 remains draft/open/unmerged.
- No changes were made to application code, database schema, runtime environment, production settings, secrets, DNS, certificates, hosting, ingress or network resources during this review.
- No merge, deployment, live payment, GPS, real-data processing or production activation was performed.


## Remediation follow-up — implementation review

The three application findings in this review were remediated on the isolated PR #11 branch, in the requested order:

- **F-01 — VERIFIED-CLOSED:** trusted proxies now fail closed unless exactly one HTTPS forwarded-proto value is present. Missing, empty, duplicate, comma-list and HTTP downgrade cases have regression tests.
- **F-03 — VERIFIED-CLOSED:** browser staff/account session creation, guest challenge verification and guest cookie-authenticated booking mutations now require exactly one exact allowlisted Origin. The shared guard rejects missing, duplicate, malformed, non-ASCII, comma-list and null values. Route-level tests cover session and guest-booking endpoints.
- **F-02 — VERIFIED-CLOSED:** trusted-proxy client IP is accepted only from a single valid edge-overwritten X-Forwarded-For value. The ASGI client identity used by rate-limit call sites is set to that parsed IP; the immediate proxy peer is retained separately. Untrusted peers cannot alter their rate-limit identity.

The final edge must strip inbound X-Forwarded-For and set exactly one client IP. This single-hop trust profile is documented; arbitrary multi-proxy chains remain unsupported.

**Current disposition:** F-01/F-02/F-03 are VERIFIED-CLOSED for the reviewed application scope. Exact-HEAD CI passed on `3bce5b81c91ad9a573a02e55d3a6e2f6da1a3121` ([run #42571302514](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42571302514)); backend/PostgreSQL 82 passed, 1 warning, and frontend, dependency and Bandit jobs passed. F-04 remains open as an ingress/hosting acceptance gate; no HSTS policy is enabled without confirmed universal HTTPS, and CSP must be finalized against the deployed frontend. This focused source review is not an independent penetration test, external SAST/DAST assessment, or live TLS scan.


### Exact-HEAD verification evidence

- Commit: `3bce5b81c91ad9a573a02e55d3a6e2f6da1a3121`
- Workflow: [#42571302514 — success](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42571302514)
- Backend/PostgreSQL: 82 passed, 1 warning; compile, Ruff, migrations, seed idempotency, Alembic parity and downgrade/re-upgrade PASS.
- Frontend tests, TypeScript, Vite build, npm audit, pip-audit and Bandit PASS.

F-04 remains OPEN and is not remediated by this application change. Actual TLS termination, HSTS/CSP ownership, ingress/network policy, external scan and provider configuration require a separately approved production-edge environment. No penetration test, live TLS scan, merge or deployment is claimed.
