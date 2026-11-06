# MaaleNex Moto — Passenger MVP Requirements Baseline v1.0

- **Status:** Owner-approved working requirements baseline
- **Approval:** 2026-11-07
- **Repository:** `akefadaka-git/maalenex-moto`
- **Planning branch:** `docs/product-scope-roadmap-v1`
- **Related specification:** [Passenger Mobility PRD v0.1](PASSENGER-MOBILITY-PRD-v0.1.md)
- **Authority:** This document records the Owner's approval of the recommended initial defaults. It supersedes conflicting provisional defaults in the PRD for planning purposes only.

## 1. Product and launch boundary

MaaleNex Moto is planned as a passenger mobility and freight logistics platform. The first product market is passenger mobility, starting in Jinka, with initial operator participation sought from transport operators operating at or participating in Jinka Bus Terminal.

The initial route priorities for validation are:
1. Jinka–Wolaita Sodo.
2. Jinka–Addis Ababa.
3. Other Jinka-originating routes only after route, operator, terminal, and boarding arrangements are verified and approved.

Freight remains a later, separately scoped domain. This baseline does not authorize freight implementation.

## 2. Approved working requirements

| ID | Area | Approved working baseline |
|---|---|---|
| PAX-BL-01 | Passenger identity | Collect passenger name and a reachable phone number as the initial booking identity. Do not require identity-document collection by default. Any legally required identity verification must be established through qualified local legal review and a separately approved policy. |
| PAX-BL-02 | Booking party | Support multiple passengers in one booking, with an explicit seat assignment for each passenger. |
| PAX-BL-03 | Seat hold | Use a configurable **10-minute** initial seat hold for MVP design and synthetic testing. The duration is a provisional operating parameter and must be validated against the selected payment flow and operator processes before live use. Expiry must release inventory safely and deterministically. |
| PAX-BL-04 | Payment collection | Keep payment collection disabled in the initial implementation scope until a lawful collection, custody, reconciliation, refund, and settlement model is separately reviewed and approved. Design an integration boundary without enabling live collection. |
| PAX-BL-05 | Payment provider | No provider selected. Provider due diligence, commercial terms, security review, and contractual approval are prerequisites to integration or live transactions. |
| PAX-BL-06 | Fare ownership | Operators propose fares. The platform applies a controlled review and authorization step before fare publication. Fare changes must not silently alter confirmed booking snapshots. |
| PAX-BL-07 | Boarding locations | Start with Jinka Bus Terminal as the initial boarding model. Intermediate boarding points are excluded from initial launch unless individually verified and approved for the relevant operator, service, and trip. |
| PAX-BL-08 | Change/cancellation/refund | Establish platform minimum passenger-protection controls and documented operator responsibilities. Exact time windows, deductions, refund amounts, and processing commitments remain unresolved and must be approved before live bookings. No refund promise may be invented by implementation. |
| PAX-BL-09 | Ticket delivery | Provide an in-app ticket with a unique server-issued reference and QR validation. Provide a printable fallback. SMS and email delivery are later enhancements, not initial MVP dependencies. |
| PAX-BL-10 | Offline boarding | Initial MVP is online-first. Offline boarding is excluded until separately designed, threat-modelled, and approved. |
| PAX-BL-11 | Platform revenue | Assume no commission, subscription, service fee, or other platform revenue for the initial pilot. Any revenue model requires separate Owner approval and applicable contractual/legal review. |
| PAX-BL-12 | Initial operator cohort | Begin with a small, verified Jinka pilot cohort. Operator names and exact cohort size remain open until Owner-led engagement and readiness review. |

## 3. Functional requirements baseline

The initial passenger product is expected to support:
- Search of approved Jinka-originating trips by origin, destination, and travel date.
- Display of verified operator, departure time, fare, boarding point, and seat availability.
- Seat selection against authoritative trip inventory.
- Multi-passenger booking with one seat per passenger.
- A configurable, expiring seat hold; concurrent requests must not allocate the same seat twice.
- A clear booking state and payment-disabled/pending state; no client-side assertion can mark a booking as paid.
- Server-issued ticket reference and QR validation.
- Authorized operator trip manifests and boarding validation with least-privilege access.
- Cancellation and disruption handling only according to an approved policy.
- Audit records for material booking, inventory, fare, trip, and boarding state changes.

