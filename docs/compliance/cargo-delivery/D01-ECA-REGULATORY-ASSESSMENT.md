# D01 — ECA Regulatory Assessment and Resolution Plan

**Item:** D01 — ECA registration / authorisation  
**Status:** PARTIAL — hybrid service lines, partner licence checks and provisional data roles mapped; applicant identity and regulatory evidence remain outstanding  
**Assessment date:** 23 November 2026  
**Scope:** MaaleNex Cargo Delivery  
**No authorisation implied:** This assessment does not authorise personal-data processing, courier operations, external submissions or production activation.

## 1. Executive finding

D01 was too broad as a single undifferentiated “ECA registration / authorisation” item. ECA regulates two separate matters relevant to this product:

1. Registration of data controllers and data processors under the Personal Data Protection Proclamation No. 1321/2024.
2. Licensing of operators providing postal or express courier services under the communications/postal regulatory framework.

They must be assessed separately. A data-handler registration is not a courier-service licence, and a courier-service licence is not a data-handler registration.

## 2. Data-handler registration — applicable in principle

The Personal Data Protection Proclamation No. 1321/2024, Article 33(1), states that a data controller or data processor must be registered with the Authority in order to process personal data. Article 33(2) requires separate register entries where processing is for two or more purposes. Article 35(2) provides for a registration certificate valid for two years.

ECA's official website confirms that ECA is the national authority responsible for personal-data protection and registers/supervises controllers and processors. Its PDP registration guide asks the applicant to identify:
- Registration role: controller, processor or both.
- Official organisation name, TIN and organisation type.
- Primary contact details.
- DPO appointment status.
- Processing purposes, lawful bases and categories.
- Retention policy.
- Sub-processors and security measures.
- International transfers and safeguards.
- Authorised representative and declaration.

The MaaleNex Cargo Delivery platform is designed to handle identifiable customer, sender, recipient, rider and delivery-related information. Unless the actual processing model materially differs, a registration assessment is required before personal-data processing. The exact controller/processor role allocation and applicant legal entity must be confirmed.

## 3. Courier-service licence — conditional on actual operating model

ECA's official Postal Services licensing page states that no person may operate a postal service or express courier service without an ECA licence. ECA's IRIS portal lists a **Domestic Express Mail (courier) Service** licence for delivery where both sender and recipient are within Ethiopia.

The classification depends on the real operation, not merely the product's label. Relevant facts include:
- Who contracts with the sender/customer for delivery?
- Who accepts responsibility for the consignment?
- Who sets or controls delivery prices and service terms?
- Who dispatches, directs or manages riders?
- Who bears loss, damage, delay and complaint responsibility?
- Does MaaleNex itself perform delivery, or only provide software/marketplace matching to independently licensed courier operators?

A platform that only provides technology to separately licensed courier operators may have a different licensing position from an entity that undertakes and operates the courier service. This distinction should be confirmed with ECA or qualified Ethiopian counsel before launch. Do not assume that outsourcing riders or calling the service a marketplace removes the licence requirement.

## 4. Official sources reviewed

All checked on 23 November 2026:

1. **Personal Data Protection Proclamation No. 1321/2024**, especially Articles 33–35:  
   https://pdp.eca.et/pdp-proclamation  
   https://pdp.eca.et/files/pdfs/pdp-proclamation/pdp_personal_data_protection_proclamation_No_1321_2024.pdf

2. **ECA — About / regulatory mandate:**  
   https://www.eca.et/about/

3. **ECA PDP Registration User Guide:**  
   https://pdp.eca.et/pdp-guide

4. **ECA — Postal Services / Courier Service Licensing:**  
   https://www.eca.et/services/

5. **ECA IRIS eService — Domestic Express Mail (courier) Service:**  
   https://iris.eca.et/

These sources establish the regulatory framework and available registration/licensing channels. They do not establish that MaaleNex has applied, been registered, or been granted a courier licence.

## 5. Evidence search and current disposition

Repository searches were run for:
- ECA registration and authorisation.
- Ethiopian Communications Authority.
- Data Protection Authority registration.
- Cargo data privacy registration.
- ECA references.

No MaaleNex-specific registration certificate, application receipt, ECA correspondence, courier licence or written non-applicability determination was returned.

