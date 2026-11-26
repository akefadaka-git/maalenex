# MaaleNex Platform — A1 v1.2 Controlled Amendment Proposal

**Version:** 1.2.0-proposed  
**Status:** DRAFT FOR OWNER REVIEW — NOT FROZEN  
**Prepared:** 2026-11-26  
**Amends:** MaaleNex Platform A1 Product Scope and Architecture Specification v1.1  
**Immutable source:** Commit `22813a4510d42d4295602075abaebabc7a83369e`; blob SHA `f7900e619f969e62d9f12c3c78457f99def23a05`  
**Companion register:** `docs/strategy/MAALENEX-A1-v1.2-CHANGE-REGISTER.md`

## 1. Purpose and legal effect

This proposal adds controlled technical, security, integration and acceptance clarifications to the Owner-approved MaaleNex platform A1 v1.1. It is additive: v1.1 remains intact, frozen and historically authoritative.

This document is not an approval or freeze record. It does not reopen unrelated v1.1 decisions, close the current A2 assessment, authorize A3 before A2 closure, authorize merge, activate a provider, permit paid services, enable live GPS or money movement, authorize commercial operations, or authorize A5 deployment.

If approved, v1.2 will be read together with v1.1. Where a proposed clarification materially conflicts with v1.1, the conflict must be explicitly decided by the Owner; no silent supersession is permitted.

## 2. Product portfolio and release sequencing

Retain the eight service lines and the product hierarchy in v1.1:

1. Passenger / Transit foundation.
2. Move and its driver/biker/operator lifecycle.
3. Delivery.
4. Cargo.
5. Market and Business.
6. Fleet capabilities integrated with the relevant service workflows.
7. Pay financial foundation, with external payment rails last and separately gated.

This is a dependency order, not a simultaneous launch commitment. Feature visibility must be conditioned on verified geography, service capability, operator eligibility, regulatory status and actual operational readiness. Code presence, synthetic fixtures or a successful build do not establish service availability.

The existing passenger application is the starting product. Extend it incrementally; do not replace it with a generic dashboard or demo.

## 3. Shared platform architecture

### 3.1 Architectural style

Use a modular monolith first. Retain the current FastAPI/Python, Pydantic Settings, SQLAlchemy 2, Alembic and PostgreSQL backend direction, and React/TypeScript/Vite/Capacitor frontend direction. Keep versioned API contracts and explicit domain ownership. Do not split into microservices until measured scale, fault isolation, team ownership or regulatory boundaries justify the additional operational burden.

These are the target starting technologies, not a claim that every proposed module is present on main or production-ready.

### 3.2 Shared platform domains

The shared platform target comprises:

- Identity and authentication.
- Trust and verification.
- Organizations and memberships.
- Authorization and tenant/resource policy.
- Audit and evidence.
- Geography and location policy.
- Files and private evidence storage.
- Notifications and communication.
- Support and disputes.
- Analytics and reporting.
- External integration boundaries.

Each service domain retains its own lifecycle, business rules, state transitions, persistence ownership and acceptance tests. Cross-domain work should use explicit application services and versioned contracts/events rather than unrestricted cross-domain table mutation.

### 3.3 Authorization contract

Every protected action must be evaluated against:

- **Principal:** authenticated person, service identity or explicitly permitted guest capability.
- **Organization/tenant:** active organization and tenant boundary, where applicable.
- **Service:** enabled service and applicable service-area policy.
- **Resource:** exact record, owner, operator, trip, shipment, vehicle, order or financial object.
- **Action:** explicit operation being requested.

Authorization is deny-by-default and enforced server-side. UI visibility is not a security boundary. Organization membership alone does not grant access to every organization resource. Preserve guest discovery and approved guest-reservation recovery; do not force account registration for basic discovery without a separately approved product change. Sensitive staff, finance, tracking and evidence access requires purpose limitation and audit records.

### 3.4 Data and migration governance

Maintain one coherent Alembic revision graph. Before any migration implementation:

