# MaaleNex Moto — Jinka Transport Operator Onboarding Specification

**Document ID:** MNM-OPS-JINKA-001  
**Version:** 0.1  
**Status:** Draft for Owner review  
**Parent scope:** `docs/PRODUCT-SCOPE-ROADMAP-v1.md`  
**Related requirements:** `docs/PASSENGER-MOBILITY-PRD-v0.1.md`  
**Initial market:** Jinka Bus Terminal, Ethiopia  
**Operator model:** Participating terminal-based transport operators  
**Implementation / live onboarding status:** Not authorized by this document

> This specification defines a proposed onboarding and verification process. It does not contact operators, collect personal documents, make eligibility decisions, establish contracts, or authorize real operator onboarding. Required evidence and legal obligations must be confirmed with qualified local advice and relevant authorities before the process is used operationally.

---

## 1. Purpose

Establish a controlled, traceable process for identifying, reviewing, approving, activating, monitoring, and—when necessary—suspending transport operators participating in MaaleNex Moto's initial Jinka passenger service.

The first cohort is limited to operators operating from or formally participating at Jinka Bus Terminal. The platform will not initially allow unrestricted self-service publication of public trips by unverified vehicle owners.

## 2. Onboarding Principles

1. **Verify before publication:** An operator cannot publish bookable trips until the required organization, operating authority, vehicles, and service information have been reviewed.
2. **Evidence-based status:** Every verification item has a status, reviewer, evidence reference, review date, and outcome.
3. **Least privilege:** Users receive only the access required for their role.
4. **Organization accountability:** Every operator account belongs to a verified organization; individual staff actions remain attributable.
5. **No false endorsement:** Platform verification confirms completion of the platform's defined checks; it must not be presented as a government guarantee or broader safety certification.
6. **Data minimization:** Collect only information needed for the defined purpose and approved retention policy.
7. **Separation of duties:** Applicant submission, review, approval, financial access, and platform administration should not all rest with one account.
8. **Controlled changes:** Changes to vehicles, routes, fares, schedules, and authorized staff are reviewed and logged.
9. **Fair suspension and appeal:** Restrictions require a recorded reason, scope, responsible reviewer, and an available escalation route.
10. **No production activity without gate approval:** This document does not authorize live onboarding or trip publication.

## 3. Operator and Account Roles

### 3.1 Operator organization roles

| Role | Permitted capabilities (proposed) |
|---|---|
| Operator Owner | Manage organization profile and nominate authorized administrators |
| Operator Administrator | Manage staff, vehicles, routes, schedules, fares, and trip publication requests |
| Dispatcher | Manage assigned schedules, trip readiness, and vehicle/crew assignment |
| Ticketing Agent | View permitted bookings and assist passengers under policy |
| Driver / Conductor | Access assigned trip manifest and perform boarding validation |
| Operator Finance User | View authorized transaction, settlement, and reconciliation records |

An individual may hold multiple operator roles only when approved and recorded. Finance access must not be granted automatically to all operator administrators.

### 3.2 Platform roles

| Role | Responsibility |
|---|---|
| Onboarding Reviewer | Check submitted organization and operating evidence |
| Vehicle Reviewer | Review vehicle and seating information |
| Route/Operations Reviewer | Review routes, schedules, and boarding locations |
| Approving Officer | Record final platform approval within delegated authority |
| Platform Administrator | Configure accounts and platform controls; cannot bypass audit |
| Compliance / Risk Reviewer | Review exceptions, incidents, and restrictions |
| Support Agent | Handle operator questions and documented cases |

Role assignment and approval authority must be configured before live use. The person submitting a record should not silently self-approve it.

## 4. Onboarding Lifecycle

Proposed organization states:

1. **Prospect** — identified but not yet invited or formally applying.
2. **ApplicationStarted** — organization has begun the process.
3. **Submitted** — required application information has been submitted.
4. **UnderReview** — evidence is being reviewed.
5. **MoreInformationRequired** — specific gaps have been recorded for the applicant.
6. **ConditionallyApproved** — limited setup access may be allowed, but public bookable trips remain disabled.
7. **Approved** — required checks and approvals are complete.
8. **Active** — authorized users, vehicles, and trip data are configured and activation checks have passed.
9. **Restricted** — selected capabilities are disabled pending review.
10. **Suspended** — service publication or other access is disabled under a documented decision.
11. **Rejected** — application is declined with a recorded reason and escalation route.
12. **Withdrawn** — applicant has withdrawn.

