# D02 — Article 40 Data Protection Officer Threshold Assessment

**Status:** IN PROGRESS — statutory tests identified; factual scale and activity evidence not yet established  
**Assessment date:** 23 November 2026  
**Scope:** MaaleNex Cargo Delivery / proposed MaaleNex Technologies PLC  
**Applicant identity:** proposed PLC remains in formation; this assessment is pre-incorporation and pre-filing  
**Decision:** NO CONCLUSION YET on whether Article 40 requires appointment; no appointment or exemption is inferred.

## 1. Question and legal test

Personal Data Protection Proclamation No. 1321/2024, Article 40(1), requires a data controller or data processor to designate or appoint a Data Protection Officer (DPO) where **any one** of these alternative conditions applies:

1. Processing is carried out by a government body, except courts acting in their judicial capacity.
2. The controller's or processor's core activities consist of processing operations which, by their nature, scope or purposes, require regular and systematic monitoring of data subjects on a large scale.
3. The controller's or processor's core activities consist of processing on a large scale of sensitive personal data.

The three limbs are alternatives. One established limb is sufficient. The test concerns the controller or processor and its processing activities; it is not a general rule that every entity handling any personal data must appoint a DPO.

Article 40(2) permits a group of entities to appoint one DPO if the officer is easily accessible to each entity. Article 40(4) requires relevant academic or professional qualifications, which may include data-protection knowledge and technical skills. Article 40(5) requires publication of the DPO's contact details and communication of those details to the Authority. Article 41 sets out the DPO's advisory, compliance, capacity-building and cooperation duties.

The Proclamation does not specify a numerical threshold for "large scale" in Article 40. Do not invent a user count, delivery count, data-volume threshold or monitoring-duration safe harbour. A defensible assessment must document the actual nature, scope, context and purposes of the processing and explain the conclusion.

## 2. Limb A — government-body processing

### Current factual assessment

- The proposed MaaleNex Technologies PLC is a private company in formation, according to the Owner.
- No fact presently establishes that MaaleNex is itself a government body.
- No government-body customer, contracting authority, public-sector programme, government mandate or government-controlled processing arrangement has been evidenced in the repository material reviewed for this assessment.
- A future public-sector contract or processing arrangement cannot be ruled out.

**Preliminary result:** NOT TRIGGERED ON CURRENT EVIDENCE for MaaleNex acting solely as a private entity for its own commercial platform and delivery purposes. This is not a permanent exemption.

### Reassessment trigger

Before onboarding any ministry, regional bureau, woreda/city administration, public enterprise or other government body, identify:
- Which legal entity determines the purpose and essential means.
- Whether MaaleNex acts as controller, processor or joint controller for each purpose.
- Whether the relevant processing is carried out by or on behalf of a government body.
- Whether the government body has its own DPO and how MaaleNex's processing role affects Article 40 duties.

Do not equate merely delivering to a government employee or collecting a public-office address with government-body processing. Conversely, do not assume that outsourcing the technical work removes the statutory trigger where the processing is carried out for a government body. Obtain a written Ethiopian legal determination for any such contract before processing starts.

**Evidence status:** no government-body processing contract, instruction set or public-sector customer is currently evidenced. Status: NOT ESTABLISHED / NOT VERIFIED.

## 3. Limb B — regular and systematic monitoring on a large scale

This limb requires all of the following to be examined:
- Monitoring of data subjects is part of the controller's or processor's **core activities**.
- Monitoring is **regular** (recurring, repeated or ongoing rather than isolated).
- Monitoring is **systematic** (organised, methodical, planned or structured).
- Monitoring is on a **large scale**, assessed from actual scope and context.

### Cargo platform monitoring features to test

