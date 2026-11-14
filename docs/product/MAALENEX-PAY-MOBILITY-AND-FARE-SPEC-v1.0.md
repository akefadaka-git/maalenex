# MaaleNex Pay, Mobility, Fare Governance and Legal Framework — Product Specification v1.0

**Status:** Owner-requested scope expansion; design baseline draft.  
**Environment:** Synthetic-only development.  
**Currency:** Ethiopian Birr (ETB) for the initial domestic product.  
**Geographic model:** Maale; South Omo Zone (Dimeka); Ari Zone (Jinka).  
**Implementation boundary:** This document specifies product behavior and controls. It does not authorize real-money processing, production personal-data processing, live dispatch, deployment, or launch.

## 1. Product objectives

Expand MaaleNex from a ride-planner prototype into a governed mobility and transport platform with passenger booking, cancellation, completion, feedback and referrals; motorcycle and other approved passenger transport; heavy-load/cargo journeys and fleet operations; wallet top-up, payment, refunds, driver/owner earnings, settlement and cash-out workflows; digital and optional physical loyalty card; transaction history, receipts and exports; configurable jurisdiction-aware fares; documented agreements, legal disclosures, dispute handling and auditability.

The platform remains a modular monolith until measured scale justifies service separation. Inspect existing domains and APIs before implementation; do not create duplicate booking, finance, identity or geography domains.

## 2. Accounts, roles and financial entitlements

| Role | Wallet and transaction capabilities | Mobility capabilities |
|---|---|---|
| Guest | Public fare estimator only; no stored value by default | Browse public services |
| Passenger | Top up own eligible wallet through an enabled provider; pay fares; view own balance, receipts and transactions; request eligible refunds | Book, view, cancel, complete, rate, report rides and refer friends |
| Motorcycle driver | View own earnings, pending/available balance, deductions and settlement history; request cash-out to verified account | Availability, trip acceptance, pickup, trip status, safety and incident reporting |
| Heavy-load driver | Same driver ledger capabilities; cargo-specific earnings and deductions | Load offers, capacity, delivery milestones and proof of delivery |
| Vehicle owner | View only earnings attributable to owned/registered vehicles; settlement according to recorded owner-driver/fleet agreement; eligible cash-out | Vehicle compliance, assignment and vehicle-level performance |
| Fleet / transport operator | Organization-scoped financial statements, reconciliation and approved settlement instructions | Fleet, drivers, vehicles, assignments and compliance |
| Administrator / finance operator | Least-privilege, dual-controlled adjustments and reconciliation; no unrestricted ledger editing | Role-scoped operations, support, fare administration and reports |
| Auditor / regulator liaison | Read-only, purpose-limited, logged access to authorized records | Compliance evidence and approved reports |

Public registration must never create administrator, finance-approver or auditor accounts. Privileged roles are separately provisioned, MFA-protected and audited. A user may hold multiple permitted roles, but active role, organization context and permissions must be explicit. Financial records are partitioned by legal account owner and organization.

## 3. Wallet, deposit and payment experience

### 3.1 Deposit / top-up

- A registered customer can initiate a top-up to their own eligible wallet using an enabled provider method.
- Support provider adapters for Telebirr, CBE Birr and participating banks only after commercial agreement, provider API approval, security review and required regulatory authorization.
- A payer may fund another account only through an explicit verified gift/top-up flow that identifies payer, recipient, consent, limits, source reference and refund destination. Never credit an arbitrary account from an unverified screenshot or free-text reference.
- Walk-in/agent cash-in is future scope only where a licensed/authorized provider and approved agent arrangement support it.
- Guest users do not receive an anonymous stored-value account by default. A guest may use provider-hosted payment for a specific booking only if legally approved and not an unregulated wallet.
- Show amount, fees, recipient, provider, processing state and refund terms before confirmation.
- Credit only after authenticated provider confirmation and reconciliation; client redirect or screenshot is not proof of payment.
- Use idempotency keys, signed callbacks/webhooks, replay protection, provider-reference uniqueness and duplicate-event handling.
- Pending, successful, failed, expired, reversed and disputed states must be visible.

### 3.2 Wallet balance and ledger