| Evidence | Result |
|---|---|
| PDP registration certificate | NOT LOCATED / NOT VERIFIED |
| PDP application receipt or reference | NOT LOCATED / NOT VERIFIED |
| ECA controller/processor role determination | NOT RECOVERED |
| Domestic courier service licence | NOT LOCATED / NOT VERIFIED |
| Written ECA/counsel determination that courier licence is not required | NOT LOCATED / NOT VERIFIED |
| Applicant legal entity / TIN evidence | NOT AVAILABLE — Owner confirms PLC incorporation is in process and not yet completed; TIN not yet issued/available |

## 6. Owner decision — hybrid operating model confirmed

**Owner decision received: C — Hybrid.** The working model is that MaaleNex may operate some deliveries directly and facilitate other deliveries performed by independent courier partners. This is now the controlled planning assumption; it is not proof that either service line is currently active or authorised.

| Service line | Regulatory treatment | Evidence required before launch |
|---|---|---|
| MaaleNex-operated deliveries | Treat MaaleNex as a prospective courier operator for this service line. ECA states that no person may operate an express courier service without a licence. The domestic courier licence is the relevant starting point where sender and recipient are both in Ethiopia. | Identify the legal operator/applicant; obtain and verify the applicable ECA licence, scope, conditions and validity; align customer contract, rider control, custody, pricing, liability and complaints with the licensed operation. |
| Partner-operated deliveries | Treat each independent courier as the prospective operator where it contracts for and performs the delivery and remains responsible for the consignment. MaaleNex's platform role must be described accurately. | Verify each partner's legal identity and current ECA licence/scope; execute platform/partner terms allocating contracting, custody, delivery, complaints, claims, data roles and subcontracting; obtain written ECA/counsel confirmation of MaaleNex's own licensing position for the intermediary activity. |
| Shared platform/data layer | Assess separately from courier licensing. MaaleNex may determine purposes/means for some processing and act as processor for other parties' instructions; roles must be mapped by purpose and contract, not assumed globally. | Processing-purpose map, controller/processor allocation, partner data-sharing/processing terms, and ECA PDP registration for the applicable role(s) before processing. |

The hybrid decision does **not** establish which delivery types, geographic routes, customer contracts or riders fall into each service line. Those facts must be mapped before a final licensing classification. A partner's licence does not automatically cover MaaleNex's separately operated deliveries.

The PDP data-handler registration assessment remains a separate requirement across both service lines. The Owner confirmed on 23 November 2026 that MaaleNex Technologies PLC is not yet incorporated and that incorporation is in process; a company TIN is therefore not yet available. Record legal-entity formation and TIN issuance as a prerequisite to filing, while continuing pre-filing service-line and data-role preparation. No application or fee payment is authorised. Until incorporation and TIN issuance are complete, maintain the application pack as a pre-filing workstream and do not submit it in the proposed PLC's name.

## 7. Pre-filing service-line and data-role map

The Owner-approved hybrid operating model has been decomposed into two service lines, a per-partner licence-verification checklist, and a purpose-based controller/processor allocation. The detailed controlled working record is [D01 Hybrid Service-Line, Partner Licence and Data-Role Map](D01-HYBRID-SERVICE-LINE-AND-DATA-ROLE-MAP.md). It distinguishes MaaleNex-operated deliveries from independent partner-operated deliveries; maps platform, direct-delivery, partner execution, onboarding, payment and compliance processing purposes; and records the incorporation/TIN, D03/D04, partner evidence and written ECA/counsel determination dependencies. This is pre-filing preparation only: no partner is represented as verified, no registration or licence is held or inferred, and no service line is authorised to operate.

## 8. Closure criteria

D01 may be closed only when all applicable items are evidenced:
1. Legal applicant exists and is evidenced by completed incorporation; exact registered legal name and TIN are confirmed. The Owner reports incorporation is currently in process and not yet complete.
2. Controller/processor/both roles and processing purposes confirmed.
3. ECA PDP registration completed and current certificate verified, or a reasoned formal legal/ECA determination establishes a specific lawful exception.
4. Courier operating model classified.
5. If MaaleNex operates express courier services, valid ECA licence and scope verified before operations; otherwise, written ECA/counsel non-applicability determination and evidence of licensed delivery partners retained.
6. Evidence references, dates, certificate numbers, scope, expiry and verification source recorded in the controlled register.

**Current D01 status: PARTIAL — hybrid model selected and pre-filing service-line/data-role mapping completed; partner-specific, operational, entity and regulatory evidence remain outstanding.** No legal closure, production processing permission or courier operating permission is claimed.