| Feature / activity | Monitoring relevance | Current evidence position |
|---|---|---|
| Consignment and dispatch lifecycle events | Repeated observation of delivery progress; potentially relevant to monitoring | IMPLEMENTED in staged backend PRs #45–#47; event counts, operational frequency and volumes NOT PROVIDED |
| Coordinate-bearing tracking events | Potential monitoring of courier/vehicle/consignment location where coordinates are linked to a person | Optional latitude/longitude pair on discrete staff-submitted events; no continuous GPS polling or sampling configuration found in inspected cargo branches; source/subject/frequency/duration NOT VERIFIED |
| Public/customer tracking links | Could enable repeated observation of recipient/customer interactions | No public tracking-link endpoint found in inspected cargo backend branches; separate frontend/integration behavior NOT VERIFIED |
| Delivery proof and private evidence | Receiver name, evidence reference, optional notes and occurrence timestamp; linked private PDF/JPEG/PNG evidence may contain additional personal data | Implemented in staged PRs #47–#49; actual file contents, upload volumes and any signature/photo/coordinate content NOT VERIFIED |
| Dispatch, performance scoring or rider ranking | Dispatch assignment/status records staff and carrier actions; scoring/ranking would increase worker-monitoring impact | Dispatch implemented in PR #46; no automatic performance-scoring or rider-ranking implementation found in inspected cargo branches |
| Fraud, risk, route or behaviour analytics | May involve profiling depending on data, purpose and decisions | No cargo-specific automated analytics/profiling implementation found in inspected PR #45–#51 branches; separate services/manual processes NOT VERIFIED |
| Delivery exceptions and resolution | Exception codes, descriptions, resolution codes/notes and staff IDs can form linked histories | Implemented in PR #47; support-system linkage, longitudinal analysis and actual volumes NOT VERIFIED |

### Scale assessment dimensions

Record and substantiate, at minimum:
1. Number of active data subjects per month and year, separately for customers, senders, recipients, riders, partner staff and other groups.
2. Number of deliveries, tracking events, GPS points and proof-of-delivery records per day/month/year.
3. Geographic reach and number of active routes, woredas, regions and cross-border destinations.
4. Duration and continuity of tracking (one-off event vs repeated/live monitoring; minutes, hours, days or longer).
5. Proportion of individuals monitored and whether monitoring covers most users/workers or only exceptional cases.
6. Data granularity, linkability, retention and ability to reconstruct movement or behaviour.
7. Whether automated analysis, profiling, performance scoring, risk flags or decisions significantly affect individuals.
8. Whether monitoring is intrinsic to the service's core business or only an incidental, limited support function.
9. Whether MaaleNex and partner processing together create a materially broader monitoring operation; assess each entity's actual role rather than aggregating by assumption.

**Preliminary result:** UNDETERMINED. Source review confirms dispatch and discrete tracking events, including optional coordinates, but no continuous GPS polling or public tracking endpoint in the inspected cargo branches. Whether repeated coordinate-bearing events constitute regular and systematic monitoring depends on their actual source, subject, frequency, duration, operational necessity and scale. No measured or approved forecast volumes are available. The lack of measured scale is not evidence that the threshold is absent.

## 4. Limb C — large-scale processing of sensitive personal data

The Proclamation's definition of sensitive personal data must be applied to the actual fields and inferences processed. The assessment must identify data that falls within the statutory definition, not label every contact detail or delivery address as sensitive. Review the complete definition in Article 2 and the conditions/restrictions in Article 9 against the official Amharic/English text and obtain counsel confirmation for borderline categories.

### Cargo data categories to test

