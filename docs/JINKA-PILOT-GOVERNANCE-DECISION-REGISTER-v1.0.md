# MaaleNex Moto — Jinka Pilot Governance Decision Register v1.0

- **Status:** Owner-approved working governance baseline, with unresolved accountable-party assignments
- **Approval:** 2026-11-07
- **Repository:** `akefadaka-git/maalenex-moto`
- **Planning branch:** `docs/product-scope-roadmap-v1`
- **Related specification:** [Jinka Operator Onboarding v0.1](JINKA-OPERATOR-ONBOARDING-v0.1.md)

## 1. Purpose and authority

This register translates the Owner-approved passenger MVP defaults into governance controls for planning a Jinka pilot. It does not appoint real people or organizations, establish legal authority, confirm terminal permission, or authorize real-world operator engagement.

## 2. Approved pilot principles

1. **Passenger-first:** Passenger mobility is the first launch domain. Freight remains later and separately scoped.
2. **Jinka-first:** The initial operating focus is Jinka Bus Terminal and verified Jinka-originating services.
3. **Small verified cohort:** Start with a small cohort. Exact operator names and count remain unresolved.
4. **Verify before publication:** No operator, vehicle, route, boarding point, fare, schedule, or trip becomes publicly bookable before the required evidence review and approval.
5. **Terminal-first boarding:** Jinka Bus Terminal is the initial boarding model. Intermediate boarding points require explicit trip/service-level approval.
6. **Separation of duties:** Submission, review, final approval, financial access, and platform administration must be controlled and attributable.
7. **No implied endorsement:** Platform verification is limited to defined checks and is not a government guarantee, roadworthiness certificate, or general safety certification.
8. **Synthetic readiness first:** Training and technical acceptance use synthetic data before any live pilot.
9. **No assumed commercial terms:** No commission, fee, settlement, or operator commercial obligation is presumed.
10. **Owner-controlled activation:** Real onboarding, public activation, live transactions, and production deployment require separate authorization.

## 3. Pilot route priorities

| Priority | Route | Initial disposition |
|---|---|---|
| 1 | Jinka–Wolaita Sodo | Candidate route for verification; not confirmed active or authorized |
| 2 | Jinka–Addis Ababa | Candidate route for verification; not confirmed active or authorized |
| 3 | Other Jinka-originating routes | Out of initial candidate set until proposed and verified |

For each route, the responsible reviewers must confirm the operator's authority, actual service pattern, schedule, terminal arrangement, stop sequence, and any required approvals before publication.

## 4. Operator onboarding control stages

| Stage | Required evidence/control | Gate outcome |
|---|---|---|
| 1. Candidate identification | Source and date of lead; no public endorsement | Candidate only |
| 2. Application | Organization details and authorized representative submission | Submitted |
| 3. Evidence review | Applicable business/operating evidence, reviewed by an assigned competent reviewer | Verified, rejected, or further information required |
| 4. Vehicle review | Vehicle identity, authorized use, capacity, seat layout, and applicable evidence | Vehicle eligible or blocked |
| 5. Route/terminal review | Operator route authority and terminal/boarding arrangements | Route and boarding scope approved or blocked |
| 6. Staff and roles | Individual accounts, least privilege, privileged-role approval | Access eligible |
| 7. Commercial/policy agreement | Participation terms, responsibilities, support, disruption and cancellation policy | Agreement complete |
| 8. Synthetic readiness | Synthetic trips, seats, booking, ticketing, manifest, boarding, exception tests | Technical/operational acceptance |
| 9. Activation decision | Recorded approval by designated authority with exact scope and effective date | Activation eligible; not automatic |

## 5. Separation of duties and minimum roles

The following are role definitions only. Accountable individuals and organizations must be designated before real onboarding.

- **Onboarding reviewer:** Reviews organization and representative evidence.
- **Vehicle reviewer:** Reviews vehicle and seating evidence; must not imply formal roadworthiness certification unless independently authorized.
- **Route/terminal reviewer:** Confirms route, terminal, and boarding-point arrangements from an appropriate source.
- **Final approving officer:** Records the final operator activation decision within delegated authority.
- **Platform administrator:** Manages platform configuration and accounts; cannot bypass approval or audit controls.
- **Compliance/risk reviewer:** Reviews exceptions, incidents, and restrictions.
- **Support owner:** Handles passenger cases and operator escalations.
- **Operator roles:** Owner, administrator, dispatcher, ticketing agent, driver/conductor, and finance user, each with least-privilege access.

The person submitting an application or material change must not silently self-approve it. Operator finance access must not be inherited automatically by all operator administrators.

## 6. Evidence and privacy controls

- Maintain an evidence register with unique reference, category, requirement, applicability, source/issuer, validity period where relevant, secure reference, review status, reviewer, timestamp, and decision notes.
- Treat uploaded evidence as submitted, not verified, until the defined check is completed.
- Collect only information needed for an approved purpose.
- Restrict representative identity and business evidence to authorized reviewers.
- Do not place sensitive documents in Git repositories, public issue comments, test fixtures, or public operator profiles.
- Define lawful basis, retention, deletion, access, and legal-hold procedures before collecting real documents.
- Confirm statutory requirements and acceptable evidence through qualified local legal review or the relevant authority; do not infer legal validity from appearance.
- Use synthetic identities and fictional vehicle identifiers in development and testing.

