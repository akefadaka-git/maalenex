# MaaleNex Platform — A1 Product Scope and Architecture Specification v1.1

**Status:** Revised A1 draft — submitted for Owner review; NOT FROZEN  
**Product:** MaaleNex  
**Tagline:** Move. Deliver. Connect. Grow.  
**Platform category:** Mobility • Logistics • Commerce • Business  
**Company:** MaaleNex Technologies PLC (in formation)  
**Repository at issue:** `akefadaka-git/maalenex-moto`  
**Revision date:** 2026-11-08  
**Supersedes:** Biker-First Mobility Platform A1 v1.0

> This document expands the approved mobility direction into a unified platform scope. It is a requirements and architecture specification only. It does not claim that the described services are implemented, freeze A1, authorize new A3 work, authorize merging, or authorize production activity.

---

## 1. Product vision and objectives

MaaleNex is one Amharic-first, mobile-first platform connecting people, transport, goods and businesses. It will provide distinct but interoperable services for local passenger mobility, intercity passenger transport, parcel delivery, freight/logistics, merchant commerce, fleet operations and business accounts.

The platform must be useful in South Omo operating conditions first, then scale across Ethiopia and potentially other African markets through configurable geography, language, currency, regulatory and provider adapters.

### 1.1 Strategic objectives

1. Help passengers find and complete safe, predictable local and intercity journeys.
2. Help bikers, drivers, couriers, carriers and transport operators access demand and manage work.
3. Help individuals and businesses send, receive and move parcels and goods.
4. Help local merchants, SMEs, cooperatives and institutions reach customers and arrange fulfilment.
5. Provide a common trusted operational and financial foundation without collapsing distinct services into one workflow.
6. Build a measurable, reliable product with locally relevant advantages rather than copying proprietary competitor systems.

### 1.2 Success principles

- Safety, reliability and trust take priority over feature count.
- The user must understand price, service provider, status, location sharing and payment status.
- No user is shown fabricated availability, live location, verification, payment success or fulfilment evidence.
- Each service is launched only after its own operational, legal, insurance, support and technical gates pass.
- Global leadership is an ambition, not a guaranteed result. Progress is measured using service reliability, retention, coverage, safety, unit economics and market adoption.

---

## 2. Product and service hierarchy

**Master platform:** MaaleNex  
**Service lines:** the following product areas share platform infrastructure but retain their own eligibility rules, user journeys, data boundaries and lifecycle state machines.

| Service | Scope | Primary participants | Core transaction |
|---|---|---|---|
| **MaaleNex Move** | Local rides: motorcycle taxis/bikers, taxis and other approved vehicle classes | Passenger, biker/driver, operator, dispatcher | Ride |
| **MaaleNex Transit** | Intercity buses, route/stop/terminal catalog, schedules, seat inventory and passenger reservations | Passenger, bus operator, terminal staff | Journey reservation |
| **MaaleNex Delivery** | Documents, parcels, local goods, shop orders and last-mile courier service | Sender, recipient, courier, merchant | Shipment |
| **MaaleNex Cargo** | Intercity goods, freight requests, truck capacity, carrier matching and delivery proof | Shipper, carrier, truck owner, consignee | Freight movement |
| **MaaleNex Market** | Merchant discovery, goods/services catalog, availability and customer orders | Customer, merchant, fulfilment operator | Commerce order |
| **MaaleNex Fleet** | Vehicles, drivers, inspections, availability, maintenance and compliance records | Fleet owner, manager, driver | Fleet asset/assignment |
| **MaaleNex Business** | Business accounts, recurring mobility/delivery, service agreements, cost centres and reporting | SME, institution, enterprise, account manager | Business service agreement/order |
| **MaaleNex Pay** | Payment-provider adapters, ETB ledger, commission, settlement, refund and reconciliation | Payer, payee, operator, finance role | Payment/ledger transaction |

These are service labels under one platform, not separate companies or independently launched applications. The master application should expose only the services enabled for the user's location, account and operating conditions.

---

## 3. Initial market and rollout boundaries

### 3.1 Geographic sequence

