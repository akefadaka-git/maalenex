# MaaleNex Moto — Passenger MVP A1 Implementation Plan

- **Document ID:** MNM-PLAN-PAX-A1-001
- **Version:** 1.0
- **Status:** Prepared for Owner review; implementation not authorized
- **Prepared:** 2026-11-07
- **Repository:** akefadaka-git/maalenex-moto
- **Planning branch:** docs/product-scope-roadmap-v1
- **Product requirements authority:** docs/PASSENGER-MVP-REQUIREMENTS-BASELINE-v1.0.md
- **Governance authority:** docs/JINKA-PILOT-GOVERNANCE-DECISION-REGISTER-v1.0.md
- **Related specifications:** docs/PASSENGER-MOBILITY-PRD-v0.1.md; docs/JINKA-OPERATOR-ONBOARDING-v0.1.md

> **Authorization statement:** This is an A1 planning artifact. It records a proposed architecture, dependencies, backlog, threat model, synthetic acceptance scenarios, migration strategy, and evidence gates. It does not authorize application code, database schema or migration changes, real operator engagement, collection of real personal data, payment integration or collection, production deployment, or live service activation. Those activities require separate explicit Owner approval.

---

## 1. Executive decision

Build the first MaaleNex Moto passenger product as a **modular monolith**: one FastAPI application, one React/TypeScript client, and PostgreSQL. Implement passenger booking around server-authoritative trip inventory, atomic seat allocation, expiring holds, immutable fare snapshots, server-issued tickets, and controlled boarding validation.

The launch planning scope is **Jinka-first, passenger-first**:
- Initial boarding model: Jinka Bus Terminal only.
- Initial candidate route priorities: Jinka–Wolaita Sodo, then Jinka–Addis Ababa. Neither route is represented as verified or active by this plan.
- Operator model: small, verified cohort of participating terminal operators; names and cohort size remain open.
- Multiple passengers per booking; one explicit seat per passenger.
- Configurable 10-minute seat hold for design and synthetic testing only.
- Passenger booking identity: name and reachable phone number; no identity-document collection by default.
- In-app ticket with unique reference and QR; printable fallback.
- Online-first; offline boarding excluded.
- Payment collection remains disabled. No provider, custody, commission, fee, settlement, or refund amount is selected.
- Freight is a later, separately scoped domain and is excluded from this implementation plan.

## 2. Repository baseline and A1 findings

### 2.1 Exact repository evidence

The following public GitHub state was inspected read-only on 2026-11-07:

| Item | Evidence |
|---|---|
| Repository default branch | main |
| Main baseline SHA | 72550a2e464f6517653580bb1ae4e7608f211f39 |
| G1 PR | PR #1, open, draft, unmerged |
| G1 branch | feat/g1-foundation-completion |
| G1 branch head | 50e38a94011eb24d06812acace7d09e4d8e81dc8 |
| Planning PR | PR #2, open, non-draft, unmerged |
| Planning branch | docs/product-scope-roadmap-v1 |
| Planning branch head before this plan | 50e6933be44d8192319eb4e38861fdc44ae43392 |

PR #1 and PR #2 are separate branches from the same main baseline. The passenger implementation must not assume G1 is merged. The G1 foundation must first pass its own review and be integrated in a separately authorized way. Do not merge either PR as part of A1.

### 2.2 Confirmed foundation capabilities and gaps

Inspected G1 files show:
- FastAPI application and versioned API prefix are scaffolded.
- CORS is restricted to the configured local frontend origin and GET methods in the current G1 baseline.
- The current API surface is root/health only; there are no passenger business endpoints.
- SQLAlchemy base, request-scoped database session, PostgreSQL/psycopg configuration, and Alembic framework are present on the G1 branch.
- Alembic revision 0001_g1_foundation deliberately creates no business tables.
- React 18, TypeScript, Vite, Vitest, and an Amharic-first shell are scaffolded.
- G1 module boundaries reserve app/domains for domain-owned services, models, and policies after the next domain approval.
- The existing G1 validation runner is a local PowerShell script. No CI execution or current full validation result is claimed by this plan.

Security baseline is explicitly development-only: no authentication, authorization, audit, rate limiting, production key management, backup/disaster recovery, or incident response is currently complete. The existing data classification prohibits personal, financial, and secret data in development.

### 2.3 A1 findings / blockers