## 7. Activation prerequisites

All applicable prerequisites must be evidenced before any public pilot activation:
- Candidate operator has completed the approved application and evidence checks.
- Authorized representative and operating authority have been reviewed.
- Responsible terminal authority/party has confirmed the applicable terminal and boarding arrangements.
- Each vehicle and seat layout has passed the defined review.
- Each route, stop, schedule, and fare has been approved for the specific service.
- Operator and platform responsibilities, support, disruption, and cancellation arrangements are documented.
- Staff accounts and role assignments are approved.
- Synthetic acceptance covers booking, seat inventory, ticket validation, boarding, and exception paths.
- Legal/privacy review and required agreements are complete.
- Final activation sign-off identifies exact operator, vehicles, routes, services, dates, and permissions.

A missing prerequisite blocks the affected activation scope. No checklist item may be marked complete without evidence.

## 8. Decision register

| ID | Decision / dependency | Current status | Required action / owner |
|---|---|---|---|
| JINKA-GOV-01 | Initial operator names and cohort size | OPEN | Owner-led candidate selection and engagement plan |
| JINKA-GOV-02 | Terminal authority and permission | OPEN | Identify responsible terminal authority; obtain documented confirmation |
| JINKA-GOV-03 | Verification evidence policy | OPEN | Complete local legal/operational review and approve evidence checklist |
| JINKA-GOV-04 | Reviewer and final approver appointments | OPEN | Owner to designate accountable roles and separation of duties |
| JINKA-GOV-05 | Vehicle/seat review authority | OPEN | Identify competent reviewer and limits of platform verification |
| JINKA-GOV-06 | Jinka–Wolaita Sodo service validation | OPEN | Verify actual operator, schedule, stops, and authority |
| JINKA-GOV-07 | Jinka–Addis Ababa service validation | OPEN | Verify actual operator, schedule, stops, and authority |
| JINKA-GOV-08 | Intermediate boarding points | DEFERRED | Terminal-first; any exception requires explicit service-level approval |
| JINKA-GOV-09 | Operator commercial terms | BLOCKED / NOT SET | No commission, fee, settlement, or revenue assumption; separate approval required |
| JINKA-GOV-10 | Passenger cancellation/refund policy | OPEN | Agree exact rules and operator/platform responsibilities before live bookings |
| JINKA-GOV-11 | Payment provider and collection model | BLOCKED / NOT SELECTED | Due diligence, legal review, security and commercial approval required |
| JINKA-GOV-12 | Passenger support and operator escalation | OPEN | Assign named accountable owner and coverage model |
| JINKA-GOV-13 | Pilot size, duration, and exit criteria | OPEN | Approve cohort, period, capacity, success measures, and stop conditions |
| JINKA-GOV-14 | Privacy, retention, and data handling | OPEN | Approve data inventory, lawful basis, access, retention, deletion, and incident process |
| JINKA-GOV-15 | Production activation | BLOCKED | Requires separate Owner approval after all readiness evidence is complete |

## 9. Pilot monitoring and stop conditions

Proposed measures for a later approved pilot:
- Published trip and schedule accuracy.
- Operator readiness and evidence expiry.
- Booking completion and seat-hold expiry.
- Duplicate seat allocation incidents (target: zero).
- Ticket/manifest/boarding discrepancies.
- Trip cancellations and disruptions.
- Passenger complaints and resolution time.
- Privacy, access-control, and security incidents.
- Payment/reconciliation measures only if a payment phase is later approved.

The pilot must pause the affected operator, vehicle, route, or function when required evidence expires, material discrepancies arise, boarding arrangements are no longer confirmed, passenger data is exposed, or an unresolved safety/security issue makes continued operation inappropriate. Any restriction or reinstatement must be recorded with evidence, scope, decision maker, and rationale.

## 10. Explicit authorization boundary

This register authorizes documentation and planning only. It does not authorize:
- Contacting or onboarding real operators.
- Collecting real business, representative, vehicle, or passenger documents.
- Confirming legal or regulatory eligibility.
- Creating real operator accounts.
- Publishing real routes, fares, schedules, or trips.
- Taking bookings or processing payments.
- Production deployment or production data changes.
- Freight implementation.

## 11. Next gate

Prepare a separately reviewable Passenger MVP implementation plan with:
- domain and architecture boundaries,
- ordered backlog and dependencies,
- data classification and threat model,
- synthetic test plan and acceptance criteria,
- migration and rollback strategy,
- security/privacy controls,
- verification evidence and phase exit criteria.

Implementation begins only after explicit Owner approval of that plan.

**Disposition:** Governance planning baseline approved. Real-world engagement, live operations, payments, production activation, and implementation remain subject to separate approval.
