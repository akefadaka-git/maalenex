# D01 — Hybrid Service-Line, Partner Licence and Data-Role Map

**Status:** PRE-FILING WORKING RECORD — NOT A LICENCE, REGISTRATION, LEGAL OPINION OR OPERATING AUTHORITY  
**Assessment date:** 23 November 2026  
**Owner decision:** Hybrid model (C)  
**Applicant identity:** MaaleNex Technologies PLC is in formation; incorporation and TIN are pending.

## 1. Purpose and decision boundary

This record translates the Owner-approved hybrid model into two distinct delivery service lines and a purpose-based personal-data role map. It is suitable for pre-filing preparation before incorporation. It does not represent that either service line has commenced, that any partner exists or has been verified, or that MaaleNex is authorised to process personal data or operate a courier service.

The regulatory tests are separate:

- Courier licensing attaches to the actual postal/express-courier operation and its operator. ECA states that no person may operate an express courier service without an ECA licence; its licensing information distinguishes national and international courier services. The domestic service definition covers sender and recipient both in Ethiopia.
- PDP registration applies to the relevant data controller(s) and data processor(s) before processing personal data. Article 33(2) requires separate register entries for separate processing purposes. A single platform can occupy different roles for different purposes.

## 2. Service-line map

### SL-01 — MaaleNex-operated delivery

**Working operator classification:** MaaleNex is the prospective courier operator for consignments it contracts to deliver and for which it accepts delivery responsibility or operational control.

| Dimension | Pre-filing position to document | Evidence required before activation |
|---|---|---|
| Customer contract | MaaleNex contracts directly with sender/customer for the delivery service | Approved customer terms naming the actual licensed legal operator |
| Acceptance/custody | Record who accepts the consignment, issues receipt/tracking reference and controls custody at each hand-off | Consignment acceptance SOP, chain-of-custody record, hand-off evidence |
| Dispatch/riders | Record whether MaaleNex assigns, directs, monitors or disciplines riders and whether riders are employees, agents or contractors | Rider agreements, dispatch SOP, employment/contractor classification, supervision model |
| Pricing/service | Record who sets delivery price, delivery promise, service area and service levels | Approved tariff/pricing schedule and service terms |
| Liability/claims | Record who is responsible for loss, damage, delay, failed delivery, refunds and complaints | Claims policy, insurance evidence, customer terms and escalation procedure |
| Geography | Classify each route as domestic (both endpoints in Ethiopia) or international | Route/service-area register; international routes excluded until separately licensed/cleared |
| ECA authorisation | Presume the applicable ECA courier licence is required if MaaleNex itself operates express courier services | Verify applicant eligibility, licence category, scope, conditions, term and current status with ECA before operations |

**Control:** A partner's licence does not authorise MaaleNex-operated consignments. If MaaleNex contracts as principal, assumes custody/delivery obligations or directs the delivery operation, do not classify the service as merely a software referral without a written ECA/counsel determination.

### SL-02 — Independent partner-operated delivery

**Working operator classification:** The partner is the prospective courier operator only where it independently contracts for and performs the courier service, accepts delivery responsibility and holds the relevant ECA licence. MaaleNex provides platform/intermediation functionality, subject to confirmation of the actual commercial and operational facts.

| Dimension | Required boundary | Evidence required for each partner |
|---|---|---|
| Legal identity | Partner must be a legally identifiable contracting entity | Registration/incorporation evidence, exact legal name, TIN and authorised signatory |
| Licence | Partner's own current licence must cover the service and territory | ECA licence/certificate, licence number, category, scope, conditions, expiry and independent verification |
| Customer contract | Identify whether customer contracts with partner directly or MaaleNex acts as disclosed agent | Executed customer/partner terms and clear operator disclosure |
| Consignment responsibility | Partner accepts consignment and remains responsible for custody, delivery, claims and proof of delivery | Partner SOP, receipt, custody/handoff records, claims process |
| Rider control | Partner recruits/contracts, dispatches, supervises and is accountable for its riders | Rider governance evidence and subcontractor list |
| Subcontracting | Partner may not silently delegate regulated delivery to an unverified operator | Prior approval, subcontractor identity/licence checks and flow-down obligations |
| Insurance and complaints | Partner demonstrates applicable insurance and operational complaint handling | Policy/certificate, exclusions/limits, claims and complaint contacts |
| MaaleNex role | Platform fee, listing, matching, status relay and customer support functions must be described accurately; any operational control or principal liability triggers reclassification review | Platform/partner agreement, process map, payment flow and customer-facing disclosures |

**Partner licence verification checklist (repeat per partner):**

