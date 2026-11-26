# MaaleNex Enhanced Implementation Strategy — A1 v1.0

- **Repository:** `akefadaka-git/maalenex`
- **Document status:** Owner-approved planning direction; controlled documentation baseline
- **Approval:** Owner instruction, 26 November 2026 (“Approved so proceed”)
- **Scope:** Platform-wide design reassessment and staged implementation strategy
- **Baseline main SHA inspected:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`
- **Implementation status:** This document does not itself authorize merging, deployment, paid-service activation, or commercial operation.

## 1. Purpose and governing decisions

This strategy converts the Owner-approved comprehensive reassessment into an implementation program. It preserves the existing passenger product and the historical A1 v1.1 baseline. It does not replace earlier approvals or silently rewrite the original specification.

Binding direction:

1. MaaleNex remains the user-facing product and platform identity.
2. IROKA remains a separately governed, invisible intelligence integration; it is not a public MaaleNex service.
3. Passenger mobility remains the first release priority.
4. The initial operating geography is Koybe/Jinka and South Omo, subject to verified service-area and operator evidence.
5. Amharic-first, mobile-first and accessible design remain mandatory.
6. Freight, Market, Business and Pay remain phased domains, not prerequisites for the passenger release.
7. Synthetic data only in public development and preview environments.
8. No fabricated route geometry, stop sequence, operator availability, payment outcome or tracking position.
9. Commercial operation requires separate regulatory, insurance, privacy, security, provider and operational approvals.
10. A5 deployment requires separate explicit Owner authorization.

## 2. Architecture principles

### 2.1 Modular monolith first

Retain the existing FastAPI modular-monolith architecture. Do not split into microservices until measured scale, team boundaries or independent deployment requirements justify that complexity.

Each domain owns its business rules, lifecycle, persistence contract and tests. Cross-domain operations use application services and explicit events/contracts rather than unrestricted direct table mutation.

### 2.2 Target domain catalogue

- Core platform: Identity, Trust, Organizations, Authorization, Audit, Geography, Files/Evidence, Notifications, Support, Analytics and Integration.
- Passenger services: Passenger, Transit, Catalog, Routes, Stops, Fares, Reservations, Bookings and Boarding.
- Operations: Move, Dispatch, Drivers/Bikers, Fleet, Operator, Scheduling, MITP tracking and Incidents.
- Logistics: Delivery, Cargo, Shipment, Carrier, Custody and Proof of Delivery.
- Commerce: Market, Merchant, Catalog, Inventory, Orders and Business Accounts.
- Finance: Pay, ETB ledger, Payment Intents, Provider Adapters, Settlement, Refunds and Reconciliation.

The catalogue is a target design. It does not imply every domain is implemented or approved for operation.

### 2.3 Backend structure

Target organization (adapt to existing paths rather than performing a wholesale rewrite):

```text
backend/app/
  core/                 # config, security, authorization, tenancy, observability
  domains/
    identity/ trust/ organizations/ geography/
    passenger/ transit/ move/ delivery/ cargo/
    fleet/ market/ business/ pay/
    notifications/ support/ audit/
  integrations/         # maps, payments, messaging, IROKA
  jobs/
  api/
