# MaaleNex Moto — Passenger Mobility Product Requirements Document

**Document ID:** MNM-PRD-PAX-001  
**Version:** 0.1  
**Status:** Draft for Owner review  
**Parent scope:** `docs/PRODUCT-SCOPE-ROADMAP-v1.md`  
**Initial market:** Jinka, Ethiopia  
**Initial operator model:** Participating operators registered at Jinka Bus Terminal  
**Initial routes:** Jinka-originating routes, prioritizing Wolaita Sodo and Addis Ababa  
**Implementation status:** Not authorized by this document

> This PRD translates the approved product direction into proposed passenger-service requirements. It is a planning artifact, not authorization to implement passenger domains, connect payment providers, onboard real operators, use production data, or deploy a service. Those activities require their own explicit approval gates.

---

## 1. Purpose and Product Outcome

Define the first commercial service for MaaleNex Moto: a passenger-facing intercity trip discovery, seat reservation, ticketing, and boarding workflow, supported by operator and terminal tools.

The service should allow a passenger to:
1. Find a published trip between supported locations.
2. compare departure, arrival estimate, fare, operator, boarding point, and seat availability.
3. Select a seat and reserve it without risk of double allocation.
4. Pay through an approved payment flow when that phase is authorized.
5. Receive a verifiable ticket and receipt.
6. Board at the exact authorized boarding point.
7. Obtain support for changes, cancellation, refunds, or disruption.

The operator should be able to publish accurate trips and manage vehicle, seat, passenger, and boarding information without exposing unauthorized passenger or financial data.

## 2. Goals and Non-Goals

### 2.1 Goals
- Launch with verified participating Jinka terminal operators.
- Support Jinka-originating trips and approved intermediate boarding/drop-off points.
- Display only operator-confirmed trip inventory as bookable.
- Prevent double booking and ambiguous payment outcomes.
- Issue unique, verifiable tickets after booking confirmation.
- Support QR-based boarding validation.
- Provide operator and terminal workflows with auditable actions.
- Deliver an Amharic-first, English-capable, mobile-first experience.
- Operate reliably on intermittent mobile connections.

### 2.2 Non-goals for the first passenger MVP
- Freight shipment booking or truck marketplace.
- Unrestricted self-service onboarding of unverified transport providers.
- Ride-hailing, taxi dispatch, or vehicle rental.
- Live GPS tracking unless separately scoped.
- Dynamic or AI-generated fares.
- Credit, lending, wallet custody, or stored-value products.
- Guaranteed availability for routes without confirmed operator inventory.
- Automated legal or regulatory eligibility decisions.
- Production payment processing before separate authorization.

## 3. Personas and Roles

| Persona / role | Primary responsibilities |
|---|---|
| Passenger | Search, reserve, pay, manage own tickets, board, request support |
| Operator owner/admin | Maintain operator profile, users, vehicles, routes, fares, schedules |
| Operator dispatcher | Prepare trips, assign vehicles and crew, monitor trip status |
| Driver/conductor | Access assigned trip manifest and validate boarding within granted scope |
| Terminal coordinator | Coordinate authorized terminal activity and view permitted departures |
| Customer support agent | Review cases and perform policy-authorized support actions |
| Platform operations admin | Verify organizations, manage platform configuration, investigate incidents |
| Finance/reconciliation role | Review payment records and settlements, without unnecessary passenger-data access |

Access is role- and organization-scoped. A user may hold multiple roles, but every privileged action must be authorized and attributable to an individual account.

## 4. Core Passenger Journeys

### 4.1 Search and discovery
1. Passenger selects origin, destination, travel date, and passenger count.
2. Platform searches published trips whose route and boarding rules permit the requested journey.
3. Results show operator, departure time, estimated arrival where available, fare, boarding point, seat availability timestamp, and relevant conditions.
4. Passenger selects a trip to inspect details and the seat layout.

Search results must distinguish:
- Confirmed published trip
- Estimated journey information
- Availability last checked
- Sold out / unavailable
- Temporarily unavailable / service disruption

No trip may be represented as available solely because a route record exists.

