# MaaleNex A5.3 — Infrastructure, Secrets/Key Lifecycle and TLS Assessment

**Stage:** A5.3 assessment only  
**Status:** ASSESSED — NOT READY; production evidence absent  
**Repository:** `akefadaka-git/maalenex-moto`  
**Branch:** `a5/deployment-readiness-assessment`  
**Assessment date:** 2026-11-09  
**Decision:** **NO-GO for production infrastructure, production credentials, public ingress or live traffic.**

## 1. Scope and safety boundary

This is a repository-backed, read-only assessment of:
- production infrastructure and hosting evidence;
- application configuration and secret handling;
- identity encryption and keyed lookup lifecycle;
- CI secret separation;
- TLS, cookies, reverse-proxy trust and CORS/ingress controls.

It does not provision infrastructure, access a cloud/DNS/secrets account, test a live hostname, retrieve or reveal secret values, connect to SMTP, rotate keys, change runtime guards, process real personal data, enable payment/GPS, deploy, merge, or authorize commercial operation.

The existing safety boundary remains mandatory:
- `APP_ENV` is limited to `development` or `test`;
- `SYNTHETIC_DATA_ONLY=true` is mandatory;
- PostgreSQL must use `localhost`, `127.0.0.1` or `::1` and database `maalenex_dev`;
- no production runtime mode is implemented or authorized.

No code changes to these restrictions are proposed in A5.3.

## 2. Evidence reviewed

Repository artifacts inspected on the A5 assessment branch:
- `backend/app/core/config.py`
- `backend/app/domains/identity/account_service.py`
- `backend/app/domains/identity/accounts.py`
- `backend/app/domains/identity/security.py`
- `backend/app/domains/identity/email_delivery.py`
- `backend/app/routers/auth.py`
- `backend/app/routers/identity.py`
- `backend/app/main.py`
- `backend/app/db/session.py`
- `backend/.env.example`
- root `.env.example`
- `.gitignore`
- `SECURITY.md`
- `README.md`
- `.github/workflows/a5-foundation-verification.yml`

This evidence establishes source-level behavior only. It does not prove how any external host, DNS zone, reverse proxy, cloud account, secrets manager, production SMTP tenant or production database is configured.

## 3. Infrastructure and hosting assessment

**Status: NOT EVIDENCED / PRODUCTION RUNTIME BLOCKED.**

| Control | Finding | Status |
|---|---|---|
| Hosting provider, account owner, region and data residency | No provider/topology evidence was available in the inspected repository artifacts | NOT EVIDENCED |
| Reproducible production infrastructure / IaC | No production deployment topology or IaC was evidenced | NOT EVIDENCED |
| Environment separation | Application supports development/test only; production is rejected | BLOCKED by deliberate guard |
| Database isolation | Runtime permits only loopback PostgreSQL and `maalenex_dev` | PASS for the development safety restriction; production NOT READY |
| Network segmentation/private database | No production network or ingress configuration evidenced | NOT EVIDENCED |
| Capacity, availability, failure and regional connectivity | No production load, resilience or regional connectivity evidence | NOT RUN |
| Provider ownership, cost ceiling, support and exit plan | No contractual/account evidence available | NOT EVIDENCED |

**Finding INF-01 — No production target architecture evidence (HIGH).** A production hosting provider, region, account owner, data-residency assessment, trust-boundary diagram, private network design and infrastructure deployment model are not evidenced. No paid infrastructure should be created as part of this assessment.

**Finding INF-02 — Runtime guard is an intentional hard block (CRITICAL / CONTROLLED).** The current settings validator rejects non-development/test mode, synthetic-only disablement, remote PostgreSQL and database names other than `maalenex_dev`. This is protective behavior. Do not bypass it through environment variables, code edits, proxy configuration or deployment scripts. Any future production architecture requires a separate specification, risk review, test plan and explicit Owner approval.

### Required exit evidence