1. Obtain a legible licence copy directly from the partner and record the issuing authority, licence number, legal holder, category, service territory, conditions, issue date and expiry.
2. Verify authenticity and current validity through ECA or another authoritative channel; retain date, verifier, channel and result.
3. Confirm that the licence covers the exact delivery mode and route. Domestic and international services are distinct categories.
4. Match the licence holder to the legal entity signing the partner agreement; investigate trading names, affiliates and subcontractors.
5. Confirm suspension/revocation status, renewal status and any restrictions before onboarding and periodically thereafter.
6. Block partner activation and new assignments if evidence is missing, expired, mismatched, restricted or unverifiable.
7. Retain re-verification evidence and a change/expiry alert owner. A screenshot or partner declaration alone is not sufficient verification.

**No partner is currently represented as verified.** Partner names, registration numbers, ECA licence numbers, licence copies and ECA verification results remain NOT PROVIDED / NOT VERIFIED.

## 3. Purpose-based controller / processor allocation

The legal test is functional. A controller determines the purposes and means of processing, alone or jointly. A processor processes personal data on behalf of a controller. Contract labels do not override actual conduct. An entity can be a controller for one purpose and a processor for another. Joint-controller status arises only where two or more parties jointly determine purposes and means.

| Processing purpose | MaaleNex provisional role | Partner provisional role | Evidence/qualification |
|---|---|---|---|
| MaaleNex account creation, authentication, platform security and user administration | Controller | Normally no role, except partner user accounts or instructed support | MaaleNex determines platform purpose and essential means |
| Customer/sender profile and platform relationship management | Controller for MaaleNex platform/customer relationship | Separate controller for partner's own customer relationship where it independently determines use | Define which party contracts with customer and whose purposes govern each record |
| SL-01 direct-delivery booking, dispatch, tracking, proof of delivery, claims and customer support | Controller for its own courier operation and associated processing | No partner role unless a partner separately processes on MaaleNex's instructions | MaaleNex's direct service responsibilities and purposes control |
| SL-02 partner delivery execution, custody, routing, proof of delivery and claims | Usually partner controller for its own courier execution; MaaleNex may be a separate controller for platform matching, account, billing, fraud prevention and its own support | Controller for independently determined courier purposes | A partner is not automatically a processor merely because it receives a platform booking |
| Platform hosting, software maintenance, cloud storage and technical support | Controller for MaaleNex's own platform purposes; may itself be a processor if operating a platform for a partner strictly on documented instructions | Controller where it determines the delivery purpose; may engage MaaleNex as processor only for clearly instructed, segregated processing | Requires purpose-specific written instructions, security terms, subprocessor controls and no independent reuse |
| Partner onboarding, licence verification, due diligence and partner performance/quality monitoring | Controller for MaaleNex's onboarding, compliance and platform-risk purposes | Independent controller for its own records and responses | Minimise collected evidence; restrict access to licence and contact data |
| Payments, commissions, invoices, tax/accounting and dispute records | Each party is generally controller for its own accounting, tax and legal obligations | Each party is generally controller for its own accounting, tax and legal obligations | Payment provider/bank roles require separate mapping; do not assume processor status |
| Legal claims, regulatory requests, safety incidents and fraud investigations | Each party may be an independent controller for its own legal/compliance purposes; joint control only if purposes and essential means are jointly determined | Same | Record legal basis, disclosure purpose, recipient and retention separately |

### Role rules to apply

- Do not designate MaaleNex as a processor for all platform data by default. It is likely a controller for its own platform, customer, security, onboarding and commercial purposes.
- Do not designate every delivery partner as a processor. A courier that independently contracts for and performs delivery will ordinarily determine its own delivery purposes and means and is likely a controller for that activity.
- Use a processor agreement only where one party processes on the other's documented instructions and does not determine its own purposes for that processing.
- Use a joint-controller arrangement only if the parties actually jointly determine purposes and essential means; document allocation of responsibilities and data-subject contact points.
- Separate controller-to-controller data sharing from processor instructions. Specify fields, purposes, lawful basis, access, retention, security, rights handling, breach escalation, onward disclosure and deletion/return.
- Reassess roles whenever contracts, payment flows, dispatch control, rider management, customer terms or data uses change.

## 4. Initial personal-data inventory for the role map

Expected categories to validate in D04/DPIA; this is a planning inventory, not proof of live collection:

- Customer/sender/recipient: names, telephone/contact details, delivery addresses, account identifiers and service communications.
- Rider/partner personnel: identity and contact details, work/contract status, assignment and performance records.
- Delivery event data: pickup/drop-off timestamps, consignment references, proof-of-delivery and complaint/claim records.
- Location data: rider/device or delivery location, if enabled. Treat continuous or granular tracking as a high-risk feature requiring necessity, transparency, access and retention controls.
- Payment/accounting data: transaction references, amounts, invoices and reconciliation records. Avoid collecting or retaining full payment credentials where not necessary.
- Platform/security data: authentication identifiers, device/session events, access logs, fraud/security signals and support records.
- Partner due-diligence data: legal entity, TIN, licence, authorised representative, insurance and compliance evidence.