### 4.2 Seat selection and reservation
1. Passenger selects an available seat.
2. Server revalidates trip status, boarding segment, seat availability, and applicable fare.
3. Server creates a time-limited hold using an atomic transaction or equivalent concurrency-safe mechanism.
4. Passenger sees the hold expiry and amount due.
5. Passenger proceeds to the payment step when payment integration is authorized.
6. If the hold expires before confirmation, the seat returns to availability.

The hold duration is a product decision to be set after operator and payment-flow research. The system must not hard-code an unapproved duration as a commercial policy.

### 4.3 Payment and ticket issuance
1. Payment initiation is associated with a unique booking attempt and idempotency key.
2. The platform records a pending payment state.
3. The payment provider's authenticated server-to-server confirmation is verified.
4. The platform reconciles the confirmed payment with the active seat hold.
5. If all conditions remain valid, booking confirmation and ticket issuance occur atomically or through a recoverable transactional workflow.
6. If payment succeeds after a hold has expired or the seat has been reassigned, the system must not issue a conflicting ticket; it must initiate a clearly recorded exception/refund/reconciliation path.
7. A passenger receives ticket status and receipt only after authoritative confirmation.

A browser redirect, screenshot, client-side message, or unverified callback is not proof of payment.

### 4.4 Boarding
1. Authorized crew member opens the assigned trip.
2. Crew scans QR or enters a short ticket reference.
3. Server validates ticket authenticity, trip, passenger/seat assignment, boarding point, ticket status, and prior boarding state.
4. Server records the boarding event with actor and timestamp.
5. Duplicate scans return the existing boarding state and do not create duplicate boardings.
6. Exceptions are recorded for authorized resolution.

Offline boarding, if later required, needs a separately designed signed-token, device authorization, synchronization, and duplicate-use policy. It is not assumed for the MVP.

### 4.5 Changes, cancellation, and support
- Passenger can view applicable policy and request eligible changes or cancellation.
- Eligibility and refund amount are derived from an approved policy version associated with the booking.
- Operator-initiated cancellation or trip disruption triggers affected-passenger notification and a recorded resolution workflow.
- Support agents cannot silently alter financial state or ticket history.
- Every refund or manual override requires authorization, reason, actor, timestamp, and reference to the originating booking/payment.

## 5. Functional Requirements

Priority: **P0** = required for first usable passenger MVP; **P1** = important follow-up; **P2** = later enhancement. Priorities are proposed and require Owner confirmation.

### 5.1 Accounts and access
- **P0 PAX-AUTH-01:** Passenger can register/sign in using the approved identity method.
- **P0 PAX-AUTH-02:** Operator staff access is scoped to their verified organization and assigned role.
- **P0 PAX-AUTH-03:** Crew access is limited to assigned trips and permitted boarding actions.
- **P0 PAX-AUTH-04:** Administrative and financial privileges are separately controlled and audited.
- **P1 PAX-AUTH-05:** Account recovery and optional stronger authentication are supported under approved security policy.

### 5.2 Locations, routes, and trips
- **P0 PAX-TRIP-01:** Platform maintains a controlled directory of cities, terminals, stops, and boarding points.
- **P0 PAX-TRIP-02:** Operator can submit routes and trip schedules for authorized publication.
- **P0 PAX-TRIP-03:** A trip references one operator, one assigned vehicle, a route, schedule, and publication status.
- **P0 PAX-TRIP-04:** Search respects origin/destination sequence and approved boarding/drop-off points.
- **P0 PAX-TRIP-05:** Only eligible published trips with current inventory appear bookable.
- **P1 PAX-TRIP-06:** Operator can publish controlled service changes and disruption notices.

### 5.3 Vehicles and seats
- **P0 PAX-SEAT-01:** Each vehicle has a versioned seating configuration with unique seat identifiers.
- **P0 PAX-SEAT-02:** A trip uses one effective seating configuration for the assigned vehicle.
- **P0 PAX-SEAT-03:** Seats blocked for safety, crew, maintenance, or operator reasons are unavailable for sale.
- **P0 PAX-SEAT-04:** Seat availability is checked and reserved on the server, not trusted from client state.
- **P0 PAX-SEAT-05:** Concurrent booking attempts cannot confirm the same seat for overlapping journey segments.
- **P1 PAX-SEAT-06:** Authorized operator can block/unblock seats with reason and audit record, subject to existing bookings.