| ID | Finding | Consequence |
|---|---|---|
| A1-F01 | G1 PR #1 is still open and unmerged | Passenger work must not assume the foundation is on main. |
| A1-F02 | No authentication or authorization exists | Identity and access design is a prerequisite to protected operator and passenger actions. |
| A1-F03 | No business schema exists | Domain schema and migration design require a separate approved implementation gate. |
| A1-F04 | No audit or security controls are implemented | Privileged workflow design must include attributable audit and authorization from its first release. |
| A1-F05 | Current CORS and API methods are GET-only | Write APIs require deliberate, narrowly scoped changes; do not broadly enable methods. |
| A1-F06 | Current data policy prohibits personal data in development | All implementation and acceptance fixtures must remain synthetic; real passenger data is prohibited. |
| A1-F07 | README still describes a motorcycle-first service | Product documentation needs controlled reconciliation to the approved passenger-first, later-freight scope. |
| A1-F08 | Operator, terminal, route, legal, support, and refund authorities are not designated | Real-world onboarding and public service activation remain blocked. |
| A1-F09 | Payment collection model and provider are unselected | No live payment integration or collection may be implemented. |

**A1 conclusion:** The technical direction is feasible within the existing modular-monolith foundation, but the repository is not ready for passenger feature implementation until the G1 integration dependency, identity/access design, domain architecture, and security controls are reviewed and approved.

## 3. Architecture boundaries

### 3.1 Architectural principles

1. Preserve the accepted modular-monolith ADR. Do not introduce microservices, message brokers, distributed caches, or a separate mobile app without evidence and separate approval.
2. Keep transport/API handlers thin. Business rules belong in domain services and policies, not routers or React components.
3. Give each domain ownership of its models, persistence mappings, validation, and state transitions.
4. Cross-domain collaboration uses explicit application interfaces or domain events; never import another domain's ORM models or repository internals.
5. PostgreSQL is the authoritative source for trip inventory, holds, bookings, ticket state, and audit records.
6. The browser is never authoritative for price, availability, payment status, booking state, ticket validity, or boarding permission.
7. Design the payment boundary as disabled and non-operational. Do not accept payment credentials or simulate provider success as if it were real.
8. Keep all development/test environments synthetic-only and local-only under the current G1 restriction.

### 3.2 Proposed logical domains

| Domain / capability | Owns | Must not own |
|---|---|---|
| Identity & Access | User identity, authentication lifecycle, sessions/tokens, role/permission evaluation, account status | Passenger trip or booking business rules |
| Organization & Operator Registry | Operator organization profile, membership, operator status, reviewer/approval records | Passenger inventory or payment custody |
| Route & Location Catalog | Cities, terminals, stops, route definitions, boarding/drop-off permissions and publication status | Vehicle maintenance or booking state |
| Fleet & Vehicle Configuration | Vehicle records, seat layouts, capacity, review state, vehicle-to-operator relationship | Trip inventory allocation |
| Schedule & Trip Operations | Schedules, trip instances, assigned vehicle/crew, trip lifecycle and publication | Booking ownership or passenger payment |
| Booking & Seat Inventory | Search eligibility, segment/seat availability, seat holds, bookings, fare snapshots, booking state machine | Provider settlement or operator onboarding decisions |
| Ticketing & Boarding | Ticket reference/QR payload, ticket status, boarding validation and trip-scoped manifests | Fare calculation, payment provider credentials |
| Support & Case Management | Passenger/operator support cases, case state, evidence references and policy-authorized actions | Independent refund or financial custody rules |
| Audit & Compliance (cross-cutting) | Append-only security/business audit events, actor attribution, correlation IDs, evidence references | General-purpose business data dumping ground |
| Notifications (later capability) | Delivery preferences and notification dispatch records | Authoritative booking or ticket state |
| Payment boundary (disabled adapter seam only) | Future provider interface contract and explicit disabled configuration | Live collection, custody, wallet, settlement, or provider selection |

**Important boundary:** Identity, audit, and authorization are cross-cutting platform capabilities but must still have clear owners and explicit interfaces. The initial passenger MVP should not create a general-purpose shared domain that accumulates unrelated business logic.

### 3.3 Proposed code organization

The following is a target structure for a separately approved implementation. It is not a claim that these packages currently exist.