| Data category / feature | Initial classification for D02 | Required validation |
|---|---|---|
| Names, phone numbers, email, ordinary delivery addresses | Personal data; not automatically sensitive solely because identifying | Verify whether a specific address or context reveals a protected sensitive attribute |
| Rider/customer precise location history | Personal data with elevated privacy risk; not automatically a statutory sensitive category merely because it is precise | Assess whether it reveals health, religious attendance, political activity, union membership or another protected attribute; document inferences |
| Proof-of-delivery image or signature | Personal data; may incidentally reveal sensitive characteristics | Determine whether images are collected, whether biometric identification/template processing occurs, and whether sensitive attributes are inferred |
| Health/disability/accessibility or emergency-delivery information | Potential sensitive personal data depending on the statutory definition and field content | Determine whether collected at all, why necessary, scale, access and retention |
| Religious, political, ethnic, racial, philosophical, trade-union or similar information | Sensitive if within the statutory definition | Do not collect for routine cargo delivery; identify any incidental or inferred processing |
| Biometric identifiers/templates used to uniquely identify a person | Potential sensitive personal data under the statutory definition | Confirm whether facial recognition, fingerprint, voiceprint or other biometric identification is implemented; ordinary photo storage is not automatically biometric identification |
| Criminal-offence/allegation information | Requires separate statutory classification and legal review | Determine whether any fraud/safety screening uses such data and the lawful authority/basis |
| Children's data | Requires heightened safeguards and separate legal review; do not assume every child's data is automatically within the sensitive-data definition | Determine whether minors can register, receive deliveries, be named as recipients or be profiled |

### Scale assessment dimensions

If sensitive personal data is processed, record:
- Exact statutory category and fields/inferences involved.
- Number and proportion of affected data subjects.
- Number of records and frequency of collection.
- Duration, geographic reach and number of systems/recipients.
- Whether processing is a core activity or incidental.
- Whether data is linked with location, identity, delivery history or profiling.
- Whether partners, cloud providers or other processors receive it.
- Whether the data is collected by design, optional, exceptional or prohibited.

**Preliminary result:** UNDETERMINED. The source review identifies open-content channels (PDF/JPEG/PNG evidence and free-text descriptions/notes) that may contain sensitive information, plus a sensitive-data flag defaulting to false. No large-scale sensitive-data processing is established, but the prior “no special-category data” assumption has not been validated against actual file contents, classification practice or volumes. Absence of a located record is not proof that such processing does not occur.

## 5. Provisional trigger matrix

| Article 40 limb | Preliminary status | Reason | Evidence needed to decide |
|---|---|---|---|
| A — government-body processing | NOT TRIGGERED ON CURRENT EVIDENCE; reassess on public-sector engagement | Proposed entity is private and in formation; no public-body processing arrangement evidenced | Customer/partner pipeline, contracts, controller/processor map and any government instructions |
| B — large-scale regular/systematic monitoring | UNDETERMINED | GPS, tracking and dispatch can involve monitoring, but actual scope, regularity, systematic nature and scale are unmeasured | Feature inventory, architecture/configuration, telemetry, user/event counts, tracking frequency/duration, analytics and DPIA |
| C — large-scale sensitive-data processing | UNDETERMINED | Sensitive categories and large-scale processing have not been established or ruled out | Statutory category-to-field map, D04 inventory, DPIA, actual data samples/schema, volumes and purpose analysis |

**D02 decision:** NO DPO-MANDATORY / NO-DPO-REQUIRED CONCLUSION AT THIS STAGE. The evidence is insufficient to conclude either way. Keep D02 OPEN.

## 6. Evidence collection plan

| Evidence ID | Required record | Owner / source | Status |
|---|---|---|---|
| D02-E01 | Government-body customer/contract and processing arrangement register | Project Owner / commercial pipeline | NOT PROVIDED |
| D02-E02 | Cargo platform feature and configuration inventory (GPS, tracking, proof-of-delivery, analytics, scoring, fraud) | Product/engineering | PARTIAL — staged backend source mapped in D03/D04; runtime config and other integrations NOT VERIFIED |
| D02-E03 | Monitoring data-flow and event taxonomy, including frequency, precision, retention and access | Engineering / D04 | PARTIAL — discrete event schema and optional coordinate fields mapped; source, frequency, duration and live access NOT PROVIDED |
| D02-E04 | Measured or responsibly forecast subject/event volumes by category and geography | Operations/product analytics | NOT PROVIDED — no production metrics or Owner-approved forecast located |
| D02-E05 | Sensitive-data statutory category-to-field/inference assessment | Legal/DPO adviser with product and engineering | PARTIAL — fields and open-content channels mapped; actual content, classification and scale NOT VERIFIED |
| D02-E06 | D03 DPIA report and its scope/version, including tracking and sensitive-data analysis | Project Owner / DPIA author | PARTIAL — recovered C06-only DPIA confirmation is not the full DPIA; complete report/screening record NOT RECOVERED / NOT VERIFIED |
| D02-E07 | Partner data-role and data-sharing arrangements for SL-01/SL-02 | Commercial/legal | PRE-FILING MAP EXISTS; executed agreements NOT PROVIDED |
| D02-E08 | Written Article 40 threshold determination, assumptions, reviewer identity and date | Qualified Ethiopian privacy counsel / designated reviewer | NOT OBTAINED |

