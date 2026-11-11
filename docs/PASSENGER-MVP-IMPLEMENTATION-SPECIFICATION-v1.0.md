# MaaleNex Moto — Passenger MVP Implementation Specification v1.0

- **Document ID:** MNM-SPEC-PAX-001
- **Version:** 1.0
- **Status:** Finalized technical specification for Owner review; A2 design baseline approved
- **Approval basis:** Owner approval of A2 decisions D01–D07 on 2026-11-07
- **Prepared:** 2026-11-07
- **Repository:** `akefadaka-git/maalenex-moto`
- **Planning branch:** `docs/product-scope-roadmap-v1`
- **Parent plan:** [Passenger MVP A1 Implementation Plan v1.0](PASSENGER-MVP-A1-IMPLEMENTATION-PLAN-v1.0.md)
- **Requirements authority:** [Passenger MVP Requirements Baseline v1.0](PASSENGER-MVP-REQUIREMENTS-BASELINE-v1.0.md)
- **Governance authority:** [Jinka Pilot Governance Decision Register v1.0](JINKA-PILOT-GOVERNANCE-DECISION-REGISTER-v1.0.md)
- **Related product draft:** [Passenger Mobility PRD v0.1](PASSENGER-MOBILITY-PRD-v0.1.md)

> **Authorization:** This document finalizes the technical design for the Passenger MVP. It does not authorize code changes, schema creation, migrations, API implementation, G1 changes, tests, real operator engagement, collection of real personal data, live bookings, payment integration or collection, ticket issuance for real travel, production deployment, or pilot activation. Each requires the applicable separate Owner approval. All implementation and acceptance environments remain synthetic-only.

---

## 1. Purpose and normative language

This specification converts the approved A2 decisions into implementable module contracts, logical data relationships, state machines, API boundaries, transaction rules, security controls, migration sequencing, and acceptance criteria.

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** express requirements:

- **MUST / MUST NOT:** mandatory for conformance.
- **SHOULD / SHOULD NOT:** expected unless a documented, reviewed exception exists.
- **MAY:** optional capability that must remain within the authorization boundary.

This specification is the controlling technical design for the initial passenger MVP. Where the older Passenger Mobility PRD v0.1 describes mandatory passenger accounts, provider-confirmed payment, payment-dependent ticket issuance, intermediate-stop inventory, or live refunds, this approved specification and the Owner-approved requirements baseline supersede those draft assumptions.

## 2. Approved design decisions

The following decisions are approved and fixed for this specification:

| ID | Approved decision | Implementation consequence |
|---|---|---|
| D01 | Guest-first passenger identity | No mandatory passenger account; booking contact and travelers are separate records. |
| D02 | Separate access models | Opaque booking-access credential plus verification challenge; staff use authenticated, role-controlled sessions. |
| D03 | Organization-level tenancy | Operator-owned data is tenant-scoped; platform-wide access is explicit and audited. |
| D04 | Reservation is not a travel ticket | Reservation reference/QR never authorizes boarding; ticket issuance and boarding entitlement remain disabled. |
| D05 | Versioned ETB fares | Operator proposes, platform approves/publishes; bookings preserve immutable fare snapshots. |
| D06 | Transactional full-trip inventory | PostgreSQL is authoritative; allocation, hold expiry and release are concurrency-safe and atomic. |
| D07 | Conservative operational/privacy controls | Trip-scoped manifest access, no live refund/cancellation promises, attributable audit, data minimization. |

### 2.1 Product scope constraints

- Initial market: passenger mobility, Jinka-first.
- Initial boarding model: Jinka Bus Terminal only.
- Candidate routes Jinka–Wolaita Sodo and Jinka–Addis Ababa remain unverified candidates until separately evidenced and approved.
- Initial cohort: small and verified; operator names and size remain unresolved.
- One booking may include multiple passengers; each traveler receives an individual seat allocation.
- Seat hold duration: configurable 10 minutes for synthetic design and testing only.
- Currency: ETB.
- Payment collection: disabled.
- No payment provider is selected.
- No commission, subscription, platform fee, settlement or revenue model is assumed.
- Intermediate stops and segment-based inventory are deferred.
- Offline boarding is excluded.
- Freight is a separate later domain and excluded from this specification.

## 3. Architecture and deployment boundary

### 3.1 Architecture

Use the accepted modular-monolith architecture:

- Backend: existing FastAPI application foundation.
- Persistence: PostgreSQL through SQLAlchemy and Alembic.
- Frontend: existing React/TypeScript application.
- API: versioned HTTP/JSON interfaces.
- Runtime: one deployable backend application and one web client for the initial MVP.

Do not introduce microservices, distributed messaging, a separate mobile application, a distributed cache, or additional infrastructure without a separate architecture decision.

### 3.2 Layering

Each domain MUST follow these boundaries:

1. **HTTP adapter:** request parsing, authentication dependency, schema validation, response mapping. No business rules or direct cross-domain ORM manipulation.
2. **Application service:** use-case orchestration, transaction boundary, idempotency, authorization context.
3. **Domain model/policy:** invariants, state transitions, value validation and domain decisions.
4. **Repository/persistence adapter:** domain-owned reads and writes.
5. **Cross-domain contract:** explicit service interface or event contract; never import another domain's ORM model or repository internals.

The browser is never authoritative for identity, authorization, fare, inventory, expiry, booking status, reservation status, ticket validity or boarding authorization.

### 3.3 Proposed backend organization

Target structure only; it does not assert these paths exist:

- `backend/app/core`: settings, dependency wiring, errors, correlation IDs, clock abstraction.
- `backend/app/db`: SQLAlchemy base, engine/session lifecycle and transaction helpers.
- `backend/app/routers/v1`: HTTP adapters.
- `backend/app/schemas`: transport schemas.
- `backend/app/domains/identity`
- `backend/app/domains/organizations`
- `backend/app/domains/catalog`
- `backend/app/domains/fleet`
- `backend/app/domains/trips`
- `backend/app/domains/fares`
- `backend/app/domains/bookings`
- `backend/app/domains/ticketing`
- `backend/app/domains/support`
- `backend/app/audit`: shared audit contract and persistence adapter.
- Frontend feature boundaries: `passenger-search`, `booking`, `reservation`, `operator`, `terminal`, and shared UI/API infrastructure.

### 3.4 Domain ownership and dependencies