- Show available, pending, reserved/held and withdrawable balances separately.
- Maintain an immutable, append-only, double-entry ledger. Never edit/delete posted entries; corrections use linked reversals/adjustments with reason, actor, approval and audit event.
- Each entry has unique transaction ID, timestamp, ETB amount, debit/credit account, type, state, counterparty, booking/service reference, provider reference, fee, tax treatment, idempotency key and audit correlation ID.
- Enforce non-negative available balance unless an explicitly approved credit product exists; no overdraft/lending is implied.
- Reconcile provider settlement files and callbacks against internal ledger daily and on demand. Unmatched items enter suspense; no silent auto-credit.
- Distinguish customer funds, company revenue, driver payable, owner payable, provider fees, taxes, refunds, promotions and loyalty liabilities in the chart of accounts.
- Display platform commission, provider fees and taxes separately.

### 3.3 Payments and refunds

- Payment options: wallet, approved external provider, and cash where the service and local rules allow.
- Support split allocations only when disclosed and contractually agreed: driver share, owner share, fleet share, platform commission, taxes/fees and authorized deductions.
- Refund to original funding source where provider rules and law require; otherwise show a legally approved alternative. Prevent duplicate refunds and refunds to unverified third parties.
- Disputes, chargebacks, partial refunds, cancellation refunds and manual adjustments require case IDs, evidence, reason codes and approvals.
- No real-money functionality in the current development environment.

## 4. Driver and vehicle-owner finance

Driver and owner dashboards show gross completed-service earnings; platform commission and disclosed deductions; provider/payment fees and legally applicable tax withholding; refunds, reversals, adjustments and dispute holds; pending, available and withdrawable balance; cash-out request status, masked destination, fees and expected settlement window; full transaction history and downloadable statements.

### Cash-out controls

- Only a verified driver, owner or authorized organization beneficiary may request settlement to an account verified as belonging to that beneficiary or otherwise legally authorized.
- Driver and owner shares follow an explicit, versioned agreement accepted by relevant parties before the first paid service.
- An owner cannot withdraw a driver's personal share, and a driver cannot withdraw the owner's share, unless a valid mandate/contract and permission authorize it.
- Apply risk-based holds for disputed trips, refunds, suspected fraud, failed KYC or provider reconciliation breaks. Show reason, review path and appeal route.
- Use maker-checker approval for privileged manual payouts and exceptional adjustments. Do not allow an admin to alter beneficiary details and approve payout in one action.
- Cash-out limits, fees and settlement SLAs are configuration items sourced from provider contracts, law and risk approval; do not hardcode invented limits.

## 5. Loyalty card, rewards and referrals

### Loyalty account and card

- Every eligible account can have a digital loyalty identity; optional physical card may use QR/barcode or a provider-supported secure credential.
- Do not store payment card PAN, CVV, PIN or provider credentials in the loyalty profile.
- Loyalty points are a separate promotional ledger, not ETB, not a deposit, not a bank account and not withdrawable cash by default.
- Define earning rules by service, completed/paid state, campaign, location, customer segment and effective date.
- Define redemption catalogue, points required, caps, expiry, exclusions, reversals and refund treatment in advance.
- Refunded/cancelled qualifying transactions reverse associated unvested points. Prevent points on fraudulent, self-referral, duplicate or reversed activity.
- Show points earned, pending, available, redeemed, expired and reversed with auditable history.

### Referrals

- Give each eligible account a referral code/link and consent-aware share action.
- Reward only after the referred user passes eligibility controls and completes a qualifying paid service; disclose reward, cap, expiry and exclusions.
- Block self-referrals, account farms, circular referrals, duplicate identities and suspicious patterns; provide human review and appeal.
- Do not upload a user's address book/contact list without separate, specific consent.

## 6. Passenger booking lifecycle

Use explicit server-validated states: Draft quote → Fare quote issued (versioned/expiry) → Booking requested → Driver assignment pending → Driver accepted/rejected/timeout → Driver en route → Driver arrived → Passenger onboard/service started → Completed; alternate terminal states include Cancelled, No-show and Disputed.

### Booking

- Select service type, pickup, destination, passengers/cargo attributes, supported accessibility needs, preferred payment method and optional notes.
- Before confirmation, show pickup/destination, assigned provider/driver/vehicle details when available, fare estimate, minimum fare, distance/time assumptions, fees, cancellation rules and quote expiry.
- Confirm only after passenger explicitly accepts quote and terms.
- Do not expose precise passenger location before assignment; share only necessary trip location with assigned driver.

### Cancellation