Transitions must be explicit, authorized, and audited. A rejected or suspended operator must not become active through an ordinary profile edit.

## 5. Stage 1 — Operator Identification and Invitation

### 5.1 Purpose
Identify transport businesses that operate from or participate in Jinka Bus Terminal and may be eligible for the initial pilot.

### 5.2 Proposed steps
- Record the operator's trading or organization name as supplied.
- Record an official contact channel and a nominated representative.
- Record the operator's claimed terminal presence and service category.
- Identify the person authorized to submit the application.
- Explain the proposed platform service, data use, verification steps, and that participation is subject to review and agreement.
- Issue a unique application reference.

### 5.3 Controls
- Do not imply terminal, government, or platform endorsement before verification.
- Do not publish an operator listing at this stage.
- Record the source and date of the initial lead.
- Obtain consent before retaining contact details beyond the approved purpose and period.

## 6. Stage 2 — Organization Application

### 6.1 Information requested
Subject to legal review and data-minimization approval:
- Organization or business name.
- Organization type and contact information.
- Business/registration identifiers where applicable.
- Principal business address and operating location.
- Authorized representative name and role.
- Evidence that the representative may act for the organization.
- Relevant transport operating authorization or permit evidence, where applicable.
- Terminal participation or operating evidence, where applicable.
- Service routes and passenger transport categories.
- Operational contact and escalation contact.
- Agreement to platform terms, privacy notice, operational rules, and pilot conditions when finalized.

### 6.2 Evidence handling
- Record document type, issuer (as stated), identifier where necessary, issue/expiry dates where applicable, review outcome, reviewer, and secure evidence reference.
- Do not store unnecessary identity-document copies.
- Restrict sensitive documents to specifically authorized reviewers.
- Never expose submitted documents in public operator profiles or passenger search.
- Record whether an item is verified, pending, expired, rejected, or not applicable.
- Confirm any statutory requirement and acceptable evidence with qualified local counsel or the relevant authority; do not infer legal validity from a document's appearance.

## 7. Stage 3 — Representative and Staff Verification

- Verify the nominated representative using an approved procedure.
- Confirm their authority to represent the organization.
- Record operator staff who require platform accounts.
- Assign roles based on job responsibility.
- Require each staff member to use an individual account; shared credentials are prohibited.
- Apply stronger authentication to privileged roles where supported and approved.
- Define account removal and access review when staff leave or change duties.
- Record approval of each privileged role assignment.

## 8. Stage 4 — Vehicle Registration and Review

### 8.1 Proposed vehicle record
- Registration/plate identifier as required for verification.
- Vehicle make, model, and type.
- Passenger capacity.
- Seating layout and seat identifiers.
- Relevant operating/inspection evidence, where applicable.
- Insurance or other required evidence, where applicable.
- Ownership, lease, or authorized-use relationship.
- Accessibility features, if any.
- Vehicle status and effective dates.
- Authorized operator and permitted service scope.

### 8.2 Review controls
- Check consistency between submitted vehicle details and evidence.
- Verify that passenger capacity and seat layout are plausible and supported.
- Mark blocked, unavailable, crew, or otherwise non-saleable seats.
- Record expiry and re-verification reminders for time-limited evidence.
- A vehicle cannot be assigned to a bookable trip while required review is incomplete or relevant evidence is expired.
- Do not represent a platform document review as a roadworthiness inspection or official certification.

### 8.3 Vehicle states
- Draft
- Submitted
- UnderReview
- Approved
- Active
- Restricted
- Suspended
- Retired

## 9. Stage 5 — Route, Terminal, and Boarding-Point Setup

For each proposed route, collect:
- Origin and destination.
- Ordered route stops.
- Terminal or station identifiers.
- Intermediate boarding and drop-off points requested by the operator.
- Planned distance and journey-time estimate, if supplied and clearly labelled.
- Operating days and service frequency.
- Any route-specific restrictions or conditions.
- Operator contact and escalation process.

### Review requirements
- Confirm the operator is authorized to offer the proposed service using evidence appropriate to the market and applicable rules.
- Confirm terminal participation and boarding arrangements with the appropriate responsible party.
- Distinguish a stop used for passenger boarding from a location used only for drop-off or operational purposes.
- A boarding point is selectable only when approved for the particular operator/service/trip.
- Record the source, reviewer, and date for route and terminal confirmation.
- Do not promise that a route is active based only on a customer request or a map entry.

