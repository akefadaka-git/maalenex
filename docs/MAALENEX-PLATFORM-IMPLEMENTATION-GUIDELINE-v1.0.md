# MaaleNex Platform — Implementation Guideline v1.0

**Document status:** Owner-direction implementation guideline; proposed baseline pending formal A1 scope freeze  
**Product:** MaaleNex  
**Tagline:** Move. Deliver. Connect. Grow.  
**Platform description:** Mobility • Logistics • Commerce • Business  
**Company:** MaaleNex Technologies PLC (in formation)  
**Repository at time of writing:** `akefadaka-git/maalenex-moto` (repository rename is a separate administrative action)  
**Date:** 2026-11-08

> This guideline restructures the delivery roadmap around the expanded MaaleNex platform. It is a planning and governance document, not evidence that proposed capabilities have been implemented, approved for production, or deployed. The existing repository and its history must be preserved.

---

## 1. Product direction

MaaleNex is a unified, modular platform for people, transport, goods and businesses. It must support local mobility, intercity passenger transport, delivery, cargo/logistics and commerce without forcing every service into one undifferentiated trip or booking workflow.

**Product promise:** Move. Deliver. Connect. Grow.

### 1.1 Product service portfolio

| Service line | Scope | Primary users |
|---|---|---|
| **MaaleNex Move** | Local passenger rides, motorcycle taxis, bikers, taxis, dispatch and scheduled/on-demand trips | Passengers, bikers, drivers, dispatchers |
| **MaaleNex Transit** | Intercity buses, routes, terminals, timetables, seat inventory and reservations | Passengers, bus operators, terminal staff |
| **MaaleNex Delivery** | Documents, parcels, local shop orders and last-mile delivery | Senders, recipients, couriers, merchants |
| **MaaleNex Cargo** | Intercity goods, truck capacity, freight requests, load matching and proof of delivery | Shippers, truck owners, carriers, consignees |
| **MaaleNex Market** | Merchant discovery, product/service listings, orders and delivery coordination | Shops, restaurants, customers |
| **MaaleNex Fleet** | Vehicles, drivers, availability, maintenance, compliance and utilization | Fleet owners, operators, managers |
| **MaaleNex Business** | Business accounts, recurring transport/delivery, contracts, invoices and operational tools | SMEs, institutions, enterprise clients |
| **MaaleNex Pay** | Payment-provider integrations, ETB ledger, commissions, settlements, refunds and reconciliation | Customers, service providers, finance operators |

Service names are product architecture labels. They do not imply that separate applications, companies, payment products or regulated services already exist.

### 1.2 Initial geographic sequence

1. **Pilot foundation:** Koybe and Jinka, Maale Woreda / South Omo.
2. **Intercity corridor:** Jinka → Wolaita Sodo → Addis Ababa, subject to authorized operator schedules and route data.
3. **Ethiopian expansion:** Add regions and corridors only after operational, regulatory, support and safety readiness.
4. **African expansion:** Country-by-country localization, legal review, payment rails and operating partners.
5. **Global ambition:** Compete on measured reliability, safety, affordability, service coverage and unit economics. A top-three global position is an ambition, not a guaranteed outcome.

---

## 2. Design principles and platform boundaries

1. **One platform, distinct service lifecycles.** Reuse identity, organizations, dispatch primitives, communication, maps, payments, audit and analytics; keep ride, bus, parcel and freight state machines distinct.
2. **Amharic-first and Ethiopia-ready.** Amharic default with English fallback; ETB; Ethiopian calendar where appropriate; local landmarks, low-bandwidth behavior and accessible mobile UX.
3. **Mobile-first, offline-tolerant.** Cache safe read data, queue retryable commands with idempotency keys, show synchronization state, and never claim a booking or payment succeeded while offline.
4. **Trust and safety by design.** Verify operators, drivers, vehicles and service eligibility; provide trip/job PINs, emergency workflows, support evidence and auditable decisions.
5. **Consent-based location.** No silent or continuous background tracking. Share precise location only with permission, for a valid active job/trip, to authorized participants, for a limited period, with freshness indicators and stop/revoke controls.
6. **Financial integrity.** Provider payment status is server-verified. Maintain an immutable, reconcilable ETB journal; separate provider fees, company commission and provider earnings.
7. **Synthetic-only engineering baseline.** CI and development use synthetic identities, routes, vehicles, transactions and location samples. Never put real personal, identity, location or payment data in repository fixtures.
8. **Incremental modular architecture.** Avoid premature microservices. Start with a modular FastAPI application and explicit domain boundaries; split services only when scale, isolation or team ownership justifies it.
9. **No proprietary copying.** Global products are benchmarks for capabilities and user experience, not sources to copy. Use third-party APIs only under their terms and with required authorization.
10. **Preserve existing working functionality.** Inventory and reuse current passenger, identity, organization, catalog, fleet, trip, fare, booking, reservation, support and audit foundations. Do not duplicate MASES/legacy behavior or disturb unrelated modules.