- Inventory all revision files, parents and current heads across the selected branches.
- Reconcile the complete model registry and metadata.
- Inspect the target database revision state only through an explicitly authorized read-only connection.
- Design any merge revision only after proving ancestry and schema compatibility.
- Validate clean upgrade, downgrade and re-upgrade against disposable PostgreSQL.
- Verify constraints, indexes, foreign keys, uniqueness, data preservation and tenant boundaries.
- Obtain backup and restore evidence before any non-disposable database migration.

No migration is to be executed against a hosted or production database during A2.

## 4. Geographic and location architecture

The preferred technical candidate is:

- PostgreSQL with PostGIS as the canonical spatial data store.
- MapLibre as the shared renderer for passenger and staff map experiences.
- Martin as a candidate vector-tile service, subject to feasibility review.

This direction is not final until A2 assesses hosting, data/tile licensing, attribution, coverage, freshness, bandwidth, offline behavior, privacy, security and cost. No paid map service or billing account is to be activated by this proposal.

Separate data classes:

1. **Public geography:** verified publishable places, boarding points, routes and stops with source, license, attribution, verification state and revision history.
2. **Restricted operational geography:** active trip/shipment/device telemetry, accessible only to authorized roles for a valid purpose, with consent, freshness, expiry, retention and audit controls.

Do not infer route geometry, intermediate stops, operator service, vehicle position or live availability from a single boarding coordinate or synthetic test data. The Koybe boarding point reference remains 5.7678630, 36.7985890; it does not authorize route interpolation or publication of an unverified corridor.

Passenger maps and MITP/staff tracking may share rendering infrastructure but must not share unrestricted data access. Public passenger queries must never expose protected telemetry.

## 5. Application and mobile experience

Preserve the existing passenger web/PWA journey and Android application. Use a shared design system, localization conventions, API client and error/loading/offline states as the codebase is incrementally reconciled.

Amharic remains the default interface language; English remains supported. Maintain mobile-first, low-bandwidth operation, accessible interaction and appropriate Ethiopian calendar/date/numeral presentation. Target WCAG 2.2 AA, with manual review and assistive-technology/device checks; automated linting alone is insufficient.

Android acceptance must verify, on an exact candidate SHA:

- Correct HTTPS API origin and environment separation.
- Login/session establishment, cookie handling and CSRF/CORS behavior.
- Logout, session expiry and recovery.
- Passenger search/reservation/recovery/support flows against the intended API.
- Offline, slow-network, retry and conflict behavior without duplicate commands.
- Physical-device install, navigation, permissions and usability.

APK assembly or a synthetic CI API does not prove persistent API connectivity or physical-device acceptance.

## 6. Notifications and external communications

The authenticated in-app inbox is the canonical notification history. Business events must be committed independently from external delivery.

Use a transactional outbox written in the same transaction as the originating business event, with an independently operated worker. Require idempotent message keys, bounded retries, dead-letter/failure visibility, signed webhook verification, delivery-state history, redacted audit records and bilingual templates.

SMS, WhatsApp Business and email are provider-neutral adapters. Provider selection requires comparison of Ethiopian reach, sender identity, API/webhook security, consent/opt-in rules, provider terms, data processing, delivery receipts, sandbox access, support and cost. No provider is selected or activated by this proposal. Telegram, if later considered, is optional and user-initiated; it is not a core dependency.

Consent must be channel-specific, purpose-specific, recorded, revocable and distinct from possession of a phone number or account.

## 7. IROKA boundary

The separate frozen MaaleNex–IROKA architecture A1 v1.0 remains a distinct governing baseline. This amendment does not replace or revise it.

For MaaleNex product integration, IROKA remains an internal, invisible, governed intelligence capability. Integration is disabled by default until the relevant contracts, trust roots, security review and authorization controls are verified. Requests must be authenticated, tenant/service scoped, purpose limited, minimized, versioned and audited. Results must be validated before use. MaaleNex remains the authority for identity, access, business rules, transactions and execution. IROKA cannot independently authorize payment, booking, boarding, dispatch, operator approval or other business mutations.

## 8. Security, privacy and operational readiness