### 5.4 Booking and ticket
- **P0 PAX-BOOK-01:** Passenger can create a booking for one or more eligible passengers under defined policy.
- **P0 PAX-BOOK-02:** Booking records origin, destination, boarding point, drop-off point, trip, seat(s), fare snapshot, policy version, and passenger reference.
- **P0 PAX-BOOK-03:** Seat holds expire deterministically and release inventory safely.
- **P0 PAX-BOOK-04:** Booking state transitions are validated server-side.
- **P0 PAX-BOOK-05:** Confirmed booking receives a unique ticket reference.
- **P0 PAX-BOOK-06:** Ticket status and boarding validation are server-verifiable.
- **P0 PAX-BOOK-07:** Duplicate requests are idempotent and cannot create duplicate bookings or tickets.
- **P1 PAX-BOOK-08:** Passenger can request eligible booking changes or cancellations.

### 5.5 Payments and settlement
- **P0 for payment-enabled phase PAX-PAY-01:** Payment provider integration is behind a provider-neutral adapter.
- **P0 PAX-PAY-02:** Payment initiation and callbacks are authenticated, validated, and idempotent.
- **P0 PAX-PAY-03:** Payment status is distinct from booking status.
- **P0 PAX-PAY-04:** Reconciliation identifies unmatched, duplicate, delayed, reversed, and disputed transactions.
- **P0 PAX-PAY-05:** No ticket is marked paid based solely on client assertion.
- **P1 PAX-PAY-06:** Operator settlement statements and refund reports are available to authorized finance roles.

Payment requirements are design requirements only until a payment phase is separately approved. No provider, commission, fee, settlement timing, or custody model is selected by this PRD.

### 5.6 Boarding and operations
- **P0 PAX-BOARD-01:** Crew can access assigned trip passenger manifests only.
- **P0 PAX-BOARD-02:** Ticket validation checks trip, status, seat, and boarding permissions.
- **P0 PAX-BOARD-03:** Boarding event records ticket, trip, actor, time, and outcome.
- **P0 PAX-BOARD-04:** Duplicate scans are safe and visible.
- **P0 PAX-BOARD-05:** Authorized roles can record and resolve boarding exceptions.
- **P1 PAX-BOARD-06:** Operator can export trip manifests using approved access controls.

### 5.7 Notifications and support
- **P0 PAX-COMM-01:** Booking confirmation and material trip changes are visible to the passenger.
- **P0 PAX-COMM-02:** Notification delivery failures do not reverse confirmed bookings.
- **P0 PAX-COMM-03:** Passenger can access support instructions and submit a case.
- **P1 PAX-COMM-04:** SMS or other external messaging channels can be added after provider and cost approval.

## 6. Proposed Domain Data Concepts

These are conceptual entities, not approved database schema or migration instructions.

- PassengerAccount
- OperatorOrganization
- OperatorMembership
- Terminal
- Location
- Route
- RouteStop
- BoardingPoint
- Vehicle
- VehicleSeatLayoutVersion
- VehicleSeat
- CrewAssignment
- Trip
- TripStop
- TripSeatInventory
- SeatHold
- Booking
- BookingPassenger
- Ticket
- PaymentAttempt
- PaymentTransaction
- Refund
- SettlementRecord
- BoardingEvent
- ServiceDisruption
- SupportCase
- PolicyVersion
- AuditEvent
- Notification

### 6.1 Critical integrity rules
1. A trip must have one authorized operator and one valid assigned vehicle.
2. A trip cannot be bookable without a published schedule and active inventory.
3. A seat is not available if blocked, held by a valid active hold, or confirmed for an overlapping segment.
4. Segment-aware inventory is required if passengers can board and alight at intermediate stops; seat conflicts must be checked across every overlapping route segment.
5. A booking must preserve fare, route, boarding, and policy snapshots used at confirmation.
6. Payment and booking states are separate and reconciled.
7. A ticket must reference one authoritative booking and must not be duplicated.
8. Boarding can be recorded only by an authorized actor against an eligible ticket and trip.
9. All administrative overrides and financial actions are attributable and auditable.

