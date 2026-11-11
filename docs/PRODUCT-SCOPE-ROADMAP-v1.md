# MaaleNex Moto
## Product Scope and Phased Roadmap Proposal

**Document ID:** MNM-PROD-001  
**Version:** 1.0  
**Status:** OWNER-APPROVED PRODUCT DIRECTION AND ROADMAP  
**Approval date:** 2026-11-06  
**Product:** MaaleNex Moto  
**Product category:** Passenger Mobility and Freight Logistics Marketplace  
**Initial market:** Jinka, Ethiopia  
**Initial service:** Intercity passenger ticketing and seat reservations  
**Future service:** Freight transport marketplace  
**Current engineering baseline:** G1 technical foundation

> **Authorization boundary:** The Owner has approved this product scope and phased roadmap. This approval does not itself authorize implementation of new business domains, live payments, production deployment, operator onboarding, commercial commitments, or changes to the G1 technical foundation. Each implementation and operational phase remains subject to its stated gate and explicit authorization.

---

## 1. Executive Summary

MaaleNex Moto is a digital transport and logistics marketplace connecting passengers, transport operators, vehicle owners, freight customers, and logistics providers.

The product has two principal business areas:

1. **Passenger Mobility:** Search routes, compare available trips, reserve seats, pay for tickets, receive digital tickets, and board at approved pickup points.
2. **Freight Logistics:** Connect individuals and businesses that need goods transported with eligible truck and cargo-vehicle operators who can provide the required capacity and route.

The initial commercial entry is passenger mobility, beginning with participating transport operators at Jinka Bus Terminal. The initial route catalogue should prioritize Jinka-originating services, including Jinka–Wolaita Sodo and Jinka–Addis Ababa, subject to verification of actual operator schedules and route availability.

The platform will use shared infrastructure and distinct business domains. Freight services can therefore be introduced later without rebuilding passenger ticketing or mixing unrelated operational rules.

**Strategic principle:** Build one integrated platform, launch one focused service, and expand through separately governed phases.

## 2. Owner-Approved Product Direction

| Decision | Approved direction |
|---|---|
| Platform model | Both passenger transport and freight logistics |
| Initial market | Passenger ticketing |
| Initial operator model | Operators registered at Jinka Bus Terminal |
| Initial route focus | Jinka-originating journeys |
| Long-term product | Integrated passenger and freight marketplace |
| Delivery approach | Staged, domain-separated development |
| Current engineering boundary | Existing G1 foundation; no new domain implementation authorized by this document alone |

## 3. Product Vision and Objectives

**Vision:** Make passenger travel and goods transportation easier to discover, arrange, pay for, and monitor through a trusted digital marketplace.

Objectives:
- Make intercity travel information accessible digitally.
- Allow passengers to reserve actual available seats before travelling.
- Reduce uncertainty around schedules, fares, boarding locations, and ticket confirmation.
- Give participating transport operators digital tools to manage services.
- Establish a marketplace connecting freight customers and transport providers.
- Provide traceable booking, payment, dispatch, and service records.
- Support Amharic-first and English interfaces, with mobile-first usability.
- Establish a scalable platform that can expand from Jinka to other Ethiopian cities.

### 3.1 Intended user groups

| User group | Principal needs |
|---|---|
| Passengers | Find trips, reserve seats, pay, receive tickets |
| Transport operators | Manage vehicles, trips, fares, seats, and passengers |
| Terminal administrators | Coordinate participating operators and boarding |
| Drivers and conductors | View trip manifests and validate boarding |
| Freight customers | Request transportation and compare offers |
| Truck owners and fleet operators | Publish capacity, routes, and freight offers |
| Platform administrators | Verify participants, manage operations, resolve disputes |
| Customer support staff | Handle complaints, cancellations, and service problems |

A person or organization may hold multiple roles, subject to appropriate authorization and verification.

## 4. Product Structure

MaaleNex Moto will use a modular architecture with shared platform capabilities and distinct business domains.

### 4.1 Shared platform foundation

- Account registration and authentication
- User and organization profiles
- Role-based access control
- Operator and vehicle verification
- Route and location directory
- Notifications and communication
- Payment integration boundary
- Transaction records and reconciliation
- Audit logging
- Customer support and dispute handling
- Reporting and analytics
- Localization and accessibility
- Administrative management