- backend/app/core — settings, dependency wiring, error handling, correlation IDs.
- backend/app/db — SQLAlchemy base, engine/session lifecycle, transaction helpers.
- backend/app/routers — versioned HTTP adapters only.
- backend/app/schemas — transport request/response contracts.
- backend/app/domains/identity — authentication, sessions, permissions.
- backend/app/domains/organizations — operator organization and approval lifecycle.
- backend/app/domains/catalog — locations, terminals, routes, boarding points.
- backend/app/domains/fleet — vehicles, seat layouts, review state.
- backend/app/domains/trips — schedules, trip instances, assignments, publication.
- backend/app/domains/bookings — holds, inventory allocation, booking state and fare snapshots.
- backend/app/domains/ticketing — ticket issuance and boarding validation.
- backend/app/domains/support — cases and authorized exception handling.
- backend/app/audit — shared audit contract and persistence adapter, subject to architecture review.
- frontend/src/app — application shell, routing, locale and session boundaries.
- frontend/src/features/passenger-search — trip search and result display.
- frontend/src/features/booking — passenger details, seat selection, hold and booking state.
- frontend/src/features/tickets — ticket display, QR and print view.
- frontend/src/features/operator — operator setup and trip operations, behind permissions.
- frontend/src/features/terminal — departure/boarding view, trip-scoped.
- frontend/src/shared — design tokens, reusable UI, API client, safe error handling.

The frontend feature folders are presentation boundaries, not independent authorities. All business validation remains server-side.

### 3.4 Core invariants

- A seat can have at most one active allocation for overlapping trip/route segments.
- A booking cannot exceed the authorized seat capacity or assign one seat twice.
- A hold has an immutable expiry timestamp and can transition out of active state only once.
- A confirmed booking preserves a fare snapshot and policy version; later fare changes do not rewrite it.
- A ticket is issued only from an eligible server-side booking state.
- A QR code is an opaque reference or signed payload, not a bearer token containing personal data.
- A ticket can be boarded only for its assigned trip and authorized boarding point, subject to the online-only rule.
- A user can access only the passenger, operator, trip, or manifest scope explicitly granted.
- A payment status cannot become paid from browser input or an unverified callback.
- Every privileged state transition is attributable and auditable.

### 3.5 Data ownership and conceptual entities

| Domain | Candidate entities (conceptual only) |
|---|---|
| Identity | User, Credential, Session, Role, Permission, RoleAssignment |
| Organization | Operator, OperatorMembership, OperatorReview, ApprovalDecision |
| Catalog | Location, Terminal, Stop, Route, RouteStop, BoardingPermission |
| Fleet | Vehicle, SeatLayout, Seat, VehicleReview |
| Trips | Schedule, Trip, TripStop, TripVehicleAssignment, TripPublication |
| Booking | Booking, PassengerReference, SeatHold, SeatAllocation, FareSnapshot |
| Ticketing | Ticket, TicketValidation, BoardingEvent |
| Support | SupportCase, CaseAction, CaseEvidenceReference |
| Audit | AuditEvent, SecurityEvent |
| Payment seam only | PaymentAttempt interface/type placeholder; no provider credentials, transaction processing, or financial ledger in this phase |

This table does not authorize schema creation. The exact entity model, tenant/organization scope, retention, constraints, and indexes must be reviewed before migrations are written.

## 4. Domain dependency graph

### 4.1 Required dependency order

1. **G1 technical foundation** — repository base, API, frontend shell, PostgreSQL/Alembic, local validation. Must be separately reviewed and integrated.
2. **Identity & Access** — minimum user/session model and permission enforcement for protected actions. Booking identity and account/session behavior must be finalized before booking implementation.
3. **Audit foundation** — attributable events for authentication, approvals, fare publication, trip publication, booking state, ticket issuance, and boarding.
4. **Organization & Operator Registry** — operator organizations and review/approval states, using synthetic operator fixtures only.
5. **Route & Location Catalog** — Jinka terminal, synthetic destinations/stops, route and boarding authorization. No real route is marked verified by seed data.
6. **Fleet & Vehicle Configuration** — synthetic vehicles and seat layouts, capacity and review gates.
7. **Schedule & Trip Operations** — synthetic schedules and trips linked to approved-in-test operator, route, and vehicle records.
8. **Booking & Seat Inventory** — search eligibility, seat holds, concurrency-safe allocation, multi-passenger booking and fare snapshot.
9. **Ticketing & Boarding** — server-issued ticket and QR, trip-scoped manifest, online validation.
10. **Support and exception workflows** — only after cancellation/disruption policy and responsibility rules are approved; unresolved refund handling remains disabled.
11. **Payment provider integration** — not part of this plan; requires separate legal, commercial, security and technical approval.
12. **Pilot readiness and production** — separate operational, privacy, security, hosting, support, legal and Owner gates.