Do not collect sensitive personal data, identity-document images, precise location history or recipient signatures/photos by default. Add each field only after purpose, necessity, lawful basis, notice, access, retention and DPIA review are documented. Children’s data and sensitive data require separate legal review and safeguards.

## 5. Pre-filing registration workplan

Prepare two separate purpose records for each actual role, consistent with Article 33(2):

- **PDP-R01 — MaaleNex controller registration pack:** platform/account/security; customer relationship; partner onboarding; own direct courier operations; billing/claims/compliance purposes as applicable.
- **PDP-R02 — MaaleNex processor registration pack (conditional):** only if a partner or other controller instructs MaaleNex to process personal data on its behalf. Identify each controller, instructions, categories, systems, subprocessors, locations, safeguards and deletion/return terms.
- **Partner-side registrations:** obtain each partner's own controller/processor registration evidence where applicable; do not assume MaaleNex registration covers partner processing.
- **Joint-controller cases:** identify the jointly determined purpose and essential means, parties, allocation and contact point; obtain a written arrangement and counsel review.

The final registration applicant must be the actual legal person. The proposed MaaleNex Technologies PLC is not yet incorporated and has no confirmed company TIN. Keep drafts and field schedules under project control only; do not submit in the proposed PLC's name or imply it already exists. Before filing, verify the registered name, incorporation evidence, TIN, organisation type, authorised representative, contact details, DPO position, purposes, lawful bases, categories, retention, processors/subprocessors, security measures and international transfers.

## 6. Evidence status and open dependencies

| Evidence item | Current status | Next evidence action |
|---|---|---|
| Owner hybrid decision | RECORDED — C | Preserve this controlled decision |
| SL-01 service boundary and licence test | MAPPED — PRE-FILING | Confirm exact customer contract, custody, dispatch, rider, pricing, liability and geography model |
| SL-02 partner boundary and verification checklist | MAPPED — PRE-FILING | Identify proposed partners and obtain/verify each licence and legal identity |
| Partner licence records | NOT PROVIDED / NOT VERIFIED | Populate one verification record per partner before onboarding |
| MaaleNex incorporation and TIN | PENDING — Owner confirms in process | Obtain certificate and TIN after issuance |
| Controller/processor purpose map | MAPPED — PROVISIONAL | Validate against actual architecture, contracts, data flows and payment/dispatch processes |
| Processing inventory and data flows | DEPENDENCY — D04 | Reconcile systems, recipients, subprocessors, locations, fields and retention |
| DPIA | DEPENDENCY — D03 | Reconcile the actual DPIA against tracking, location, proof-of-delivery, scale and partner flows |
| ECA courier classification for platform-only SL-02 | NOT DETERMINED | Obtain written ECA or qualified Ethiopian counsel determination based on final contracts and operations |
| PDP registration certificate(s) | NOT FILED / NOT VERIFIED | File only after applicant identity, role, purposes and required particulars are complete |

## 7. D01 exit criteria and hand-off to D02

D01 pre-filing mapping is sufficiently documented for a controlled hand-off when:
1. The two service lines and their operator tests are approved and reflected in customer/partner contract templates.
2. A partner licence verification template and no-go rule are in place; actual partner evidence is required before any partner activation.
3. The purpose-based controller/processor map is reconciled against D04 data flows and D03 DPIA, with unresolved rows explicitly marked.
4. The incorporation/TIN dependency and ECA/PDP filing gates are recorded.
5. The unresolved platform-only courier licensing boundary is assigned for written ECA/counsel determination.

D02 may then proceed as a separate threshold assessment under Article 40. D02 must assess whether core activities involve (a) a government body, (b) large-scale regular and systematic monitoring of data subjects, or (c) large-scale processing of sensitive personal data. Do not infer DPO appointment is mandatory or unnecessary from the current incomplete inventory. D02 is not a substitute for completing D01 filing dependencies.

## 8. Sources and legal review

1. Personal Data Protection Proclamation No. 1321/2024, especially definitions, Articles 16–17, 33, 40–43, 47 and 51: https://pdp.eca.et/pdp-proclamation and https://pdp.eca.et/files/pdfs/pdp-proclamation/pdp_personal_data_protection_proclamation_No_1321_2024.pdf
2. ECA Postal Services licensing information: https://www.eca.et/services/
3. ECA Portal listing Domestic Express Mail and International Express Mail courier services: https://portal.eca.et/
4. Communications Service License and Regulatory Fees Directive No. 1024/2024, definitions of domestic and international express mail: https://eca.et/wp-content/uploads/2024/10/1024-_COMMUNICATIONS_SERVICE_LICENSE_AND_REGULATORY_FEES_DIRECTIVE_NO._1024-2024.pdf
5. Ministry of Justice law catalogue entry for Proclamation No. 1321/2024: https://justice.gov.et/en/law/personal-data-protection-proclamation/

This is a working compliance map, not a substitute for a written Ethiopian legal opinion or ECA determination. Confirm current directives, application requirements and licence conditions with ECA before filing or operation.
