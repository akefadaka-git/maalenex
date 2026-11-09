# MaaleNex A5.3.4 — Fail-Closed Edge Security Implementation Report

**Stage:** A5.3.4 implementation and synthetic verification  
**Status:** IMPLEMENTED ON ISOLATED BRANCH; exact-HEAD GitHub Actions verification PASS on `60ea65e85a6a02e9467ab10ea0970750d49c5376` (run [#42568481664](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42568481664))  
**Repository:** `akefadaka-git/maalenex-moto`  
**Implementation branch:** `a5/a5-3-4-edge-security-hardening`  
**Review PR:** [#11 — A5.3.4 edge security configuration and regression tests](https://github.com/akefadaka-git/maalenex-moto/pull/11)  
**Base:** `a5/deployment-readiness-assessment`  
**Owner authorization:** Approved in conversation before implementation.

## 1. Scope and outcome

Implemented the application-level controls that can be safely exercised without selecting or provisioning production infrastructure:

- startup validation for exact credentialed CORS origins;
- validation of explicit trusted-proxy IP/CIDR entries and paired canonical hosts;
- fail-closed processing of forwarded scheme/host metadata based on the immediate socket peer;
- removal of forwarded/client-IP headers before application routing;
- baseline HTTP security response headers;
- exact Origin validation for cookie-authenticated session mutations, in addition to the existing CSRF token/digest checks;
- Secure attribute preservation when session cookies are cleared;
- mandatory SMTP transport TLS whenever email delivery is enabled;
- a dedicated synthetic verification workflow;
- documented Uvicorn launch with built-in proxy-header handling disabled.

The implementation does not claim to configure or secure a real public ingress. TLS protocol/cipher configuration, certificate validity/renewal, edge redirects, HSTS, WAF, network firewalling, provider topology and external scans remain operationally unverified.

## 2. Application changes

| File | Change |
|---|---|
| `backend/app/core/config.py` | Exact-origin validation and normalization; reject wildcard, null, malformed and non-loopback HTTP origins; reject duplicate origins after default-port normalization; validate trusted proxy CIDRs and canonical-host pairing; preserve development/test, synthetic-only and local DB hard stops; require SMTP TLS when delivery is enabled |
| `backend/app/core/proxy.py` | New pure-ASGI middleware: trust immediate peer only; accept only one HTTPS forwarded-proto value; validate forwarded host against exact canonical hosts; reject duplicate/conflicting/malformed metadata; strip forwarded headers; add baseline response security headers |
| `backend/app/core/request_security.py` | Exact allowed-Origin requirement for cookie-authenticated state changes |
| `backend/app/main.py` | Install trusted-proxy middleware outside CORS middleware so validated scheme/host are established before CORS and routing |
| `backend/app/routers/auth.py` | Require exact Origin alongside existing staff CSRF verification; preserve Secure when clearing session/CSRF cookies |
| `backend/app/routers/identity.py` | Require exact Origin alongside existing account CSRF verification; preserve Secure when clearing all account session/CSRF cookies |
| `backend/tests/test_edge_security_config.py` | Synthetic configuration, proxy-spoofing, host-validation, secure-scheme, CORS and SMTP TLS regression tests |
| `backend/.env.example` | Document paired trusted-proxy/canonical-host settings and exact CORS/Secure-cookie settings |
| `README.md` | Disable Uvicorn implicit proxy-header trust in the documented launch command |
| `.github/workflows/a5-3-4-edge-security-verification.yml` | Exact-branch / PR verification: backend/PostgreSQL, frontend, dependency audit and Bandit |

## 3. Security behavior implemented

### Proxy and host handling

- No proxy trust is configured by default.
- `TRUSTED_PROXY_IPS` and `CANONICAL_HOSTS` must be configured together.
- Overly broad CIDRs are rejected: IPv4 must be `/24` or narrower and IPv6 `/64` or narrower; entire address-family trust is impossible.
- Untrusted forwarded headers are stripped and cannot upgrade the ASGI scheme.
- Trusted peers must provide one unambiguous `X-Forwarded-Proto: https` value to establish HTTPS.
- Forwarded host values must exactly match configured canonical hosts.
- Uvicorn built-in proxy-header handling is disabled in the documented command so it cannot independently normalize forwarded headers before the application middleware.

### Cookie and CSRF behavior

- Session cookies remain HttpOnly, SameSite=Lax and host-only (no Domain attribute).
- Secure is true for direct HTTPS or a scheme normalized by the trusted-proxy middleware; an explicit `SECURE_COOKIES=true` can force Secure in a controlled environment.
- Cookie deletion now retains the Secure attribute decision.
- Cookie-authenticated session revocation requires an exact configured Origin and the existing double-submit plus server-stored CSRF digest check.
- Existing admin mutation routes invoke the same CSRF guard; all 26 implemented admin mutation routes invoke the CSRF guard, and the 3 account-session revocation routes invoke the same Origin-plus-CSRF guard; A5.2 operator HTTP fixtures supply the exact development Origin and CSRF cookie/header.

### CORS and SMTP

- CORS origin values are parsed as exact HTTP(S) origins, normalized for scheme/host and default ports, and reject wildcard, null, path, query, fragment, credentials and non-loopback plaintext HTTP origins.
- Credentialed CORS continues to use explicit allowed origins, not wildcard or reflected origins.
- Enabled SMTP delivery now fails startup validation if both STARTTLS and implicit TLS are disabled. This is configuration validation only; this task did not connect to SMTP or send email.

## 4. Verification

### Isolated synthetic unit execution

A local isolated test run using the implementation and test source copied from this branch completed:

- **23 tests passed**
- Python runtime: 3.13.5
- Covered SMTP TLS fail-closed validation, exact CORS validation and response behavior, duplicate/default-port normalization, narrow proxy CIDR validation, Origin validation, trusted/untrusted peer behavior, forwarded-header stripping, host spoofing rejection, secure-scheme derivation and response security headers.

This isolated run is not a substitute for the repository's exact-HEAD GitHub Actions workflow or the full PostgreSQL integration suite.

### GitHub Actions

- Dedicated workflow added: `.github/workflows/a5-3-4-edge-security-verification.yml`.
- Jobs: backend/PostgreSQL/migrations/full pytest, frontend tests/typecheck/build/npm audit, Python pip-audit and Bandit.
- Workflow sets `APP_ENV=test`, `SYNTHETIC_DATA_ONLY=true`, local `maalenex_dev`, disables SMTP delivery and hides test tokens.
- **Exact-HEAD GitHub Actions result: PASS** — run [#42568481664](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42568481664), workflow run #27, tested commit `60ea65e85a6a02e9467ab10ea0970750d49c5376`.
- The workflow was corrected so every checkout uses `${{ github.event.pull_request.head.sha || github.sha }}`; backend job logs confirm checkout and `git log -1` both resolved to the exact branch HEAD `60ea65e85a6a02e9467ab10ea0970750d49c5376`.
- Backend/PostgreSQL: compile PASS; Ruff PASS; migrations PASS; registry seed idempotency PASS; full PostgreSQL test suite **70 passed, 1 warning**; Alembic parity PASS; full downgrade and clean re-upgrade PASS.
- Frontend: clean lockfile install, tests, TypeScript, Vite build and npm audit all PASS.
- Python security: pip-audit and Bandit high-severity scan both PASS.
- The earlier run #42568318940 is superseded: it exposed the missing `_canonical_origin` helper and failed Ruff. The helper was added in commit `a418474d4e7680d5529c6c7994aeb61f6c747643`; the corrected exact-HEAD run above passes.
- Branch history reconciliation: assessment branch `4a88653b1caef2c594587e24c67f004967b9bc10` is now an ancestor of the implementation branch; comparison is 35 ahead / 0 behind. PR #11 remains draft and unmerged.

## 5. Safety and non-authorizations

- `APP_ENV` remains restricted to `development` or `test`.
- `SYNTHETIC_DATA_ONLY=true` remains mandatory.
- PostgreSQL remains loopback-only and database `maalenex_dev`.
- No production runtime mode or production host has been added.
- No trusted proxy CIDRs or canonical production hosts have been configured in the current runtime.
- No DNS, certificate, TLS endpoint, firewall, ingress, WAF, hosting, infrastructure, secret or key was changed or provisioned.
- No real personal data, SMTP connection/email, SMS, payment, GPS, public endpoint scan or external TLS scan was performed.
- No production deployment, merge, pilot or commercial activation occurred.
- PR #11 remains draft and unmerged.

## 6. Remaining gaps

1. Exact-HEAD GitHub Actions run and complete repository test suite must pass.
2. Review all existing browser mutation flows against the Origin/CSRF guard.
3. Verify real ASGI-server launch configuration and trusted-proxy chain in a separately approved staging topology.
4. Configure and externally verify TLS protocols/ciphers, certificates, renewal, redirects, HSTS, ingress limits, firewall isolation, rate controls and logging only after provider/topology approval.
5. Exercise certificate, proxy, CORS, session and ingress incident/rollback runbooks.
6. Keep privacy, Ethiopian regulatory, backup/recovery, monitoring and operations gates open.

**A5.3.4 disposition: IMPLEMENTED ON ISOLATED BRANCH; automated repository verification pending.**  
**Overall A5 readiness: NOT READY / NO-GO.**  
Implementation does not authorize merge, provisioning, deployment or production activation.

## Focused security review

- Review report: [MAALENEX-A5-3-4-FOCUSED-SECURITY-REVIEW.md](MAALENEX-A5-3-4-FOCUSED-SECURITY-REVIEW.md)
- Reviewed exact application HEAD: `973660973bcdd328d725bf22ef7f3b154eab8d18`.
- Disposition: **COMPLETED — FINDINGS OPEN**. F-01 trusted-proxy missing HTTPS metadata (P1), F-02 proxy client-IP/rate-limit collapse (P2), F-03 optional Origin on login/guest challenge bootstrap (P2), F-04 HSTS/CSP edge hardening (P2).
- Confirmed positive control: all 26 admin mutation handlers enforce strict Origin plus session-bound CSRF through `_require_mutation()`; staff/account session revocation routes also enforce CSRF.
- A5.3.4 is **NOT SECURITY-CLOSED** pending F-01 through F-03 remediation and exact-HEAD regression tests. No application-code changes were made during the review.


## 8. Focused-review remediation — F-01, F-03 and F-02

The focused-review findings were addressed in the order requested:

1. **F-01 — trusted proxy HTTPS metadata:** trusted immediate peers now require exactly one X-Forwarded-Proto: https. Missing, blank, duplicate, comma-separated and downgraded values fail with HTTP 400 before routing. The prior permissive regression test was replaced with explicit fail-closed cases.
2. **F-03 — browser Origin enforcement:** staff and account session creation now call the shared strict Origin guard. Guest booking challenge verification and all guest cookie-authenticated booking mutations use the strict guard. The guard inspects raw ASGI headers and rejects missing, duplicate, non-ASCII, comma-list, null and non-allowlisted Origin values. Route-level regression tests exercise staff login, account login, guest challenge verification and guest reservation mutation.
3. **F-02 — rate-limit client identity:** for a trusted immediate proxy only, the middleware requires one valid IP literal in X-Forwarded-For, treats the final edge as responsible for overwriting that header, maps the validated address into the ASGI client identity used by existing rate-limit call sites, and retains the immediate proxy peer separately in scope["maalenex.proxy_peer"]. Missing, duplicated, comma-separated, blank and invalid values fail closed. Untrusted peers retain their direct socket identity and cannot spoof it with forwarding headers.

The approved ingress contract was clarified to require a single-hop final edge that strips inbound X-Forwarded-For and writes exactly one observed client address. Multi-proxy chains are not supported by this G1 profile.

Regression coverage now includes trusted-proxy scheme failure, client-IP separation across requests, spoof resistance, invalid client-IP rejection, duplicate/malformed Origin rejection and authenticated/browser route Origin gates.

**Verification status:** **PASS — exact-HEAD CI completed** on `3bce5b81c91ad9a573a02e55d3a6e2f6da1a3121` ([workflow #42571302514](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42571302514)). Backend/PostgreSQL suite: **82 passed, 1 warning**; compile, Ruff, migrations, registry seed idempotency, Alembic parity and full downgrade/re-upgrade passed. Frontend tests, TypeScript, Vite build and npm audit passed. pip-audit and Bandit passed. No production proxy, DNS, certificate, ingress, runtime configuration, secret, email, payment, GPS, merge or deployment action was performed. F-04 (HSTS/CSP ownership and live-edge verification) remains a production-edge acceptance gate.


## 9. Exact-HEAD verification closure

- Exact source HEAD: `3bce5b81c91ad9a573a02e55d3a6e2f6da1a3121`
- GitHub Actions: [run #42571302514 — success](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42571302514)
- Backend/PostgreSQL: 82 passed, 1 warning; compilation, Ruff, migrations, registry seed idempotency, Alembic metadata parity, full downgrade and clean re-upgrade all PASS.
- Frontend: clean lockfile install, tests, TypeScript typecheck, Vite build and npm audit PASS.
- Python security: pip-audit and Bandit high-severity scan PASS.
- The run checked out the exact branch commit; all three jobs completed successfully.

**F-01, F-02 and F-03: VERIFIED-CLOSED for the application-level scope and regression coverage described in this report.** F-04 remains OPEN as a production-edge acceptance gate: HSTS/CSP ownership, actual TLS termination, ingress behavior and external edge verification still require an approved hosting/ingress environment. This does not establish production readiness or authorize merge/deployment.


## 10. F-04 production-edge design disposition

The Owner-requested F-04 design and acceptance package is recorded in [A5.3.5 F-04 Production-Edge Security Design and Acceptance](MAALENEX-A5-3-5-F04-PRODUCTION-EDGE-DESIGN-AND-ACCEPTANCE.md). It assigns HSTS and CSP exclusively to the public ingress edge, defines TLS termination/private encrypted origin topology, staged HSTS rollout, CSP report-only-to-enforced rollout, exact external evidence IDs, operational rollback and production no-go criteria. No provider, hostname or infrastructure was selected or provisioned; no runtime or application code changed.

**F-04: DESIGN-RESOLVED / OPERATIONAL ACCEPTANCE PENDING.** No live TLS scan, public redirect/header probe, CSP browser observation, origin-bypass test or operational rollback exercise is claimed. Overall production readiness remains NOT READY / NO-GO.