1. Approved production architecture and data-flow/trust-boundary diagrams.
2. Account owner, provider, hosting region and data-residency/legal assessment.
3. Separate development/staging/production accounts, networks, databases and credentials.
4. Reproducible infrastructure configuration with reviewed change/rollback controls.
5. Private database reachability and ingress isolation tests.
6. Load, outage, regional-connectivity and provider-failure test evidence.
7. Cost ceiling, provider support, renewal ownership and export/exit plan.

## 4. Secrets and cryptographic key lifecycle

**Status: PARTIAL IMPLEMENTATION; NO PRODUCTION KEY-MANAGEMENT EVIDENCE.**

### 4.1 What the code currently does

- Identity encryption and keyed lookup use separate settings: `IDENTITY_ENCRYPTION_KEY` and `IDENTITY_LOOKUP_KEY`.
- The key-material helper requires at least 32 UTF-8 bytes, then derives a 32-byte value with SHA-256.
- Identifier values are encrypted with AES-256-GCM. The stored value is a 12-byte random nonce followed by authenticated ciphertext; identifier type is authenticated as associated data.
- Lookup values use HMAC-SHA-256 with the lookup key.
- Passwords use PBKDF2-HMAC-SHA-256 with 600,000 iterations and per-password random salts; raw passwords are not stored.
- Session and challenge tokens are random opaque values; persisted session/challenge representations use SHA-256 digests.
- Root and backend environment examples leave identity keys and SMTP credentials blank. The root `.gitignore` excludes `.env` files while allowing the example template.
- A5 CI uses synthetic ephemeral test values and a separate test workflow context. Existing SMTP CI credentials are CI test credentials only; they are not production key-management evidence.

### 4.2 Lifecycle gaps

| Control | Finding | Status |
|---|---|---|
| Secret storage | Runtime reads settings from environment/.env; no production secrets manager or equivalent is evidenced | NOT EVIDENCED |
| Production/CI/staging separation | CI test configuration exists; production environment and credentials are not authorized or evidenced | PARTIAL |
| Key entropy and generation ceremony | Minimum byte length is checked, but no approved generation/entropy ceremony or ownership evidence exists | NOT EVIDENCED |
| Key versioning | Encrypted identifier payload has no explicit key-version envelope/metadata | GAP |
| Encryption-key rotation | No staged old/new key decrypt-and-reencrypt procedure is evidenced | GAP |
| Lookup-key rotation | No dual-key lookup or controlled digest re-index migration is evidenced | GAP |
| Revocation/compromise response | No production key compromise and revocation exercise is evidenced | NOT RUN |
| Key backup/recovery | No controlled recovery/escrow procedure or restoration exercise is evidenced | NOT EVIDENCED |
| Secret access audit | No production secrets-manager IAM/access audit evidence is available | NOT EVIDENCED |
| CI exposure boundary | A5 verification workflow does not require production secrets; CI secrets must remain unavailable to untrusted PR jobs | PARTIAL / REVIEW REQUIRED |

**Finding KEY-01 — No managed production secret store (HIGH).** Environment-backed configuration is acceptable for the current synthetic development baseline, but no production secrets manager, scoped IAM, MFA, access audit, break-glass process or secret recovery evidence exists.

**Finding KEY-02 — No versioned encryption-key envelope (HIGH).** AES-GCM ciphertext is stored as nonce plus ciphertext/tag, with identifier type as associated data. The record does not identify a key version. Introducing key rotation without versioned ciphertext and a tested decrypt/re-encrypt migration could make existing identifiers unreadable.

**Finding KEY-03 — Lookup-key rotation is not designed (HIGH).** The lookup HMAC digest is used to find accounts. Rotating its key requires a controlled re-index strategy using decryptable original identifiers, dual-read/dual-write or another explicitly tested migration. Simply replacing the environment variable would make existing identifiers unfindable.

**Finding KEY-04 — Minimum length is not a key-generation standard (MEDIUM).** The 32-byte minimum does not prove cryptographic entropy, uniqueness, independent generation, secure delivery or separation of duties. A documented cryptographic generation ceremony and secret inventory are required.

**Finding KEY-05 — Production secret recovery and compromise handling are unproven (HIGH).** No tested key recovery, rotation, revocation, access review or incident exercise is evidenced.

### Required key-management design before production work