| Domain | Owns | Depends on | Explicitly does not own |
|---|---|---|---|
| Identity & Access | Staff users, credentials, sessions, roles, permissions, memberships | G1 | Booking/trip business state |
| Organization & Operator Registry | Operator organization, membership, review and activation state | Identity, Audit | Passenger booking or payment custody |
| Catalog | Locations, terminals, routes, route stops, boarding-point permissions | Operator, Audit | Seat inventory |
| Fleet | Vehicles, versioned seat layouts, seat definitions, vehicle review | Operator, Audit | Trip seat allocation |
| Trips | Schedules, trip instances, assignments, publication and operational state | Catalog, Fleet, Operator | Fare approval, booking allocation |
| Fares | Fare proposals, versions, approval and publication | Operator, Trips/Catalog references, Audit | Payment collection |
| Booking & Inventory | Booking contacts, passengers, bookings, holds, allocations, fare snapshots | Identity/booking access, Trips, Fares, Audit | Ticket entitlement and payment settlement |
| Reservation Access | Opaque reservation reference and access challenge | Booking, Identity/security primitives | Boarding authorization |
| Ticketing & Boarding | Future travel ticket and boarding-validation boundary | Booking, Trips, Identity, Audit | Reservation QR conversion without entitlement |
| Support | Cases and authorized support actions | Identity, Booking, Audit | Unapproved refunds or financial changes |
| Audit | Attributable event records and restricted query interface | Core identity/context | Business workflow ownership |
| Notifications | Provider-neutral notification requests and delivery status; later | Domain events | Authoritative business state |
| Payment Boundary | Disabled future adapter seam only | Separate future approval | Collection, custody, wallet, settlement |

### 3.5 Cross-domain interaction rules

- Trips consume approved operator, route, vehicle and seat-layout references.
- Fare proposals reference an operator and applicable trip/route scope. Published fare versions are immutable.
- Booking consumes a published trip and applicable published fare version.
- Booking requests a seat allocation through the Inventory application interface.
- Reservation access consumes booking identity and issues access-limited references; it cannot create boarding entitlement.
- Ticketing is a separate, disabled capability. It may read booking state through an explicit interface but cannot mutate booking internals.
- Audit receives structured events from application services; it is not a general-purpose dump of request bodies.
- Support invokes approved application commands and cannot directly update financial or ticket state.
- Notifications are non-authoritative and cannot reverse or confirm a booking.

## 4. Logical entity model

The following is a logical contract, not a physical schema. Attribute types are implementation-neutral. The migration design must map them to PostgreSQL types, constraints, indexes and foreign keys after a separate implementation authorization.

### 4.1 Common conventions

- Primary identifiers: opaque UUIDs generated server-side.
- Timestamps: UTC-aware timestamps stored consistently; display localization is a presentation concern.
- Money: integer minor units plus explicit ISO currency code; no floating-point monetary values.
- Currency: `ETB` for this initial product scope.
- State fields: controlled enumerations, with transitions enforced in application services and, where suitable, database constraints.
- Versioning: mutable aggregates expose a version number for optimistic concurrency where needed.
- Tenant ownership: operator-owned records carry an organization reference or inherit it through a parent with an enforced tenant-scoped query.
- Deletion: business records with audit or operational value are not physically deleted through ordinary workflows. Retention and erasure policies remain subject to legal review.
- Secrets and verification credentials are stored only as secure hashes or through an approved secret-management mechanism; never store plaintext credentials in ordinary records or logs.

### 4.2 Identity and organization entities

**User**
- `id`
- `login_identifier` (unique, normalized; exact login method is an implementation/security decision)
- `display_name`
- `status` (pending, active, suspended, disabled)
- `created_at`, `updated_at`
- `version`

**Credential**
- `id`, `user_id`
- `credential_type`
- `secret_hash_or_external_reference`
- `status`
- `created_at`, `expires_at`, `revoked_at`

**Session**
- `id`, `user_id`
- `session_secret_hash`
- `created_at`, `last_seen_at`, `expires_at`, `revoked_at`
- `security_context` (minimal device/risk metadata; no unnecessary fingerprinting)

**Role / Permission / RoleAssignment**
- `Role(id, code, description)`
- `Permission(id, code, description)`
- `RolePermission(role_id, permission_id)`
- `RoleAssignment(id, user_id, role_id, organization_id nullable, assigned_by, assigned_at, revoked_at)`

A null organization scope MUST NOT silently mean unrestricted access. Platform-wide scope requires a distinct privileged permission and auditable assignment.

**Organization**
- `id`
- `organization_type` (operator for this scope)
- `legal_or_display_name`
- `status` (candidate, submitted, under_review, approved, restricted, suspended, rejected)
- `created_at`, `updated_at`
- `version`

**OrganizationMembership**
- `id`, `organization_id`, `user_id`
- `membership_status`
- `created_at`, `revoked_at`
- Unique active membership policy for organization/user.

**OperatorReview**
- `id`, `organization_id`
- `review_type`, `status`, `evidence_reference`
- `reviewer_user_id`, `decision_reason`
- `submitted_at`, `decided_at`

Real operator onboarding and real evidence collection are not authorized by this specification.

### 4.3 Catalog, fleet and trip entities

**Location**
- `id`, `name`, `location_type`, `status`
- Optional geographic metadata only where justified and approved.

**Terminal**
- `id`, `location_id`, `name`, `status`
- Initial approved product model references Jinka Bus Terminal; a live authority/permission assertion remains unresolved.

**Route**
- `id`, `code`, `origin_location_id`, `destination_location_id`
- `status` (draft, submitted, approved, published, suspended, retired)
- `created_at`, `updated_at`, `version`

**RouteStop**
- `id`, `route_id`, `location_id`, `sequence_number`
- `boarding_allowed`, `alighting_allowed`, `status`
- For the first MVP, only the approved terminal boarding model is enabled; no intermediate boarding permission is inferred.

**Vehicle**
- `id`, `organization_id`
- `vehicle_reference` (synthetic in all development/test environments)
- `status`, `review_status`
- `created_at`, `updated_at`, `version`

**SeatLayoutVersion**
- `id`, `vehicle_id`, `version_number`, `status`
- `effective_from`, `effective_to`
- A published/used layout version is immutable.

**VehicleSeat**
- `id`, `seat_layout_version_id`
- `seat_code`, `row_label`, `position_metadata`
- `seat_type`, `is_sellable`
- Unique `(seat_layout_version_id, seat_code)`.

**Schedule**
- `id`, `organization_id`, `route_id`
- `departure_rule`, `status`, `version`

**Trip**
- `id`, `organization_id`, `route_id`, `schedule_id`
- `vehicle_id`, `seat_layout_version_id`
- `departure_at`, optional `arrival_estimate_at`
- `status` (draft, submitted, approved, published, boarding, in_transit, completed, cancelled, disrupted)
- `published_at`, `version`
- Organization must match the assigned vehicle's organization.

**TripSeat**
- `id`, `trip_id`, `vehicle_seat_id`
- `seat_code_snapshot`, `sellable_status`
- Unique `(trip_id, vehicle_seat_id)`.
- Represents full-trip inventory, not segment inventory.

### 4.4 Fare entities

**Fare**
- `id`, `organization_id`, `route_id`
- Optional `trip_id` if a trip-specific fare is required.
- `status`, `created_at`, `updated_at`