- **Pilot geography:** Koybe and Jinka, Maale Woreda / South Omo.
- **First intercity corridor:** Jinka → Wolaita Sodo → Addis Ababa, including validated intermediate stops and return direction where operator supply exists.
- **Ethiopia expansion:** additional service areas and corridors only after local operator supply, customer support, safety, regulatory and unit-economics review.
- **African expansion:** country-specific configuration, operating partners, currency, languages, payment rails, legal review and data residency assessment.
- **Global ambition:** long-term objective; no fixed rank or timeline is promised.

### 3.2 Initial market sequencing

1. Validate local Move demand and operator supply.
2. Validate Transit route/operator data and reservation operations.
3. Add Delivery for documents, parcels and local merchant fulfilment.
4. Add Cargo only after carrier capacity, insurance, goods restrictions and claims handling are established.
5. Add Market and Business capabilities where merchant and SME demand is demonstrated.
6. Activate Pay rails only after provider onboarding, legal and security gates.

The platform architecture should allow all service lines, but implementation and launch are phased. A broad product vision is not authorization to launch every service simultaneously.

---

## 4. User groups, roles and authorization boundaries

### 4.1 User groups

- Passenger/customer and guest customer.
- Biker, motorcycle taxi operator, driver and courier.
- Transport company, bus operator, fleet owner and dispatcher.
- Shipper, carrier, truck owner, warehouse/storage operator and consignee.
- Merchant, shop, restaurant, wholesaler, farmer/cooperative and SME.
- Business/institution account administrator and staff member.
- Customer support, safety/incident responder and dispute reviewer.
- Finance/reconciliation operator, platform administrator and security auditor.

### 4.2 Authorization requirements

- A user may hold multiple roles, but each action must be authorized against the active organization, service, resource and transaction.
- Organization membership does not automatically grant access to all other organizations or customer data.
- Operators can access only their own approved vehicles, staff, trips, shipments, orders and financial statements.
- Customers can access only their own records and transactions, plus explicitly shared active trip/shipment information.
- Support and safety access must be purpose-limited, audited and restricted to the minimum data required.
- Finance roles must be segregated from operational approval where feasible; no single unreviewed role should silently create, approve and reconcile the same financial movement.
- Platform administrators must not have unrestricted routine access to secrets, payment credentials or customer content.
- All privileged actions require audit actor, action, target, timestamp, reason and correlation reference.

A detailed permission matrix and tenant-boundary review are required deliverables for A2 before implementation.

---

## 5. Functional scope by service

### 5.1 MaaleNex Move — local mobility

- Passenger ride request with pickup/drop-off, landmark assistance and service class.
- Biker/driver onboarding, identity and document review, vehicle registration and eligibility approval.
- Availability, dispatch, accept/decline, arrival, pickup confirmation, in-progress, completion and cancellation.
- Fare estimate and transparent fare confirmation before trip acceptance.
- Trip PIN/QR or equivalent verification at the correct lifecycle transition.
- Consent-based live location only during an eligible active matched trip.
- Contact/call-to-verify action; masked/relay calling only if an authorized provider and lawful service are available.
- SOS, emergency contact, support, incident and dispute workflows.
- Biker/driver job history and earnings statements; no live payouts until Pay is separately approved.

### 5.2 MaaleNex Transit — intercity passenger transport

- Operator and route onboarding; authorized stops, terminals and route sequence.
- Operator-published schedules, fares, departure/arrival estimates and seat capacity.
- Search by origin, destination, date, passenger count and available connection.
- Seat inventory and concurrency-safe reservation.
- Passenger manifest, check-in and boarding as distinct states.
- Timetable changes, delay, missed connection, cancellation, refund and support workflows.
- Ticket issuance must be explicitly implemented and verified; a reservation is not automatically a ticket or proof of boarding.
- The initial corridor is Jinka ↔ Wolaita Sodo ↔ Addis Ababa, subject to operator-authorized data.

### 5.3 MaaleNex Delivery — local parcel and goods delivery

- Sender/recipient details with data minimization and delivery-contact controls.
- Parcel category, dimensions/weight, handling needs and prohibited/restricted-goods checks.
- Quote, delivery window, booking, courier assignment and pickup confirmation.
- Custody events, tracking status, recipient verification and proof of delivery.
- Failed delivery, recipient unavailable, return-to-sender, damage/loss claim and dispute paths.
- Merchant order handoff and order/shipment status synchronization.
- Delivery pricing, courier compensation and service-zone policy must be explicit and versioned.