### 4.2 Passenger Mobility domain — initial commercial domain

**Passenger capabilities**
- Search by origin, destination, date, and passenger count.
- View available operators and trips.
- View fares, estimated departure times, and journey information.
- View seat maps and booking availability.
- Select and temporarily hold a seat.
- Complete payment through an approved payment provider.
- Receive a confirmed ticket and transaction receipt.
- View, cancel, or request changes to eligible bookings.
- Receive departure and service notifications.
- Present a QR-coded ticket for boarding validation.
- View booking history and request support.

**Operator capabilities**
- Register an organization and submit verification information.
- Register vehicles and seating configurations.
- Define routes, stops, and boarding points.
- Publish trip schedules and fares.
- Assign vehicles and authorized personnel to trips.
- Monitor bookings and remaining seat capacity.
- View passenger manifests.
- Validate tickets and record boarding.
- Review settlements, fees, and operational reports.

**Terminal administration capabilities**
- Manage participating operators and terminal information.
- Register authorized boarding locations.
- Coordinate departure and boarding procedures.
- View relevant trip and passenger information.
- Record operational incidents and service disruptions.

### 4.3 Freight Logistics domain — planned second commercial domain

**Freight customer capabilities**
- Create a shipment request.
- Specify pickup and delivery locations.
- Describe goods, weight, dimensions, quantity, and handling requirements.
- Specify preferred collection and delivery dates.
- Receive offers from eligible transport providers.
- Compare offers and agree on a price.
- Book a transport service.
- Track shipment milestones.
- Confirm delivery or submit a dispute.

**Transport provider capabilities**
- Register trucks and cargo vehicles.
- Specify vehicle type, payload capacity, and permitted cargo.
- Publish routes, availability, and capacity.
- Respond to shipment requests.
- Submit transport quotations.
- Accept and manage confirmed assignments.
- Update pickup, transit, and delivery status.
- Provide delivery confirmation.

**Freight administration capabilities**
- Verify operators and vehicles.
- Manage shipment disputes.
- Review service performance.
- Monitor assignments and delivery records.
- Support settlement and commission reconciliation.

Passenger and freight operations must remain separate where their business rules differ. A passenger seat reservation must never be represented as a freight capacity reservation.

## 5. Initial Market Scope: Jinka Passenger Services

### 5.1 Launch approach

The initial launch should recruit participating operators at Jinka Bus Terminal rather than opening unrestricted vehicle registration.

The platform should first establish verified operational data:
- Participating transport operators
- Their authorized vehicles
- Actual seat configurations
- Approved routes and destinations
- Departure schedules
- Fares and applicable charges
- Boarding and pickup locations
- Cancellation and refund policies
- Operator contact and escalation procedures

A route existing in the directory does not make a trip bookable. A bookable trip requires an authorized operator, an assigned vehicle, a published schedule, and reliable seat inventory.

### 5.2 Initial route catalogue

Priority destinations:
1. Jinka to Wolaita Sodo
2. Jinka to Addis Ababa
3. Other Jinka-originating destinations confirmed by participating operators

The route catalogue should support intermediate stops and approved pickup points.

A passenger may select an alternative boarding location only when the operator has explicitly authorized that location for the selected trip. A booking must show the exact boarding point, reporting time, and applicable conditions.

### 5.3 Booking lifecycle

1. Passenger searches for a trip.
2. Platform displays eligible trips and verified availability.
3. Passenger selects a seat.
4. Platform places a temporary hold on that seat.
5. Passenger completes payment within the hold period.
6. Payment provider confirms the transaction.
7. Platform atomically confirms the booking and issues a ticket.
8. Passenger receives the ticket and receipt.
9. Operator validates the ticket at boarding.
10. Platform records the boarding outcome and closes the trip passenger manifest.

Payment callbacks must be verified before a ticket is issued as paid. Duplicate callbacks, interrupted payments, expired seat holds, and concurrent seat selections must be handled safely. The platform must never sell the same seat twice for the same trip.

### 5.4 Initial ticket requirements