## 10. Stage 6 — Schedule and Fare Setup

### 10.1 Schedule data
- Route and service identifier.
- Operating days and effective date range.
- Departure time and terminal.
- Intermediate stop sequence and planned times where available.
- Expected arrival time, clearly marked as estimate if not guaranteed.
- Assigned vehicle and crew.
- Capacity and booking cutoff rules.
- Service status and disruption contact.

### 10.2 Fare data
- Fare by permitted origin/destination segment.
- Currency and included/excluded charges.
- Effective date range.
- Fare owner and authorizing operator role.
- Applicable passenger categories or concessions, if approved.
- Change/cancellation/refund policy reference.
- Approval and publication timestamps.

Fare edits must not silently change an already-confirmed booking. Existing bookings preserve the fare and policy snapshot applicable at confirmation, except through a documented, authorized correction process.

## 11. Stage 7 — Agreement and Operational Readiness

Before activation, the operator and platform must complete the approved agreements and operational checklist, including:

- Operator participation terms.
- Responsibilities for trip accuracy and schedule updates.
- Vehicle and crew responsibilities.
- Passenger handling and boarding procedures.
- Ticket validation process.
- Cancellation, disruption, and refund responsibilities.
- Complaint and incident escalation.
- Data protection and passenger information access.
- Payment and settlement responsibilities, only if the relevant payment phase is approved.
- Service fees or commissions, only if separately approved and contractually agreed.
- Pilot scope, dates, locations, contacts, and exit conditions.

No unapproved fee, commission, settlement arrangement, or contractual obligation may be inferred from platform configuration.

## 12. Stage 8 — Sandbox Training and Activation

Before any public bookable trip:
1. Create operator staff accounts with least-privilege roles.
2. Register reviewed vehicles and approved seat layouts.
3. Configure approved routes and boarding points.
4. Configure synthetic trip schedules and fares.
5. Train dispatchers, ticketing staff, drivers, and conductors using synthetic data.
6. Test trip publication, booking, seat holds, ticket validation, boarding, cancellation, and exception workflows in a non-production environment.
7. Verify support contacts and escalation coverage.
8. Obtain final activation sign-off from the designated approving roles.
9. Record the exact approved scope and effective date.

Production activation and real passenger transactions require separate Owner authorization and all applicable legal, operational, and technical readiness checks.

## 13. Operator Quality Monitoring

Proposed ongoing indicators:
- Schedule accuracy and update timeliness.
- Trip cancellation and disruption frequency.
- Vehicle/crew assignment accuracy.
- Boarding validation compliance.
- Passenger complaints and resolution time.
- Ticketing and manifest discrepancies.
- Evidence expiry and renewal status.
- Security incidents and unauthorized access.
- Settlement exceptions, if payment services are later approved.

Reviews should be risk-based and proportionate. A low metric score should trigger review, not an automatic unsupported accusation.

## 14. Changes and Re-Verification

Require review for material changes, including:
- Organization ownership or authorized representative.
- Operating authorization or terminal participation.
- Vehicle registration, ownership, seating capacity, or condition evidence.
- Routes, stops, and boarding points.
- Staff with privileged access.
- Service schedules and fares.
- Contact and escalation details.

Changes affecting passenger safety, service authorization, or legal eligibility may require immediate restriction of the affected vehicle, route, trip, or account pending review.

Maintain history rather than overwriting the previous approved record without trace.

## 15. Suspension, Restriction, and Reinstatement

### 15.1 Potential triggers
- Expired or invalidated required evidence.
- Material discrepancy in submitted information.
- Unauthorized vehicle, route, or boarding-point use.
- Repeated unannounced schedule failures.
- Confirmed misuse of passenger data.
- Fraud indicators or security compromise.
- Serious unresolved passenger or operational incidents.
- Contractual or legal suspension instruction from an authorized source.

### 15.2 Controls
- Record the trigger, evidence, decision maker, date, scope, and rationale.
- Restrict only the affected capability where safe and practical.
- Protect already-booked passengers through a documented disruption workflow.
- Notify the operator through an approved channel.
- Provide a response or appeal route unless a lawful restriction prevents it.
- Preserve relevant audit evidence.
- Reinstate only after the designated reviewer records that conditions have been satisfied.