## 7. State Models

### 7.1 Trip
Proposed states:
- Draft
- SubmittedForReview
- Published
- Boarding
- InTransit
- Completed
- Cancelled
- Disrupted

Allowed transitions must be explicitly defined. For example, a completed or cancelled trip cannot silently return to Published.

### 7.2 Seat hold
Proposed states:
- Active
- ConvertedToBooking
- Expired
- Released
- Cancelled

Expiration and conversion must be concurrency-safe.

### 7.3 Booking
Proposed states:
- Pending
- AwaitingPayment
- Confirmed
- ChangeRequested
- CancellationRequested
- Cancelled
- Expired
- ExceptionReview

Exact transitions, payment dependencies, and policy conditions must be approved before implementation.

### 7.4 Payment
Proposed states:
- Created
- Pending
- Succeeded
- Failed
- Reversed
- RefundPending
- PartiallyRefunded
- Refunded
- ReconciliationRequired

A payment state change does not independently imply a booking state change without validated business rules.

### 7.5 Ticket
Proposed states:
- Issued
- ValidatedForBoarding
- Used
- Cancelled
- Expired
- SuspendedForReview

## 8. User Interface Requirements

### Passenger experience
- Amharic-first interface with English option.
- Search form optimized for small Android screens.
- Clear trip cards showing operator, time, fare, boarding point, and availability.
- Accessible seat map with a non-visual alternative.
- Explicit hold expiry and payment status.
- Ticket view usable offline for display, while boarding validity remains server-authoritative unless offline validation is separately approved.
- Large, readable QR code with a human-readable reference.
- Clear cancellation and support instructions.

### Operator experience
- Dashboard for trips requiring action.
- Vehicle and seat-layout management.
- Schedule and fare publishing workflow.
- Passenger manifest and boarding workflow.
- Service disruption and cancellation controls.
- Operational reports appropriate to the user's role.

### Terminal experience
- Departure overview and authorized boarding-point directory.
- Trip status and exception visibility.
- No unrestricted access to passenger personal or financial information.

## 9. Non-Functional Requirements

Proposed acceptance requirements to refine during technical design:

- **Security:** deny-by-default authorization; tenant/organization isolation; secure session handling; rate limiting; protected secrets; audit logging.
- **Privacy:** collect only necessary passenger information; document retention and deletion policy; restrict manifest access.
- **Integrity:** enforce booking and seat constraints at the database/service boundary; use idempotency and transaction-safe workflows.
- **Availability:** define service-level objectives before pilot; provide graceful degradation and clear status on outages.
- **Performance:** define measurable search and booking response targets after baseline testing on representative low-cost Android devices and network conditions.
- **Accessibility:** target WCAG 2.2 AA for applicable web interfaces.
- **Localization:** Amharic and English strings separated from business logic; test Ethiopic text rendering and input.
- **Observability:** structured logs, correlation IDs, metrics, alerting, and traceable transaction references.
- **Recovery:** documented backup, restore, and incident recovery objectives before production.
- **Compatibility:** current supported Android browsers and responsive desktop operator workflows.

No numerical uptime, latency, or recovery target is approved in this draft.

## 10. Reporting and Success Metrics

Measure, at minimum:
- Search result availability and freshness
- Search-to-booking conversion
- Seat-hold expiration rate
- Confirmed booking rate
- Duplicate seat allocation incidents (target: zero)
- Payment reconciliation exceptions
- Ticket validation success and exception rates
- Boarding completion rate
- Operator schedule accuracy
- Trip cancellation and disruption rates
- Refund processing time
- Passenger support case volume and resolution time
- Mobile page load and API error rates

Numerical targets require baseline data and Owner approval.

## 11. Dependencies and External Preconditions