**FareVersion**
- `id`, `fare_id`, `version_number`
- `amount_minor_units` (non-negative integer; currency-specific precision defined centrally)
- `currency_code` = `ETB`
- `effective_from`, `effective_to`
- `status` (draft, submitted, approved, published, rejected, retired)
- `proposed_by`, `approved_by`, `published_by`
- `approved_at`, `published_at`
- Unique `(fare_id, version_number)`.
- Published versions are immutable; a correction creates a new version.

**FareApproval**
- `id`, `fare_version_id`
- `decision`, `reviewer_user_id`, `reason`, `decided_at`

### 4.5 Passenger and booking entities

**BookingContact**
- `id`
- `name`
- `phone_normalized`
- `created_at`, `updated_at`
- Access to this record is restricted; phone is contact data, not an authenticator.

**Passenger**
- `id`
- `display_name`
- Optional additional fields only after documented necessity and approval.
- No national identity document fields are required by default.

**Booking**
- `id`, `booking_reference` (unique, non-sequential, non-secret display reference)
- `booking_contact_id`, `trip_id`
- `status` (draft, held, pending_confirmation, reserved, expired, cancelled, exception_review)
- `currency_code`, `fare_snapshot_id`
- `created_at`, `updated_at`, `confirmed_at`, `expires_at`
- `version`
- The status `reserved` means reservation accepted under the payment-disabled workflow; it does not mean paid or boarding-entitled.

**BookingPassenger**
- `id`, `booking_id`, `passenger_id`
- `trip_seat_id`
- `passenger_sequence`
- Unique `(booking_id, passenger_sequence)`.
- A traveler may appear in multiple separate bookings; no global passenger account is required.
- One active seat assignment per booking passenger.

**SeatHold**
- `id`, `booking_id`, `trip_id`, `trip_seat_id`
- `status` (active, converted, expired, released, cancelled)
- `created_at`, immutable `expires_at`
- `released_at`, `release_reason`
- Server time is authoritative.

**SeatAllocation**
- `id`, `booking_id`, `booking_passenger_id`, `trip_id`, `trip_seat_id`
- `status` (active, released, expired, cancelled)
- `allocated_at`, `released_at`
- A database-enforced strategy MUST prevent conflicting active allocations for one trip seat.
- Allocation must be tied to a booking passenger, not only to a booking header.

**BookingFareSnapshot**
- `id`, `booking_id`, `fare_version_id`
- `amount_minor_units`, `currency_code`
- `fare_description_snapshot` (minimal human-readable context)
- `captured_at`
- Immutable after booking reservation is accepted.

**ReservationReference**
- `id`, `booking_id`
- `public_reference` (unique and unguessable enough to avoid enumeration; not an authenticator)
- `qr_payload_version`, `qr_payload_reference`
- `status` (active, revoked, expired)
- `created_at`, `revoked_at`
- QR payload MUST contain no passenger PII, phone number, fare secret, or bearer credential.

**BookingAccessGrant**
- `id`, `booking_id`
- `credential_hash` (never plaintext)
- `scope` (read, permitted booking management)
- `created_at`, `expires_at`, `revoked_at`, `last_used_at`
- A challenge/verification event is required before issuing or renewing a grant.

### 4.6 Ticketing and boarding entities — disabled boundary

**TravelTicket**
- `id`, `booking_id`, `booking_passenger_id`, `trip_id`
- `ticket_reference`, `qr_token_hash_or_reference`
- `status` (issued, voided, expired, suspended)
- `issued_at`, `valid_from`, `valid_until`, `voided_at`
- Creation is disabled in this phase. No record is issued merely because a reservation exists.

**BoardingEvent**
- `id`, `travel_ticket_id`, `trip_id`, `actor_user_id`
- `event_type`, `result`, `occurred_at`
- `request_id`, `reason_code`
- Boarding validation is disabled for real travel; synthetic negative tests may verify that reservation references are rejected.

### 4.7 Support and audit entities

**SupportCase**
- `id`, `case_reference`, `booking_id` nullable
- `opened_by`, `assigned_to`, `category`, `status`
- `created_at`, `updated_at`, `closed_at`

**SupportCaseAction**
- `id`, `support_case_id`, `actor_user_id`
- `action_type`, `reason`, `created_at`
- No action may bypass booking/ticket state machines or initiate a refund.

**AuditEvent**
- `id`, `event_type`, `occurred_at`
- `actor_type`, `actor_id`, `actor_role_snapshot`
- `organization_id` nullable, `resource_type`, `resource_id`
- `action`, `outcome`, `reason_code`
- `request_id`, `correlation_id`
- `metadata_redacted`
- No passwords, session secrets, verification codes, full QR credentials, payment credentials, or unnecessary passenger PII.

### 4.8 Relationship cardinalities and integrity

| Relationship | Cardinality / rule |
|---|---|
| Organization → Membership | One organization has many memberships; each membership links one user and one organization. |
| User → Session | One user has zero or many sessions; each session belongs to one user and can be revoked independently. |
| Organization → Vehicle | One operator organization owns many vehicles; a vehicle belongs to one organization. |
| Vehicle → SeatLayoutVersion | One vehicle has many layout versions; one version belongs to one vehicle. |
| SeatLayoutVersion → VehicleSeat | One version contains many unique seats. |
| Route → RouteStop | One route has ordered stops; stop sequence is unique within route. |
| Organization → Trip | One operator organization operates many trips; each trip belongs to one organization. |
| Trip → TripSeat | One trip exposes many trip seats; one trip seat maps to one vehicle seat in the trip's assigned layout. |
| Fare → FareVersion | One fare has many immutable versions; one version belongs to one fare. |
| BookingContact → Booking | One contact may create many bookings; each booking has one booking contact. |
| Booking → BookingPassenger | One booking contains one or more booking-passenger records; each record identifies one traveler in that booking. |
| BookingPassenger → SeatAllocation | At most one active seat allocation per booking passenger in the initial full-trip model. |
| TripSeat → SeatAllocation | At most one active allocation per trip seat. |
| Booking → BookingFareSnapshot | Exactly one snapshot for an accepted reservation; immutable thereafter. |
| Booking → ReservationReference | One active reference at a time; revoked references remain historically attributable. |
| Booking → TravelTicket | Zero tickets in this phase; future issuance requires a separately approved entitlement rule. |
| TravelTicket → BoardingEvent | Zero or more attempted validation events; no valid boarding without a valid ticket. |
| User → AuditEvent | An event may be performed by a user or system actor; every privileged human action identifies the actor. |

## 5. State machines and transition contracts

All state transitions are server-side commands. A caller cannot set a status field directly. Each command MUST validate the current state, actor authorization, business preconditions, aggregate version and idempotency context, then commit state and audit evidence atomically.

### 5.1 Booking state machine

States:

- `draft`: incomplete, not holding seats.
- `held`: all requested seats are held until the server-generated expiry.
- `pending_confirmation`: reservation submission is being finalized; no payment is implied.
- `reserved`: reservation accepted under the payment-disabled model.
- `expired`: hold expired before reservation acceptance.
- `cancelled`: authorized cancellation under synthetic/test or later approved policy.
- `exception_review`: integrity or operational exception requiring authorized review.

Allowed transitions:

| From | To | Command / guard |
|---|---|---|
| draft | held | `create_hold`; all requested trip seats available and transaction succeeds |
| held | pending_confirmation | `submit_reservation`; hold remains active and all passenger/seat records are complete |
| held | expired | `expire_hold`; server time >= expiry and hold has not converted |
| held | cancelled | `release_hold`; authorized actor or safe user cancellation before reservation |
| pending_confirmation | reserved | `accept_reservation`; policy-enabled payment-disabled reservation acceptance and all seats still allocated |
| pending_confirmation | cancelled | `reject_or_cancel_reservation`; authorized reason |
| pending_confirmation | exception_review | integrity inconsistency or uncertain transaction outcome |
| reserved | cancelled | Only synthetic/authorized action until live cancellation policy is approved |
| reserved | exception_review | integrity/security/operational exception |
| exception_review | reserved | Authorized resolution after invariant restoration; no ticket implication |
| exception_review | cancelled | Authorized resolution with reason |

No transition to a payment-confirmed state exists in this scope. `reserved` MUST NOT be described as paid, ticketed or boarding-authorized.

### 5.2 Seat hold state machine

| From | To | Guard |
|---|---|---|
| active | converted | Reservation acceptance commits the corresponding allocation |
| active | expired | Database transaction confirms server time >= immutable expiry |
| active | released | Authorized release or failed all-or-nothing booking transaction |
| active | cancelled | Authorized cancellation before conversion |
| converted | — | Terminal for hold lifecycle |
| expired/released/cancelled | — | Terminal; a new attempt creates a new hold |

A hold's `expires_at` is immutable. Extension, if ever required, must be a distinct command, policy and audit event; it is not part of the initial MVP.

### 5.3 Seat allocation state machine

- `active` → `released` only through an authorized booking cancellation/release, expiry, or correction workflow.
- Released allocations are historical and cannot be reactivated.
- A new allocation creates a new allocation record.
- A database uniqueness/exclusion strategy MUST prevent two active allocations for the same `trip_id + trip_seat_id`.
- The exact partial unique index or equivalent database-enforced strategy must be validated against the chosen PostgreSQL version during implementation.

### 5.4 Fare state machine

`draft → submitted → approved → published → retired`

Alternative transitions:
- `submitted → rejected`
- `rejected → draft` through a new revision, not mutation of a reviewed immutable version.
- `approved → retired` if publication is withdrawn before use, with audit and reason.

Rules:
- Proposer and approver MUST be different principals for the same fare version.
- Publication requires approval and effective-date validity.
- Published versions are immutable.
- A fare change creates a new version.
- A booking references the exact version and stores a snapshot.
- No fare can be published for an unapproved operator/route/trip scope.

### 5.5 Operator lifecycle

`candidate → submitted → under_review → approved`

Other outcomes:
- `under_review → rejected`
- `approved → restricted`
- `approved/restricted → suspended`
- `restricted → approved` only after an authorized review and evidence.
- `suspended → approved` only through explicit reinstatement approval.

This is a design model for synthetic fixtures. Real onboarding and status decisions are not authorized.

### 5.6 Trip lifecycle

`draft → submitted → approved → published → boarding → in_transit → completed`

Exceptional paths:
- `submitted → rejected`
- `published → cancelled`
- `published/boarding/in_transit → disrupted`
- `disrupted → cancelled` or a controlled resumption state, if policy later defines one.

A completed or cancelled trip MUST NOT silently return to published. Publication requires approved operator, route, vehicle, seat layout and fare references. Initial live publication remains blocked by governance prerequisites.

### 5.7 Reservation access lifecycle

- A challenge is created with a short expiry, rate limits and one-time-use semantics.
- Successful verification issues a scoped, opaque access grant.
- Grant can be revoked, expired or rotated.
- The raw credential is returned only at issuance and is never stored or logged.
- Access grant scope is limited to the relevant booking and permitted operations.
- Verification provider is abstracted; synthetic adapter only until provider approval.

### 5.8 Ticket and boarding lifecycle — disabled

Future ticket state: `issued → voided/expired/suspended`.

There is no transition from reservation reference to travel ticket without a separately approved entitlement condition. In this phase:
- Ticket issuance command returns a controlled disabled-capability error.
- Boarding validation rejects reservation references.
- No real boarding event can be authorized.
- Synthetic negative tests may exercise these rejection rules.

## 6. API contract baseline

Base path: `/api/v1`.

All APIs use JSON over HTTPS in any later approved deployed environment. During development, current G1 local-only restrictions remain controlling. Exact Pydantic schema names and code files are implementation details; the semantic contracts below are normative.

### 6.1 Common request/response rules

- JSON field names use consistent snake_case.
- Timestamps are RFC 3339 UTC timestamps.
- Monetary values are integer minor units plus `currency_code`.
- IDs are opaque UUIDs.
- Responses include a request/correlation identifier where applicable.
- Mutating requests use an idempotency key where retries could duplicate effects.
- Commands include an expected aggregate version where concurrent edits are possible.
- Server-derived fields (status, fare, availability, expiry, organization scope, ticket validity) are never accepted as authoritative client input.
- Validation errors identify fields without exposing internal stack traces or sensitive resource existence.
- List endpoints are paginated with bounded page sizes and tenant scope enforced server-side.

### 6.2 Common error envelope

Semantic shape:

- `error.code`: stable machine-readable code.
- `error.message`: safe user-facing message.
- `error.fields`: optional field validation details.
- `error.request_id`: correlation reference.

Required error classes include:
- `VALIDATION_ERROR`
- `AUTHENTICATION_REQUIRED`
- `ACCESS_DENIED`
- `RESOURCE_NOT_FOUND`
- `STATE_CONFLICT`
- `VERSION_CONFLICT`
- `IDEMPOTENCY_CONFLICT`
- `INVENTORY_UNAVAILABLE`
- `HOLD_EXPIRED`
- `FARE_NOT_PUBLISHED`
- `CAPABILITY_DISABLED`
- `RATE_LIMITED`
- `INTERNAL_ERROR`

Do not reveal whether an arbitrary booking exists in responses to unauthenticated recovery or access challenges.

### 6.3 Authentication and staff sessions

**`POST /auth/sessions`**
- Request: approved staff login identifier and credential proof.
- Response: authenticated session metadata; session secret is delivered only through secure cookie handling.
- Guards: account active, credential valid, rate limits, security checks.
- No passenger guest registration is required.

**`DELETE /auth/sessions/current`**
- Revokes current session; clears cookie.