---

## 3. Current implementation baseline — do not overstate

The repository began as **MaaleNex Moto** and currently contains a passenger-MVP foundation. The following are not yet established as production capabilities:

- Verified live biker dispatch and production rider onboarding.
- Production GPS streaming, maps provider integration or background location.
- Call relay/masked calling.
- Complete ticket issuance, boarding, cancellation or refund operations.
- Production payment collection, provider settlement or an activated commission policy.
- Parcel delivery, cargo/freight matching, merchant commerce or warehouse workflows.
- A persistent, approved HTTPS API endpoint for installed mobile clients.
- Commercial operations, regulatory approvals or production deployment.

Existing PR work and synthetic CI results must be reconciled against exact current branch and main SHAs before reuse. GitHub Actions environments are ephemeral and are not a persistent backend host.

---

## 4. Target logical architecture

Use a modular domain architecture with explicit ownership, API contracts, event boundaries and migration responsibility.

### 4.1 Shared platform foundation

- Identity, authentication, sessions, role-based and organization-scoped authorization.
- Organization, operator, merchant and enterprise account management.
- Trust, verification, document metadata, approvals and compliance reminders.
- Service catalog, pricing policies, service areas and eligibility rules.
- Geospatial primitives, maps/routing adapters and location-session authorization.
- Dispatch/matching primitives with service-specific eligibility.
- Communication, notifications, masked-call provider adapter where legally and technically supported.
- Payments, immutable ledger, commission policy, settlement and reconciliation.
- Support, disputes, safety incidents, audit and evidence retention.
- Analytics, operational reporting, feature flags and public/partner API gateway.

### 4.2 Service domains

- **Move:** ride request, quote, matching, accept/decline, pickup, in-progress, completion, cancellation and dispute.
- **Transit:** operator route/timetable, terminal/stop, departure, seat inventory, reservation, manifest, check-in, boarding and refund.
- **Delivery:** shipment quote, parcel classification, pickup, custody events, route, delivery attempt, proof of delivery and return.
- **Cargo:** freight request, vehicle/load capacity, carrier bids, matching, contract, pickup, custody, tracking, delivery and claims.
- **Market:** merchant onboarding, catalog, availability, cart/order, fulfilment and customer support.
- **Fleet:** vehicle/driver assignment, availability, inspection, maintenance, insurance/licence expiry and utilization.
- **Business:** account hierarchy, cost centres, recurring jobs, service agreements, invoicing and reporting.
- **Pay:** provider adapters, payment intents, webhook verification, ledger posting, commission calculation, payout and reconciliation.

### 4.3 Core data and integration rules

- Every service has a documented state machine and transition authorization.
- Use stable IDs, UTC timestamps internally, localized presentation, idempotency keys and optimistic/concurrency controls.
- Use transactional outbox/inbox patterns for asynchronous events and provider callbacks.
- Keep payment/ledger records append-only; correct with compensating entries, not silent mutation.
- Commission rules are versioned with effective dates, service scope and explicit approval. No rate is assumed in this guideline.
- Do not expose internal domain tables as public APIs; publish versioned contracts.
- Data retention, deletion, access logging and incident response must be specified before real personal data is processed.

---

## 5. Phased implementation roadmap

Each phase has an entry condition, bounded work, exit evidence and a governance gate. Work must not skip a gate because a later feature appears attractive.

### P0 — Repository and product preparation

**Objective:** Establish the authoritative starting point and prepare a complete product specification.

**Work:**
- Confirm repository, default branch, open PRs, branches, exact main SHA and active implementation heads.
- Reconcile the current passenger MVP and Android work; record reusable code and unresolved findings.
- Complete service catalogue, user/role matrix, service lifecycle maps and end-to-end journeys.
- Define geographic pilot boundaries, operating assumptions, service eligibility and initial launch exclusions.
- Produce screen inventory, API/domain inventory, data classification, integration register and issue breakdown.
- Define accessibility, Amharic/English localization, Ethiopian calendar and low-connectivity requirements.
- Define product naming and rebrand inventory; preserve repository history and existing Android application ID unless a separately assessed migration is approved.

