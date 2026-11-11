# MaaleNex Platform — A2 Read-only Reconciliation and Closure Report

**Status:** A2 READ-ONLY RECONCILIATION — VERIFIED-CLOSED WITH RECORDED GAPS  
**A1 baseline:** `docs/MAALENEX-PLATFORM-A1-v1.1.md`, Owner-approved and frozen 2026-11-08  
**Authoritative repository:** `akefadaka-git/maalenex-moto`  
**Default branch:** `main`  
**Exact main SHA inspected:** `72550a2e464f6517653580bb1ae4e7608f211f39`  
**Report date:** 2026-11-08

> This is a read-only baseline and integration assessment. No application code, database migration, default-branch ref, merge, release or deployment was changed by A2. A3 implementation is authorized after this A2 closure, on isolated feature branches. Merge and A5 deployment remain separately gated.

## 1. Executive determination

A1 v1.1 is the frozen product baseline for the eight service lines: Move, Transit, Delivery, Cargo, Market, Fleet, Business and Pay.

The repository contains a reusable but incomplete passenger-mobility foundation. It is not yet a complete multi-service platform. Existing implementation work is split across a dependency stack. The primary implementation path is:

1. G1 repository/runtime/database foundation (PR #1).
2. Passenger identity, organization, catalog, fleet, trip, fare, booking, reservation-access, support and audit foundation (PR #3).
3. In parallel after the passenger base: synthetic route/catalog fixtures (PR #6) and Android packaging (PR #4).
4. Android device/API-origin remediation (PR #5) after PR #4 and a persistent approved test API are available.
5. Platform implementation beyond passenger transit: shared platform foundation, then Move, Delivery, Cargo, Market, Fleet expansion, Business and Pay in the approved dependency order.

The current A2 baseline is suitable to begin bounded A3 work. It is not a merge recommendation and does not establish production readiness.

## 2. Exact repository and PR register

| PR | Branch / base | Exact head SHA | Current disposition |
|---|---|---|---|
| #1 G1 foundation | `feat/g1-foundation-completion` → `main` | `50e38a94011eb24d06812acace7d09e4d8e81dc8` | Required foundation; review before integration |
| #2 Passenger scope/roadmap docs | `docs/product-scope-roadmap-v1` → `main` | `3bf77bdbf6d017331a5ec2ea64e2a36577f9c8b6` | Historical documentation; superseded by frozen A1 v1.1 |
| #3 Passenger MVP | `feat/a3-passenger-mvp` → PR #1 branch | `0a01631a21a823b720337d1d80aa690e5df347bc` | Reusable API/DB/UI foundation; A4 code-level evidence recorded |
| #4 Android debug APK | `feat/android-debug-apk` → PR #3 branch | `24a5e3af527e7e306e29e4c613f36e08722ff50c` | APK build workflow; dependent on PR #3 |
| #5 Android device remediation | `fix/android-device-acceptance` → PR #4 branch | `563bd5c9eba6e69c1de08a29f00b113679c19cc5` | Device/API-origin changes; dependent on PR #4 |
| #6 A1 v1.1 + synthetic catalog | `feat/biker-first-platform-a1-test-catalog` → PR #3 branch | `22813a4510d42d4295602075abaebabc7a83369e` | Frozen A1 spec and synthetic seed/workflow; dependent on PR #3 for application schema |
| #7 Platform guideline | `docs/maalenex-platform-guideline` → `main` | `276fbb6d02d47421466199d477a4fe770c1f117e` | Independent documentation; now aligned with A1 freeze |

All seven PRs were observed open and unmerged during this review. PR #1, #3, #4, #5 and #6 are draft; PR #2 is open and non-draft; PR #7 is draft. No PR was merged or closed. The default branch remained at the exact inspected SHA above.

### Branch dependency graph

```text
main (72550a2)
├── PR #1 G1 foundation (50e38a9)
│   └── PR #3 Passenger MVP (0a01631)
│       ├── PR #4 Android debug APK (24a5e3a)
│       │   └── PR #5 Android device remediation (563bd5c)
│       └── PR #6 A1 v1.1 + synthetic catalog (22813a4)
├── PR #2 historical passenger-only planning documents (3bf77bd)
└── PR #7 platform implementation guideline (276fbb6)
```

Do not merge PR #3, #4, #5 or #6 as if each were based independently on `main`. Their declared bases are part of the dependency chain. PR #6 includes the passenger branch in its ancestry; its seed code uses the passenger schema and is not independently applicable to the current main schema.

## 3. Reuse and implementation baseline

### 3.1 Reusable foundations verified in PR #3

- FastAPI modular application and versioned `/api/v1` API.
- PostgreSQL, SQLAlchemy and Alembic metadata registration.
- Staff identity, password credentials, sessions, CSRF token binding, persistent login throttling and explicit permission checks.
- Organization, membership, operator approval and invitation foundations.
- Append-oriented audit events, metadata redaction and database-level audit protections.
- Locations, terminals, routes/stops, vehicles, versioned seat layouts, trips, trip seats and ETB fare versions.
- Booking/seat-hold transactions, idempotency, guest contact challenge and booking-access controls.
- Support cases, staff case handling, operator trip manifest and bounded booking-maintenance worker.
- Amharic-first passenger web interface, trip search, seat selection, reservation recovery and support views.

The reservation reference/QR is explicitly not a travel ticket and does not authorize boarding. Payment collection, ticket issuance, boarding, production passenger records and commercial operations remain disabled.

### 3.2 Shared foundations still missing for the full A1 scope

The current identity/organization work is staff/operator-centric and is not yet a complete cross-service identity and account model for passengers, bikers, couriers, carriers, merchants, fleet managers and enterprise users.

The following require explicit A3 design/implementation rather than assumptions that they already exist:

- Cross-service account/profile and service-role model with organization/tenant scoping.
- Versioned service registry, service-area eligibility, feature flags and configuration.
- Common trust/verification and document metadata lifecycle for drivers, vehicles, couriers, carriers and merchants.
- Consent-bound, time-limited location sessions and location freshness/revocation controls.
- Durable transactional outbox/inbox and observable background job retry/dead-letter handling.
- Notification/communication adapters and delivery status.
- Provider-neutral payment intents and append-only double-entry ETB ledger; no live provider adapter or money movement yet.
- Service-specific dispatch and state machines for Move, Delivery and Cargo.
- Merchant catalog/order/fulfilment and Business account/contracts/cost-centres.
- Fleet driver/vehicle inspection, maintenance, insurance/licence and compliance-expiry workflows.
- Data retention, deletion, evidence access and incident-response policies before real personal data.

### 3.3 Database and migration assessment

PR #3 provides one linear Alembic chain:

`0001_g1_foundation` → `0002_identity_audit_orgs` → `0003_passenger_domains` → `0004_staff_auth_controls` → `0005_booking_access_challenges` → `0006_guest_access_rate_limits` → `0007_operator_invites_support`.

- PR #3 A4 workflow successfully upgraded the isolated PostgreSQL 16 database, ran Alembic metadata parity, ran backend/PostgreSQL tests and downgraded/re-upgraded cleanly.
- PR #6 adds no migration. Its deterministic synthetic seed uses the existing catalog, organization, fleet, trip and fare models.
- No duplicate migration revision was found in the inspected PR #3 chain.
- Future platform domains must append a single linear migration chain after `0007_operator_invites_support`; do not create competing migration heads on sibling branches.
- Before adding cross-service tenancy, verify every organization-scoped foreign key, unique constraint, authorization query and delete/revocation rule. Migration/model parity alone does not prove tenant isolation.

## 4. Verification evidence and limitations

| Scope | Exact tested SHA / run | Result | What it proves |
|---|---|---|---|
| Passenger API/DB/frontend A4 | `0a01631a21a823b720337d1d80aa690e5df347bc`; [run #42453257303](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42453257303) | PASS | PostgreSQL 16, 28 backend tests, migration upgrade/parity/downgrade/re-upgrade, focused Ruff, frontend tests, typecheck and build |
| Android base APK | `24a5e3af527e7e306e29e4c613f36e08722ff50c`; [run #42455064070](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42455064070) | PASS | Frontend production build, Capacitor sync, Gradle debug APK assembly and artifact upload |
| Android device-remediation APK | `563bd5c9eba6e69c1de08a29f00b113679c19cc5`; [run #42458074134](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42458074134) | PASS | Frontend tests/build and debug APK packaging on the remediation branch |
| Synthetic route/catalog | `22813a4510d42d4295602075abaebabc7a83369e`; [run #42461985677](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42461985677) | PASS | PostgreSQL migration, idempotent synthetic seed, API health, locations/routes and Jinka–Wolaita Sodo–Addis passenger search |
| G1 foundation PR #1 | `50e38a94011eb24d06812acace7d09e4d8e81dc8` | NOT RUN in PR body | PR body explicitly reports local tests/typecheck/build/PostgreSQL migration as not run |

These workflows are synthetic CI. GitHub Actions service containers are ephemeral; they do not provide a persistent API or database endpoint for an installed APK.

### Android limitation

The Android remediation workflow reads `MAALENEX_TEST_API_BASE_URL` from a repository variable. The checked-in example is a placeholder. If the variable is empty, the installed WebView uses same-origin API requests and cannot reach a separately hosted FastAPI service. No verified persistent HTTPS API origin was found. Physical-device acceptance remains NOT RUN. Do not treat a successful APK build as device acceptance or backend connectivity.

## 5. PR disposition and ordered integration register

| Order | PR | Disposition | Dependency / action when separately approved |
|---:|---|---|---|
| 1 | #1 | **INTEGRATE FIRST** | G1 base on main; retain synthetic-only/local-DB safeguards; rerun its declared validation gates before merge |
| 2 | #3 | **COORDINATED WITH #1** | Passenger API/DB implementation depends on #1; its A4 evidence is strong, but verify current base/HEAD and repeat final integration CI after #1 lands |
| 3A | #6 | **COORDINATED WITH #3** | Frozen A1 v1.1 document plus synthetic catalog seed/workflow; preserve the PR #3 schema dependency; no separate migration |
| 3B | #4 | **COORDINATED WITH #3** | Android debug packaging; do not present APK as connected to a hosted API |
| 4 | #5 | **AFTER #4** | Device navigation/API-origin remediation; only complete physical acceptance after an authorized persistent test API exists |
| — | #7 | **INDEPENDENT DOCUMENTATION** | Keep as the platform implementation guideline; its A1/A2/A3 status has been synchronized with the Owner freeze |
| — | #2 | **HISTORICAL / SUPERSEDED** | Passenger-only product scope and roadmap are superseded by A1 v1.1. Preserve as reference; do not treat as the active platform specification |

No merge, retarget, close, or branch deletion was performed in A2.

## 6. Security, privacy and operational findings

| Finding | Severity | A2 status | Required treatment |
|---|---|---|---|
| Full multi-role, cross-service identity/tenant model is incomplete | HIGH | OPEN | A3 shared foundation; deny-by-default authorization and cross-tenant regression tests |
| Location/GPS consent, scope, expiry and revocation are not implemented | HIGH | OPEN | A3 Move/location foundation; no live tracking before separate approval |
| Payment ledger, webhook integrity, settlement and reconciliation are absent | HIGH | OPEN | A3 Pay foundation only with synthetic ledger events; live money movement separately gated |
| Persistent HTTPS backend for Android is unavailable/unverified | HIGH | BLOCKER for device acceptance | Assess no-cost hosting options; do not invent or guess a host |
| Delivery, Cargo, Market and Business service lifecycles are not implemented | HIGH | OPEN | Build as distinct domain state machines after shared foundation |
| Fleet is currently a vehicle/seat-layout foundation, not full fleet compliance management | MEDIUM | OPEN | Add driver, maintenance, inspection and compliance domains |
| No independent penetration test, external security review or WCAG 2.2 AA audit evidenced | MEDIUM | NOT RUN | Schedule before production-readiness claims |
| Regulatory, insurance, operator contract, consumer protection and data-protection approvals | HIGH | UNKNOWN / NOT EVIDENCED | Track by service and jurisdiction before live operation |

### Non-negotiable controls retained

- Synthetic identities, locations, trips, bookings and financial events only in CI.
- No real passenger/operator/merchant personal data in repository fixtures.
- No secrets, PINs, OTPs or payment credentials in source control.
- No silent or continuous location tracking.
- No payment success, ticket issuance, boarding or commercial activation claims.
- No paid hosting/provider prerequisite; record unavailable paid dependencies as blockers and assess no-cost alternatives.

## 7. A3 implementation sequence authorized by Owner

A3 begins from the existing verified passenger foundation and must preserve it. The first increment is the shared platform foundation, not an attempt to launch all eight service lines at once.

1. **A3.1 Shared account and tenancy contracts:** define public/customer and provider identities, organization membership, service roles, authorization scopes and tenant-isolation tests; reuse existing staff identity and organization foundations.
2. **A3.2 Service registry and eligibility:** versioned service definitions, service-area enablement, capability flags and Amharic-first configuration; no false activation of unavailable services.
3. **A3.3 Trust and documents foundation:** synthetic verification cases, review/approval/revocation, document metadata and audit; no real identity documents.
4. **A3.4 Audit and async foundation:** correlation/causation IDs, transactional outbox/inbox, idempotent workers, retry limits and failure observability.
5. **A3.5 Location-consent contracts:** consent records, purpose, active-job scope, expiry, revocation and freshness state; synthetic location samples only.
6. **A3.6 Move service lifecycle:** quote/request/matching/accept/pickup/in-progress/completion/cancel/dispute contracts with concurrency-safe assignment; no live dispatch/GPS.
7. **A3.7 Delivery and Cargo domain foundations:** separate shipment/freight state machines, custody events, capacity and proof-of-delivery contracts using synthetic fixtures.
8. **A3.8 Market, Business and Fleet expansion:** merchant catalog/orders, organization accounts/contracts/cost centres and fleet driver/vehicle compliance.
9. **A3.9 Pay ledger foundation:** synthetic-only ETB double-entry journal, idempotent posting, immutable corrections and reconciliation invariants. No payment-provider integration or live money movement without separate approval.

Each increment requires focused tests, migration parity, concurrency/failure-path coverage where applicable, exact-commit GitHub Actions evidence and an updated A3 implementation report. A4 follows after A3 completion and separate A4 entry review.

## 8. Stage-gate closure

| Gate | Status | Evidence |
|---|---|---|
| A1 specification and freeze | **VERIFIED-CLOSED** | Owner approval recorded; frozen spec on PR #6 branch |
| A2 read-only reconciliation | **VERIFIED-CLOSED WITH GAPS** | Exact main/PR SHA register, dependency graph, migration review, workflow evidence, security findings and integration order in this report |
| A3 implementation | **AUTHORIZED — READY TO START** | Owner instruction: “Approved so proceed implementation”; implementation branch remains separate |
| A4 verification | **NOT STARTED for new platform increments** | Existing PR #3 A4 evidence applies only to its passenger foundation |
| A5 deployment | **NOT AUTHORIZED** | Separate Owner approval required |

**A2 closure statement:** The existing repository baseline and PR dependencies have been reconciled sufficiently to begin bounded A3 implementation. Recorded gaps are explicit work items/blockers, not silently accepted production risks. Main remains unchanged at `72550a2e464f6517653580bb1ae4e7608f211f39`.