### 5.4 MaaleNex Cargo — freight and logistics

- Shipper, carrier and truck-owner onboarding and verification.
- Freight request with load type, dimensions, weight, quantity, handling and route constraints.
- Vehicle/load capacity and compatibility checks before matching.
- Carrier offers, matching, booking/contract, pickup and custody transitions.
- Shipment tracking, delivery confirmation, proof of delivery, damage/loss claims and dispute handling.
- Multi-stop, return-load and backhaul support only where capacity, contract and safety rules permit.
- Warehouse, storage, transfer point and consolidation coordination are later increments requiring separate workflow and liability definitions.
- Restricted goods, hazardous goods and regulated cargo must be excluded until lawful handling controls and insurance are verified.

### 5.5 MaaleNex Market — commerce

- Merchant onboarding, business verification and store profile.
- Product/service catalog, availability, price, location and fulfilment options.
- Customer discovery, order creation, order confirmation and fulfilment status.
- Merchant cancellation, substitutions, returns/refunds and customer support.
- Delivery may be fulfilled through Delivery or an approved merchant's own delivery process.
- Inventory and catalog updates must not imply real-time stock unless the merchant integration supports it.

### 5.6 MaaleNex Fleet — fleet operations

- Vehicle, owner, operator, driver and service assignment records.
- Vehicle classes, capacity, inspection and operational status.
- License, registration, insurance and document expiry reminders.
- Maintenance, downtime, safety inspection and service history.
- Utilization and availability reporting.
- A fleet record is not proof of regulatory approval; document status and verification source must be visible.

### 5.7 MaaleNex Business — SME and enterprise tools

- Business account hierarchy, members, roles and cost centres.
- Recurring ride, parcel, cargo and delivery requests.
- Service agreements, quotes, invoices and statements.
- Spending limits, approval workflows and business reporting.
- Contracted service levels, fulfilment evidence and dispute handling.
- Farmer/cooperative, wholesaler, institution and local business workflows should be validated through discovery before detailed implementation.

### 5.8 MaaleNex Pay — payment and financial operations

Target rails may include Telebirr, CBE Birr and supported Ethiopian bank/mobile-transfer providers, subject to current documentation, provider onboarding, merchant authorization, credentials, commercial agreement and regulatory review.

- Provider-neutral adapter contract; each provider implementation remains isolated.
- Server-created payment intents and immutable provider transaction references.
- Authenticated/signed provider callback verification and server-to-server status checks.
- Idempotent processing; duplicate callbacks cannot double-charge or double-credit.
- ETB double-entry ledger with gross transaction, provider fee, company commission, service-provider payable, refund, reversal and chargeback entries.
- Commission policy is versioned, effective-dated, service-scoped and disclosed before confirmation. No rate is set by this A1.
- Settlement, payout, failed-payment recovery and daily reconciliation.
- Never collect/store customer banking PINs, OTPs, passwords or full payment credentials.
- No real money movement before separate approval and successful provider, legal, security and operational gates.

---

## 6. Cross-platform capabilities and shared infrastructure

Build shared capabilities once, with service-specific policy and authorization:

1. **Identity and access:** authentication, sessions, recovery, organization membership, role/permission enforcement and revocation.
2. **Trust and verification:** person/operator/merchant/vehicle/carrier verification status, document metadata, approval history and expiry alerts.
3. **Catalog and geography:** service areas, locations, landmarks, terminals, routes, service availability and localized names.
4. **Pricing and policy:** versioned quotes, fares, fees, cancellation/refund policies and commission rules.
5. **Dispatch and matching:** shared matching primitives, with separate eligibility, capacity and priority rules per service.
6. **Maps and geospatial:** provider adapter, route estimates, landmark search and location freshness. Do not hardwire the product to one provider before cost/coverage review.
7. **Location sessions:** explicit consent, active resource binding, participant-scoped access, expiry, revocation and retention controls.
8. **Communication:** notifications, support messaging and authorized call relay integration where available.
9. **Payments and ledger:** provider adapters, immutable journal, reconciliation and role segregation.
10. **Audit and evidence:** append-only event history for critical service, trust, safety and finance actions.
11. **Support and safety:** incident reporting, emergency escalation, claims, disputes and appeals.
12. **Analytics:** operational KPIs, data quality, privacy-preserving product analytics and fraud/abuse signals.
13. **Partner API:** versioned contracts, scoped credentials, webhook signing, quotas, partner lifecycle and revocation.
14. **Localization:** Amharic default, English fallback, ETB, Ethiopian calendar display where appropriate, accessible layouts and local date/time conventions.