### 4.2 Dependency rules

- Trips depend on approved-in-test operator, route, vehicle, and seat layout.
- Booking depends on trip publication, authoritative inventory, fare approval, and identity/access.
- Ticketing depends on confirmed booking state and audit.
- Boarding depends on valid ticket, trip assignment, authorized staff, and trip-specific boarding rules.
- Support depends on audit and the approved policy for the action requested.
- Payment is deliberately not a dependency for the initial synthetic booking lifecycle; payment state must remain disabled/not collected. A future paid journey cannot be activated until payment is separately approved.
- Notifications are not a dependency for MVP ticket validity. The in-app ticket and printable fallback are sufficient for the initial functional scope.

## 5. Prioritized implementation backlog

Priority definitions: **P0** = blocking prerequisite for passenger MVP; **P1** = required for initial end-to-end synthetic acceptance; **P2** = deferred or optional enhancement. Estimates and sprint dates are intentionally omitted until implementation approval and capacity planning.

| ID | Priority | Work package | Main deliverable | Dependencies | Exit evidence |
|---|---|---|---|---|---|
| PAX-A1-01 | P0 | G1 integration readiness | Confirm G1 PR #1 review, exact head, validation evidence, and approved integration order | Existing PR #1 | Exact SHA, PR review and validation record |
| PAX-A1-02 | P0 | Architecture and contracts | Domain map, ownership rules, API conventions, state machines, transaction boundaries | A1 approval | Reviewed architecture decision and contract inventory |
| PAX-A1-03 | P0 | Identity/access | Authentication/session baseline, role/permission matrix, organization scoping, account lifecycle | G1; A1-02 | Negative/positive permission tests; session security evidence |
| PAX-A1-04 | P0 | Audit/security foundation | Audit event contract, redaction, correlation IDs, privileged action audit | G1; A1-02 | Audit completeness and tamper-resistance design review |
| PAX-A1-05 | P0 | Organization/operator registry | Synthetic operator application, review, approval and restriction lifecycle | Identity; audit | State-transition and separation-of-duties tests |
| PAX-A1-06 | P0 | Route/location catalog | Synthetic Jinka terminal, destination, route, stop and boarding permission catalogue | Operator; audit | Unauthorized/unapproved route and stop cannot publish |
| PAX-A1-07 | P0 | Fleet/seat layout | Synthetic vehicles, seat maps, capacity and review status | Operator; audit | Capacity/layout consistency tests |
| PAX-A1-08 | P0 | Trip operations | Synthetic schedules, trip instances, vehicle assignment and publication controls | Catalog; fleet; operator | Only approved synthetic trips appear in search |
| PAX-A1-09 | P0 | Booking/seat inventory | Search, multi-passenger booking, 10-minute configurable hold, atomic seat allocation, fare snapshot | Identity; trips; audit | Concurrency, expiry, idempotency and fare snapshot tests |
| PAX-A1-10 | P0 | Ticketing/boarding | Unique ticket reference, QR validation, printable ticket, assigned-trip manifest | Booking; identity; audit | Ticket forgery/replay/scope tests and boarding tests |
| PAX-A1-11 | P0 | Synthetic passenger UX | Amharic-first/English-capable search, seat selection, booking, ticket flow | API contracts; booking; ticketing | Accessibility, responsive and end-to-end synthetic checks |
| PAX-A1-12 | P1 | Support and trip exceptions | Case workflow and disruption handling without live financial refunds | Audit; policy approval | Authorization and policy-state tests |
| PAX-A1-13 | P1 | Operational reporting | Synthetic trip, seat, booking, boarding and exception summaries | Trips; booking; ticketing | Role-scoped report access and reconciliation tests |
| PAX-A1-14 | P2 | SMS/email notifications | Delivery adapters and preferences | Notification policy, provider approval | Delivery retry/privacy evidence |
| PAX-A1-15 | P2 | Offline boarding | Separate offline threat model, signed manifests, replay/reconciliation controls | Not in MVP | Requires new Owner approval |
| PAX-A1-16 | P2 | Intermediate boarding | Segment-based inventory and trip-specific stop authorization | Legal/operational validation | Requires separate route and boarding approval |

**Explicitly excluded backlog:** live payment provider, wallet, stored value, commissions, settlements, real operator onboarding, production data migration, public service launch, freight, and offline boarding.