- Allow passenger cancellation before and during service where operationally possible.
- Apply cancellation fee only if permitted by approved local fare/consumer rules and disclosed before booking; display reason and exact amount.
- Define separate cases for passenger cancellation, driver cancellation, driver no-show, passenger no-show, unsafe conditions, route/service interruption and force majeure.
- Refunds and driver compensation follow published, versioned policy; never silently charge.
- Provide dispute/appeal flow and evidence timeline.

### Completion, rating and safety

- Driver and passenger each confirm completion; support timeout and dispute fallback.
- Capture passenger rating, structured tags and optional text after completion. Prevent retaliation/rating manipulation; moderate abusive content and allow appeals.
- Provide incident report, emergency information, lost-item, complaint and support flows.
- Driver rating must not be the sole basis for automatic deactivation; provide transparent review and appeal.
- Referral rewards are evaluated only after settlement/eligibility checks.

## 7. Woreda / zone fare governance

### 7.1 Fare rule dimensions

A fare rule is scoped by authoritative jurisdiction type/code (region, zone, woreda, town administration or other competent authority); origin/destination and route/corridor; service type (motorcycle passenger, other passenger vehicle, heavy-load/cargo, scheduled transfer); vehicle class/capacity and operating conditions; effective dates and publication/approval status; ETB currency and rounding rule; approving authority, instrument/reference, evidence document and version.

### 7.2 Fare calculation model

The engine supports this model without assuming any rate:

    quoted_fare = max(approved_minimum_charge,
                      base_charge + billable_distance_km * approved_per_km_rate
                      + approved_time_charge + approved_accessorials)

Then separately calculate approved booking/platform fee, provider fee, tax and discount. Passenger sees full payable total and itemized breakdown. A discount cannot reduce a legally mandated minimum unless the authority expressly permits it.

- Minimum charge and per-kilometre rate are separate fields.
- Support distance bands, waiting time, night/holiday rates, remote-area/access surcharge, return/empty-leg charge, cargo weight/volume, loading/unloading and tolls only where explicitly approved and disclosed.
- Prevent double-charging the same distance/time component.
- Fare quote is immutable once accepted; changes require a new quote and passenger consent, except a narrowly defined lawful adjustment with evidence and appeal.
- Keep old rule versions for historical recalculation and disputes.

### 7.3 Multi-jurisdiction trips

- Identify the competent authority for each fare corridor; do not assume a zone/woreda can set another jurisdiction's tariff.
- For cross-boundary journeys, apply a published corridor tariff or documented rule approved by competent authorities. If no valid rule exists, do not invent a rate: mark fixed-price booking unavailable or require a lawful negotiated quote before acceptance.
- Store source jurisdictions, selected tariff IDs, calculation trace and effective date.
- Display applicable jurisdiction/rule source in fare detail and receipt.

### 7.4 Administration and publication

- Admin fare editor supports draft, review, approval, scheduled publication, suspension and expiry.
- Separation of duties: author cannot approve own tariff; require at least two authorized approvers for publication.
- Store official order, tariff schedule, approval record, authority identity, issue/effective dates and supersession relationship.
- Public fare table in Amharic and English; offline cached copies show version and last-updated date.
- Notify affected drivers, owners and passengers when rates change. Never retroactively alter accepted bookings.

**No ETB minimum charge or per-kilometre rate is set by this specification.** Rates remain UNRESOLVED until competent authorities and applicable agreements provide authoritative values.

## 8. Transaction history and exports

Provide filters for date range, status, transaction type, service, provider, account, vehicle and reference ID, subject to role scope.

Required formats:
- **PDF:** printable statement/receipt with logo, account holder, period, ETB totals, opening/closing balances, line items, fees, references, generated timestamp and verification code.
- **XLSX:** structured workbook with transaction sheet, summary, filters, typed numeric/date cells and data dictionary.
- **CSV:** interoperable transactions with UTF-8 encoding and stable column names.
- **JSON:** versioned export representation for integrations and portability.
- **PNG/JPEG:** individual receipt image or shareable proof, not entire sensitive ledger by default.
- **Print/share:** native print and OS share-sheet support where available.

Export controls: same authorization and tenant/account filters as on-screen data; mask sensitive identifiers; exclude secrets, PINs, full bank/card numbers and unnecessary personal data; audit actor, scope, format, timestamp and purpose; use expiring download links; queue large exports; include tamper-evident verification reference. Do not describe an ordinary PDF/image as cryptographic proof unless signed and verifiable.