---

## 7. Architecture constraints and technology direction

### 7.1 Starting architecture

- Backend: modular FastAPI application with explicit domain packages, service boundaries and API contracts.
- Data: PostgreSQL with Alembic-managed migrations; assess geospatial extension compatibility before adopting it.
- Frontend: React, TypeScript and Vite; mobile-first responsive UI and installable PWA/Android wrapper as validated by the current app architecture.
- Background work: durable job processing and transactional outbox/inbox patterns for events and external callbacks.
- Real-time: authenticated WebSocket or managed pub/sub only where required; resource-scoped authorization, heartbeat, expiry, replay protection and rate limits.
- Observability: structured logs, correlation IDs, metrics, health/readiness checks and actionable alerts.
- Integrations: provider adapters behind interfaces; no provider credentials or secrets in source.

Do not split into microservices prematurely. Modular monolith first; extract a service only when scale, fault isolation, deployment ownership or regulatory boundary justifies the operational cost.

### 7.2 Data and transaction rules

- Each service owns its lifecycle and invariants.
- Use stable identifiers, explicit status transitions, timestamps and idempotency keys.
- Protect seats, vehicle capacity, courier assignments and freight capacity with database constraints/transactions and deterministic concurrency handling.
- Use an outbox for reliable event publication and an inbox/idempotency record for external callbacks.
- Financial journals are append-only; corrections use compensating entries.
- Separate customer, operator, merchant, shipment, location and finance data access by purpose and authorization.
- Data retention, deletion, export and legal hold rules must be defined before real personal data is processed.

### 7.3 Mobile and connectivity

- Amharic-first interface, English fallback and accessibility requirements.
- Offline-safe read cache for appropriate data; retryable writes with idempotency and explicit queued/synced/failed states.
- Never claim a booking, dispatch acceptance, payment, ticket, delivery or cancellation succeeded before authoritative server confirmation.
- Minimize battery/data usage; location permission must be requested in context and can be revoked.
- Support low bandwidth and interrupted sessions without duplicating financial or operational commands.

---

## 8. Privacy, safety, security and compliance requirements

### 8.1 Location and communication

- No silent tracking or collection before a valid purpose and explicit permission.
- Precise location visibility is restricted to the matched active trip/shipment and authorized safety/support access.
- Show last update time and stale status; stop or expire sharing at trip/job completion, cancellation or revocation.
- Do not expose a user's home address or precise location to unrelated users.
- Trip PIN/QR is a confirmation control, not a replacement for identity verification.
- Masked/relay calls require provider support and legal review; a call is not proof of identity or completion.

### 8.2 Security baseline

- Deny by default; test cross-tenant, cross-role, cross-trip, cross-order and cross-shipment access.
- Strong session/device revocation, rate limiting, brute-force protection and abuse detection.
- Encrypt traffic; protect stored sensitive data and secrets; minimize data collection.
- Audit privileged changes and critical service/financial transitions.
- Verify provider callbacks cryptographically and defend against replay.
- Security review and incident-response procedures precede production data use.

### 8.3 Regulatory and operating readiness

Each service requires a separate compliance checklist covering applicable Ethiopian transport, commercial, consumer protection, insurance, tax, privacy/data protection, payments and local administrative requirements. The A1 does not assert that any license, permit, insurance or provider agreement has been obtained.

---

## 9. Global product benchmark and differentiation framework

Benchmark leading products for capabilities, not proprietary code, confidential workflows or protected designs. API integration is permitted only where an authorized public/partner API and applicable terms allow it.