**`GET /auth/sessions/current`**
- Returns current staff identity, organization memberships and effective permissions, excluding secrets.

**`POST /auth/recovery/challenges`**
- Starts a generic recovery process without account enumeration.
- External delivery disabled until provider approval; synthetic adapter may be used in test.

### 6.4 Passenger booking-access APIs

**`POST /passenger-access/challenges`**
- Request: booking reference and permitted contact verification input.
- Response: generic challenge-accepted response; never confirms booking existence to an untrusted caller.
- Rate limited by multiple risk dimensions.

**`POST /passenger-access/challenges/{challenge_id}/verify`**
- Request: challenge response.
- Response: one-time booking access grant, delivered securely.
- Challenge is single-use, expires and is rate-limited.
- Synthetic verification is the only enabled adapter before provider approval.

**`POST /passenger-access/grants/{grant_id}/revoke`**
- Revokes the current scoped grant, requiring proof of possession and policy authorization.

### 6.5 Catalog and trip search

**`GET /catalog/locations`**
- Returns active public-searchable locations only.

**`GET /catalog/routes`**
- Returns published route definitions and permitted public boarding model.

**`GET /trips/search`**
- Query: origin_id, destination_id, travel_date, passenger_count.
- Response: eligible published trip summaries, published fare, seat availability snapshot time, boarding terminal and operational status.
- Must exclude draft, suspended, unpublished, stale or ineligible trips.
- Initial product configuration exposes only the terminal-first boarding model.
- Search availability is indicative; booking revalidates inventory transactionally.

**`GET /trips/{trip_id}`**
- Returns a public-safe trip detail for an eligible published trip.
- Does not expose operator private data or passenger information.

### 6.6 Operator, fleet and trip administration APIs

Representative routes:

- `POST /operators`: submit an operator application (synthetic fixtures only in this phase).
- `GET /operators/{organization_id}`: organization-scoped or explicitly privileged access.
- `POST /operators/{organization_id}/reviews`: authorized review action.
- `POST /fleet/vehicles`: create vehicle record under caller's organization.
- `POST /fleet/vehicles/{vehicle_id}/seat-layout-versions`: create a draft layout version.
- `POST /trips`: create a draft trip under authorized organization scope.
- `POST /trips/{trip_id}/submit`: submit for review.
- `POST /trips/{trip_id}/publish`: publish only after all required approvals.

Every command validates tenant ownership, operator status, role, referenced resources and state transitions. Client-supplied organization IDs are never sufficient authorization.

### 6.7 Fare APIs

- `POST /fares`: create a draft fare under authorized operator scope.
- `POST /fares/{fare_id}/versions`: propose a new immutable version.
- `POST /fares/{fare_id}/versions/{version_id}/submit`: submit for platform review.
- `POST /fares/{fare_id}/versions/{version_id}/approve`: platform reviewer approval; proposer cannot approve own version.
- `POST /fares/{fare_id}/versions/{version_id}/publish`: publish approved version.
- `GET /fares/{fare_id}/versions`: authorized version history.

Request amount is integer minor units and currency must be `ETB` for this scope. Published versions cannot be edited.

### 6.8 Booking and inventory APIs

**`POST /bookings/holds`**
- Request: trip_id, passengers array (name per traveler), requested trip_seat_ids, booking_contact (name and phone), idempotency key.
- Server validates trip publication, booking eligibility, passenger count, fare publication, seat membership and availability.
- Server creates booking, passengers, hold and seat allocations atomically.
- Response: booking reference, hold expiry, assigned seat labels, fare snapshot and currency.
- Hold duration comes from server configuration; initial synthetic default is 10 minutes.
- No payment intent is created.

**`POST /bookings/{booking_id}/submit-reservation`**
- Requires booking access or authorized staff scope.
- Requires active hold and complete passenger/seat mapping.
- Atomically converts hold into a reserved booking under the payment-disabled reservation policy.
- Returns reservation reference and QR representation, not a travel ticket.

**`GET /bookings/{booking_id}`**
- Requires booking access grant or authorized staff scope.
- Returns minimum necessary booking details and current reservation state.
- Sensitive contact data is masked unless the access scope permits it.

**`POST /bookings/{booking_id}/cancel`**
- Disabled for live passenger self-service until cancellation policy approval.
- Synthetic/admin test command may cancel with reason and audit record.
- Must not claim refund initiation or completion.

**`GET /trips/{trip_id}/inventory`**
- Returns server-derived seat availability and observation timestamp.
- Never returns other passengers' identities or booking references.

### 6.9 Reservation reference APIs

**`GET /reservations/{reference}`**
- Requires a valid scoped booking access grant.
- Returns reservation details only; the reference alone is not authorization.

**`GET /reservations/{reference}/qr`**
- Requires booking access.
- Returns a QR payload containing an opaque reservation reference/version only.
- QR cannot be used as a bearer credential and cannot authorize boarding.

### 6.10 Ticketing and boarding APIs — disabled

- `POST /tickets`: returns `CAPABILITY_DISABLED` in this phase.
- `POST /tickets/{ticket_id}/void`: unavailable until ticket issuance is separately approved.
- `POST /boarding/validate`: rejects reservation QR/reference and returns a safe not-authorized outcome.
- `POST /boarding/events`: unavailable for real travel in this phase.

A future activation requires a separate Owner decision specifying the entitlement condition, payment or non-payment authorization basis, legal/operational process, ticket cancellation/expiry rules and boarding authority.

### 6.11 Audit and support APIs

- `POST /support/cases`: create a support case with minimum necessary data.
- `GET /support/cases/{case_id}`: access limited to requester and assigned support roles.
- `POST /support/cases/{case_id}/actions`: policy-bound action; cannot bypass domain state machines.
- `GET /audit/events`: restricted to explicit audit/security roles; tenant and resource filters enforced.
- Audit export requires separate permission, reason and event recording.

### 6.12 API authorization matrix

| Capability | Guest | Booking grant | Operator staff | Trip crew | Platform reviewer/admin | Support/audit |
|---|---:|---:|---:|---:|---:|---:|
| Search public trips | Yes | Yes | Yes | Yes | Yes | As needed |
| Create guest hold | Yes | Yes | No, unless authorized support/test role | No | Synthetic/admin only | No |
| View own booking | No | Scoped | Only if assigned operational need | Only trip-scoped minimum | Explicit privileged scope | Assigned case only |
| Manage operator records | No | No | Own organization/role | No | Explicit permission | No |
| Propose fare | No | No | Authorized operator fare role | No | No, unless delegated | No |
| Approve/publish fare | No | No | No | No | Explicit reviewer role | No |
| Publish trip | No | No | Authorized operator role plus approval | No | Explicit permission | No |
| View trip manifest | No | No | Assigned trip and role | Assigned trip only | Explicit operational need | Case-scoped only |
| Issue travel ticket | No | No | Disabled | Disabled | Disabled | Disabled |
| Validate boarding | No | No | Disabled | Disabled | Disabled | Disabled |
| View audit records | No | No | Own permitted scope only if explicitly granted | No | Explicit audit role | Explicit audit role |
| Cross-tenant access | No | No | No | No | Explicit privileged permission | No by default |