## 4. Non-functional and control requirements

- Mobile-first experience suitable for low-bandwidth Android usage.
- Clear, accessible search, seat-selection, booking, and ticket states.
- Server-authoritative inventory and booking state transitions.
- Idempotent booking and payment-boundary operations.
- Tenant/operator isolation and role-scoped passenger/manifest access.
- No sensitive identity or operator evidence in Git, public issue comments, or test fixtures.
- Synthetic identities, operators, vehicles, trips, and transactions for development and acceptance testing.
- Traceable audit history for approvals and operational changes.
- No public listing of an operator, route, vehicle, fare, or trip before the required checks and publication approval.

## 5. Explicitly blocked pending separate approval

The following remain outside this requirements approval:
1. Selecting or integrating a payment provider.
2. Enabling payment collection, custody, refunds, settlement, commissions, or fees.
3. Contacting, contracting, or onboarding real operators.
4. Collecting or reviewing real passenger, representative, or vehicle documents.
5. Publishing real routes, fares, schedules, or bookable trips.
6. Opening public booking or processing live passenger transactions.
7. Production deployment or production data changes.
8. Intermediate boarding-point activation.
9. Offline boarding.
10. Freight-domain implementation.

## 6. Unresolved decisions and dependencies

| ID | Open item | Required resolution |
|---|---|---|
| PAX-OPEN-01 | Cancellation/refund detail | Approve specific timelines, responsibilities, deductions, exceptions, and passenger communications after legal and operator review. |
| PAX-OPEN-02 | Payment model/provider | Complete provider and legal due diligence; approve collection/custody, reconciliation, settlement, refund, and dispute model. |
| PAX-OPEN-03 | Operator cohort | Identify candidate operators and confirm Owner-led engagement authority. |
| PAX-OPEN-04 | Passenger privacy/legal basis | Validate collection, retention, access, deletion, and any statutory identity requirements with qualified local counsel. |
| PAX-OPEN-05 | Verification authority | Name accountable reviewers and final approver for operator, vehicle, route, and terminal evidence. |
| PAX-OPEN-06 | Terminal arrangements | Confirm the responsible terminal authority and permitted boarding operations. |
| PAX-OPEN-07 | Route validation | Verify route operation, schedules, stops, and operator authority for each initial route. |
| PAX-OPEN-08 | Seat-hold validation | Validate the provisional 10-minute duration against payment and operator workflows before live use. |
| PAX-OPEN-09 | Support ownership | Assign passenger support and operator escalation responsibility for the pilot. |
| PAX-OPEN-10 | Pilot size/duration | Approve exact cohort size, duration, service capacity, and measurable exit criteria. |

## 7. Acceptance criteria for a later synthetic MVP

A separately approved implementation must demonstrate, using synthetic data:
- Search returns only approved and published synthetic trips.
- A multi-passenger booking reserves distinct eligible seats.
- Concurrent booking attempts cannot confirm the same seat.
- Seat holds expire at the configured deadline and release inventory exactly once.
- Booking state transitions are enforced server-side and are idempotent.
- No payment can be represented as successful without a trusted, verified payment event; payment collection remains disabled in this phase.
- Ticket references are unique and QR validation is server-authoritative.
- Operator users see only authorized trips and manifests.
- Unapproved boarding points, fares, vehicles, and trips cannot be published or selected.
- Audit events preserve actor, action, timestamp, and relevant before/after state.
- Cancellation/refund paths remain disabled or explicitly non-financial until the policy and payment model are approved.

## 8. Next authorization gate

The next deliverable is a passenger-domain implementation plan covering architecture/domain boundaries, backlog, data classification, threat model, synthetic test scenarios, migration/rollback strategy, and evidence gates. It must be submitted for separate Owner approval before passenger-domain code, schema, API, or frontend implementation begins.

**Disposition:** Requirements baseline approved for planning. Implementation, real-world onboarding, live payments, production activation, and freight implementation remain unauthorized.