A confirmed ticket should contain:
- Unique ticket reference
- Passenger identification details appropriate to the applicable policy
- Operator and vehicle information
- Origin and destination
- Approved boarding point
- Departure date and time
- Seat number
- Fare and payment status
- QR code or equivalent validation reference
- Ticket issuance time
- Relevant cancellation and boarding conditions

Sensitive passenger information must not be exposed in publicly accessible QR codes.

## 6. Commercial and Revenue Model

The following are proposed models for future evaluation, not approved prices or commercial commitments.

**Passenger revenue options**
- Per-ticket service fee
- Percentage commission on completed bookings
- Operator subscription
- Optional operator management tools
- Contracted terminal or institutional service arrangements

**Freight revenue options**
- Commission on completed freight assignments
- Subscription for fleet operators
- Optional premium listing or business-management features
- Contracted enterprise logistics services

### 6.1 Financial control requirements

Before real payment processing is activated, the product must define:
- Who receives passenger payments.
- Whether the platform acts as a marketplace intermediary or another legally approved arrangement.
- Operator settlement schedules.
- Platform service fees.
- Refund and cancellation rules.
- Failed and reversed payment handling.
- Transaction reconciliation.
- Fraud and dispute handling.
- Applicable tax, licensing, and consumer-protection obligations.

Payment-provider selection and commercial settlement arrangements require separate approval and verification. No real-money processing is authorized by this document.

## 7. Product Architecture Principles

### 7.1 Proposed domain boundaries

| Domain | Responsibility |
|---|---|
| Identity and Access | Accounts, authentication, permissions |
| Organizations | Operators, business profiles, memberships |
| Locations and Routes | Cities, terminals, stops, route definitions |
| Fleet | Vehicles, capacity, configurations, assignments |
| Passenger Mobility | Trips, seat inventory, bookings, tickets |
| Payments and Settlements | Payment records, reconciliation, refunds |
| Freight Logistics | Shipment requests, quotations, assignments, delivery |
| Notifications | Booking and operational messages |
| Support and Disputes | Complaints, cases, resolutions |
| Reporting | Operational and commercial reporting |
| Audit and Compliance | Traceability, access history, policy evidence |

These are approved product-design boundaries, not authorization to create these modules in the current repository.

### 7.2 Technical principles

- Preserve the approved FastAPI and React/TypeScript/Vite technical foundation.
- Use PostgreSQL for persistent transactional data.
- Use Alembic for controlled schema evolution.
- Keep domain boundaries explicit.
- Define and version API contracts.
- Use database transactions and appropriate locking for seat inventory.
- Use idempotency for payment and booking operations.
- Keep external payment providers behind a controlled integration boundary.
- Use synthetic data in development and automated tests.
- Maintain audit trails for material operational and financial events.
- Design for intermittent connectivity and mobile use.
- Support Amharic-first and English localization.
- Apply security, privacy, and accessibility requirements throughout development.

A modular monolith is a reasonable initial architecture: independently bounded domains within one deployable backend, with clear interfaces. Microservices should be considered only when demonstrated operational or scaling needs justify their additional complexity.

## 8. Phased Product Roadmap

The roadmap is approved as the intended product sequence. Each phase still requires its own entry authorization and acceptance gate.

### Phase 0 — G1 Technical Foundation

**Purpose:** Establish a reliable, runnable technical base.

Scope:
- FastAPI backend foundation
- React/TypeScript/Vite frontend foundation
- PostgreSQL configuration
- Alembic baseline
- Domain and module boundaries
- API contract conventions
- Responsive Amharic-first application shell
- Synthetic-only configuration and fixtures
- Local developer documentation and validation

Exit criteria:
- Documented local setup works.
- Backend and frontend validation evidence is available.
- Database configuration and migration path are verified.
- API and frontend foundations are reviewable.
- No unexplained changes or unrelated modifications.
- Exact commit and review evidence are recorded.

**Boundary:** Continue only the separately approved G1 work. No passenger, freight, or payment domain implementation is authorized by this roadmap approval.

### Phase 1 — Passenger Mobility Product Design

**Purpose:** Complete detailed requirements and operational design for the first commercial service.

Scope:
- Passenger journey mapping
- Operator onboarding process
- Route and stop data model
- Vehicle and seat configuration
- Trip and schedule model
- Seat inventory and reservation rules
- Boarding and ticket validation rules
- Cancellation and refund policy design
- API contracts and interface specifications
- Synthetic end-to-end scenarios