## 9. Legal, agreement and compliance document set

These are required templates/workflows, not final legal advice or government approvals.

| Document | Parties | Key provisions |
|---|---|---|
| Passenger Terms of Service | Passenger ↔ MaaleNex | Booking, fare quote, cancellation/no-show, payment, refunds, safety, complaints, liability subject to law, ratings, referrals, privacy and dispute process |
| Driver Service Agreement | Driver ↔ MaaleNex / relevant operator | Eligibility, licences, conduct, safety, service acceptance, fares, commission, deductions, earnings, cash-out, insurance, taxes, suspension, appeal and data use |
| Vehicle Owner Agreement | Owner ↔ MaaleNex / fleet / driver as applicable | Vehicle authority, compliance, driver authorization, revenue split, maintenance, insurance, liability, settlement, disputes and termination |
| Fleet / Operator Agreement | Fleet/operator ↔ MaaleNex | Fleet authority, sub-users, service levels, compliance, payment allocation, audit, data roles, liability and termination |
| Payment Provider Agreement | MaaleNex ↔ licensed PSP/bank | Licensing, permitted services, settlement, fees, reconciliation, callbacks, security, fraud, disputes, refunds, data processing, incident notification and exit |
| Data Processing / Sharing Agreement | MaaleNex ↔ processors / authorized partners | Controller/processor roles, purpose, legal basis, minimization, retention, security, subprocessors, cross-border transfer and rights |
| Government / Authority MoU | MaaleNex ↔ competent government body | Legal mandate, scope, approved data, public-interest purpose, fare approval, inspection, reporting, confidentiality, security, retention, audit, liability and termination |
| Loyalty Programme Terms | Member ↔ MaaleNex | Points are promotional, earning/redemption, expiry, reversals, fraud, limits, changes and complaints |
| Privacy Notice & Consent Records | MaaleNex ↔ each data subject | Data categories, purpose, lawful basis, sharing, retention, rights, location processing, marketing choice and contact |
| Cancellation / Refund Policy | Passenger, driver, owner and company | Scenario matrix, fees, compensation, refund route, timeframes, evidence and appeal |

Each accepted document has language, version, effective date, parties, acceptance timestamp, consent method, document hash, withdrawal/supersession record and exact version accepted. Provide Amharic and English; legal translations require review.

### Government relationship boundaries

A government office is not automatically a contracting party or data recipient. Obtain written authority and a defined legal basis before sharing personal, financial or location data. Share only minimum information for a lawful documented purpose. Fare approval or operating licence must be recorded as documentary evidence, not inferred from a meeting or informal statement. Do not claim endorsement, partnership or authorization until verified.

## 10. Legal and regulatory research register (Ethiopia)

Initial official sources identified; counsel and competent authorities must confirm current applicability, implementing directives and local requirements before launch:

1. **National Bank of Ethiopia — payment-system directives:** official NBE index lists ONPS/10/2025 amendment and related payment-system directives. Payment instrument issuance and payment-system operation are regulated activities; MaaleNex must use appropriately licensed/authorized providers and must not assume it can issue stored value or operate a payment system itself.  
   https://nbe.gov.et/directives/poyment-system/  
   https://nbe.gov.et/files/onps-10-2025-oversight-of-the-natioanl-payment-system-licensing-and-authorization-of-payment-instrument-issuer-amendment-directive/

2. **Road Transport Proclamation No. 1274/2022:** official Ministry of Justice entry lists it as in force and identifies road-transport regulation and lower-level administration. Determine exact licence, operator, vehicle, service and fare provisions for each service class.  
   https://justice.gov.et/en/law/road-transport-proclamation/

3. **Personal Data Protection Proclamation No. 1321/2024:** official Ministry of Justice entry lists it as in force. Privacy design, lawful processing, consent where applicable, data-subject rights, sensitive data, security, retention and cross-border processing require legal mapping.  
   https://justice.gov.et/en/law/personal-data-protection-proclamation/

4. **Ministry of Transport and Logistics — transport laws resource:** discovery source for road-transport, freight-operator competency, driver licensing and related instruments; verify authoritative gazette/instrument and applicability before relying on a listed file.  
   https://motl.gov.et/resource_types/transport-law-1