1. Select an approved secrets manager or equivalent protected store; record provider, region, data residency, account owner, access roles and audit capabilities.
2. Maintain separate unique key material for each environment and purpose. Never reuse CI/test keys in staging or production.
3. Define a versioned envelope for encrypted identifiers, including key identifier/version and a backward-compatible migration plan.
4. Define encryption rotation as a staged process: introduce new version, retain narrowly controlled old-key decrypt access, re-encrypt in bounded batches, verify counts/integrity, switch active writes, then revoke/destroy old key only after verified completion and recovery window.
5. Define lookup-key rotation independently, including old/new digest dual lookup and a complete re-index reconciliation; do not overwrite the current key as a shortcut.
6. Define generation, access approval, least privilege, MFA, access logging, backup/recovery, rotation schedule, emergency revocation, personnel departure and destruction procedures.
7. Ensure production secrets are not available to pull-request jobs, untrusted branches, frontend bundles, ordinary build logs or artifacts.
8. Add automated tests for wrong-key failure, ciphertext tampering, key-version selection, rotation/re-index correctness, rollback and secret redaction.
9. Publish a secret inventory containing only purpose, environment, owner, key version, storage location, rotation date and status—never secret values.

No production key should be generated or requested during A5.3.

## 5. TLS, ingress, cookies and network security

**Status: APPLICATION PRIMITIVES EXIST; PRODUCTION TLS/INGRESS NOT EVIDENCED.**

### 5.1 Application-level observations

- `secure_cookies` defaults to false.
- Cookie security is enabled when that setting is true or when the ASGI request URL scheme is HTTPS.
- The application does not trust arbitrary forwarded headers in the inspected configuration. This avoids blindly trusting client-supplied proxy metadata, but there is no explicit trusted-proxy allowlist evidenced.
- Session cookies are HttpOnly, SameSite=Lax and path-scoped; CSRF cookies are JavaScript-readable for the double-submit CSRF pattern. Both use the computed Secure flag.
- CORS allows credentials and defaults to `http://localhost:5173`; the allowed-origin list is environment-configurable.
- SMTP delivery uses Python's default TLS context when STARTTLS or implicit TLS is selected, preserving normal certificate verification.
- SMTP STARTTLS defaults to true, but configuration validation does not require either STARTTLS or implicit SSL when email delivery is enabled. A misconfiguration can therefore permit SMTP transport without TLS.
- No production TLS endpoint, DNS configuration, certificate lifecycle, ingress policy or external TLS scan is evidenced.

### 5.2 Findings

**Finding TLS-01 — No production TLS endpoint evidence (CRITICAL).** No production hostname, DNS ownership evidence, trusted CA certificate, TLS termination point, external scan, renewal alert or ingress policy was available. HTTPS availability cannot be inferred from application code.

**Finding TLS-02 — Reverse-proxy scheme and cookie behavior need an explicit contract (HIGH).** If TLS terminates at a proxy and the ASGI application receives an HTTP request, the request-scheme check alone will not set Secure cookies. The explicit `SECURE_COOKIES` setting can force the flag, but no production configuration or trusted-proxy integration evidence exists. Before any future deployment, specify exactly which proxy terminates TLS, which proxy addresses are trusted, how scheme metadata is conveyed, and how the app rejects spoofed forwarded headers. Do not enable blanket forwarded-header trust.

**Finding TLS-03 — SMTP encryption is configurable but not fail-closed (HIGH).** STARTTLS defaults on, but the validator permits email delivery with both STARTTLS and implicit SSL disabled. Require a TLS transport mode whenever SMTP delivery is enabled, and test downgrade/STARTTLS-unavailable behavior before any future provider activation. No SMTP connection or email was sent during this assessment.

**Finding TLS-04 — CORS is development-default, not a production allowlist (HIGH).** Credentialed CORS defaults to localhost. Production origins, methods, headers and allowed credentials need an explicit reviewed policy. No wildcard or broad origin fallback should be introduced.