## 6. Security and privacy threat model

### 6.1 Data classes and permitted fixtures

| Data class | Examples | A1 implementation rule |
|---|---|---|
| Public | Product documentation, generic route labels | Allowed |
| Synthetic | Fictional passenger names/phones, fake operators, fake vehicles, synthetic trips | Allowed only when clearly fictional and non-routable |
| Personal | Real passenger name/phone, identity documents, precise location, operator representative identity | Prohibited in development and test |
| Financial | Real payment credentials, transaction records, settlement data | Prohibited; no live payment flow |
| Secrets | Passwords, session secrets, API keys, signing keys | Never commit; use local-only development secrets where necessary |

Synthetic phone numbers must use reserved/non-routable test patterns and must not be capable of reaching a real person. Synthetic QR values must not validate against any real service.

### 6.2 Threat register

| ID | Threat / abuse case | Impact | Required control / mitigation | Verification evidence |
|---|---|---|---|---|
| TH-01 | Unauthorized account access or session theft | Passenger/operator account compromise | Secure session lifecycle, appropriate password/verification policy, secure cookie/token handling, CSRF protection where cookie auth is used, session revocation | Session fixation, expiry, revocation, CSRF and unauthorized access tests |
| TH-02 | Broken object-level authorization / IDOR | Cross-passenger or cross-operator data disclosure | Enforce ownership, organization and trip scope in every query and action; deny by default | Cross-tenant and cross-role negative tests |
| TH-03 | Privilege escalation or self-approval | Unverified operator/vehicle/trip becomes active | Role separation, approval workflow, immutable decision audit, no submitter self-approval | Role matrix and forbidden transition tests |
| TH-04 | Double booking under concurrency | Two passengers receive same seat | Database-enforced allocation invariant, transaction isolation/locking strategy, idempotency keys, unique constraints | Concurrent race test with one winner only |
| TH-05 | Hold expiry race or replay | Stale hold blocks or reclaims seat incorrectly | Persisted expiry, atomic transition, server clock, idempotent release, compare-and-set/locking | Expiry boundary, duplicate expiry worker and replay tests |
| TH-06 | Fare tampering | Underpayment or misleading price | Server-side fare selection, immutable fare snapshot, controlled fare publication | Client-supplied price ignored; historical booking unchanged |
| TH-07 | Ticket/QR forgery or replay | Unauthorized boarding or duplicate boarding | Opaque random reference or signed minimal payload, server-side lookup, trip binding, one-time boarding event, replay detection | Forged, altered, expired, wrong-trip and repeated QR tests |
| TH-08 | Manifest overexposure | Passenger personal data disclosed to unauthorized staff | Trip-scoped, least-privilege manifest; field minimization; access audit | Unauthorized role and unassigned trip access denied |
| TH-09 | Personal data leakage through logs/errors | Persistent privacy exposure | Structured log allowlist, redact names/phones/tokens, generic client errors, restricted log access | Log inspection with synthetic canary data |
| TH-10 | Abuse of search/booking endpoints | Enumeration, denial of service, hold exhaustion | Rate limits, bounded queries, abuse monitoring, per-account/session quotas after identity design | Rate-limit and resource-exhaustion tests |
| TH-11 | Malicious or oversized uploads | Malware/storage exhaustion | No document upload in initial passenger MVP; future uploads require isolated scanning and retention design | Verify upload routes absent/disabled |
| TH-12 | Secret or configuration exposure | Account takeover or service compromise | No secrets in Git; secret scanning; environment separation; rotation procedure | Repository scan and configuration review |
| TH-13 | Database compromise or excessive privilege | Broad passenger/operator data exposure | Least-privilege DB account, local-only dev DB, encryption-at-rest decision for later hosting, parameterized ORM queries | DB role/config review and injection tests |
| TH-14 | Unsafe dependency or supply-chain change | Remote code execution/data theft | Pinned/controlled dependencies, vulnerability review, lockfile discipline, minimal packages | Dependency inventory and vulnerability review |
| TH-15 | Payment spoofing or fake callback | False paid booking | Payment endpoints and callback routes absent/disabled; no client can mark paid | Route inventory and negative payment-state tests |
| TH-16 | Audit deletion or repudiation | Cannot reconstruct privileged action | Append-only application contract, restricted write path, immutable external retention only after production design | Audit event completeness and tamper test |
| TH-17 | Insecure offline validation | Replay or stale manifest permits duplicate boarding | Offline boarding excluded from MVP | Confirm no offline boarding path shipped |
| TH-18 | Misleading operator/route endorsement | Passenger harm or false service promise | Explicit evidence states, publication approval, no route marked verified from seed data | Unapproved records remain unbookable |