### 6.13 HTTP semantics

Recommended status mapping:
- 200: successful read or command with representation.
- 201: resource created.
- 202: asynchronous request accepted, only where asynchronous processing is genuinely used.
- 204: successful command without body.
- 400: malformed request.
- 401: authentication or booking-access proof required.
- 403: authenticated but unauthorized.
- 404: resource not found or safely concealed.
- 409: state, inventory, version or idempotency conflict.
- 422: semantic validation failure.
- 429: rate limit exceeded.
- 503: explicitly disabled/unavailable external dependency, without implying a successful operation.

## 7. Transaction, concurrency and idempotency contracts

### 7.1 Full-trip seat allocation

PostgreSQL is authoritative. The booking service MUST perform all seat allocation decisions inside a database transaction.

Required sequence:

1. Begin transaction.
2. Resolve the trip and confirm it is eligible for reservation.
3. Confirm the assigned vehicle and effective seat-layout version.
4. Lock the relevant trip-seat inventory rows or use a proven equivalent serialization mechanism.
5. Evaluate active allocations and holds using database-consistent server time.
6. Verify all requested seats are distinct, belong to the trip and are sellable.
7. Verify passenger count equals requested seat count.
8. Resolve one current published fare version and calculate the snapshot server-side.
9. Create booking, booking passengers, hold records, seat allocations and fare snapshot atomically.
10. Write the corresponding audit event in the same transaction where feasible.
11. Commit only if every requested seat is secured; otherwise roll back the entire booking allocation.

The implementation MUST choose and document the exact PostgreSQL concurrency mechanism. Acceptable design candidates include row-level `SELECT ... FOR UPDATE` locking of stable trip-seat rows plus database uniqueness, or an equivalent serializable/constraint-backed strategy. Application-only pre-checks are insufficient.

### 7.2 Database constraints

At minimum, the physical schema must enforce:

- Unique trip/vehicle-seat mapping.
- Unique seat code within a seat-layout version.
- Unique booking reference.
- Unique reservation public reference.
- Unique fare version number per fare.
- Unique booking passenger sequence per booking.
- At most one active allocation for a trip seat.
- At most one active allocation per booking passenger.
- Foreign-key integrity across booking, trip, seat, fare snapshot and passenger relationships.
- Organization consistency between trip, vehicle and operator.
- Non-negative monetary amount and valid currency.
- Valid timestamp ordering and expiry conditions where expressible.

Partial unique indexes may be used for active allocations, but the selected design must be validated on the target PostgreSQL version. A background cleanup job is not a substitute for the database constraint.

### 7.3 Hold expiry

- Expiry uses database/server UTC time, not browser time.
- `expires_at` is assigned once at hold creation.
- Allocation transaction rechecks expiry before conversion.
- A cleanup worker may release expired holds but is an optimization, not the source of correctness.
- Expiry/release is idempotent.
- A late retry cannot resurrect an expired hold.
- If a request outcome is uncertain after a network failure, idempotency lookup returns the original result or a safe conflict; it must not create a second booking.

### 7.4 Idempotency

For booking creation and other retry-sensitive commands:

- Client sends an idempotency key with a bounded length and safe character set.
- Server scopes the key to principal/guest challenge context and operation.
- Server stores a request fingerprint and resulting resource reference.
- Reuse with identical request returns the original result.
- Reuse with a different request returns `IDEMPOTENCY_CONFLICT`.
- Retention period must be at least seven days for booking creation and other high-impact commands, subject to storage and policy review.
- Idempotency records must not store secrets or unnecessary PII.

### 7.5 Fare snapshot atomicity

The fare version is resolved and copied into the booking snapshot within the same booking transaction. Client-supplied fare amounts are ignored. If the fare becomes ineligible before the transaction commits, the booking fails safely.

## 8. Security, privacy and audit requirements

### 8.1 Authentication and session security

- Staff authentication is distinct from guest booking access.
- Session cookies MUST be Secure in deployed HTTPS environments, HttpOnly and appropriately SameSite-configured.
- Session rotation occurs after authentication and privilege changes.
- Logout, suspension and credential reset revoke applicable sessions.
- Privileged roles SHOULD require MFA before any production activation.
- Password/credential verification is rate-limited and resistant to enumeration.
- Secrets are never logged or returned in ordinary API responses.

### 8.2 Guest booking access

- Phone number is contact information, not authentication.
- Booking references are not secrets and do not authorize access.
- Access grants are random, high entropy, scoped, expiring and revocable.
- Store only credential hashes.
- Verification challenges are one-time, short-lived, rate-limited and generic in their external response.
- No real SMS/email provider is selected or integrated in this phase.
- Synthetic test adapters must be impossible to enable accidentally in production.

### 8.3 Tenant isolation

- Every operator query and mutation enforces organization scope server-side.
- Client-supplied organization IDs never grant access.
- Cross-tenant access is denied by default.
- Platform-wide permissions are explicit, separately assigned, reviewed and audited.
- Support access is case-scoped and time-bounded where feasible.
- Tenant isolation tests cover list, detail, search, export, nested resources and mutation endpoints.

### 8.4 Passenger-data minimization

- Collect booking contact name and reachable phone.
- Collect each traveler's name for the reservation.
- Do not collect national ID, passport, photo, birth date or additional contact details by default.
- Do not include passenger PII in QR payloads, URLs, routine logs, analytics events or public trip responses.
- Restrict manifest access to the assigned trip and minimum necessary fields.
- Mask contact data in general operator views.
- Retention, deletion, legal basis and data-subject handling require qualified local legal review before real data collection.

### 8.5 Manifest and boarding security

- Manifest access requires authenticated staff, assigned trip and explicit role permission.
- Exports require a separate permission and audit event.
- Reservation QR is never accepted as a travel ticket.
- Boarding authorization is server-side and online-only if a future ticket phase is approved.
- QR contents are opaque and contain no PII or reusable bearer secret.
- Repeated validation attempts and replay attempts are detectable and auditable.

### 8.6 Audit integrity

Audit events are append-only at the application boundary. Ordinary application roles cannot update or delete historical events. Database grants, restricted writer role, event validation and controlled retention must enforce this.

This is not a claim of cryptographic immutability or tamper-proof storage. Stronger guarantees require separate infrastructure and security review.

### 8.7 Threat-to-control mapping