## 7. DPO readiness if a trigger is established

If any Article 40(1) limb is established, prepare:
- Appointment/designation instrument identifying the controller/processor entity and effective date.
- Role description and authority to advise and monitor compliance.
- Direct access to senior management and adequate resources.
- Independence and conflict-of-interest assessment, particularly where the person also owns product, security, HR, operations or commercial decisions.
- Relevant academic/professional qualifications and data-protection competence evidence under Article 40(4).
- Contact details for publication and communication to ECA under Article 40(5).
- Duties aligned to Article 41: advice, compliance monitoring, staff capacity building, DPIA advice and cooperation with the Authority.
- If a group DPO is considered under Article 40(2), demonstrate easy accessibility to every covered entity and document entity-specific accountability.

A DPO appointment does not cure missing registration, lawful basis, DPIA, security or other compliance requirements. Do not make an appointment merely to create the appearance of compliance if the role lacks independence, competence or resources.

## 8. Relationship to D01, D03 and D04

- D01's pre-filing map supplies the provisional controller/processor allocation for direct and partner-operated deliveries. D02 must test Article 40 separately for each actual controller/processor and processing purpose.
- D03 DPIA is a key input because it should describe high-risk tracking, location, profiling, proof-of-delivery and sensitive-data processing. The DPIA's existence and acceptance remain subject to the historical evidence reconciliation; do not treat it as verified.
- D04 must supply the authoritative inventory of actual fields, data subjects, purposes, recipients, systems, processors, locations, event frequency and retention.
- If the D03/D04 evidence shows a large-scale Article 40 trigger, update this assessment and prepare the DPO appointment gate before the relevant processing begins.
- Article 47 DPIA thresholds are distinct from Article 40 DPO thresholds. A DPIA trigger does not automatically prove a DPO trigger, and the absence of a DPO trigger does not remove any DPIA duty.

## 9. Sources

1. **Official Personal Data Protection Proclamation No. 1321/2024 (ECA PDF)** — Article 40 (DPO), Article 41 (DPO duties), Article 2 (definitions), Article 9 (sensitive personal data), Article 47 (DPIA):  
   https://pdp.eca.et/files/pdfs/pdp-proclamation/pdp_personal_data_protection_proclamation_No_1321_2024.pdf
2. **ECA PDP Proclamation page** — official proclamation and chapter navigation:  
   https://pdp.eca.et/pdp-proclamation
3. **Ministry of Justice law catalogue** — Proclamation No. 1321/2024, listed in force:  
   https://justice.gov.et/en/law/personal-data-protection-proclamation/

The assessment should be checked against the official Amharic text and current ECA guidance by qualified Ethiopian counsel before a final legal determination. No numeric large-scale threshold is asserted in this record.

## 10. Closure criteria

D02 may be closed only when:
1. Government-body involvement is tested against the actual customer/contract/processing pipeline.
2. Monitoring features, regularity, systematic nature, core-activity status and scale are evidenced with actual or responsibly forecast metrics.
3. Sensitive-data categories, fields/inferences, core-activity status and scale are mapped against the statutory definition.
4. D03 and D04 evidence is reconciled and any material unknown is explicitly retained.
5. A written Article 40 conclusion is signed/attributed to a qualified reviewer and records each limb independently.
6. If any limb is triggered, a qualified DPO is appointed/designated, conflict/independence and resources are assessed, and contact publication/Authority communication are evidenced.
7. If no limb is triggered, the evidence-based rationale and reassessment events are documented; no blanket future exemption is claimed.