### 6.3 Privacy-by-design requirements

- Collect only passenger name and reachable phone number as approved initial booking identity.
- Do not collect identity-document images or precise GPS location in the initial MVP.
- Decide whether passenger accounts are mandatory or guest booking is allowed before implementing identity UX; the approved identity fields do not by themselves decide account policy.
- Define lawful purpose, notice/consent where applicable, retention, deletion, access, correction, and incident response with qualified local advice before real data collection.
- Keep passenger identity out of public URLs, QR payloads, analytics events, and general logs.
- Restrict passenger details to the passenger and specifically authorized support/operator personnel for a legitimate trip-related purpose.
- Define separate retention and access rules for bookings, audit, support cases, and operator evidence.
- No real personal-data processing, production hosting, or cross-border transfer is permitted under the current development baseline.

## 7. Synthetic acceptance scenarios

All scenarios use generated fictional passengers, operators, vehicles, routes, schedules, fares, and tickets. Test data must never contain real names/phone numbers or real operational documents.

| ID | Scenario | Expected result |
|---|---|---|
| SYN-01 | Seed one fictional Jinka terminal, two candidate destinations, one synthetic operator, vehicle and trip | Records are visibly synthetic; no route is represented as live/verified |
| SYN-02 | Search a published synthetic trip | Only trips passing operator, route, vehicle, schedule and publication gates are returned |
| SYN-03 | Search an unpublished or suspended trip | Trip is not bookable and status is not misrepresented |
| SYN-04 | Book two passengers with two distinct seats | One booking contains two passenger references and two distinct allocations |
| SYN-05 | Two sessions attempt the same seat concurrently | Exactly one active allocation succeeds; the other receives a safe conflict response |
| SYN-06 | Hold remains within configured 10-minute window | Seat remains unavailable to competing booking attempts |
| SYN-07 | Hold reaches expiry boundary | Hold expires once; inventory is released once; a later valid request can reserve it |
| SYN-08 | Expiry processor retries the same hold | Idempotent result; no duplicate release or inconsistent inventory |
| SYN-09 | Passenger retries booking request after network timeout with same idempotency key | Same booking result is returned; duplicate booking is not created |
| SYN-10 | Client submits a modified fare | Server ignores client amount and uses the authorized fare; booking snapshot is immutable |
| SYN-11 | Fare is changed after a booking is confirmed | Existing booking retains original fare and policy snapshot |
| SYN-12 | Operator user attempts to publish without approval | Denied and audited |
| SYN-13 | Applicant attempts to approve own application | Denied; separation of duties enforced |
| SYN-14 | User from Operator A requests Operator B vehicle, trip or manifest | Denied without leaking record existence or details |
| SYN-15 | Unassigned driver/conductor requests a trip manifest | Denied |
| SYN-16 | Valid ticket QR is scanned for its assigned trip | Server validates ticket and records one authorized boarding event |
| SYN-17 | Altered, random, expired, wrong-trip or already-used ticket is scanned | Rejected; reason safely recorded without exposing passenger data |
| SYN-18 | Passenger requests another passenger's ticket | Denied |
| SYN-19 | User submits a client-side paid flag or fake payment callback | No paid state is created; payment remains disabled |
| SYN-20 | Application logs process synthetic name/phone and secret canary values | Sensitive values are absent/redacted from logs and errors |
| SYN-21 | Search/booking requests exceed configured rate/resource limits | Controlled rejection; service remains stable |
| SYN-22 | Database transaction fails during seat allocation | Full transaction rollback; no partial booking or seat lock remains |
| SYN-23 | Fare, trip, approval, booking or boarding privileged action occurs | Actor, action, timestamp, target, result and correlation reference are auditable |
| SYN-24 | User tries to select an intermediate boarding point not approved for the trip | Rejected; initial launch remains terminal-first |
| SYN-25 | Application is configured with production environment or synthetic-only disabled | Startup fails closed under the current development restriction |

### 7.1 Required test layers