| Benchmark category | Example references | Capabilities to study |
|---|---|---|
| Ride-hailing and dispatch | Uber, Lyft, DiDi, Grab, Gojek, Bolt, inDrive, Rapido, Careem | Matching, driver tools, fare transparency, safety and marketplace liquidity |
| Shared/intercity travel | BlaBlaCar, Rome2Rio | Route discovery, connections, schedules and passenger information |
| Maps and navigation | Google Maps, Waze, Moovit | Geocoding, landmarks, route estimates, transit information and offline usability |
| Local commerce and delivery | DoorDash, Uber Eats, Lalamove | Merchant onboarding, order lifecycle, courier dispatch and fulfilment |
| Parcel and freight logistics | DHL, FedEx, Flexport | Tracking, custody, shipment exceptions, carrier visibility and business logistics |

### 9.1 MaaleNex differentiation hypotheses to validate

- Amharic-first user journeys and practical local-language support.
- Low-bandwidth and offline-tolerant workflows for regional connectivity.
- Local landmarks and mixed formal/informal transport realities.
- Mobility, parcel and freight coordination on shared infrastructure with distinct safety rules.
- Transparent ETB pricing and traceable provider earnings.
- SME, cooperative, merchant and regional operator enablement.
- Human-accessible support and dispute recovery for local operating conditions.

No claim of being better than, or ranked above, a benchmark is accepted without comparative user, reliability, safety and business evidence.

---

## 10. Acceptance matrix for A1 and downstream gates

A1 acceptance means requirements are complete enough to assess and plan. It does not mean the features are built.

| ID | Requirement to freeze | Required evidence in A1/A2 |
|---|---|---|
| A1-01 | Master product and eight service-line scope | Approved product hierarchy and explicit exclusions |
| A1-02 | Geography and rollout order | Pilot geography, first corridor and expansion gates |
| A1-03 | Personas and authorization | Role matrix, organization boundaries and access scenarios |
| A1-04 | Service lifecycles | State diagrams for ride, bus reservation, parcel, freight, order, fleet and payment |
| A1-05 | Shared architecture | Domain map, API/event boundaries and ownership |
| A1-06 | Data and migration safety | Existing-schema reuse map, migration dependency and collision plan (A2) |
| A1-07 | Privacy and location | Consent, visibility, expiry, revocation, retention and abuse cases |
| A1-08 | Financial integrity | Ledger model, commission policy requirements, callback and reconciliation controls |
| A1-09 | External integrations | Provider/API dependency register and sandbox/production boundaries |
| A1-10 | Localization and accessibility | Amharic/English, ETB, Ethiopian calendar, offline and accessibility acceptance |
| A1-11 | Security and reliability | Threat model, authorization tests, idempotency, concurrency and recovery gates |
| A1-12 | Operational readiness | Support, safety, dispute, insurance, compliance and operator readiness checklist |
| A1-13 | Measurement | KPI definitions, baseline plan, targets to be set after discovery |
| A1-14 | Delivery order | Dependencies, phased scope, risks and release gates |

### 10.1 Minimum downstream verification

- Move: request/match/accept/complete/cancel, unauthorized access rejection, location consent/revoke and safety flow.
- Transit: route search, seat hold/reservation concurrency, manifest/check-in/boarding state separation and cancellation/refund.
- Delivery: parcel eligibility, assignment, custody chain, recipient verification, proof of delivery and failed-delivery recovery.
- Cargo: capacity/weight/size checks, carrier matching, custody, claims and delivery evidence.
- Market: merchant authorization, catalog availability, order/fulfilment and cancellation/refund.
- Fleet: vehicle/driver assignment, expiry/inspection controls and maintenance status.
- Business: organization isolation, member roles, approvals, recurring requests and statement correctness.
- Pay: signed callback, replay/duplicate idempotency, ledger invariants, refunds and reconciliation.

---

## 11. Delivery sequence and stage gates

The detailed execution guideline is maintained in `docs/MAALENEX-PLATFORM-IMPLEMENTATION-GUIDELINE-v1.0.md`. The A1-level sequence is:

| Stage | Scope | Exit gate |
|---|---|---|
| **A1** | Freeze product scope, personas, service lifecycles, architecture, privacy, acceptance and phased plan | Explicit Owner A1 approval |
| **A2** | Read-only reconciliation of repo, PRs, code reuse, schema, migrations, security and dependencies | A2 closure report and Owner approval |
| **A3-P2** | Shared platform foundation | Domain/API/security/migration tests |
| **A3-P3** | Local Move | End-to-end and device acceptance |
| **A3-P4** | Transit corridor | Operator-authorized catalog and seat/boarding tests |
| **A3-P5** | Delivery | Shipment lifecycle and custody acceptance |
| **A3-P6** | Cargo | Carrier/capacity/custody and claims acceptance |
| **A3-P7** | Market, Fleet and Business | Merchant, fleet and business workflow acceptance |
| **A3-P8** | Pay | Provider sandbox, ledger, callback and reconciliation gates |
| **A3-P9** | Intelligence and partner ecosystem | Measured model/API/security acceptance |
| **A4** | Integrated security, regression, concurrency, privacy, accessibility, performance and device verification | Exact-SHA A4 closure |
| **A5** | Hosting, live provider activation, pilot and production deployment | Separate explicit Owner authorization |

A2 is read-only: no main changes, no merge and no implementation edits under the A2 assessment label. A4 does not imply A5 approval.

---

## 12. Current verified baseline, blockers and exclusions

### 12.1 Known existing baseline

The repository currently has a passenger-MVP foundation and synthetic catalog/route inventory work. Existing domain areas include identity, audit, organization, catalog, fleet, trips, fares, bookings, reservations and support. Existing implementation and PRs must be reconciled against exact SHAs during A2.

The existing passenger MVP is not a complete multi-service platform. Do not represent proposed biker dispatch, production location, parcel delivery, freight, merchant commerce, provider payments or business workflows as already implemented.

### 12.2 Known blockers

- No persistent, approved HTTPS API endpoint is established for installed mobile clients; ephemeral CI API services are not production/test hosting.
- No approved map/geocoding/routing provider is selected.
- No production GPS stream, location retention service or call-relay provider is implemented.
- No verified payment-provider API credentials, agreements or sandbox acceptance evidence are established here.
- No commission rate or settlement agreement is approved.
- No parcel/cargo insurance, restricted-goods policy, carrier contract or claims operation is approved.
- No complete merchant onboarding, inventory or order fulfilment domain is established.
- No production operator onboarding, commercial launch, regulatory clearance or deployment is authorized by this document.

### 12.3 Explicit exclusions

- No proprietary competitor code copying or unauthorized API use.
- No real personal data, identity documents, production location traces or payment credentials in repository/CI.
- No real GPS collection, live payment activation, payout, commission charging or commercial operations.
- No paid service, deposit, top-up or billing dependency is to be assumed. If an integration requires paid access, record it as a blocker and assess authorized no-cost alternatives without weakening controls.
- No merging PRs, modifying main, production hosting or deployment by virtue of this specification.
- No automatic Android application ID/package rename; assess upgrade compatibility separately before any identity migration.

---

## 13. A1 decisions required from Owner

The following remain open for explicit decision or validation before A1 can be frozen:

1. Confirm the eight-service portfolio and the proposed order of delivery.
2. Confirm Koybe/Jinka as the pilot area and Jinka → Wolaita Sodo → Addis Ababa as the first intercity corridor.
3. Confirm that Cargo and Market are phased after Move/Transit/Delivery foundations, not simultaneous launch commitments.
4. Approve the role/organization matrix after A2 identifies existing access-control behavior.
5. Confirm service-specific safety and prohibited-goods boundaries after legal/insurance review.
6. Select maps, messaging and payment providers only after free/available options, coverage, provider terms and integration requirements are assessed.
7. Set pricing and commission only after cost, provider fees, market validation and operator consultation; no values are assumed.
8. Approve the final acceptance matrix and measurable pilot KPIs.

**A1 status remains DRAFT / NOT FROZEN until the Owner explicitly approves the completed specification and decisions.**

---

## 14. Immediate next steps

1. Review this expanded A1 v1.1 specification against the implementation guideline.
2. Resolve open product decisions and service boundaries; do not infer approval from silence.
3. Conduct the authorized A2 read-only reconciliation against exact current main and PR heads.
4. Produce the final A1 closure package and ordered A2 integration register.
5. Begin A3 only after the applicable Owner approval and bounded implementation authorization.

**Revision note:** v1.1 expands the earlier biker-first A1 draft to the complete MaaleNex Mobility, Logistics, Commerce and Business platform. Existing synthetic test catalog code and passenger MVP behavior are unchanged by this document revision.