| Threat | Required control | Acceptance evidence |
|---|---|---|
| Booking enumeration | Opaque references, generic challenge responses, rate limiting | Enumeration tests |
| Phone-only account takeover | Independent challenge and scoped grant | Negative access tests |
| Cross-tenant data exposure | Server-side organization scope and explicit privileged permission | Cross-tenant API tests |
| Double booking | Transaction locks plus DB uniqueness | PostgreSQL concurrency tests |
| Expired hold reuse | Transactional expiry check and immutable expiry | Boundary/race tests |
| Fare tampering | Server-resolved published fare and immutable snapshot | Client-tampering tests |
| Reservation QR misuse | Separate ticket entity and disabled boarding path | Reservation QR rejection tests |
| Manifest overexposure | Trip/role scope and field minimization | Role matrix tests |
| Audit manipulation | Restricted DB permissions and append-only application interface | Negative update/delete tests |
| Secret leakage | Redaction and secure credential storage | Log scanning and test fixtures |
| Privilege escalation | Least privilege, session revocation, MFA for privileged deployment roles | Authorization/session tests |
| Synthetic provider enabled live | Environment guard and startup failure if unsafe configuration is present | Configuration tests |

## 9. Frontend contract

### 9.1 Passenger journey

1. Search published Jinka-originating trips using origin, destination, date and passenger count.
2. Review trip, boarding terminal, published fare and availability timestamp.
3. Select a trip and individual seats.
4. Enter booking-contact name/phone and each traveler's name.
5. Review server-calculated fare and hold expiry.
6. Submit reservation while the hold is active.
7. Receive reservation reference and reservation QR.
8. Retrieve the reservation using the scoped booking-access verification process.

The interface MUST label the result as a **reservation**, not a paid ticket or boarding pass. It must clearly state that payment collection and travel-ticket issuance are not enabled in this phase.

### 9.2 Operator journey

- Maintain synthetic operator profile and users.
- Maintain synthetic vehicles and seat-layout drafts.
- Propose fares and view approval status.
- Prepare synthetic trips and submit them for review.
- View only assigned operational data.
- No real operator activation, public trip publication or live passenger manifest is authorized.

### 9.3 Localization and accessibility

- Amharic-first with English capability.
- Responsive-first layout suitable for small Android screens.
- Keyboard and screen-reader alternatives for seat selection.
- Clear validation and state feedback.
- Target WCAG 2.2 AA for applicable interfaces.
- Ethiopic font rendering and input must be tested.
- Business rules and API state values must not be embedded in translation strings.

## 10. Migration and rollback design

No migration is authorized by this document. Once implementation is approved, migration work must follow this order:

1. Verify exact G1 base SHA and its separate approval/integration status.
2. Confirm PostgreSQL version and migration environment.
3. Add identity, organization, membership, role and permission tables.
4. Add audit event persistence and restricted write model.
5. Add catalog and operator records.
6. Add fleet, seat-layout versions and vehicle seats.
7. Add trips and trip-seat inventory.
8. Add fare and immutable fare-version tables.
9. Add booking contact, passenger, booking, hold, allocation and fare snapshot tables.
10. Add reservation references and booking-access grants.
11. Add support case structures.
12. Keep travel-ticket and boarding capabilities disabled; any future schema addition must be separately approved.

### 10.1 Migration safety

- Migrations must be forward-only and reviewed; destructive changes require explicit approval.
- Use expand/contract for incompatible changes.
- Create constraints only after precondition checks and data validation.
- Never seed real operators, real passenger details, actual vehicle identifiers or asserted real routes.
- Synthetic seed data must be clearly marked and isolated.
- Backups and restore tests are mandatory before any production schema change.
- Migration execution must record exact source SHA, migration revision, environment, operator and result.

### 10.2 Rollback

- Application rollback must be compatible with the expanded schema during the transition window.
- Prefer disabling a feature flag or reverting application code over destructive schema rollback.
- If a migration has written data, rollback must preserve audit evidence and booking integrity.
- No automatic destructive downgrade in production.
- Recovery procedure must identify the last known-good application SHA and database revision.
- Production rollback and deployment remain outside current authorization.

## 11. Synthetic acceptance test specification

All tests in this phase use synthetic data and local/test infrastructure. PostgreSQL integration and concurrency tests are mandatory; SQLite-only evidence is insufficient.

### 11.1 Identity and booking access

- **PAX-ACC-001:** Guest creates a booking without staff/passenger account registration.
- **PAX-ACC-002:** Booking contact and traveler identities are stored separately.
- **PAX-ACC-003:** Phone number alone cannot retrieve or modify a booking.
- **PAX-ACC-004:** Invalid, expired, reused or revoked challenge is rejected.
- **PAX-ACC-005:** Booking grant cannot access another booking.
- **PAX-ACC-006:** Credential secret is not stored plaintext or logged.
- **PAX-ACC-007:** Recovery response does not reveal booking existence.

### 11.2 Tenant and authorization

- **PAX-TEN-001:** Operator A cannot read Operator B's vehicle, trip, fare or membership.
- **PAX-TEN-002:** Operator A cannot mutate Operator B's resources by changing path/body identifiers.
- **PAX-TEN-003:** A removed member loses organization access.
- **PAX-TEN-004:** Platform-wide access requires explicit permission and produces an audit event.
- **PAX-TEN-005:** Unassigned crew cannot access a trip manifest.
- **PAX-TEN-006:** Support access is limited to assigned cases and authorized actions.

### 11.3 Fare

- **PAX-FAR-001:** Operator can propose a synthetic fare.
- **PAX-FAR-002:** Proposer cannot approve the same fare version.
- **PAX-FAR-003:** Unapproved fare cannot be published or booked.
- **PAX-FAR-004:** Published fare version cannot be mutated.
- **PAX-FAR-005:** Fare revision does not change an existing booking snapshot.
- **PAX-FAR-006:** Client-supplied fare amount is ignored/rejected.
- **PAX-FAR-007:** Amount uses integer minor units and explicit ETB currency.

### 11.4 Inventory and booking

- **PAX-INV-001:** One passenger receives one seat allocation.
- **PAX-INV-002:** Multi-passenger booking allocates a distinct seat to every passenger.
- **PAX-INV-003:** Duplicate seat request within one booking is rejected.
- **PAX-INV-004:** Two concurrent transactions cannot allocate the same trip seat.
- **PAX-INV-005:** Multi-seat failure rolls back all allocations.
- **PAX-INV-006:** Hold expiry is evaluated using server/database time.
- **PAX-INV-007:** Expired hold cannot be converted.
- **PAX-INV-008:** Repeated expiry processing is idempotent.
- **PAX-INV-009:** A delayed retry returns the original idempotent result or safe conflict.
- **PAX-INV-010:** Seat availability cannot be trusted from stale client state.
- **PAX-INV-011:** Trip-seat layout mapping matches the trip's immutable effective layout version.

### 11.5 Reservation and ticket boundary