- Unit tests: domain invariants, state transitions, fare snapshot, permissions, expiry.
- Database integration tests: constraints, locking, transaction rollback, idempotency.
- API tests: validation, authentication, authorization, safe errors, rate limits.
- Frontend tests: Amharic default, language switch, responsive states, accessible controls, API failure and expired hold handling.
- End-to-end tests: search → seat selection → hold → booking confirmation in a synthetic payment-disabled state → ticket → boarding.
- Security tests: IDOR, role escalation, CSRF/session controls as applicable, injection, QR replay, log redaction.
- Migration tests: fresh database upgrade, upgrade from G1 baseline, downgrade/rollback on disposable test database, repeatability.

A test result must identify exact source SHA, environment, command, full output/log reference, exit code, and data classification. NOT RUN is not PASS.

## 8. Migration and rollback strategy

### 8.1 Preconditions

- Do not create passenger migrations until the architecture, domain ownership, data classification, threat model, and schema design are approved.
- G1 revision 0001_g1_foundation is intentionally a no-op baseline. Confirm exact migration state from the integrated G1 source before adding a child revision.
- Never run passenger migrations against production or a database containing real personal or financial data.
- Use a disposable local PostgreSQL database with synthetic fixtures only.

### 8.2 Migration design

1. Each domain owns its tables and migration changes; cross-domain foreign keys and shared-table ownership require explicit architecture review.
2. Prefer additive, backward-compatible migrations: create new tables/columns/indexes first; avoid destructive rename/drop in the same release as application code.
3. Define database constraints for critical invariants, including unique ticket references, unique active seat allocation for the applicable trip/segment, foreign keys, not-null requirements, and valid state constraints where appropriate.
4. Store all timestamps in UTC in persistence; render local times only at presentation boundaries with an explicit timezone policy.
5. Use integer minor units or a precisely specified decimal representation for fares; do not use floating-point currency arithmetic. ETB display and rounding rules require a separately reviewed contract.
6. Make seed fixtures deterministic and idempotent. Seed only fictional entities with clearly synthetic identifiers.
7. Capture migration revision, schema diff, generated SQL, and test database state in the evidence record.
8. Never silently edit an already-applied migration; create a new corrective migration.

### 8.3 Rollback / recovery

- **Before migration:** pin exact commit and migration revision; export schema-only snapshot of the disposable local database if useful.
- **During test migration:** run against a fresh disposable database; on failure, stop, preserve logs, drop/recreate only that disposable database, and rerun after correction.
- **Application rollback:** retain previous tested application SHA; use backward-compatible schema changes so the previous application version can run during rollback.
- **Data correction:** use explicit, reviewed compensating scripts/transactions with synthetic fixtures; never hand-edit production rows.
- **Destructive schema changes:** not permitted in initial passenger phases. Require separate impact analysis, verified backup/restore exercise, maintenance plan, and explicit Owner approval.
- **Production recovery:** out of scope. No production database, backup, restore, or deployment procedure is authorized by this A1 plan.

### 8.4 Migration exit evidence

- Source and target SHAs.
- Alembic current/head revisions before and after.
- Generated SQL and schema diff.
- Fresh-database upgrade result.
- Upgrade-from-G1 result.
- Rollback or recovery exercise result on disposable database.
- Referential integrity and critical uniqueness checks.
- Full command output and exit codes.
- Confirmation that only synthetic data was used.

## 9. Evidence gates and phase controls

Evidence labels: **PASS**, **VERIFIED-CLOSED**, **PARTIAL**, **MISSING**, **UNRESOLVED**, **UNKNOWN**, **NOT RUN**. Never infer PASS from an absent failure.

| Gate | Scope | Required evidence | Exit decision |
|---|---|---|---|
| A1 — Plan and assessment | This document and repository read-only assessment | Exact repo/PR SHAs, architecture map, dependency graph, prioritized backlog, threat model, synthetic scenarios, migration/rollback strategy, open decisions | Owner approves or returns plan; no implementation yet |
| A2 — Read-only design verification | Inspect G1 integration, domain contracts, data model proposal, legal/privacy dependencies and security controls without code changes | Exact SHA review, API/schema contract review, threat-model disposition, migration review, open-decision register | Approve a bounded implementation specification or return for revision |
| A3 — Implementation | Only separately approved P0 backlog items on a dedicated branch | Approved scope/SHA, code review, migration diff, synthetic fixtures, no real data, no payment provider, no production | Feature-complete synthetic implementation; no deployment |
| A4 — Verification | Execute all approved validation and security scenarios | Exact tested SHA, commands, full logs, exit codes, coverage, concurrency/authorization/security results, migration evidence, defects and disposition | PASS only when all mandatory acceptance criteria pass; otherwise PARTIAL/FAIL |
| A5 — Deployment / pilot activation | Not included in this plan | Separate legal, privacy, security, hosting, support, operator/terminal, payment (if any), backup/DR and Owner approval | No deployment or live activation without a new explicit authorization |

