# MaaleNex — Owner-Directed A1 Expanded Product Scope Amendment

- **Document ID:** MNX-A1-EXP-001
- **Version:** 1.0
- **Prepared:** 2026-11-15
- **Status:** PROPOSED — SUBMITTED FOR OWNER REVIEW / APPROVAL
- **Repository:** `akefadaka-git/maalenex`
- **Amendment branch:** `docs/a1-expanded-product-scope-amendment`
- **Baseline branch / SHA:** `main` / `78884c0f2609edbfc94a24e42d84824bff9eed20`
- **Related implementation PR:** [#25 — passenger-only guest preview and reviewed Android integration](https://github.com/akefadaka-git/maalenex/pull/25)
- **Related historical planning source:** PR #2, branch `docs/product-scope-roadmap-v1`, head `3bf77bdbf6d017331a5ec2ea64e2a36577f9c8b6`
- **Related brand/design source:** PR #14, branch history; original PR scope and design evidence retained in repository history.
- **Decision authority:** Owner
- **Implementation authorization:** NONE
- **Deployment / commercial activation authorization:** NONE

> **Approval status is deliberately pending.** This is a prepared amendment for Owner decision. It does not claim that the Owner has approved this expanded specification, does not close or freeze A1, and does not authorize A2 code changes, A3 implementation, payment-provider activation, production data processing, deployment, or commercial operations. An explicit Owner approval must identify this document/version and its exact commit SHA.

---

## 1. Purpose and decision requested

This amendment expands MaaleNex from the narrow passenger-only public guest preview into a proposed **integrated, AI-enabled mobility, payments and business-services platform**. The public landing page is one entry point in a broader product, not the complete product.

The Owner is asked to approve or return for revision:

1. The full product vision, application suite and feature register in this amendment.
2. A passenger-first, Jinka-first initial operating focus, while retaining a modular path to wider Ethiopian markets and separately gated freight/logistics capabilities.
3. A provider-integrated financial architecture, including a customer wallet only where the legal and licensed-provider model permits it.
4. Live geospatial services, journey planning, tracking and operational map capabilities subject to verified data and lawful location processing.
5. An omnichannel customer-care and call-center system.
6. A governed IROKA integration boundary, with IROKA remaining a separate intelligence project/system.
7. A diversified but transparent business model, with all prices, commissions and commercial terms unresolved until separately approved.
8. The acceptance criteria, dependencies, exclusions and stage gates below.

**No implementation is authorized by preparation or review of this document.**

## 2. Source reconciliation and authority

### 2.1 Historical product sources inspected

The following source artifacts were retrieved from the historical planning branch associated with PR #2:

| Source | Exact source reference | What it establishes |
|---|---|---|
| Passenger MVP A1 Implementation Plan v1.0 | `docs/PASSENGER-MVP-A1-IMPLEMENTATION-PLAN-v1.0.md`; blob `86184d7b9435012b43a0b210ed5598e9bbe0743b` | Passenger-first modular-monolith proposal, Jinka-first, booking/seat inventory, ticketing, support, security, synthetic testing and staged delivery |
| Product Scope and Phased Roadmap v1.0 | `docs/PRODUCT-SCOPE-ROADMAP-v1.md`; blob `0f0fb082db129d5b81ebb4f5c302aa9d64b1f7c5` | Owner-approved direction for passenger mobility first and freight as a later distinct business domain; shared platform services and role groups |
| Passenger Mobility PRD v0.1 | `docs/PASSENGER-MOBILITY-PRD-v0.1.md`; blob `1f480edd62ab376fcc87721e962b92d0ef6fdf06` | Passenger discovery, search, booking, payment/ticketing concepts and operational experience |
| Passenger MVP Requirements Baseline v1.0 | `docs/PASSENGER-MVP-REQUIREMENTS-BASELINE-v1.0.md`; blob `3af3ba0345eb29bf18b87b494043d96566ecd41c` | Passenger identity minimum, multi-passenger seats, provisional 10-minute holds, payment disabled, fare and refund controls, Jinka terminal-first, QR ticket and online-first constraints |
| Jinka Pilot Governance Decision Register v1.0 | `docs/JINKA-PILOT-GOVERNANCE-DECISION-REGISTER-v1.0.md`; blob `561b9ab763a498117171a460460cd29e424a45ea` | Verification before publication, small verified cohort, separation of duties, open local authorities and commercial/operational dependencies |
| Passenger MVP Implementation Specification v1.0 | `docs/PASSENGER-MVP-IMPLEMENTATION-SPECIFICATION-v1.0.md`; blob `48aa9a7436358426fc3edd9c2ddc14f6b1856564` | Detailed domain contracts, entities, state machines, APIs, authorization, concurrency, migration and synthetic acceptance baseline |
| PR #2 planning record | PR #2 head `3bf77bdbf6d017331a5ec2ea64e2a36577f9c8b6` | Confirms seven planning artifacts and explicitly documentation-only / implementation-not-authorized status |

PR #14 established the MaaleNex brand identity and Android design-system workstream. Its original PR record identifies the vector emblem/wordmark, bilingual brand asset, Android adaptive launcher resources and frontend design-system remediation. This amendment retains that brand/design foundation; it does not authorize a visual rebrand.

### 2.2 Later repository scope and implementation evidence inspected

| Source | Current branch reference | Reconciliation |
|---|---|---|
| `README.md` | PR #25 head `d4bf907556430b6aab5d886ee381a06d7ec64d18` | Current public app is deliberately a guest-only, non-operational passenger preview; no real accounts, booking, payments, live dispatch or commercial activation |
| `docs/product/MAALENEX-PAY-MOBILITY-AND-FARE-SPEC-v1.0.md` | PR #25 branch; blob `0a20c7f69d47f60f9c4807975a68d4ddd6536698` | Preserves prior requested wallet, payments, driver/owner finance, loyalty, booking lifecycle, fare governance, exports, legal documents, controls and staged acceptance as FUTURE SCOPE ONLY |
| `docs/product/MAALENEX-FUTURE-SCOPE-v1.0.md` | PR #25 branch; blob `c48aca14996aa4c92b7c5a68a15c34810e0ee14a` | Preserves motorcycle driver, heavy-load/cargo and fleet/operator domains as future scope requiring their own gates |
| `docs/A3-OPERATIONS-RUNBOOK-v1.0.md` | PR #25 branch; blob `240f9d7a55bea114687bf7717774d26b2435c025` | Records existing synthetic passenger booking/access/support/manifest behavior and strict non-production boundary |
| A3/A4 consolidated evidence report | PR #25 branch; blob `be8cfe02b12d6138f8c57bdbf92ef59812e9db85` | Records limited implementation and verification status; does not prove expanded features exist |

### 2.3 Reconciliation findings

1. The original approved product direction is broader than the current public preview: passenger mobility first, a longer-term integrated transport/logistics marketplace, shared platform services, and distinct business domains.
2. The original passenger MVP is an intercity scheduled passenger reservation/ticketing model, Jinka-first, with authoritative trip inventory, seat holds, server-issued QR references, operator/terminal workflows and controlled boarding.
3. The original requirements deliberately disabled payment collection, selected no payment provider, set no commission/revenue model, left cancellation/refund amounts unresolved, and excluded offline boarding.
4. The later Pay/Mobility/Fare specification adds substantial future requirements: wallets, double-entry ledger, provider adapters, driver/owner earnings and settlement, loyalty/referrals, configurable jurisdiction-aware fares, statements/exports, agreements and audit controls. It explicitly disclaims implementation authority.
5. The current PR #25 is a narrowed guest-preview implementation. Its removal of account registration, public driver/fleet workspaces, public administration and unsupported live-service claims is a valid security boundary for that preview. It is not a complete implementation of the historical product vision.
6. This amendment consolidates the above sources and adds explicit live-map, call-center, feedback, IROKA intelligence, broader application-suite and business-model requirements. These additions are new proposed scope, not historical requirements retroactively attributed to the earlier approved baseline.
7. No contradiction is resolved by pretending an unverified service, route, operator, payment provider, government permission, fare or commercial arrangement exists.

### 2.4 Supersession rule

If approved, this amendment will **supersede and extend the product-scope portions** of the earlier A1 baseline only to the extent explicitly stated here. It will preserve still-compatible decisions and historical records. It will not rewrite old approvals, erase prior restrictions, retroactively authorize implementation, or change PR #25. The exact Owner approval and accepted amendment commit must be recorded in a subsequent A1 decision/closure record.

---

## 3. Product vision, positioning and principles

**Proposed vision:** MaaleNex is an Amharic-first, locally grounded, intelligent mobility and financial-services ecosystem that helps people and organizations discover, arrange, pay for, manage and monitor transport services through one trusted platform.

**Product principle:** One integrated platform; focused initial passenger service; independently governed domains; expand only when evidence, legal authority, partner capability and operational readiness support it.

### 3.1 Differentiation objectives

- Passenger-first usability with transparent fares, reliable trip information and clear service status.
- Local-first design for Ethiopian transport realities, languages, calendars, payment rails and connectivity.
- Interoperable finance instead of a closed, opaque payment island.
- Human support with traceable case ownership and escalation, not AI-only complaint handling.
- Live maps that distinguish verified live information, estimates, cached data and demonstrations.
- Governed IROKA intelligence that explains and assists without bypassing human and financial controls.
- Modular passenger, driver, operator, finance, support and administration experiences over shared services.
- Accessibility, privacy, safety, auditability and low-bandwidth resilience as core product qualities.

### 3.2 Product quality principles

No dark patterns; no hidden fees; no fabricated availability; no undisclosed fare changes; no forced contact-list upload; no sale of identifiable movement histories; no unauthorized money custody; no autonomous AI money movement or safety-critical dispatch; no role elevation through public registration; no unverified government/partner endorsement.

---

## 4. Complete feature register

Register statuses: **BASELINE** = supported by historical A1 source; **PRESERVED** = present in later future-scope specification; **NEW** = proposed by this amendment; **DEPENDENCY** = unresolved evidence/partner/legal decision. Status does not mean implemented.

### 4.1 Shared platform, identity and experience

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| PLT-001 | Unified account and secure authentication lifecycle | BASELINE | Auth/session/credential lifecycle tests; no client-only authorization |
| PLT-002 | Role, permission and organization-context authorization | BASELINE | Deny-by-default matrix and cross-tenant negative tests |
| PLT-003 | Passenger, driver, operator, owner, agent, support, finance, auditor and platform-admin role definitions | BASELINE + expanded | Approved role matrix; privileged roles separately provisioned |
| PLT-004 | Amharic-first interface, English, qualified Maale localization and extensible language packs | BASELINE + NEW | Locale coverage, translation review and fallback tests |
| PLT-005 | Ethiopian Calendar default with Gregorian preference and explicit date conversion | NEW | Date boundary, leap-year and dual-calendar tests |
| PLT-006 | Responsive mobile/PWA/Android/web design system using canonical MaaleNex identity | BASELINE + NEW | Design tokens, responsive and visual regression evidence |
| PLT-007 | Light/dark theme, typography, accessibility preferences and reduced-motion option | NEW | Theme persistence and accessibility checks |
| PLT-008 | Notifications inbox, push/email/SMS adapters, preferences and delivery status | BASELINE + expanded | Consent, retry, deduplication and delivery-state tests |
| PLT-009 | Search, saved places, favorites, recent activity and universal help entry | NEW | Search/navigation and state persistence tests |
| PLT-010 | Privacy dashboard, consent records, data export and account closure request workflows | NEW | Data-subject workflow tests and audit evidence |
| PLT-011 | Offline-aware shell, retry, queued non-financial actions and synchronization conflict handling | NEW | Offline/online transition tests; no duplicate financial action |
| PLT-012 | Document/evidence management with access controls, version and expiry metadata | BASELINE + expanded | Permission, retention and audit tests |

### 4.2 Passenger mobility, trip and ticketing

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| PAX-001 | Guest discovery of public, verified information without mandatory account | BASELINE | Guest routes expose no protected data/actions |
| PAX-002 | Passenger registration, sign-in, recovery and session/device management | BASELINE; withheld in current preview | Secure end-to-end auth and abuse/rate-limit tests |
| PAX-003 | Search by origin, destination, date, passenger count and service class | BASELINE | Search returns only approved/published trips |
| PAX-004 | Operator, trip, route, boarding point, departure, fare and availability detail | BASELINE | Every public field traces to verified source and effective version |
| PAX-005 | Seat map, multi-passenger selection and explicit seat per passenger | BASELINE | Capacity and uniqueness/concurrency tests |
| PAX-006 | Configurable provisional 10-minute seat hold, expiry and release | BASELINE | Expiry/retry/concurrency tests; duration revalidated before live use |
| PAX-007 | Booking lifecycle: quote, request, assignment, en-route, arrived, started, completed, cancelled, no-show, disputed | BASELINE + expanded | Server-enforced transition and invalid-transition tests |
| PAX-008 | Immutable accepted fare/policy snapshot and itemized payable amount | BASELINE | Historical quote reproducibility; no silent repricing |
| PAX-009 | Passenger ticket with unique server-issued opaque QR/reference and printable fallback | BASELINE | Uniqueness, tamper, scope and expiry tests |
| PAX-010 | Boarding validation and trip-scoped manifests with least privilege | BASELINE | Online server-authoritative validation and manifest isolation |
| PAX-011 | Booking change, cancellation, refund request, disruption and appeal workflows | BASELINE | Scenario matrix; exact policy approved before live use |
| PAX-012 | Passenger trip history, receipts, saved journeys and notifications | BASELINE + expanded | Account ownership and privacy tests |
| PAX-013 | Group/family/corporate bookings and accessibility requests | NEW | Delegation/consent and per-passenger seat tests |
| PAX-014 | Scheduled/recurring journeys and service alerts | NEW | Schedule integrity and notification tests |
| PAX-015 | Trip sharing and trusted-contact safety check-in | NEW | Explicit consent, time-bounded sharing and revocation |
| PAX-016 | Lost property, emergency information and incident reporting | BASELINE + expanded | Case ownership, escalation and privacy tests |

### 4.3 Live maps, location and routing

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| MAP-001 | Interactive map, pan/zoom, location search and map/list synchronized results | NEW | Functional UI and map provider contract tests |
| MAP-002 | User-selected current location with permission explanation and manual fallback | NEW | Permission denial/revocation and manual selection tests |
| MAP-003 | Verified terminals, stations, stops, pickup/drop-off points and landmarks | BASELINE + NEW | Evidence provenance and publication approval |
| MAP-004 | Route geometry, stop sequence, corridor and jurisdiction boundaries | BASELINE + NEW | Versioned source data and topology validation |
| MAP-005 | Journey alternatives, distance/time estimates and routing explanations | NEW | Source, timestamp, confidence and estimate labelling |
| MAP-006 | Live vehicle/driver location and ETA for an assigned active trip | NEW | Authorized source, freshness indicator and access-scope tests |
| MAP-007 | Traffic, disruption and incident overlays where licensed data exists | NEW | Provider terms, freshness, attribution and fallback tests |
| MAP-008 | Geofences for service areas, pickup points and operational zones | NEW | Boundary, spoofing and false-positive tests |
| MAP-009 | Offline/cached map and last-known trip status with staleness warning | NEW | Cache expiry, stale-data warning and recovery tests |
| MAP-010 | Driver/operator navigation and route deviation alerts | NEW | Driver authorization, route integrity and human override |
| MAP-011 | Map privacy controls, location minimization and retention | NEW | Data-flow review, retention enforcement and access audit |
| MAP-012 | Map-provider abstraction and data-source licensing/attribution registry | NEW | Provider swap contract tests and legal provenance register |

Live map dependencies: map tile/routing/geocoding provider and terms; verified route/stop registry; authorized GPS source and driver consent; mobile location permissions; connectivity and accuracy targets; location privacy impact assessment. No provider, GPS coverage, traffic feed, live vehicle fleet or service coverage is presumed.

### 4.4 Wallet, payment, ledger and finance

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| FIN-001 | Wallet eligibility and legally defined customer-funds model | PRESERVED + dependency | Legal/provider sign-off; no stored value before authorization |
| FIN-002 | Wallet dashboard: available, pending, held/reserved and withdrawable balances | PRESERVED | Balance-to-ledger reconciliation tests |
| FIN-003 | Immutable append-only double-entry ledger and chart of accounts | PRESERVED | Every journal balances; no update/delete of posted entries |
| FIN-004 | ETB domestic base currency and explicit multi-currency extension boundary | PRESERVED + NEW | Currency precision, rounding and FX controls |
| FIN-005 | Provider-neutral payment adapter interface | PRESERVED | Contract tests with fake/sandbox adapters |
| FIN-006 | Telebirr, CBE Birr, bank, EthSwitch/PSP and other eligible integrations considered only after provider diligence | PRESERVED + dependency | Written provider API, commercial, security and legal approval |
| FIN-007 | Top-up, payment intent, signed webhook, idempotency, replay protection and state machine | PRESERVED | Duplicate/out-of-order/forged webhook tests |
| FIN-008 | Cash payment recording where service/legal rules permit | PRESERVED + dependency | Receipt, reconciliation and operator accountability tests |
| FIN-009 | Refund, reversal, dispute, chargeback and cancellation adjustment | PRESERVED | Original funding route, duplicate prevention and approval tests |
| FIN-010 | Driver, vehicle-owner and operator payable subledgers and settlement | PRESERVED | Agreement-based allocation and beneficiary isolation |
| FIN-011 | Payout/cash-out to verified beneficiary, maker-checker and risk holds | PRESERVED | Beneficiary-change and dual-control negative tests |
| FIN-012 | Daily/on-demand reconciliation, settlement batch and suspense account | PRESERVED | Break detection, ageing, resolution and audit evidence |
| FIN-013 | Fees, commissions, taxes, withholding and deductions as separately itemized components | PRESERVED + dependency | Approved source and reproducible calculation |
| FIN-014 | Financial dashboard, receipts, statements and exports (PDF/XLSX/CSV/JSON) | PRESERVED | Permission-scoped, audited, accurate exports |
| FIN-015 | Fraud/risk monitoring, velocity limits, anomaly review and case escalation | PRESERVED + NEW | Explainable alerts, false-positive review and audit |
| FIN-016 | Financial close, ledger reconciliation, finance reports and controlled adjustments | NEW | Period close and dual approval tests |
| FIN-017 | Agent-assisted cash-in/cash-out only via licensed partner and approved agency | PRESERVED + dependency | Partner authorization, agent controls and reconciliation |
| FIN-018 | Customer payment security, step-up authentication and transaction alerts | PRESERVED + NEW | Threat-model and end-to-end security tests |

**Non-negotiable:** MaaleNex must not assume it may issue regulated stored value, take deposits, operate a payment system, lend, hold customer funds or provide investment/crypto products. Start with licensed provider/bank arrangements. Any wallet is a product ledger/account only within the legal model approved by counsel, the competent authority and the provider. No real-money activity in synthetic development.

### 4.5 Loyalty, rewards and referrals

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| LTY-001 | Digital loyalty identity and optional physical QR/barcode card | PRESERVED | Secure token and privacy tests |
| LTY-002 | Separate promotional points ledger, never silently represented as ETB | PRESERVED | Ledger separation and redemption tests |
| LTY-003 | Earn, pending, available, redeem, expire and reverse points | PRESERVED | Refund/cancel and expiry tests |
| LTY-004 | Campaigns, coupons, travel passes and eligibility rules | PRESERVED + NEW | Versioned campaign and abuse tests |
| LTY-005 | Referral code/link and qualifying-event rewards | PRESERVED | Self-referral and duplicate-account controls |
| LTY-006 | Loyalty terms, caps, expiry, exclusions and appeals | PRESERVED | Disclosure and dispute tests |

### 4.6 Customer care, call center and feedback

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| CARE-001 | Unified customer case/ticket system linked to authorized booking/payment/incident references | BASELINE + NEW | Role-scoped linking and audit |
| CARE-002 | In-app help, chat and asynchronous messaging | NEW | Delivery, retention, abuse and escalation tests |
| CARE-003 | Public phone support and agent desktop/call-center console | NEW | Call routing, case creation and access controls |
| CARE-004 | IVR, language selection, queue, callback and operating-hours notices | NEW | Queue and fallback simulations |
| CARE-005 | Case categories: booking, route, payment, refund, driver, safety, lost property, accessibility, privacy and general | NEW | Correct triage and priority tests |
| CARE-006 | Assignment, claim, SLA timer, escalation, resolution and reopen | BASELINE + NEW | Lifecycle and overdue escalation tests |
| CARE-007 | Human escalation; no AI-only closure of high-impact cases | NEW | Mandatory human review for safety/finance/privacy cases |
| CARE-008 | Call/chat consent, recording policy, notice, retention and deletion | NEW | Consent and retention audit |
| CARE-009 | AI-assisted transcription/summary/response suggestion with disclosure and human review | NEW | Accuracy sampling, redaction and human override |
| CARE-010 | Trip ratings, operator/driver feedback and structured tags | BASELINE + NEW | Verified completed-trip eligibility and abuse moderation |
| CARE-011 | Complaints, appeals, incident evidence and resolution tracking | BASELINE + NEW | Traceable case evidence and appeal |
| CARE-012 | Customer satisfaction, first-response, resolution-time and repeat-contact metrics | NEW | Defined metric semantics and privacy review |

Call-center dependencies: accountable service owner, staffing/coverage and language plan, published phone/SIP/telephony provider, recording/consent policy, escalation directory, safety incident response and support SLAs. No phone number, 24/7 coverage or staffed operation is claimed until confirmed.

### 4.7 Driver, operator, fleet and terminal suite

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| OPS-001 | Operator organization application, evidence review and approval | BASELINE | Evidence provenance, reviewer and final approval |
| OPS-002 | Vehicle, capacity, seat layout and compliance registry | BASELINE | Vehicle eligibility and expiry tests |
| OPS-003 | Driver/conductor identity, licence and eligibility review | BASELINE | Legal checklist and least-privilege access |
| OPS-004 | Routes, stops, schedules, trip instances and publication workflow | BASELINE | Unapproved data cannot publish |
| OPS-005 | Dispatch, driver assignment, acceptance and trip status | NEW | Server-authoritative state transitions |
| OPS-006 | Driver app: availability, assigned trips, navigation, earnings, safety and support | BASELINE + NEW | Driver-scope and offline recovery tests |
| OPS-007 | Operator workspace: fleet, staff, schedules, manifests and performance | BASELINE | Tenant isolation and audit |
| OPS-008 | Owner workspace: owned vehicles, agreements, attributable earnings and settlement | PRESERVED | Ownership/contract-based data access |
| OPS-009 | Terminal workspace: departure board, boarding coordination and incident reporting | BASELINE | Terminal scope and manifest access tests |
| OPS-010 | Compliance document expiry, suspension and reinstatement | NEW | Evidence-based lifecycle and appeal |
| OPS-011 | Operator and driver service-quality analytics | NEW | Reproducible metrics and role scope |

Public driver, operator and fleet registration remains disabled until secure identity, server-side authorization, tenant isolation, licensing, insurance, evidence review and agreements are accepted.

### 4.8 Freight/logistics and future transport modes

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| FRT-001 | Cargo request, goods attributes, weight/dimensions/handling and pickup/delivery | BASELINE FUTURE | Separate A1/A2 service and legal review |
| FRT-002 | Truck/cargo vehicle capacity and permitted cargo | BASELINE FUTURE | Vehicle and cargo compliance checks |
| FRT-003 | Provider offers, quotation, acceptance and negotiated terms | BASELINE FUTURE | Transparent quote and contract evidence |
| FRT-004 | Shipment milestones, tracking, proof of delivery and dispute | BASELINE FUTURE | Custody/evidence and exception tests |
| FRT-005 | Cargo insurance, restrictions, loading/unloading and liability | BASELINE FUTURE | Applicable legal/insurance evidence |
| FRT-006 | Additional passenger modes (including motorcycle passenger service) | PRESERVED FUTURE | Separate service-class and regulatory gate |

Freight and motorcycle passenger services are retained in the long-term platform architecture but are not automatically included in the first commercial release.

### 4.9 IROKA intelligence integration

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| AI-001 | IROKA service/API integration boundary, identity separation and versioned contracts | NEW | Contract, auth and failure-isolation tests |
| AI-002 | Passenger conversational assistant in Amharic-first language experience | NEW | Qualified language evaluation and safe fallback |
| AI-003 | Journey discovery explanations and route/option comparison | NEW | Grounded source, freshness and uncertainty labels |
| AI-004 | Customer-care classification, summaries and response suggestions | NEW | Human approval, redaction and quality sampling |
| AI-005 | Demand forecasting and operator capacity insights | NEW | Backtesting, drift and confidence reporting |
| AI-006 | Fraud/anomaly signals for human review | NEW | Explainability, false-positive and appeal controls |
| AI-007 | Business copilot and natural-language analytics for authorized roles | NEW | Query permission enforcement and data minimization |
| AI-008 | Localization assistance and translation workflow | NEW | Human-reviewed Maale/Amharic/English content |
| AI-009 | Governed workflow suggestions and bounded automation | NEW | Explicit policy, approval, audit and rollback |
| AI-010 | Model registry, prompt/version trace, evaluation and incident controls | NEW | Reproducible evaluations and model-change approval |

IROKA remains a separate project/system. MaaleNex consumes approved intelligence services through a documented, authenticated, least-privilege interface. No direct cross-repository code coupling, shared secrets, uncontrolled model training on passenger data, or autonomous financial/dispatch action is permitted. Human approval is mandatory for refunds, payouts, beneficiary changes, fare publication, account sanctions, safety response and other high-impact actions.

### 4.10 Administration, compliance, reporting and integrations

| ID | Capability / requirements | Source status | Acceptance evidence |
|---|---|---|---|
| ADM-001 | Separate privileged account provisioning, MFA and least privilege | BASELINE | Privilege escalation negative tests |
| ADM-002 | Maker-checker approvals for finance, fare, operator and sensitive changes | PRESERVED + NEW | Separation-of-duties tests |
| ADM-003 | Immutable audit trail with actor, time, action, reason and correlation | BASELINE | Audit completeness and tamper-resistance review |
| ADM-004 | Fare/jurisdiction policy authoring, approval, publication and version history | PRESERVED | Authority evidence and historical quote replay |
| ADM-005 | Legal agreements, consent, terms and policy versioning | PRESERVED | Exact accepted-version retrieval |
| ADM-006 | PDF/XLSX/CSV/JSON export and receipt sharing | PRESERVED | Data scope, masking, expiry and audit |
| ADM-007 | Analytics dashboards and business reports | BASELINE + NEW | Metric definitions, access and reproducibility |
| ADM-008 | Provider integration registry, webhook health and reconciliation queue | NEW | Contract, signature, replay and outage tests |
| ADM-009 | Incident response, backup/restore and continuity operations | BASELINE + NEW | Recovery exercise and incident simulation |
| ADM-010 | Partner APIs and controlled integration portal | NEW | OAuth/scopes, rate limits, audit and versioning |

---

## 5. Application suite and information architecture

A coordinated suite shares platform services and design language. It must not become a collection of unrelated products or a single overloaded screen.

| Application / workspace | Primary users | Core navigation / areas |
|---|---|---|
| **MaaleNex Passenger** | Guest and passenger | Home, Explore, Map, Trips, Tickets, Wallet, Rewards, Notifications, Help, Account/Settings |
| **MaaleNex Driver** | Approved passenger-service driver | Today, Requests/Assignments, Map, Active Trip, Earnings, Safety, Support, Profile |
| **MaaleNex Operator** | Transport operator and dispatcher | Overview, Trips, Routes, Schedules, Fleet, Drivers, Bookings, Manifests, Settlements, Reports |
| **MaaleNex Owner** | Vehicle owner | Vehicles, Assignments, Agreements, Earnings, Settlements, Documents, Support |
| **MaaleNex Terminal** | Authorized terminal personnel | Departure board, trip readiness, manifests, boarding validation, incidents |
| **MaaleNex Finance** | Restricted finance staff | Ledger, payment intents, provider events, reconciliation, refunds, payouts, settlements, close, reports |
| **MaaleNex Care** | Call-center and support agents | Queue, customer/case lookup, trip/payment context, contact history, escalation, knowledge base, QA |
| **MaaleNex Admin & Compliance** | Privileged platform/compliance users | Access control, approvals, evidence, fare governance, risk, audit, legal/policy records |
| **MaaleNex Business** | Corporate travel and approved business customers | Organization, travelers, travel policy, bookings, invoices, account reporting |
| **MaaleNex Intelligence** | Authorized business users | IROKA assistant, forecasts, alerts, explanations and governed workflow proposals |

Passenger bottom navigation target: **Home · Explore · Trips · Wallet · Account**. The map is a first-class Explore experience and may also open contextually from trip details. Settings, help and safety are always reachable without overcrowding the primary navigation.

The guest preview remains a safe public subset: verified informational content, demo map clearly labelled, About, Help, language, accessibility and privacy information. Protected account and operational workspaces require implemented server-side identity and authorization.

---

## 6. Financial architecture and accounting invariants

### 6.1 Domain boundary

Finance is a first-class bounded domain. It owns wallet eligibility, account/ledger records, payment intents, provider events, refunds, payouts, settlement and reconciliation. Booking owns trip/seat reservation and fare snapshots. Finance references booking/trip IDs; it does not own booking state. No domain directly edits another domain's records.

### 6.2 Proposed logical components

- **Wallet Account Registry:** account holder, legal basis/product type, currency, status, limits and provider relationship.
- **Chart of Accounts:** customer liability (only if legally applicable), driver/owner/operator payable, company revenue, provider clearing, fees/taxes, refunds, promotion liability and suspense.
- **Double-Entry Journal:** balanced debit/credit postings, immutable after posting, linked reversals.
- **Payment Orchestrator:** payment intent, provider adapter, signed event intake, idempotency and state transitions.
- **Reconciliation:** provider statements/events versus ledger, unmatched suspense, ageing and resolution.
- **Refund & Dispute:** case, reason, evidence, approval, original-source routing and provider outcome.
- **Payout & Settlement:** beneficiary verification, contractual allocation, maker-checker, batch, provider result and statement.
- **Finance Reporting:** statements, exports, period close and audit.

### 6.3 Required transaction lifecycle

`created → pending_provider → confirmed | failed | expired | reversed | disputed`

Provider redirect, client message, SMS or screenshot is never proof of settlement. Credit is posted only from authenticated provider evidence under the approved reconciliation policy. Duplicate and out-of-order callbacks must be safe. An idempotency key must bind to a stable request and payload hash.

### 6.4 Mandatory invariants

1. Every posted journal balances to zero by currency.
2. Posted journal entries are immutable; correction is a linked reversal or authorized adjustment.
3. No duplicate provider reference, payment intent or refund is processed twice.
4. No customer can spend funds that are pending, held or unavailable.
5. No payout exceeds the beneficiary's settled, eligible payable balance.
6. Driver/owner shares follow accepted versioned agreements and cannot cross beneficiary boundaries.
7. Every fee, tax, commission and deduction is itemized and traceable to an approved rule.
8. Daily reconciliation is required before settlement close; unexplained breaks remain in suspense.
9. Privileged adjustment and payout approval use separation of duties.
10. No production secrets, bank credentials, card PAN/CVV/PIN or real financial records in source control or synthetic test fixtures.

### 6.5 Provider and regulatory boundary

The earlier specification names Telebirr, CBE Birr and participating banks as candidate adapters, not selected/contracted providers. The expanded architecture may evaluate banks, licensed payment-system operators and other authorized providers, including interoperable payment rails, but no specific integration is assumed available. Before a real integration: verify current National Bank of Ethiopia requirements and provider licence/authorization, product permissions, API documentation, commercial agreement, settlement account/custody model, KYC/AML responsibilities, data-processing roles, security assessment, reconciliation files, refund/dispute process and incident SLAs.

No MaaleNex-issued stored-value product, payment instrument, deposit-taking, lending, savings, investment, crypto-token or payment-system operation is authorized by this amendment. The legal form of any “wallet” must be determined before implementation beyond a synthetic interface and non-custodial provider-payment reference experience.

### 6.6 ETB and multi-currency

ETB is the initial domestic accounting and display baseline. Monetary values use exact decimal/minor-unit rules defined by accounting and provider contracts; no binary floating-point arithmetic for ledger values. Multi-currency may be supported architecturally later, but foreign exchange, conversion spreads, settlement and regulatory permission require separate approval. No FX rate or fee is invented.

---

## 7. Live maps, tracking and location architecture

### 7.1 Architecture

- **Geography Catalog:** authoritative place IDs, jurisdiction hierarchy, terminals, stops, pickup/drop-off points and route corridors.
- **Map Provider Adapter:** tile, geocoding, routing and traffic interfaces, provider attribution, quotas and license terms.
- **Trip Location Service:** time-stamped, accuracy-labelled location events from an authorized driver/device source.
- **ETA/Route Engine:** estimates with source, confidence and last-update time.
- **Geofence Service:** service areas and operational boundaries.
- **Privacy & Retention Policy:** purpose-limited collection, access scope, retention and deletion.

### 7.2 Data quality and user presentation

Every location/route/ETA has provenance, timestamp, confidence/freshness and state: **verified**, **live**, **estimated**, **cached/stale**, or **demonstration**. Stale or missing data must be visible. Never show a moving vehicle icon as live unless an authenticated recent location feed exists. A route geometry is not proof that a transport service operates it.

### 7.3 Location permissions and privacy

- Ask permission contextually; explain purpose before requesting precise location.
- Provide manual origin/destination selection and graceful denial behavior.
- Collect driver location only during an authorized duty/trip window and under a reviewed lawful basis/notice.
- Share precise passenger pickup only with the assigned provider/driver and authorized support roles for the required period.
- Do not expose public live passenger location.
- Restrict location histories and support access; log sensitive reads.
- Define retention/deletion and incident response before live tracking.
- Protect against spoofing, replay, account sharing and false location events; treat GPS as evidence with uncertainty, not absolute truth.

### 7.4 Offline behavior

Cache public map/place metadata and last-known trip state where provider licences allow. Display last update time and stale warning. Offline actions may be queued only if idempotent and safe. No offline payment confirmation, ticket issuance or boarding authorization in the initial design; offline boarding remains excluded pending separate threat model and approval.

---

## 8. Call center, support and customer protection

### 8.1 Service model

One case-management system serves in-app help, web contact, telephone/IVR, email and approved messaging channels. The call-center console is a restricted workspace with role-based queues and a full case timeline. The platform must support human contact; AI is an assistive tool, not a barrier to human escalation.

### 8.2 Case lifecycle

`new → triaged → queued → assigned → in_progress → waiting_on_customer/partner → resolved → closed`

A customer may reopen or appeal within a defined policy. Safety, payment loss, privacy breach and account compromise receive priority routing. Every case has a case ID, category, severity, owner, timestamps, related booking/payment references, actions, resolution code and appeal state.

### 8.3 Channels and capabilities

- Public telephone number and staffed call-center routing once contracted and staffed.
- IVR language choice, callback request, queue position/estimated wait where reliable.
- In-app chat and asynchronous messaging.
- Email and provider-supported messaging integration.
- Agent desktop with customer verification, least-privilege trip/payment context and knowledge base.
- Supervisor queue, escalation, QA sampling and complaint analytics.
- Call recording/transcription only with lawful basis, notice/consent where required, restricted access and retention controls.
- Emergency and safety incident playbooks with human escalation and contact directory.

### 8.4 AI-assisted support

IROKA may classify, summarize, translate, retrieve approved knowledge and draft responses. Agents remain responsible for sending advice and resolving high-impact cases. AI must not autonomously deny refunds, close safety incidents, sanction users, change financial records or disclose restricted data. AI-generated content must be distinguishable to the agent, source-grounded and logged according to approved retention rules.

### 8.5 Service metrics

Define and report: first response time, resolution time, first-contact resolution, reopened cases, escalation rate, customer satisfaction, complaint category, unresolved age, safety incident acknowledgement time and quality-review findings. Targets and staffed coverage are UNRESOLVED until an operating model is approved; do not claim 24/7 support without evidence.

---

## 9. Feedback, ratings, reputation and safety

- Post-trip passenger rating and structured feedback.
- Driver/operator feedback about trip readiness and passenger conduct, subject to policy.
- Verified-trip review eligibility; clearly label unverified general feedback.
- Moderation for harassment, personal data, threats, spam and manipulation.
- Right of reply, appeal and correction process.
- No automatic driver deactivation solely on a rating threshold without human review and due process.
- Safety incident reporting, lost property, accessibility complaints and service-disruption feedback.
- Feedback analytics by route/operator/service with minimum aggregation thresholds to avoid identifying individuals.
- No public exposure of sensitive case narratives or passenger travel history.

---

## 10. IROKA integration governance

IROKA is a separate intelligence system/project. MaaleNex integrates through a versioned API or approved adapter with scoped service identity, explicit data contract, purpose limitation, rate limits, audit and revocation.

### 10.1 Approved candidate use cases

- Passenger conversational assistant and journey discovery explanations.
- Amharic-first help and reviewed language assistance.
- Search and itinerary comparison using verified current catalogue data.
- Customer-care classification, summarization and response drafting.
- Demand forecasting and operator capacity analysis.
- Fraud/anomaly signals for human investigation.
- Authorized business analytics copilot.
- Operational recommendations and bounded workflow proposals.

### 10.2 Prohibited autonomous actions

IROKA may not independently:
- transfer, hold, release or refund money;
- change ledger entries, beneficiaries, bank details or settlement instructions;
- publish fares, alter accepted quotes or apply hidden dynamic pricing;
- approve operator/driver identity, licences or legal eligibility;
- dispatch a driver or override a human safety decision;
- close high-impact support/safety/privacy cases;
- suspend or permanently sanction an account;
- grant itself or a user additional permissions.

### 10.3 AI governance and acceptance

- Data minimization and explicit permitted fields per use case.
- No training on identifiable passenger, financial, voice or location data without separate lawful basis and approval.
- Prompt/model version, input provenance, output, confidence/uncertainty and human decision trace for high-impact assistance.
- Evaluation sets for Amharic, English and qualified Maale content; human language review.
- Prompt injection, data exfiltration, hallucination, unsafe recommendation and cross-tenant retrieval tests.
- Human override, disable switch, provider outage fallback and incident process.
- Model changes require evaluation and controlled release.
- AI outputs are suggestions unless a separately approved low-risk automation policy permits a bounded action.

---

## 11. Proposed business model and commercial controls

The original Passenger MVP baseline assumed **no platform revenue** for the initial pilot. This amendment introduces options for future Owner consideration; it does not approve any fee, commission or commercial term.

| Revenue model candidate | Potential payer / basis | Conditions before adoption |
|---|---|---|
| Per-booking platform fee or disclosed commission | Passenger and/or operator under agreed terms | Legal/consumer review, transparent display, operator contract and unit economics |
| Operator SaaS subscription | Transport operator | Demonstrated value, service levels, tier definitions and contract |
| Fleet/dispatch/analytics subscription | Fleet or corporate operator | Tenant isolation, support commitments and measurable ROI |
| Corporate mobility contracts | Employer/business | Contract billing, duty of care, invoicing and privacy controls |
| Reservation/ticketing service fee | Contractually designated party | No hidden charge; lawful tariff/consumer review |
| Permitted payment integration revenue | Licensed PSP/bank arrangement | Regulatory permission, partner contract and clear disclosure |
| Authorized agent network commissions | Licensed/authorized partner | Agency authorization, cash controls, reconciliation and fraud prevention |
| Optional premium travel/support services | Passenger or business | Must not degrade basic safety or access; clear opt-in and pricing |
| Clearly labelled advertising/sponsorship | Advertiser/partner | Privacy-respecting targeting, moderation and no influence on fare/AI answers |

### 11.1 Unit economics and governance

Before choosing a model, prepare route/service-level contribution margin, customer acquisition cost, retention, booking conversion, support cost, payment/provider cost, refunds/fraud loss, operator acquisition cost, infrastructure/map/AI cost and working-capital/settlement exposure. Define gross merchandise value separately from recognized revenue and pass-through funds. Never count wallet balances or operator payable as company revenue.

No fee, rate, commission, subscription price, agent commission, settlement period or revenue share is fixed by this amendment. Every commercial rule requires explicit Owner approval, partner agreement, legal review and versioned publication.

---

## 12. Benchmarking and product differentiation

The product may study established mobility, marketplace, ticketing, digital-wallet and contact-center systems for design patterns. This is a **capability benchmark**, not an endorsement, copying instruction or claim that competitors' features are available to MaaleNex.

Adopt proven patterns where they improve user outcomes:
- friction-reduced search and booking;
- transparent price breakdown and quote expiry;
- reliable live-trip status with freshness labels;
- verified trip-linked reviews;
- multiple payment rails and visible transaction state;
- fast refund/dispute initiation;
- human support escalation and unified case history;
- operator tools and performance reporting;
- offline-aware information access and accessible design.

Explicitly avoid common failure modes:
- hidden or unpredictable fees;
- opaque fare/dispatch decisions;
- false live-map indicators;
- support loops that block a human;
- untraceable payment/refund states;
- weak driver/operator accountability;
- over-collection of identity/location data;
- AI decisions without explanation, appeal or human control;
- monolithic navigation overloaded with every role and function.

The differentiation target is local trust, financial traceability, multilingual usability, reliable low-connectivity behavior, open integration boundaries and accountable AI—not feature count alone.

---

## 13. Architecture and data-domain boundaries

### 13.1 Architecture decision carried forward

Retain the accepted **modular monolith** as the default until measured load, reliability or independent scaling needs justify service extraction. One backend application, API layer and PostgreSQL database may host strongly bounded domains. No microservices, broker, distributed cache or new infrastructure is justified by aspiration alone.

### 13.2 Proposed domain ownership

| Domain | Owns | Explicit boundary |
|---|---|---|
| Identity & Access | Identity, authentication, sessions, permissions, MFA | Does not own bookings, wallet or trip rules |
| Organizations & Verification | Organization, membership, evidence, approval | Does not own tenant data of another organization |
| Geography & Catalog | Places, terminals, stops, routes, jurisdiction references | Does not claim a route is operational without publication evidence |
| Fleet & Driver | Vehicles, capacity, driver qualification, assignments | Does not own booking or ledger |
| Schedule & Dispatch | Schedules, trip instances, assignment and trip operations | Does not own customer money |
| Booking & Ticketing | Quotes, holds, reservations, tickets, boarding reference | Does not assert payment settlement |
| Fare Governance | Rules, authority evidence, versioned quote calculation | Does not invent legal tariff |
| Location & Maps | Provider adapters, location events, ETA, geofence | Does not expose unauthorized location |
| Finance | Wallet eligibility, ledger, payment, refund, payout, reconciliation | Does not mutate booking state |
| Loyalty | Promotional points, campaigns, referral | Never merges points with cash ledger |
| Support & Feedback | Cases, conversations, ratings, appeals | Does not directly post financial adjustments |
| Notifications | Preferences, templates, delivery attempts | Does not own source-of-truth business state |
| Documents & Agreements | Versioned terms, acceptance, evidence references | Does not make legal approval decisions |
| Analytics & Reporting | Aggregated metrics, exports and reports | Must enforce row/tenant scope and privacy thresholds |
| AI Gateway / IROKA Adapter | Governed model/API calls and evaluation metadata | No direct unrestricted DB or privileged action |
| Audit & Compliance | Append-only security/business audit events | Not a dumping ground for sensitive payloads |

### 13.3 Cross-domain rules

- Reuse existing identity, organization, geography, booking, fares, fleet, support and audit components after A2 inventory; do not duplicate them.
- Domain-owned services and repositories; explicit application interfaces/events for collaboration.
- PostgreSQL remains source of truth for financial journals, bookings, inventory, approvals and audit.
- All important state transitions are server-side, transactional, idempotent and auditable.
- API contracts are versioned; provider adapters are replaceable.
- Separate public, passenger, driver, operator, terminal, finance, support and administrative authorization scopes.
- Preserve data classification and synthetic-only development restrictions.

---

## 14. Localization, accessibility, privacy and resilience

### Localization
- Amharic-first, English, and qualified Maale-language experience.
- Ethiopian Calendar default; Gregorian preference; correct date/time-zone conversion.
- ETB formatting and localized numbers with explicit currency.
- Translation glossary and human review for safety, financial and legal text.
- Avoid machine-only legal or fare translation.

### Accessibility
- Target WCAG 2.2 AA for web/PWA and equivalent Android accessibility practices.
- Semantic landmarks, heading order, labels, focus visibility, keyboard operation, screen-reader announcements, contrast, scalable text, touch target sizing and reduced motion.
- Test on narrow Android screens, large display/font settings, rotation and low-end devices.
- TalkBack/assistive-technology testing is a required release gate unless the Owner explicitly defers a specific test; a deferral must be recorded as a residual limitation, not a pass.

### Privacy and security
- Map every personal, identity, financial, voice, device and location data flow.
- Establish lawful basis, purpose, minimization, retention, deletion, data-subject access and processor contracts.
- MFA for privileged and high-risk financial actions; step-up authentication for beneficiary changes and cash-out.
- Encryption in transit/at rest, secrets management, least privilege, secure sessions, rate limits, fraud controls and security monitoring.
- Tenant/organization isolation, object-level authorization and negative tests.
- Incident response, breach notification assessment, backup/restore and disaster recovery.
- No sensitive production data or secrets in Git, CI artifacts or public logs.

### Resilience
- Low-bandwidth mobile-first operation, bounded retries and visible stale/offline state.
- Safe retry/idempotency for bookings and payments.
- Provider outage fallback and circuit-breaking at adapter boundaries.
- No false confirmation when a provider, map or notification service is unavailable.
- Define service objectives only after load, partner and operating evidence exists.

---

## 15. Legal, regulatory and operational dependency register

This section records dependencies, not legal conclusions. Qualified Ethiopian counsel and competent authorities must verify current instruments and applicability.

| ID | Dependency | Current status | Required evidence / exit condition |
|---|---|---|---|
| LEG-001 | Road transport service classification, operator/vehicle/driver permissions | UNRESOLVED | Current federal and regional rules and competent authority determination |
| LEG-002 | Passenger service and intercity route authority | UNRESOLVED | Documentary operator and route authority |
| LEG-003 | Jinka terminal and boarding permissions | UNRESOLVED | Written terminal/competent-party confirmation |
| LEG-004 | Motorcycle passenger-service rules | UNRESOLVED | Service-specific legal determination before that mode |
| LEG-005 | Freight/heavy-load operator and cargo rules | UNRESOLVED | Separate legal/insurance assessment |
| LEG-006 | Fare-setting authority and tariff values | UNRESOLVED | Authoritative tariff/order for each jurisdiction/corridor |
| LEG-007 | Payment-system, issuer, PSP and wallet legal model | UNRESOLVED | NBE/counsel determination and licensed partner contracts |
| LEG-008 | KYC/AML, sanctions, fraud and recordkeeping allocation | UNRESOLVED | Provider/legal responsibility matrix and controls |
| LEG-009 | Personal data protection, precise location and call recording | UNRESOLVED | Privacy impact assessment, notices, lawful basis and retention |
| LEG-010 | Insurance, passenger liability and incident response | UNRESOLVED | Applicable insurance coverage and operational protocol |
| LEG-011 | Tax, withholding, invoicing and revenue recognition | UNRESOLVED | Qualified tax/accounting advice and documented policy |
| LEG-012 | Consumer rights, cancellation/refund and dispute resolution | UNRESOLVED | Approved policy and enforceable terms |
| LEG-013 | Call-center staffing, number, languages and service hours | UNRESOLVED | Named owner, provider, staffing and SLA |
| LEG-014 | Map tile/geocoding/routing/traffic licensing | UNRESOLVED | Provider terms, attribution, data-use and cost assessment |
| LEG-015 | IROKA data-sharing and AI governance | UNRESOLVED | API contract, purpose, data boundary, security and evaluation |
| LEG-016 | Operator cohort, schedules, fleet and pilot scope | UNRESOLVED | Verified candidate evidence and explicit activation decision |

Reference instruments already identified in the retained Pay/Mobility/Fare specification include Road Transport Proclamation No. 1274/2022, Personal Data Protection Proclamation No. 1321/2024 and National Bank of Ethiopia payment-system directives including the ONPS/10/2025 amendment. Their current text, implementing rules and application to each product flow must be checked before relying on them. Regional, zone, woreda and local instruments must also be obtained. This amendment does not certify licensing or compliance.

---

## 16. Delivery plan and stage gates

| Gate | Scope | Required deliverables | Exit condition |
|---|---|---|---|
| **A1-A — Expanded scope amendment** | This document and full feature register | Source reconciliation, product/domain scope, unresolved decision register, acceptance criteria | Explicit Owner approval of exact document version/commit |
| **A2 — Read-only architecture reconciliation** | Inspect current main, PR #25, historical approved specs, code, schema, APIs, tests, workflows and dependencies | Feature-to-code matrix; reuse/gap map; duplicate-domain analysis; architecture/security/legal dependency review; cost/provider options | Owner-reviewed A2 report; no code/schema/workflow changes |
| **A3 — Controlled implementation** | Only approved backlog and architecture | Incremental UI/API/domain implementation; synthetic fixtures; provider sandbox adapters only when approved | Exact-head tests, reviews and documented evidence |
| **A4 — Verification and acceptance** | Security, accounting, privacy, operations, accessibility and user experience | Independent review, ledger invariants, provider simulations, map data quality, support operations, device tests | All critical blockers resolved; Owner accepts residuals |
| **A5 — Deployment / activation** | Production environment and real-world operations | Legal/partner approvals, credentials, monitoring, support staffing, rollback, financial controls and launch plan | Separate explicit written Owner authorization |

A2 is read-only. Do not modify main or PR #25 during A2. A3 must use a new feature branch and only the scope accepted by the Owner. A5 is always separate.

### 16.1 Proposed workstream sequence after A1/A2

1. Product shell, navigation, design system, localization and accessibility.
2. Shared identity/authorization, organization, geography, audit and notification foundations.
3. Passenger journey discovery, verified catalog, booking and ticketing.
4. Maps, route visualization, authorized location and trip tracking.
5. Finance ledger and provider-neutral sandbox payment orchestration.
6. Refund, reconciliation, settlement and financial reporting.
7. Support, call center, complaints, feedback and safety.
8. Driver/operator/terminal workspaces and dispatch.
9. IROKA gateway, assistant and governed analytics.
10. Loyalty/referrals, corporate business services and later freight modules.
11. Consolidated security, privacy, operational readiness and independent verification.

This is a dependency-aware proposed sequence, not an authorization to execute it.

---

## 17. Consolidated acceptance criteria

All acceptance below is synthetic or sandbox-only until A5. A test must assert both allowed and denied behavior.

### 17.1 Product and UX
- Every application suite has a defined role, navigation map, responsive layouts and empty/loading/error/offline states.
- Passenger app provides Home, Explore/Map, Trips, Wallet, Help and Account/Settings entry points.
- About, service information, privacy, terms, contact and support are reachable from guest preview.
- Login/registration screens do not collect real credentials until secure backend authentication and policy are approved.
- Amharic/English are complete for critical flows; Maale content is not claimed complete without qualified review.
- Date, calendar, currency and number formatting are consistent.
- Keyboard/focus, screen reader, scalable text, contrast and narrow-layout evidence is recorded.

### 17.2 Mobility and maps
- Only verified, approved routes, stops, operators, schedules, vehicles, fares and trips can be published.
- Search and route details expose source and freshness where applicable.
- Booking, seat holds, ticketing and boarding enforce server-side state and authorization.
- Concurrent booking cannot double-allocate seats; expiry releases inventory once.
- Live map only shows live assets from an authenticated, authorized, sufficiently fresh source.
- Stale, estimated, cached and demonstration information is visually distinguishable.
- Location permissions can be denied/revoked without blocking manual journey planning.
- Precise location is not publicly exposed and is retained only under approved policy.
- Map provider failure produces an honest degraded state, not fabricated ETA or availability.

### 17.3 Finance
- Every posted journal balances; all reversals link to original transactions.
- Duplicate, replayed, forged, delayed and out-of-order provider callbacks cannot double-credit or double-debit.
- No browser redirect, screenshot or client claim can mark payment successful.
- Available, pending, held and withdrawable balances reconcile to ledger.
- Refunds, fees, taxes, commissions and beneficiary allocations are itemized and reproducible.
- Driver/owner/operator settlement follows accepted agreements and beneficiary authorization.
- Maker-checker and audit controls prevent one actor from changing beneficiary and approving payout.
- Daily reconciliation detects missing, duplicate and mismatched provider records.
- Exports preserve role/tenant boundaries, mask sensitive data, expire securely and are audited.
- No real funds or production credentials are used in development/CI.

### 17.4 Call center and feedback
- Every channel creates or updates a single case identity and timeline.
- Case routing, assignment, escalation, SLA breach, reopen and appeal are testable.
- Safety, fraud, payment and privacy cases require designated human handling.
- Call recording/transcription respects approved notice, consent, access and retention.
- AI support suggestions are reviewable; agents can override; no AI-only high-impact closure.
- Ratings are linked to eligible trips; abuse, retaliation and appeal paths are tested.
- Service metrics have definitions, time windows, exclusions and privacy-safe aggregation.

### 17.5 IROKA
- All calls use scoped service identity and versioned contracts.
- IROKA cannot read unrestricted production data or bypass tenant/role permissions.
- AI outputs disclose uncertainty and provenance for journey/business recommendations.
- Prompt injection, data exfiltration, hallucination, unsafe action and cross-tenant retrieval tests pass.
- Human approval is required for high-impact finance, fare, identity, safety and dispatch actions.
- Disable switch, outage fallback, audit and model-version evaluation are verified.

### 17.6 Business and governance
- Each revenue stream has a named payer, value proposition, price basis, cost model, disclosure and legal/contractual dependency.
- GMV, company revenue, customer funds and operator payables are not conflated.
- No commission/fee is enabled without explicit approval and versioned terms.
- Operator onboarding and publication require complete evidence and separation of duties.
- Freight and additional transport modes cannot be exposed before their own scope and activation gates.
- Production readiness is not inferred from CI, a successful demo or an A1 approval.

### 17.7 Cross-cutting release blockers
No unresolved critical security, privacy, accounting, regulatory, safety, accessibility or data-integrity defect may be waived implicitly. Any accepted residual must identify severity, affected users/data, compensating controls, expiry/review date and explicit Owner acceptance.

---

## 18. Unresolved Owner and evidence decisions

These decisions are deliberately not guessed in this amendment:

| ID | Decision required | Proposed default for planning | Status |
|---|---|---|---|
| DEC-001 | Product name and brand | MaaleNex; retain established identity | EXISTING DIRECTION; confirm unchanged |
| DEC-002 | Initial market | Jinka-first, Ethiopia | EXISTING DIRECTION |
| DEC-003 | First commercial service | Passenger mobility; scheduled/intercity and verified local services need product prioritization | OWNER DECISION REQUIRED |
| DEC-004 | Initial transport modes | Passenger modes only after legal classification; motorcycle passenger mode not presumed | UNRESOLVED |
| DEC-005 | Initial operator cohort and terminal | Small verified cohort; Jinka terminal-first | UNRESOLVED |
| DEC-006 | Map/routing/GPS providers | Provider-neutral adapters; compare cost, coverage, offline rights and licensing | UNRESOLVED |
| DEC-007 | Wallet legal form and custody model | Licensed partner/bank-led; no independent stored-value issuance assumed | LEGAL / OWNER DECISION |
| DEC-008 | Payment provider selection | None selected; perform due diligence | UNRESOLVED |
| DEC-009 | Fees, commissions and subscriptions | No fees assumed; evaluate options and unit economics | OWNER DECISION REQUIRED |
| DEC-010 | Fare authority and actual tariffs | Only documented competent-authority rules | UNRESOLVED |
| DEC-011 | Call-center channel, staffing and hours | Human escalation available in approved operating hours; no 24/7 claim | UNRESOLVED |
| DEC-012 | IROKA integration contract and data scope | Separate authenticated API; minimal permitted data | UNRESOLVED |
| DEC-013 | Localization priority and Maale language review | Amharic-first, English, qualified Maale | OWNER / LANGUAGE REVIEW |
| DEC-014 | Freight launch phase | Separate later A1/A2 and commercial gate | DEFERRED |
| DEC-015 | Corporate mobility and agent network | Future business domains subject to contracts and licensing | DEFERRED |
| DEC-016 | Production hosting, data residency, RTO/RPO and operating budget | No production choice assumed | UNRESOLVED |

---

## 19. Explicit exclusions and authorization boundaries

This amendment does **not** authorize:

- code, schema, migration, API, UI, workflow or infrastructure implementation;
- changes to `main`, PR #25, its branch, its title/body, reviews or merge state;
- merge, release, deployment, production secrets or live service activation;
- collection of real passenger, driver, operator, identity, voice, financial or precise location data;
- live bookings, ticket issuance, boarding, dispatch or transport operations;
- wallet issuance, custody, deposit-taking, lending, cash-in/cash-out or real-money payment;
- selection or activation of any payment, bank, map, telephony, SMS, email or AI provider;
- operator, driver, terminal, government or commercial partner engagement;
- publication of real routes, schedules, fares, service coverage or availability;
- IROKA autonomy over financial, identity, fare, dispatch or safety-critical actions;
- freight, heavy-load or new transport-mode activation;
- any statement that MaaleNex is licensed, insured, approved, partnered or production-ready without documentary evidence.

Synthetic UI prototypes, architecture documentation and test adapters may be proposed in later gates; they are not implied authorization in this A1 document.

## 20. A1 amendment disposition and next action

**Prepared disposition:** SUBMITTED FOR OWNER REVIEW — NOT APPROVED / NOT FROZEN.

Required next action:
1. Owner reviews this amendment and its decision register.
2. Owner either approves this exact version/commit, requests named revisions, or rejects the amendment.
3. If approved, record the approval, accepted SHA, scope supersession and A1 closure/freeze in a separate governance record.
4. Only then prepare A2 read-only repository-wide reconciliation against the accepted feature register.
5. No A3 implementation begins until A2 is complete and separately authorized.

**Progress status:** A1 amendment artifact prepared; approval pending. A2 not started. A3 expanded implementation not authorized. A4 remains limited to the earlier guest-preview scope. A5 not started.

**Owner authority remains controlling.**