5. **Ministry of Justice — public and private transportation sector:** discovery source for additional current federal laws and directives.  
   https://justice.gov.et/am/sector/public-and-private-transportation/

6. **Ministry of Justice — financial services / licensing resources:** use with NBE to identify current payment-service requirements.  
   https://justice.gov.et/en/directives/licensing-and-authorization-of-payment-system-operators-directive-no-313-2020/

The register is not exhaustive. Local South Ethiopia Regional State, South Omo Zone, Ari Zone, Maale Woreda and town-level instruments must be obtained and reconciled. Fare authority/amounts, motorcycle passenger-service classification, heavy-load permissions, insurance minimums, tax treatment, consumer redress, cash handling, agent networks and data-sharing mandates remain **UNRESOLVED** pending primary-source evidence.

## 11. Security, privacy and financial integrity controls

Strong authentication; MFA for privileged/high-risk financial actions; step-up confirmation for beneficiary changes and cash-out; role/attribute access control; server-side account/fleet/vehicle/jurisdiction isolation; encryption in transit/at rest; managed secrets; provider callback signature verification, replay protection, idempotency, rate limits, fraud monitoring; immutable journal, daily reconciliation, suspense handling, dual control and audit trail; privacy-by-design for precise location, identity and financial records; secure exports with expiring access; incident response, backup/restore, complaints and dispute evidence preservation. No biometric collection or continuous location tracking unless separately justified, approved and lawful. No crypto-token, lending, savings, deposit-taking or investment product is implied.

## 12. Required domain boundaries and data concepts

Reuse existing equivalents where present:
- Identity & Access; Organization & Fleet; Geography & Jurisdiction; Fare Governance;
- Booking & Dispatch; Trip Execution & Safety; Wallet & Double-Entry Ledger;
- Payment Provider Adapters & Reconciliation; Driver/Owner Settlement;
- Loyalty & Referral; Documents & Agreements; Notifications & Support;
- Reporting & Export; Compliance & Audit.

Conceptual records: FareSchedule, FareRuleVersion, FareApproval, FareQuote, Booking, Trip, CancellationCase, WalletAccount, LedgerJournal, LedgerEntry, PaymentIntent, ProviderEvent, Refund, PayoutRequest, SettlementBatch, LoyaltyAccount, LoyaltyEntry, Referral, AgreementVersion, ConsentRecord, ExportJob and AuditEvent. These are conceptual names, not a mandate to create duplicate tables. Inspect current schema and owner-approved architecture before migrations.

## 13. Delivery stages and acceptance gates

| Stage | Deliverable | Exit evidence |
|---|---|---|
| A1 — Requirements/legal/fare specification | Freeze roles, wallet/loyalty distinction, booking lifecycle, fare model, legal register and exclusions | Owner-approved signed/versioned baseline |
| A2 — Read-only reconciliation | Inventory APIs, models, migrations, UI, tests and dependencies; map reuse/gaps | Exact-HEAD evidence, duplicate-domain review, no code changes |
| A3 — Synthetic implementation | UI, API contracts, synthetic ledger/booking/fare/loyalty flows and provider sandbox adapters only | Tests, migration review, security controls and synthetic fixtures |
| A4 — Verification | Accounting invariants, role isolation, fare calculations, booking transitions, export safety, webhook simulation, accessibility and independent security review | Exact-HEAD CI and review evidence; blockers resolved |
| A5 — Production authorization | Legal approvals, licensed provider contracts, regulator/authority permissions, operational readiness and explicit owner approval | Separate written approval; not implied by A1–A4 |

No merge, deployment, live payment, real-money cash-in/cash-out, production personal-data processing or launch is authorized by this specification.

## 14. Definition of done

Passenger can obtain valid fare quote, book, cancel under disclosed policy, complete, rate and refer. Driver/owner see only correctly allocated balances and transactions. Ledger postings balance; reversals/refunds/fees/commissions are traceable. Top-up and cash-out work end-to-end in provider sandbox with signed callbacks/reconciliation; production calls remain disabled. Loyalty points never silently become cash. PDF, XLSX, CSV, JSON and receipt-image exports are permission-scoped and audited. Every fare has approval source, jurisdiction, effective date and immutable version. Agreements/consents are versioned and retrievable. Tests prove role and tenant isolation, no double-spend, idempotency, cancellation/refund rules, fare reproducibility and export privacy. No unresolved critical security, legal, accounting or safety blocker remains before production authorization.