**Current D02 status: IN PROGRESS — government-body limb not triggered on current evidence; monitoring and sensitive-data limbs remain undetermined after source-level feature reconciliation. Operational configuration, actual/forecast volumes and sensitive-content classification remain missing. No DPO appointment conclusion is made.**


## 11. Source-level implementation reconciliation — 23 November 2026

The source-level reconciliation is recorded in:
- [D03 DPIA Source-to-Implementation Reconciliation](D03-DPIA-SOURCE-TO-IMPLEMENTATION-RECONCILIATION.md)
- [D04 Cargo Personal-Data Inventory and Processing-Flow Reconciliation](D04-CARGO-PERSONAL-DATA-INVENTORY-AND-FLOW-RECONCILIATION.md)

### Confirmed in staged cargo backend branches

- PR #45 implements consignment records containing sender name, recipient name, destination, free-text description, optional weight, status, assigned organisation, staff creator and lifecycle timestamps.
- PR #46 implements dispatch records and append-only tracking events. A tracking event accepts a bounded event type, optional description, optional latitude/longitude pair and occurrence timestamp. The API is staff-authenticated and permission-scoped to assigned carriers/platform dispatchers; occurrence times are bounded to the previous 30 days and not materially in the future.
- No continuous GPS polling, periodic device-location sampling, live map feed or public tracking-link endpoint was found in the inspected cargo branches. This is a source-scope finding, not proof that no separate app or integration exists.
- PR #47 implements carrier profiles, delivery proof (received-by name, evidence reference, optional notes, occurrence time and staff submit/review identifiers) and exception records with descriptions and resolution notes.
- PR #48 supports private, dispatch-scoped PDF/JPEG/PNG evidence uploads, maximum 10 MiB, with a 300-second presigned upload intent and object type/size/signature verification.
- PR #49 and PR #51 add evidence lifecycle, retention, legal-basis, privacy-notice, transfer, sensitive-data, rights-request and DPO-review metadata.
- PR #51 audit records retain actor/resource/action metadata while redacting specified sensitive metadata keys. This does not make the audit record anonymous.

### Runtime configuration and deployment boundary

The inspected configuration defaults `synthetic_data_only=true`, `scheduler_enabled=false` and `object_storage_enabled=false`. Development/test configuration requires synthetic-only mode. The cargo feature increments are staged in unmerged pull requests; PR #51 reports no hosted migration, deployment, production policy activation, deletion or scheduler activation. These defaults and PR statements do not replace inspection of a live runtime configuration, but no live cargo processing environment or production dataset was evidenced.

### Sensitive-data qualification

The earlier reviewer statement that no special-category data is processed was an assumption. The current schema contains open-content fields and private uploaded files that could incidentally contain sensitive information. The PR #51 sensitive-data flag defaults to false; no content-classification process or representative file review was evidenced. No biometric identification, facial recognition or automated profiling implementation was found in the inspected cargo branches. Therefore limb C remains undetermined, not ruled out.

### Operational scale

No measured production volumes or Owner-approved forecast was found. Unique senders, recipients, couriers, partner staff, active carriers, deliveries, tracking events, coordinate-bearing events, proof records, file uploads/bytes, exceptions, geographic reach, monitoring duration and event frequency are all MISSING. Test/CI fixtures are synthetic and are not operational volume evidence. D03/D04 specify the exact dataset required.

### Effect on Article 40 conclusion

The source review makes the feature and field analysis more concrete but does not supply the scale, runtime or actual processing evidence needed to decide whether monitoring is regular/systematic on a large scale or whether sensitive personal data is processed on a large scale. No numeric threshold is invented. D02 remains OPEN; no DPO-required or DPO-not-required conclusion is made.