**Exit evidence:** A1 requirements pack, architecture decision record, risk register, acceptance matrix, dependency map and prioritized backlog.

**Gate:** Owner approval of the A1 scope freeze. Until then, this guideline remains proposed direction.

### P1 — A2 read-only technical reconciliation

**Objective:** Verify what already exists and determine the safe implementation order without modifying application code or main.

**Work:**
- Inspect every relevant open PR and branch against exact current main.
- Map existing modules to Move, Transit, Delivery, Cargo, Market, Fleet, Business and shared foundation.
- Build file-level reuse/duplicate register, migration-collision register and API dependency graph.
- Review authentication, authorization, tenancy, audit, secrets, rate limits, privacy and data retention.
- Assess database schema, concurrency, transaction boundaries, background jobs and event delivery.
- Verify frontend/mobile architecture, accessibility, offline queue behavior and Android build reproducibility.
- Record PR dispositions: merge independently, coordinated API/App group, redesign, retire or unresolved.
- Identify hosting, maps, messaging and payment-provider prerequisites without purchasing services or weakening security.

**Exit evidence:** A2 baseline report, exact SHA/PR register, ordered integration plan, security findings, migration plan and R1 acceptance matrix.

**Gate:** Owner approval of A2 closure and implementation scope. A2 is read-only: no main changes and no unapproved merges.

### P2 — Shared platform foundation

**Objective:** Build the reusable security, data and operational foundations required by all service lines.

**Work:**
- Identity, organization tenancy, role/permission matrix and operator/merchant account lifecycle.
- Verification workflow and auditable approval/revocation.
- Service catalog, geography/service zones, configuration and versioned pricing/commission policy framework.
- Audit, support, notifications and transactional outbox.
- API versioning, idempotency, rate limits, observability, secrets handling and feature flags.
- Offline command queue contracts and synchronization/error recovery.
- Synthetic fixtures and repeatable CI database setup.

**Exit evidence:** Domain contracts, migration parity, authorization tests, audit tests, idempotency tests, CI and documented operational runbooks.

### P3 — Local mobility: MaaleNex Move

**Objective:** Complete safe biker/operator and passenger workflows for the pilot area.

**Work:**
- Biker/driver onboarding, identity and document review, vehicle registration and eligibility.
- Availability, dispatch, accept/decline, fare quote and trip lifecycle.
- Passenger booking, matched provider details, trip PIN and support.
- Consent-driven location session, location freshness, revocation and authorized trip sharing.
- Safety/SOS workflow, incident reporting, call-to-verify adapter design and masked calling only where supported.
- Biker earnings statements using synthetic financial events until financial controls are approved.
- Cancellation, no-show, dispute and service recovery policies.

**Exit evidence:** End-to-end passenger and biker tests, authorization and location privacy tests, concurrency tests, safety workflow tests and physical-device acceptance.

### P4 — Intercity passenger transport: MaaleNex Transit

**Objective:** Evolve the Jinka → Wolaita Sodo → Addis Ababa corridor from synthetic catalog tests into an operator-authorized reservation workflow.

**Work:**
- Operator onboarding and route/terminal/stop management.
- Published schedules, fares, capacity and seat inventory.
- Search, reservation, passenger manifest, check-in and boarding state transitions.
- Cancellation/refund rules and operator reconciliation.
- Timetable change, delay, missed connection and customer support workflows.
- Clearly distinguish reservation from ticket issuance and boarding.

**Exit evidence:** Operator-authorized catalog tests, seat concurrency tests, manifest/check-in tests and complete service lifecycle acceptance.

### P5 — Local delivery: MaaleNex Delivery

**Objective:** Support documents, parcels and merchant deliveries with custody and proof-of-delivery controls.

**Work:**
- Sender/recipient profiles, parcel categories, restricted-goods policy and size/weight limits.
- Quote, booking, courier assignment, pickup and custody scans.
- Recipient verification, proof of delivery, failed attempt, return and dispute.
- Merchant order handoff and delivery status synchronization.
- Service zones, delivery windows, delivery pricing and courier earnings calculation.

**Exit evidence:** Full parcel lifecycle tests, custody/audit trail, recipient privacy tests and exception-handling tests.

### P6 — Freight and cargo: MaaleNex Cargo

