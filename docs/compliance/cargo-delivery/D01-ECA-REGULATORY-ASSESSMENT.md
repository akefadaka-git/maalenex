# D01 — ECA Regulatory Assessment and Resolution Plan

**Item:** D01 — ECA registration / authorisation  
**Status:** UNRESOLVED — regulatory requirement established in principle; entity-specific evidence and operator classification pending  
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
| Applicant legal entity / TIN evidence | NOT VERIFIED in this D01 evidence set |

## 6. Owner decision required — one operating-model choice

**Which operating model is intended for MaaleNex Cargo Delivery?**

A. **MaaleNex is the courier operator:** it contracts with customers for delivery, accepts delivery responsibility, and controls/dispatches its own or contracted riders. Treat ECA domestic courier licensing as required unless ECA gives a contrary written determination.

B. **MaaleNex is a technology marketplace only:** it provides software and matching, while independent, separately licensed courier companies contract for and perform delivery and remain responsible for the consignment. Prepare the platform/operator boundary and seek written ECA/legal confirmation that MaaleNex itself is outside courier-operator licensing.

C. **Hybrid:** MaaleNex operates some deliveries and intermediates others. Map each service line and obtain the corresponding licence/authority determinations.

The PDP data-handler registration assessment remains a separate requirement whichever model is selected.

## 7. Closure criteria

D01 may be closed only when all applicable items are evidenced:
1. Exact legal applicant/operator entity and TIN confirmed.
2. Controller/processor/both roles and processing purposes confirmed.
3. ECA PDP registration completed and current certificate verified, or a reasoned formal legal/ECA determination establishes a specific lawful exception.
4. Courier operating model classified.
5. If MaaleNex operates express courier services, valid ECA licence and scope verified before operations; otherwise, written ECA/counsel non-applicability determination and evidence of licensed delivery partners retained.
6. Evidence references, dates, certificate numbers, scope, expiry and verification source recorded in the controlled register.

**Current D01 status: UNRESOLVED.** No legal closure, production processing permission or courier operating permission is claimed.