Before A4 acceptance, require evidence for:

- Authentication, session/token lifecycle, revocation, recovery and CSRF/origin controls.
- Deny-by-default authorization and cross-tenant/resource isolation.
- Rate limits, abuse controls, idempotency and replay protection.
- Secrets management, key rotation/revocation and least privilege.
- Private file/evidence access, upload validation and retention/deletion controls.
- Location consent, purpose, scope, freshness, expiry and revocation.
- Signed provider callbacks and safe external-input handling.
- Dependency/supply-chain review and independent application/API/mobile security assessment.
- Privacy notice, data minimization, retention schedule, incident response and applicable regulatory/insurance evidence.
- Structured redacted logs, metrics, alerting, backup/restore, recovery objectives and operational runbooks.

A successful CI run or synthetic test is not an independent security audit, legal opinion or commercial readiness certificate.

## 9. Synthetic preview and provider boundaries

Any future hosted preview must have a distinct, explicitly identified synthetic-only runtime and database. It must reject production data, real passenger/operator identity documents, live payment credentials, production location streams and commercial transactions. The preview must not be represented as a production service.

No hosting provider, map service, messaging provider, payment provider, paid plan, billing activation, deposit or top-up is authorized by this amendment. If a required service cannot be used without payment, record the limitation and assess no-cost alternatives; do not weaken security or silently incur cost.

## 10. Acceptance and stage gates

### A1 v1.2 exit

- The amendment is traceable to frozen v1.1 and the change register.
- All material conflicts are resolved or explicitly deferred.
- Owner decisions and deferred evidence are recorded.
- The Owner explicitly approves and freezes v1.2.

### A2 exit

- Current repository, PR dependency graph, exact heads and changed files are reconciled.
- Passenger and staff integration boundaries are explicit.
- Alembic heads, model registry, runtime configuration and workflow triggers are reconciled.
- GIS, notification, identity/tenancy, Cargo evidence, Android/API and synthetic preview gaps have evidence-backed dispositions.
- Security, privacy, regulatory, hosting and operational gaps are either closed or explicitly recorded as blockers with owners and acceptance criteria.
- A2 closure is separately reviewed and recorded; historical A2 closure is not substituted for current-scope evidence.

### A3 entry

A3 may begin only after the applicable A1 version is frozen and current A2 is completed and closed, with bounded work packages and separate implementation authorization. No code or migration work is authorized by this proposal.

### A4 acceptance

A4 requires exact-SHA backend/frontend/Android tests; database migration parity and rollback/re-upgrade; concurrency and authorization tests; independent security review; accessibility and physical-device acceptance; GIS provenance/licensing; and backup/restore, monitoring and incident evidence.

### A5 deployment

A5 remains a separate explicit Owner approval. A4 acceptance does not imply permission to deploy or launch commercially.

## 11. Explicit exclusions

This amendment does not authorize:

- Editing or replacing the frozen v1.1 source document.
- Reopening the separate frozen MaaleNex–IROKA A1 baseline.
- Modifying main or merging any pull request during A2.
- Starting A3 before A1 freeze and A2 closure.
- Executing migrations against hosted or production databases.
- Dispatching or rerunning CI workflows.
- Activating paid providers, billing, deposits, payment rails or external map/messaging accounts.
- Processing real passenger/operator personal data or identity documents in public development/preview.
- Live GPS collection, real money movement, ticket/boarding activation or commercial operation.
- Production deployment or A5 activities.

## 12. Approval record

| Field | Value |
|---|---|
| Proposed version | 1.2.0 |
| Source baseline | A1 v1.1, frozen 2026-11-08 |
| Proposal status | DRAFT FOR OWNER REVIEW — NOT FROZEN |
| Owner approval of this amendment | PENDING |
| A2 current-scope closure | PENDING |
| A3 implementation entry | NOT AUTHORIZED |
| A5 deployment | NOT AUTHORIZED |

**Owner decision required:** approve, revise or reject this proposed v1.2 amendment. A separate explicit freeze record is required before it becomes the active A1 baseline.