### 9.1 A1 current evidence assessment

| Item | Status | Evidence / limitation |
|---|---|---|
| Repository and branch baseline | VERIFIED-CLOSED | GitHub read-only inspection; exact SHAs recorded in §2 |
| Modular-monolith direction | VERIFIED-CLOSED | Accepted ADR-0001 and G1 module-boundary document |
| G1 technical readiness | PARTIAL | PR #1 open/draft/unmerged; no claim of integration |
| Passenger domain code/schema | MISSING | No passenger business models, routes, or migrations in inspected G1 tree |
| Identity/access | MISSING | No authentication or authorization baseline |
| Audit/security controls | MISSING | Explicit gaps in current security baseline |
| Privacy and legal operational prerequisites | UNRESOLVED | Real-data lawful basis, retention, terminal/operator evidence, and authority assignments remain open |
| Payment provider/model | BLOCKED | Not selected; collection explicitly disabled |
| Synthetic acceptance execution | NOT RUN | Test scenarios specified here; no new tests executed |
| Production readiness | NOT READY | Production use and deployment are not authorized |

## 10. Open decisions required before A2/A3

| ID | Decision | Required resolution |
|---|---|---|
| PAX-PLAN-OD-01 | Passenger account model | Decide guest booking versus mandatory account; define phone verification only after provider/legal/security review |
| PAX-PLAN-OD-02 | Authentication/session approach | Select a secure approach compatible with the FastAPI/React architecture; document CSRF/session/token threat controls |
| PAX-PLAN-OD-03 | Operator tenancy | Confirm whether each operator is a separate tenant and define platform-level administrative scope |
| PAX-PLAN-OD-04 | Passenger manifest fields | Minimize exactly what conductor/driver/terminal staff can view |
| PAX-PLAN-OD-05 | Currency/fare contract | Approve ETB representation, rounding, tax display, and fare validity semantics |
| PAX-PLAN-OD-06 | Booking cancellation | Define allowed states and deadlines before enabling passenger self-service cancellation |
| PAX-PLAN-OD-07 | Refund policy | Remains unresolved; no refund execution or promise in this plan |
| PAX-PLAN-OD-08 | Operator and terminal approvers | Designate accountable reviewer and final approval roles before real-world onboarding |
| PAX-PLAN-OD-09 | Route evidence | Confirm what source and authority establish each route, schedule, terminal and stop as eligible |
| PAX-PLAN-OD-10 | Passenger support owner | Assign support responsibility and escalation coverage before any live pilot |
| PAX-PLAN-OD-11 | Retention and privacy | Obtain qualified local legal/privacy review and approve purpose, retention, deletion, access and incident process |
| PAX-PLAN-OD-12 | Payment phase | Separate future decision; provider, custody, settlement, refund and legal model remain unselected and blocked |
| PAX-PLAN-OD-13 | Hosting and data location | No production hosting or cross-border processing decision is made here; assess before A5 |
| PAX-PLAN-OD-14 | Operator cohort/pilot limits | Owner to determine candidate cohort, capacity, duration, support and stop conditions after engagement is separately authorized |

## 11. A1 deliverables and immediate next action

A1 has produced:
1. Repository-backed architecture and current-state assessment.
2. Proposed domain ownership and code boundaries.
3. Dependency order and P0/P1/P2 backlog.
4. Security/privacy threat register and synthetic data policy.
5. Synthetic acceptance scenario catalogue.
6. Migration, rollback, and evidence requirements.
7. Explicit authorization boundaries and unresolved decision register.

**Recommended next step:** Owner review of this A1 plan. If approved, proceed to A2 read-only design verification and resolve the decisions required for a bounded implementation specification. Do not begin A3 code or schema work until the A2 output and exact implementation scope are separately approved.

**Disposition:** A1 plan prepared for Owner review.
**Implementation authorization:** NOT GRANTED.
**Tests:** NOT RUN.
**Production readiness:** NOT READY.
**Payment collection:** BLOCKED.
**Real operator onboarding:** NOT AUTHORIZED.
**Freight implementation:** OUT OF SCOPE.