```

Maintain Python 3.11+, FastAPI, Pydantic Settings, SQLAlchemy 2, Alembic and PostgreSQL. Preserve versioned API contracts and existing test conventions.

### 2.4 Identity and authorization

Use a common platform identity with scoped memberships and permissions. Authorization decisions must account for principal, organization, service, resource and action. Guest passenger discovery and the approved guest-reservation access model must not be broken by forcing registration for basic discovery.

Staff, driver, agent, operator and administrator privileges must be separated. Tracking access is staff-scoped and organization/resource-scoped. Sensitive actions require audit evidence.

### 2.5 Database and migrations

The known passenger/runtime history and MITP history contain parallel Alembic heads. No migration merge is accepted merely because revision identifiers differ or table names appear distinct.

Required controls:

- Inventory all revision files and dependency edges.
- Identify every current head and all model imports.
- Produce one merged revision graph without dropping either domain.
- Verify model-registry completeness and metadata parity.
- Run clean upgrade, downgrade and re-upgrade on disposable PostgreSQL.
- Check constraints, indexes, foreign keys, uniqueness and data-preserving downgrade semantics.
- Inventory deployed database revision rows and obtain backup/restore evidence before any real database migration.
- Do not run migrations against a hosted or production database during A2.

### 2.6 Geographic architecture

Preferred direction for technical evaluation: canonical PostGIS storage, MapLibre shared rendering and a controlled vector-tile service such as Martin. This remains subject to A2 validation of hosting, tile/data licensing, OSM attribution, bandwidth, freshness, privacy and operating cost.

Separate publishable geography (verified public locations, routes and stops) from restricted operational geography (device telemetry and active-trip location). Use provenance, verification status, timestamps, retention and access controls.

Koybe boarding point: 5.7678630, 36.7985890. This coordinate does not authorize inference of a route trace or intermediate stops.

### 2.7 Application experience

Preserve the existing passenger web/PWA application. Improve it incrementally; do not replace it with a generic demo dashboard.

Shared experience capabilities: Amharic-first localization, English alternative, responsive design, accessible components, common API client, authentication/session handling, error conventions, loading/empty/offline states and role-aware navigation.

Introduce separate workspaces progressively: Passenger; Driver/Biker; Operator; Agent; Dispatcher; Fleet Administrator; Business; Platform Administrator. MITP must be a protected staff workspace, not a replacement root application.

Retain React, TypeScript, Vite and Capacitor. Android acceptance requires configured HTTPS API origin, session/cookie and CSRF/CORS verification, login/logout, real API journey tests, offline/error recovery and physical-device installation/acceptance. APK assembly alone is insufficient.

### 2.8 Notifications and integrations

Use a transactional outbox and durable in-app inbox as the notification foundation. Add SMS, WhatsApp Business and email only through consent-aware provider adapters with idempotency, signed callback verification, retries, delivery state and failure handling. Provider activation is separately authorized.

IROKA integration must be disabled by default, authenticated, audited, data-minimizing and subordinate to MaaleNex authorization. It cannot independently authorize payment, boarding, dispatch or other transactions.

### 2.9 Security and operations

Security requirements include secure authentication and recovery, scoped authorization, CSRF/session protections, rate limits, idempotency, secrets isolation, private evidence storage, retention controls, audit trails, device credential rotation/revocation, replay protection, consent and purpose limitation for location, monitoring, incident response and tested backup restoration.

Financial controls include immutable double-entry postings, reconciliation, reversals/refunds, segregation of duties and signed provider callbacks. No live money movement until separately approved.

## 3. Service release strategy

1. **Passenger / Transit:** route discovery, verified stops, fares, availability, reservation/booking, guest access, account recovery, support and notifications.
2. **Move:** driver/biker onboarding, vehicle checks, service areas, dispatch, trip lifecycle, safety and consent-based location.
3. **Delivery:** parcel creation, pricing, assignment, custody, proof of delivery and disputes.
4. **Cargo:** carrier onboarding, freight capacity/matching, custody, claims and governed evidence lifecycle.
5. **Market / Business:** merchant onboarding, catalog, inventory, orders, business accounts and reporting.
6. **Pay:** ledger controls first; provider rails only after financial, legal, security and operational approvals.

Service visibility must be area-, capability- and authorization-aware. A feature being present in code does not mean the service is available commercially.

## 4. Staged implementation plan and exit criteria

### Phase 0 — Baseline and inventory
- Preserve A1 v1.1 and the current main baseline.
- Build exact branch/PR dependency map with base/head SHAs.
- Classify each feature as merged, unmerged, incomplete, superseded or unverified.
- Record file ownership, migration ownership and evidence references.

**Exit:** reproducible implementation inventory and no ambiguous integration candidate.

### Phase 1 — Controlled A1 amendment
- Prepare a versioned A1 v1.2 amendment referencing, not overwriting, A1 v1.1.
- Reconcile product scope, architecture, domain catalogue, identity, GIS, mobile, security, privacy, operational and release requirements.
- Maintain a change log and trace each amendment to an Owner decision.

**Exit:** complete amendment package and explicit A1 freeze record.

### Phase 2 — A2 read-only reconciliation
- Reconcile PR #42/#43 disposition and exact-head evidence.
- Reconcile PR #32–44 dependencies, plus PR #53 tracking and PR #54 Android.
- Reconcile migration graph, model registry, config, main router composition and workflow triggers.
- Select canonical GIS approach with licensing/cost review.
- Reconcile passenger/staff UI and API boundaries.
- Review Cargo PR #49–52 evidence and retention governance separately.
- Close security, regulatory, privacy, hosting and operations evidence gaps.

**Exit:** evidence-backed A2 closure; no code changes to main during A2.

### Phase 3 — Shared platform engineering (A3 priority 1)
- Configuration and runtime profiles.
- Identity, organization, tenancy and scoped authorization.
- Audit, model registry, canonical migration graph.
- API contracts, error handling and health/readiness.
- Transactional outbox, worker contracts and private file interfaces.

**Exit:** integrated foundation passes backend, database, security and authorization tests.

### Phase 4 — Passenger and Transit (A3 priority 2)
- Passenger identity/session and guest reservation access.
- Verified geography, routes, stops, schedules and fares.
- Availability and concurrency-safe reservation lifecycle.
- Ownership/recovery, support, reports, complaints and notifications.
- Operator scheduling and staff workflows.
- Passenger map and Android/PWA connectivity.

**Exit:** complete synthetic passenger journey verified across web and Android.

### Phase 5 — Geographic and MITP platform (A3 priority 3)
- Canonical PostGIS schema and data provenance.
- Shared MapLibre renderer and controlled tile service.
- Public passenger geography separated from protected telemetry.
- Device registration, credential rotation/revocation, replay protection and scoped tracking.
- Synthetic telemetry only.

**Exit:** public map and staff tracking pass independent access-control and data-quality tests.

### Phase 6 — Move and operations (A3 priority 4)
- Driver/biker onboarding and trust.
- Fleet and service-area eligibility.
- Fare policy and dispatch.
- Trip lifecycle, PIN/QR confirmation, incident and emergency handling.
- Consent-bound location sessions.

**Exit:** synthetic end-to-end ride and safety workflows verified.

### Phase 7 — Delivery and Cargo
- Delivery and shipment lifecycle.
- Carrier and capacity workflows.
- Custody, proof of delivery, claims and disputes.
- Private evidence and retention controls.

**Exit:** synthetic shipment lifecycle and legal/evidence governance acceptance.

### Phase 8 — Market and Business
- Merchant/business onboarding.
- Catalog, inventory, orders and fulfilment.
- Business accounts, service agreements and reporting.

**Exit:** synthetic merchant and business workflows verified.

### Phase 9 — Pay and financial integrations
- Double-entry ETB ledger and posting invariants.
- Payment intent/provider adapter contracts.
- Signed callbacks, idempotency, reversals/refunds and settlement reconciliation.
- Financial role segregation.

**Exit:** synthetic financial acceptance; real-money rails remain separately gated.

### Phase 10 — A4 integrated verification
- Full regression, migration and concurrency testing.
- Tenant/resource authorization tests.
- Independent security review and vulnerability remediation.
- Accessibility and physical Android acceptance.
- GIS integrity/licensing checks.
- Backup restore, monitoring, incident and operational runbooks.

**Exit:** evidence-backed A4 acceptance report.

### Phase 11 — A5 deployment
- Production infrastructure, credentials, TLS, monitoring and backups.
- Controlled database migration, rollout and rollback.
- Commercial launch controls and operator readiness.

**Exit:** separate explicit Owner deployment approval. This strategy does not authorize A5.

## 5. Immediate execution register

| ID | Task | Priority | Deliverable |
|---|---|---|---|
| MN-001 | Reconcile frozen A1 v1.1 and proposed amendments | Critical | A1 v1.2 change register |
| MN-002 | Reconcile PR/branch dependency graph | Critical | Exact SHA integration register |
| MN-003 | Close PR #43 exact-head evidence gap | Critical | Candidate verification evidence |
| MN-004 | Resolve competing Alembic heads | Critical | One migration graph design |
| MN-005 | Finalize identity and tenancy contracts | Critical | Identity/authorization specification |
| MN-006 | Freeze canonical GIS architecture | Critical | GIS decision record |
| MN-007 | Reconcile passenger and MITP map interfaces | High | Shared map contract |
| MN-008 | Reconcile passenger web/Android API flows | High | End-to-end acceptance plan |
| MN-009 | Finalize notification outbox and channel design | High | Notification architecture |
| MN-010 | Reconcile Cargo evidence lifecycle | High | Legal/technical review package |
| MN-011 | Define synthetic hosted-preview boundary | High | Runtime and database identity specification |
| MN-012 | Produce final A2 closure record | Critical | Evidence-backed A2 closure package |

## 6. Acceptance status vocabulary

- **PASS:** criteria verified with evidence.
- **VERIFIED-CLOSED:** issue closed with supporting evidence.
- **PARTIAL:** some criteria met; remaining work explicit.
- **MISSING:** required implementation/evidence absent.
- **UNRESOLVED:** conflicting or incomplete decision.
- **UNKNOWN:** authoritative source evidence unavailable.
- **NOT RUN:** acceptance not executed.
- **NOT AUTHORIZED:** action outside approved scope.

Every implementation report must record repository, branch, base/head SHA, changed files, PR, workflow evidence where available, migration/test status, approvals, unresolved risks and next action.

## 7. Governance and constraints

- Preserve unrelated changes and historical approvals.
- Do not modify main during A2.
- Do not merge PRs without separate explicit approval.
- Do not dispatch or rerun workflows without authorization.
- Do not activate paid services, billing or deposits without separate approval.
- Do not deploy without separate A5 authorization.
- Do not treat synthetic tests as proof of legal or commercial readiness.
- Do not infer that the strategy approval closes A1/A2 evidence gates automatically.

## 8. Current baseline and limitations

This strategy is based on the repository state and PR/migration evidence inspected for the Owner's reassessment. It is a planning baseline, not an independent security audit, legal opinion, complete source-code audit or production certification. All implementation status must be revalidated against exact branch heads before execution.

**Owner decision:** The Owner approved the enhanced reassessment and instructed that work proceed. This document records the approved planning direction. A1 v1.1 remains preserved; the detailed A1 v1.2 amendment and A2 closure evidence remain controlled deliverables.