Exit criteria:
- Requirements and acceptance criteria approved.
- Booking and seat inventory invariants documented.
- Operator and terminal operating model agreed.
- Security and privacy review completed.
- Owner separately authorizes implementation.

### Phase 2 — Passenger Booking MVP

**Purpose:** Implement the first passenger booking workflow using synthetic or otherwise explicitly authorized non-production arrangements.

Scope:
- Passenger trip search
- Route and schedule management
- Vehicle and seat configuration
- Seat availability
- Temporary seat holds
- Booking lifecycle
- Ticket generation
- Operator trip dashboard
- Passenger booking history
- QR ticket validation using test credentials
- Notifications using test services

Exit criteria:
- No duplicate seat allocation under concurrent booking tests.
- Booking lifecycle handles failures and retries.
- Ticket validation works with synthetic tickets.
- Operator workflows pass acceptance tests.
- Security and authorization checks pass.

### Phase 3 — Payment Integration and Controlled Pilot

**Purpose:** Prepare and conduct an approved pilot with participating Jinka operators.

Scope:
- Select and assess an authorized payment provider.
- Define and approve settlement arrangements.
- Integrate payment sandbox first.
- Test payment success, failure, duplicate callbacks, and reversals.
- Validate refunds and reconciliation.
- Complete operator agreements and operational readiness.
- Conduct a controlled pilot only after required approvals.

Exit criteria:
- Payment and settlement evidence reconciles.
- Operator and terminal authorization is verified.
- Legal and operational prerequisites are addressed.
- Pilot readiness is independently reviewed.
- Owner separately approves any live transaction or deployment.

### Phase 4 — Freight Logistics Marketplace

**Purpose:** Introduce the second major business area without compromising passenger operations.

Scope:
- Freight customer and provider onboarding
- Truck and cargo vehicle registration
- Capacity and availability
- Shipment request creation
- Quotation and negotiation
- Assignment and booking
- Shipment status and delivery confirmation
- Freight settlement and dispute handling

Exit criteria:
- Freight lifecycle is independently tested.
- Passenger and freight data and permissions are properly separated.
- Provider verification and cargo-handling policies are established.
- Financial reconciliation and dispute processes are validated.

### Phase 5 — Regional and National Expansion

**Purpose:** Expand beyond the initial Jinka market.

Potential additions:
- Additional South Omo and regional destinations
- More Ethiopian cities and intercity operators
- Additional terminals and boarding points
- More passenger transport categories
- Freight corridors and logistics providers
- Local and regional transport services
- Vehicle rental and other approved mobility services
- Business and institutional accounts
- Advanced operational reporting

Expansion must be based on verified operator participation, route availability, support capacity, and compliance readiness—not merely the ability to add a city to a dropdown.

### Phase 6 — Advanced Platform Capabilities

Potential future capabilities:
- Live vehicle tracking
- Predictive trip and demand analytics
- Dynamic capacity and fleet utilization
- Automated dispatch assistance
- Warehouse and storage marketplace
- Multi-stop freight planning
- Business logistics integrations
- Loyalty and customer engagement
- Advanced fraud detection and operational risk monitoring

These are optional future capabilities and are not required for the first launch.

## 9. Cross-Cutting Requirements

### 9.1 Localization
- Amharic-first user experience.
- English language option.
- Extensible localization for other Ethiopian languages.
- Clear typography and mobile-friendly layouts.
- Localized dates, times, and currency presentation.
- Ethiopian Birr display where applicable.

### 9.2 Connectivity and reliability
- Responsive interfaces for low-cost Android devices.
- Efficient API requests and lightweight screens.
- Clear handling of weak or interrupted connections.
- Safe retry behavior for booking and payment operations.
- No assumption that a failed mobile request means a transaction failed.

### 9.3 Security and privacy
- Strong authentication and authorization.
- Operator verification and controlled administration.
- Secure storage and transmission of personal data.
- Minimal passenger data collection.
- Restricted access to manifests and financial information.
- Audit trails for sensitive actions.
- Secure QR ticket validation.
- No credentials or real customer data in source control or synthetic fixtures.