- **PAX-TKT-001:** Successful synthetic reservation produces a unique reservation reference.
- **PAX-TKT-002:** Reservation QR contains no passenger PII.
- **PAX-TKT-003:** Reservation reference alone does not grant booking access.
- **PAX-TKT-004:** Reservation QR presented to boarding validation is rejected.
- **PAX-TKT-005:** Ticket issuance API returns capability-disabled response.
- **PAX-TKT-006:** No booking state transition implies payment received or ticket issued.
- **PAX-TKT-007:** Voided/expired/unknown future ticket states cannot authorize boarding in test fixtures.

### 11.6 Audit, privacy and operational controls

- **PAX-AUD-001:** Booking creation and each state transition create attributable audit events.
- **PAX-AUD-002:** Fare approval/publication includes actor, reason and timestamps.
- **PAX-AUD-003:** Manifest view/export creates an audit event.
- **PAX-AUD-004:** Ordinary application role cannot update/delete audit history.
- **PAX-PRI-001:** Logs contain no plaintext credentials, challenge codes or QR secrets.
- **PAX-PRI-002:** Manifest fields are minimized by role.
- **PAX-OPS-001:** Live cancellation/refund command remains disabled without approved policy.
- **PAX-OPS-002:** Synthetic cancellation is authorized, reasoned and idempotent.
- **PAX-OPS-003:** No real operator or passenger data exists in test fixtures.

### 11.7 Test evidence requirements

Every test run record must identify:
- exact source commit SHA,
- database engine and version,
- migration revision,
- test command and environment,
- passed/failed/skipped counts,
- failure logs and disposition,
- test data classification (synthetic),
- reviewer and timestamp.

A passing test suite does not itself authorize production use.

## 12. Observability and operational readiness

Before any later production proposal, define and verify:

- structured logs with request/correlation IDs and PII redaction;
- metrics for booking attempts, hold expiry, allocation conflicts, fare publication, reservation state and API errors;
- alerting for inventory integrity failures, authorization anomalies and audit-write failures;
- backup schedule, restore objectives and demonstrated restore;
- incident response, credential rotation and access revocation;
- support ownership and escalation;
- data retention and deletion schedule;
- legal review and operator/terminal authority evidence.

No numerical service-level objective, uptime target, latency target, recovery point objective or recovery time objective is approved by this document.

## 13. Implementation backlog and dependency gates

| Sequence | Work package | Prerequisite | Exit evidence |
|---|---|---|---|
| G0 | G1 exact-SHA readiness | Separate G1 review and Owner-authorized integration path | Exact SHA, review disposition, validation evidence |
| P0-01 | Identity, sessions and permission engine | G1 | Authentication/session tests; role matrix |
| P0-02 | Audit foundation | G1 and identity context | Event contract; redaction and write-restriction tests |
| P0-03 | Operator organization registry | Identity, audit | Tenant and lifecycle tests using synthetic organizations |
| P0-04 | Catalog | Operator registry | Approval/publication and route-scope tests |
| P0-05 | Fleet and seat layouts | Operator registry | Layout and capacity integrity tests |
| P0-06 | Trip operations | Catalog, fleet, operator | Trip publication and eligibility tests |
| P0-07 | Fare & Pricing | Operator, catalog/trips, audit | Approval separation, versioning and snapshot tests |
| P0-08 | Booking & inventory | Identity/booking access, trips, fares, audit | PostgreSQL concurrency, hold, idempotency tests |
| P0-09 | Reservation access and QR | Booking | Credential scope, privacy and reservation QR tests |
| P0-10 | Passenger UX | Stable API contracts | Responsive, Amharic/English and synthetic end-to-end tests |
| P1 | Support and exception workflows | Approved cancellation/disruption policy | Role, audit and policy tests |
| P2 | Notifications | Provider and privacy approval | Delivery adapter and failure-handling tests |
| Future | Ticket issuance, boarding, payments, intermediate stops, offline mode | Separate Owner decisions and operational/legal readiness | New specification and approval gate |

Implementation work must not begin until the Owner separately authorizes A3 and confirms the exact G1 base/integration dependency. The approval of D01–D07 approves this design baseline, not A3 implementation.

## 14. Open policy and operational dependencies

The following remain unresolved and block the corresponding live capability:

| ID | Dependency | Blocks |
|---|---|---|
| OPEN-01 | Applicable passenger privacy/legal basis, retention, deletion and data-subject process | Real passenger data |
| OPEN-02 | Terminal authority and boarding permission | Live Jinka terminal operations |
| OPEN-03 | Operator verification and named reviewer/approver appointments | Real operator activation |
| OPEN-04 | Route and schedule evidence for each candidate route | Public trip publication |
| OPEN-05 | Exact cancellation/refund windows, responsibility and passenger remedies | Live cancellation/refund |
| OPEN-06 | Support ownership and escalation coverage | Live passenger service |
| OPEN-07 | Fare approval delegation and publication authority | Public fare publication |
| OPEN-08 | Payment collection/custody/provider/settlement model | Any payment-enabled operation |
| OPEN-09 | Travel entitlement condition and ticketing/boarding policy | Real ticket issuance and boarding |
| OPEN-10 | Pilot cohort, duration, capacity, stop conditions and activation authority | Production pilot |

## 15. Traceability to approved decisions

| Decision | Specification sections | Key acceptance tests |
|---|---|---|
| D01 Guest-first identity | 4.5, 6.4–6.5, 9.1 | ACC-001–002 |
| D02 Separate authentication/recovery | 4.2, 4.5, 5.7, 6.3–6.4, 8.1–8.2 | ACC-003–007 |
| D03 Organization tenancy | 4.2, 4.3, 6.6, 6.12, 8.3 | TEN-001–006 |
| D04 Reservation/ticket separation | 4.6, 5.8, 6.9–6.10 | TKT-001–007 |
| D05 Versioned ETB fare | 4.4, 5.4, 6.7, 7.5 | FAR-001–007 |
| D06 Transactional full-trip inventory | 4.3, 4.5, 5.2–5.3, 7 | INV-001–011 |
| D07 Operational/privacy/audit | 4.7, 5, 6.11, 8, 11.6, 12 | AUD, PRI, OPS tests |

## 16. Conformance and change control

An implementation conforms only when:
- module ownership and cross-domain contracts follow this specification;
- all mandatory invariants are enforced server-side and at the database boundary where applicable;
- all required synthetic acceptance tests pass against PostgreSQL;
- no disabled capability is accidentally enabled;
- security/privacy review and evidence gates are complete;
- exact source SHA and unresolved issues are recorded.

Any change to guest/account policy, payment enablement, ticket entitlement, boarding authorization, tenant boundary, intermediate-stop inventory, offline operation, passenger-data collection or commercial model requires an explicit decision record and Owner approval before implementation.

**Disposition:** Technical specification finalized for Owner review against approved A2 decisions D01–D07.

**A2 design baseline:** Approved.

**A3 implementation:** Not authorized.

**Code/schema/migrations/tests:** Not performed by this document.

**Real operators/passenger data/payments/tickets/boarding/production:** Not authorized.