- Participating operator agreements and authorization.
- Verified terminal and boarding-point operating arrangements.
- Accurate vehicle, seating, route, schedule, and fare data.
- Approved passenger identity and privacy policy.
- Approved cancellation, refund, and disruption policies.
- Legal and regulatory review of the intended transport marketplace and payment model.
- Payment provider due diligence and contractual approval before payment integration.
- Customer support ownership and escalation coverage.
- Connectivity and device testing in the target operating environment.

This document does not assert that any specific licence, permit, provider approval, or legal interpretation has been obtained.

## 12. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Incorrect or stale schedules | Operator confirmation, publication controls, freshness indicators |
| Double-booking | Atomic inventory reservation and concurrency tests |
| Intermediate-stop seat conflicts | Segment-aware inventory and overlap constraints |
| Payment/booking mismatch | Independent state machines, idempotency, reconciliation |
| Unauthorized pickup | Explicit trip-specific boarding-point authorization |
| Ticket fraud | Server-side validation and unique references |
| Unauthorized manifest access | Trip assignment and role-scoped permissions |
| Operator disruption | Passenger notification and documented resolution workflow |
| Weak connectivity | Resilient client, safe retries, clear pending states |
| Unclear refund responsibility | Approved policy and operator agreement before live operation |

## 13. Acceptance Gate for Passenger MVP

The passenger MVP is not accepted until evidence demonstrates:

1. A verified operator can publish an authorized route, vehicle, fare, and trip.
2. Passenger search returns only eligible published trips.
3. Seat inventory correctly handles overlapping route segments.
4. Concurrent attempts cannot confirm the same seat.
5. Seat holds expire and release correctly.
6. Booking and payment state transitions are validated and idempotent.
7. Ticket issuance and QR validation are server-authoritative.
8. Crew access is restricted to assigned trips.
9. Boarding events and exceptions are auditable.
10. Cancellation and disruption workflows follow approved policy.
11. Passenger and operator interfaces meet localization, accessibility, and mobile requirements.
12. Security, privacy, backup, monitoring, and support readiness are reviewed.
13. All acceptance tests use synthetic data until separately authorized.
14. Exact source SHA, test evidence, unresolved issues, and Owner approval are recorded.

## 14. Open Owner Decisions

The following decisions remain open and must not be silently assumed:

| ID | Decision | Options / required clarification |
|---|---|---|
| PAX-OD-01 | Passenger identity at booking | Minimum data and any verification requirements |
| PAX-OD-02 | Booking party size | Single passenger only or multiple passengers per booking |
| PAX-OD-03 | Seat hold duration | Set after payment-flow and operator research |
| PAX-OD-04 | Payment collection model | Direct operator collection, approved marketplace collection, or other lawful arrangement |
| PAX-OD-05 | Payment provider | Select only after due diligence and approval |
| PAX-OD-06 | Fare ownership | Operator-managed fare, platform-administered publication, or controlled approval workflow |
| PAX-OD-07 | Pickup flexibility | Terminal-only initially or selected operator-approved intermediate stops |
| PAX-OD-08 | Change/cancellation policy | Operator-specific policy within platform-enforced minimum controls, or standardized policy |
| PAX-OD-09 | Ticket delivery | In-app only initially or additional SMS/email/print channels |
| PAX-OD-10 | Offline boarding | Online-only MVP or separately designed offline mode |
| PAX-OD-11 | Platform revenue | Fee/commission/subscription model; no amount assumed |
| PAX-OD-12 | Initial operator cohort | Names and number of operators after Owner-led engagement |

## 15. Authorization and Next Gate

This PRD is submitted for Owner review. Approval of the PRD would authorize the requirements baseline only if the Owner explicitly says so; it does not automatically authorize code changes.

The next gate after PRD approval is a separately approved passenger-domain implementation plan with:
- domain boundary and architecture review,
- prioritized implementation backlog,
- data classification and threat model,
- synthetic test scenarios,
- migration and rollback strategy,
- acceptance and evidence plan.

**Disposition:** Draft for Owner review.  
**Implementation:** Not authorized.  