**Objective:** Coordinate intercity goods movement and available truck capacity.

**Work:**
- Shipper, carrier and truck-owner onboarding.
- Freight request, load dimensions/weight/classification and vehicle capacity.
- Carrier offers, matching, booking/contract and pickup.
- Cargo custody, tracking, proof of delivery, claims and dispute.
- Compatible shared-capacity rules for bus/vehicle trips only where operator consent, passenger safety, vehicle capacity, insurance and law permit.
- Warehouse/storage and transfer-point coordination as separately scoped workflows.

**Exit evidence:** Capacity validation, matching tests, custody traceability, claims workflow and legal/insurance review.

### P7 — Commerce and business services: MaaleNex Market / Business / Fleet

**Objective:** Enable merchants and organizations to use the same platform infrastructure.

**Work:**
- Merchant onboarding, catalog, availability and service listings.
- Cart/order/fulfilment lifecycle and customer support.
- SME and institutional accounts, recurring transport/delivery, contracts and cost centres.
- Fleet vehicle/driver assignment, maintenance, inspections and compliance expiry.
- Warehouse, wholesaler, farmer/cooperative and local-business participation only after validating the operating model.
- Business reporting, invoices and service-level performance.

**Exit evidence:** Merchant/order tests, business account authorization tests, fleet compliance tests and accounting reconciliation.

### P8 — MaaleNex Pay and financial operations

**Objective:** Introduce payment rails and company commission only when provider and legal prerequisites are satisfied.

**Work:**
- Provider-neutral payment adapter interface.
- Telebirr, CBE Birr and bank-transfer adapters only after current provider documentation, onboarding, credentials and permission are available.
- Server-side payment intents, signed callback verification, idempotent processing and reconciliation.
- Immutable ETB double-entry ledger for gross amount, provider fees, company commission, provider payable, refunds and chargebacks.
- Versioned commission policy with transparent disclosure and explicit Owner approval.
- Settlement/payout workflow, failed payment recovery and financial operations controls.
- Never request, store or process customer PINs, OTPs or banking passwords.

**Exit evidence:** Provider sandbox evidence, security review, duplicate-callback tests, ledger invariants, reconciliation reports, finance controls and compliance approval.

**Gate:** No live money movement until separately authorized and all provider, legal, security and operational prerequisites pass.

### P9 — Intelligence, optimization and partner ecosystem

**Objective:** Add differentiated capabilities after reliable operational data and service foundations exist.

**Work:**
- Demand forecasting and supply positioning.
- Dispatch, route and multi-stop optimization.
- Cargo/vehicle capacity matching.
- Fraud and abuse signals with human review and appeal paths.
- Operator, merchant and fleet analytics.
- Public/partner APIs, webhook subscriptions and documented integration lifecycle.
- Localization and country configuration to support future African expansion.

**Exit evidence:** Measured offline/online evaluation, model-risk controls, human override, API security review and partner sandbox acceptance.

### P10 — A4 verification, A5 deployment and post-deployment operations

**A4 verification:**
- Backend, frontend, database migration, Android build and device acceptance.
- Unit, integration, contract, end-to-end, regression, concurrency and failure-path tests.
- Security, privacy, access control, abuse, accessibility, localization and performance checks.
- Backup/restore, observability, alerting, incident response and operational readiness.
- Verify all claims against exact final source SHA and linked workflow runs.

**A5 deployment — separate approval required:**
- Select an authorized, affordable hosting approach with persistent HTTPS API and database.
- Configure DNS/TLS, secrets, backups, monitoring, access controls and recovery.
- Complete provider onboarding and production data-protection/legal prerequisites.
- Run a controlled pilot with approved operators and limited geography.
- Roll out gradually with rollback criteria and a named incident owner.

**Post-deployment:**
- Daily operational and safety review during pilot; monitor uptime, latency, failed jobs, payment reconciliation and support queues.
- Track rider/driver/merchant retention, fulfilment reliability, cancellation, on-time performance, safety incidents, contribution margin and repeat usage.
- Conduct weekly issue triage and release review; preserve audit and financial records.
- Expand service zones only after measurable readiness and Owner approval.

**Gate:** A4 closure does not authorize A5. Deployment, production data use, live GPS, live payment activation and commercial launch each require their applicable approvals.

---

## 6. Cross-cutting acceptance criteria

A release cannot pass by feature demonstration alone. Applicable criteria must be evidenced by automated tests, manual device checks or operational artifacts.