### 9.4 Operational trust
- Transparent fares and booking conditions.
- Verified operator and vehicle information.
- Clear boarding instructions.
- Complaint and dispute resolution.
- Recorded cancellation and refund decisions.
- Accurate trip and shipment status.
- Visible distinction between estimated and confirmed information.

## 10. Principal Risks and Controls

| Risk | Required control |
|---|---|
| Operators publish inaccurate schedules | Operator verification and schedule confirmation |
| Double-booked seats | Atomic reservation and database concurrency controls |
| Payment succeeds but booking is not confirmed | Idempotent payment processing and reconciliation |
| Passenger boards at an unauthorized stop | Operator-approved boarding points |
| Fraudulent or duplicated tickets | Secure ticket references and server-side validation |
| Unreliable vehicle or driver information | Verification and periodic review |
| Freight cargo disputes | Shipment descriptions, evidence, and dispute procedures |
| Weak connectivity | Resilient client behavior and safe transaction retries |
| Premature national expansion | Controlled market onboarding and readiness gates |
| Unclear legal or commercial responsibilities | Legal, licensing, and contractual review before live operations |

## 11. Success Measures

Targets should be established after baseline discovery and pilot planning. The following metrics define what should be measured.

**Passenger service**
- Search-to-booking conversion
- Successful booking rate
- Seat allocation accuracy
- Payment confirmation rate
- Boarding validation rate
- Cancellation and refund rates
- Departure punctuality
- Passenger complaints and resolution time

**Operator service**
- Verified operators onboarded
- Active vehicles and published trips
- Schedule accuracy
- Operator adoption and retention
- Settlement accuracy
- Trip completion rate

**Freight service**
- Verified freight providers
- Active vehicle capacity
- Shipment request-to-assignment rate
- Successful delivery rate
- Delivery time variance
- Dispute rate and resolution time

**Platform reliability**
- API availability
- Booking transaction failure rate
- Duplicate booking incidents
- Payment reconciliation exceptions
- Security incidents
- Mobile performance and error rate

No numerical target should be represented as an established baseline until supported by actual pilot evidence.

## 12. Governance and Authorization Gates

| Gate | Required Owner decision |
|---|---|
| P0 | Product direction and roadmap approval — **APPROVED 2026-11-06** |
| P1 | Approve detailed passenger requirements and operating model |
| P2 | Authorize passenger MVP implementation |
| P3 | Approve payment integration and pilot preparation |
| P4 | Separately approve live transactions and production deployment |
| P5 | Approve freight requirements and implementation |
| P6 | Approve regional and national expansion |

Approval of a phase does not automatically authorize the next phase.

Changes to architecture, domain boundaries, data policy, commercial rules, payment handling, deployment, and production operations must be reviewed under their respective approval gates.

## 13. Explicit Exclusions from Current Authorization

This product-scope approval does not authorize:
- Changes to the existing G1 repository or branch beyond its separately approved G1 work.
- Creation or implementation of new passenger or freight domains.
- Changes to G1 requirements or architecture without review.
- Live payment processing or financial transactions.
- Production deployment or public service activation.
- Recruitment or onboarding of real transport operators on the platform.
- Use of real passenger or shipment data.
- Commercial pricing, commissions, or contractual commitments.
- Paid services, subscriptions, or infrastructure purchases.
- Repository merge or release.

## 14. Recommendation and Approved Direction

Adopt a **unified platform strategy with staged commercial delivery**:

1. Complete and verify the existing G1 technical foundation.
2. Prepare detailed passenger mobility requirements and operating procedures.
3. Build the passenger booking MVP after separate implementation authorization.
4. Validate payment and operating arrangements before a controlled pilot.
5. Introduce freight logistics as a separately governed domain.
6. Expand geographically only after operational readiness is demonstrated.

This approach preserves the long-term ambition while limiting initial operational complexity and protecting the quality of the technical foundation.

---

**Document disposition:** Owner-approved product direction and roadmap.  
**Approval date:** 2026-11-06.  
**Next proposed activity:** Prepare the Passenger Mobility Product Requirements Document (PRD) and Jinka Operator Onboarding specification for Owner review.  
**Implementation status:** Not authorized by this document; separate phase approvals remain required.