Suspension must not be used to conceal complaints or avoid refund obligations.

## 16. Data Protection and Records

- Define a data inventory and purpose for each collected field.
- Classify organization, representative, vehicle, and staff records by sensitivity.
- Keep identity and authorization evidence access-restricted.
- Use secure storage and controlled access.
- Define retention, deletion, legal hold, and access-request procedures before live onboarding.
- Do not place sensitive documents in Git repositories, issue comments, public URLs, or test fixtures.
- Use synthetic identities and fictional vehicle identifiers in development and test environments.
- Log document access, verification decisions, role changes, and status transitions.

Retention periods and lawful bases must be determined through qualified legal review and approved policy; this specification does not invent statutory periods.

## 17. Required Onboarding Evidence Register

Each operator application should have a controlled checklist with these fields:

| Field | Description |
|---|---|
| Evidence ID | Unique reference |
| Category | Organization, representative, vehicle, route, terminal, agreement |
| Requirement | What must be demonstrated |
| Applicability | Required, conditional, or not applicable |
| Submitted reference | Secure document/evidence reference |
| Issuer/source | As stated by applicant or verified source |
| Validity | Issue/expiry or applicable period, if relevant |
| Review status | Missing, Submitted, UnderReview, Verified, Rejected, Expired, NotApplicable |
| Reviewer | Accountable reviewer |
| Review timestamp | When the decision was made |
| Decision notes | Reason and outstanding gaps |
| Next review date | If periodic review is required |

A status of Verified must mean the defined check was actually completed and recorded. It must not mean merely that a file was uploaded.

## 18. Onboarding Acceptance Checklist

An operator is eligible for activation only when all applicable checks are complete:

- [ ] Organization identity and application reviewed.
- [ ] Authorized representative reviewed.
- [ ] Applicable operating evidence reviewed by designated reviewer.
- [ ] Terminal participation/boarding arrangements confirmed.
- [ ] Operator agreement and applicable policies accepted.
- [ ] Required staff accounts and roles approved.
- [ ] Each vehicle reviewed and approved.
- [ ] Seat layouts match reviewed vehicle capacity.
- [ ] Routes, stops, and boarding points reviewed.
- [ ] Schedules and fares approved for publication.
- [ ] Cancellation and disruption responsibilities documented.
- [ ] Support and escalation contacts tested.
- [ ] Synthetic training and operational acceptance completed.
- [ ] Final activation sign-off recorded.
- [ ] Any applicable legal and production readiness gate separately satisfied.

An incomplete or inapplicable item must have a documented disposition; checklist completion must not be fabricated.

## 19. Open Owner Decisions

| ID | Decision | Clarification needed |
|---|---|---|
| JINKA-OD-01 | Initial operator cohort | Which operators should be approached first, and who will lead engagement? |
| JINKA-OD-02 | Terminal relationship | Which terminal authority or responsible body must confirm participation and boarding arrangements? |
| JINKA-OD-03 | Evidence policy | Which organization, representative, vehicle, and operating evidence is required after local legal review? |
| JINKA-OD-04 | Verification authority | Who can review and who can finally approve an operator? |
| JINKA-OD-05 | Vehicle review | Which competent party confirms vehicle and seating information? |
| JINKA-OD-06 | Route priorities | Confirm initial Jinka–Wolaita Sodo and Jinka–Addis Ababa services and any additional routes. |
| JINKA-OD-07 | Boarding model | Terminal-only first, or approved intermediate boarding points at initial launch? |
| JINKA-OD-08 | Operator commercial terms | Fee, commission, settlement, and responsibility model; no terms assumed. |
| JINKA-OD-09 | Support ownership | Who handles passenger support and operator escalations during the pilot? |
| JINKA-OD-10 | Pilot scope | Proposed cohort size, duration, and success criteria. |

## 20. Authorization Boundary and Next Gate

This document is submitted for Owner review. It does not authorize:
- Contacting or onboarding real operators.
- Collecting personal or business evidence.
- Approving legal or regulatory eligibility.
- Creating operator accounts for real organizations.
- Publishing real routes, fares, schedules, or trips.
- Taking bookings or processing payments.
- Deploying production services.

After review, the next gate is approval of the operator engagement plan, evidence policy, responsible reviewers, and pilot operating model. Only then should any real-world onboarding begin.

**Disposition:** Draft for Owner review.  
**Implementation and live onboarding:** Not authorized.