**Finding TLS-05 — Ingress and edge protections are not evidenced (HIGH).** No production HTTP-to-HTTPS redirect, HSTS policy, TLS protocol/cipher policy, request-size/time limits, rate limiting at ingress, DDoS controls, security-header/CSP policy, private admin/database exposure test or certificate renewal runbook is evidenced.

### Required exit evidence

1. DNS/domain ownership and MFA evidence for registrar/DNS administration.
2. Trusted CA certificate and automated renewal with expiry alert exercise.
3. HTTPS-only ingress, HTTP redirect, approved TLS protocol/cipher baseline and HSTS rollout plan.
4. External TLS scan for every production hostname.
5. Trusted-proxy allowlist and spoofed-forwarded-header tests.
6. HTTPS browser/API tests proving Secure, HttpOnly, SameSite and CSRF behavior behind the actual TLS terminator.
7. Reviewed CORS allowlist, security headers/CSP, ingress rate/size/time limits and private database/admin reachability.
8. Certificate renewal, DNS change/failover and ingress outage runbooks.
9. SMTP TLS-only configuration validation and non-delivery connectivity test in an explicitly authorized non-production environment.

## 6. Risk register and disposition

| ID | Risk | Severity | Disposition |
|---|---|---|---|
| INF-01 | No production hosting/topology/data-residency evidence | HIGH | OPEN |
| INF-02 | Current runtime explicitly blocks production | CRITICAL / intentional | PRESERVE; do not bypass |
| KEY-01 | No managed production secrets store/IAM evidence | HIGH | OPEN |
| KEY-02 | No versioned encryption-key envelope/rotation migration | HIGH | OPEN |
| KEY-03 | Lookup-key rotation/re-index not designed | HIGH | OPEN |
| KEY-04 | No approved key entropy/generation ceremony | MEDIUM | OPEN |
| KEY-05 | No key recovery/revocation exercise | HIGH | OPEN |
| TLS-01 | No production TLS endpoint/certificate/DNS evidence | CRITICAL | OPEN |
| TLS-02 | Reverse-proxy trust and Secure-cookie deployment contract absent | HIGH | OPEN |
| TLS-03 | SMTP TLS can be disabled by configuration | HIGH | OPEN |
| TLS-04 | CORS defaults to localhost | HIGH | OPEN |
| TLS-05 | No ingress/edge hardening or external scan evidence | HIGH | OPEN |

## 7. A5.3 gate results

| Gate | Result |
|---|---|
| Repository configuration and identity crypto source inspection | PASS — assessment completed |
| Production infrastructure evidence | NOT EVIDENCED |
| Production secrets manager and access controls | NOT EVIDENCED |
| Encryption key versioning/rotation/recovery | NOT READY |
| Lookup key rotation/re-index plan | NOT READY |
| Production TLS/DNS/certificate evidence | NOT EVIDENCED |
| Trusted proxy and production cookie behavior | NOT RUN |
| External TLS scan | NOT RUN |
| SMTP TLS downgrade/negative tests | NOT RUN |
| Provisioning, key generation, rotation or deployment | NOT PERFORMED / NOT AUTHORIZED |

**A5.3 outcome: PARTIAL assessment complete; all production readiness controls remain NOT READY or NOT EVIDENCED.** Source-level protections are useful but cannot substitute for operational evidence.

## 8. Next actions (separately gated)

1. A5.3.1 — prepare a production architecture decision record and trust-boundary/data-flow diagram, without selecting or purchasing a provider.
2. A5.3.2 — prepare a versioned identity-encryption and lookup-key lifecycle design, including migration, rollback and recovery test specifications. No keys are to be generated.
3. A5.3.3 — specify a TLS termination, trusted-proxy, cookie, CORS and ingress security contract. No DNS or certificate changes.
4. A5.3.4 — add safe configuration validation and synthetic tests for fail-closed SMTP TLS and proxy/cookie behavior only after the Owner separately authorizes implementation.
5. Reassess external provider/account evidence only when supplied through an authorized, secure channel. Do not request or place secrets in chat or Git.

A5.3 closure requires verified design artifacts and evidence for the scoped controls; it does not itself authorize production provisioning or deployment. Production activation remains a separate approval gate.