### Security and privacy
- Deny-by-default authorization; tenant, role, trip, order and shipment boundaries tested.
- Sensitive actions are audited with actor, reason, timestamp and correlation ID.
- Location is consented, scoped, time-bound, revocable and visibly fresh/stale.
- Secrets are not committed; provider callbacks are authenticated; rate limits and abuse controls are tested.
- Personal and financial data are minimized, classified, retained and deleted according to an approved policy.

### Reliability and data integrity
- Idempotent commands and callbacks; duplicate delivery cannot double-book, double-charge or double-credit.
- Concurrency controls protect seats, vehicle capacity, dispatch assignment and ledger posting.
- Migrations support clean upgrade and documented rollback/recovery.
- Outbox/inbox retries are observable and do not silently lose events.
- Backup/restore and degraded-network behavior are tested before production.

### User experience and localization
- Amharic-first end-to-end journeys, with English fallback.
- Accessible touch targets, readable contrast, screen-reader labels and clear error states.
- Offline, slow-network and synchronization states are explicit.
- Ethiopian calendar and ETB formatting are consistent wherever presented.
- No fake GPS, payment success, ticket issuance, operator verification or delivery proof.

### Business readiness
- Service pricing and commission are disclosed and versioned.
- Operator, courier, carrier and merchant eligibility is explicit.
- Support, dispute, cancellation, refund and incident workflows are operationally owned.
- Regulatory, insurance, tax, consumer protection and data-protection reviews are completed for each service and jurisdiction.

---

## 7. Benchmark and differentiation policy

Use global products as capability references, not templates to copy. Benchmark categories include ride-hailing and dispatch, maps/navigation, public/intercity transport, parcel delivery, local delivery marketplaces and freight platforms. Examples include Uber, Lyft, DiDi, Grab, Gojek, Bolt, inDrive, Rapido, Careem, BlaBlaCar, Google Maps, Waze, Moovit, Rome2Rio, DoorDash, Lalamove, DHL, FedEx and Flexport.

MaaleNex differentiation should be validated around:
- Amharic-first and local-language service access.
- Low-bandwidth and offline-tolerant workflows.
- Local landmarks and mixed formal/informal transport realities.
- Unified passenger, parcel and freight coordination with separate safety rules.
- Transparent ETB pricing and auditable provider earnings.
- Local SME, cooperative and regional operator enablement.
- Trust, verification and service recovery that work in local operating conditions.

Do not claim superiority or global ranking without independent, comparable performance and market evidence.

---

## 8. Governance, release and evidence rules

- Maintain the Owner stage gates: **A1 assessment/specification/freeze → A2 read-only reconciliation → A3 implementation → A4 verification → A5 deployment**.
- Record the exact base SHA and head SHA for each implementation branch and PR.
- A2 must not modify main or merge code.
- Keep implementation in feature branches and PRs; preserve unrelated work and repository history.
- No merge, deployment, live provider activation, real GPS collection or commercial launch without separate authorization.
- Report each gate as **PASS, VERIFIED-CLOSED, PARTIAL, MISSING, UNRESOLVED, UNKNOWN or NOT RUN**. Never infer PASS from a successful build alone.
- Every closure report must include scope, exact SHA, PR/branch, changed files, workflow/run links, test evidence, migration status, remaining risks and next gate.
- Prefer free/public CI and authorized free-tier resources. Do not make payment/top-up/deposit a prerequisite; if a required provider or hosting service is unavailable without payment, record it as a blocker and present no-cost alternatives for assessment.
- Do not weaken security controls to make a demo or CI workflow pass.

---

## 9. Immediate execution order

1. Complete and freeze the expanded A1 product requirements and acceptance matrix.
2. Run the read-only A2 repository/PR reconciliation against exact current main and branch SHAs.
3. Approve an ordered integration register and migration plan.
4. Implement P2 shared foundation before broad service expansion.
5. Deliver Move and Transit in bounded, independently verifiable increments.
6. Add Delivery, Cargo, Market, Business and Fleet through shared contracts, not duplicated foundations.
7. Add live payment rails only after provider onboarding and financial/security gates.
8. Complete A4 evidence and closure; obtain separate A5 approval before any production deployment.

**Current next action:** revise the existing A1 specification to incorporate the complete MaaleNex service portfolio, then submit the expanded A1 package for Owner review. This guideline itself does not freeze A1 or authorize implementation beyond already approved scope.
