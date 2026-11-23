# D01–D14 Controlled Register — Owner Review Draft

**Disposition:** FOR OWNER REVIEW — NOT APPROVED FOR EXTERNAL SUBMISSION  
**Version:** 1.0 review draft  
**As-of date:** 23 November 2026  
**Responsible role recorded in the 06:30 reconciliation:** Project Owner for each item.

## 1. Reconciliation matrix

| ID | Category | 06:30 recovered reconciliation | PR #51 repository submission snapshot | Evidence reference/location | Closure prerequisites |
|---|---|---|---|---|---|
| D01 | ECA PDP data-handler registration and hybrid courier-service licensing | **UNRESOLVED** — no PDP registration certificate or courier licence/non-applicability determination supplied; Owner selected hybrid operating model. | **NOT LOCATED IN SOURCES SEARCHED** — L01–L07 discusses ECA requirements; it is not a registration certificate or formal non-applicability determination. | Owner confirms PLC not yet incorporated (in process) and TIN not yet available; hybrid decision C recorded in D01 assessment; no registration certificate, application receipt, ECA determination or courier licence located. | Complete incorporation and obtain TIN for the actual applicant; then map MaaleNex-operated and partner-operated service lines; obtain ECA licence for MaaleNex-operated courier service; verify each partner's licence and obtain written ECA/counsel boundary determination; register applicable controller/processor roles before processing. |
| D02 | Data Protection Officer | **UNRESOLVED** — no written threshold determination. | **NOT LOCATED IN SOURCES SEARCHED** — no executed appointment or registration evidence surfaced. | D02–D04 reconciliation plus A2 client/integration inspection recorded. No Cargo client found in reviewed repository/PR #45–#49; passenger-only Google Maps geolocation is separate. Proposed event caps and one-shot coordinate controls are in CARGO-TRACKING-COLLECTION-AND-SUBJECT-COUNTING-SPEC-v1.0.md. Actual runtime, separate partner apps, unique-person counts and sensitive-file scale remain unverified. | Verify any separate/deployed Cargo and partner clients; validate proposed controls before A3; obtain deduplicated subject counts and sensitive-file classification; complete all Article 40 tests; obtain attributed written determination; if triggered appoint qualified DPO and evidence contact publication/Authority communication. |
| D03 | DPIA | **PARTIAL** — DPIA report exists; Owner acceptance required. | **NOT LOCATED IN SOURCES SEARCHED** — repository submission snapshot says no completed DPIA or approval record surfaced. | Conflicting source assessments retained. Dr. Kebene Wodajo's separate DPIA confirmation is recorded in C06 source history; exact repository path/file reference NOT RECOVERED / NOT VERIFIED. | Identify the actual DPIA and its version; reconcile scope and completeness; record Owner acceptance and DPO determination; retain evidence of review. |
| D04 | Data inventory and processing flows | **PARTIAL** — technical inventory described; reconciliation not evidenced. | **NOT LOCATED IN SOURCES SEARCHED** — no MaaleNex cargo-specific inventory/flow map surfaced in the PR #51 submission search. | D04 inventory, forecast reconciliation and A2 client/integration inspection recorded. No Cargo UI/client found in reviewed repository or PR #45–#49; passenger Google Maps geolocation is separate. Proposed collection/event/counting controls are in CARGO-TRACKING-COLLECTION-AND-SUBJECT-COUNTING-SPEC-v1.0.md. Separate partner apps, deployed runtime, distinct subjects, processors/locations and measured volumes remain unverified. | Confirm whether separate/deployed Cargo or partner clients exist; reconcile actual runtime and vendor configurations; validate proposed controls before A3; implement deduplicated subject-count method only after approval; verify file-content classification, partner/processor contracts, hosting/transfers, notices, lawful bases and measured volumes. |
| D05 | Hosting / data residency | **UNRESOLVED** — hosting architecture not evidenced. | **NOT LOCATED IN SOURCES SEARCHED** — no provider contract, hosting-region attestation, backup-location evidence or support-access record surfaced. | NOT RECOVERED / NOT VERIFIED. | Hosting architecture with primary, backup, replica and disaster-recovery locations; provider terms; support-access locations and evidence. |
| D06 | International transfers | **UNRESOLVED** — no transfer assessment supplied. | **NOT LOCATED IN SOURCES SEARCHED** — no completed assessment, safeguards contract or regulator approval surfaced; applicability remains for counsel/DPO to determine. | NOT RECOVERED / NOT VERIFIED. Interdependent with D05. | Transfer assessment, destination/access map, contractual safeguards and any required ECA approval; reconcile with hosting and support arrangements. |
| D07 | Privacy notices, lawful bases and retention schedule | **UNRESOLVED** — no published notice or approved schedule. | **NOT LOCATED IN SOURCES SEARCHED** — L01–L07 contains principles/issues, not final notices or a populated approved processing register. | NOT RECOVERED / NOT VERIFIED. | Published privacy/collection notices; approved lawful-basis register; category-specific retention schedule with triggers, exceptions and communications. |
| D08 | Processor agreements | **UNRESOLVED** — no agreements supplied. | **NOT LOCATED IN SOURCES SEARCHED** — no signed cargo-specific processor agreement surfaced. | NOT RECOVERED / NOT VERIFIED. | Executed processor agreements, security/confidentiality obligations, processing instructions and complete sub-processor list. |
| D09 | Data-subject rights | **UNRESOLVED** — technical handling described; written procedure and tests absent. | **PARTIAL — SOFTWARE ONLY** — PR #51 C05 contains rights-triage controls and exact-head CI evidence; no approved SOP, case records or operational exercise evidence surfaced. | PR #51 head `b81e788b55bb5c988d77412ce54f483106675e82`; Actions run #691. Operational SOP/test evidence NOT RECOVERED / NOT VERIFIED. | Written rights-request procedure, erasure/restriction reconciliation rule, roles/escalation, case evidence and operational test. |
| D10 | Security controls | **UNRESOLVED** — controls described; assurance evidence absent. | **PARTIAL — ENGINEERING EVIDENCE ONLY** — PR #51 and Actions run #691 evidence implemented controls/tests; no consolidated security assessment, key-management evidence, backup/access review, incident exercise or independent report surfaced. | PR #51 exact head and Actions run #691; run link: https://github.com/akefadaka-git/maalenex/actions/runs/45056584444. Broader assurance evidence NOT RECOVERED / NOT VERIFIED. | Control matrix and assurance evidence covering access/privilege, encryption and keys, logging, backups, incident response, vulnerability management and independent testing. |
| D11 | Tombstone / audit-log retention | **PARTIAL** — periods determined; implementation and testing not evidenced. | **PARTIAL — SOFTWARE METADATA ONLY** — PR #51 C06 adds retention metadata/justification fields; final periods are not approved and no purge mechanism is present. | C06 reviewer determinations in 06:21 record; PR #51 C06 metadata and CI evidence. Approved schedule and operational tests NOT RECOVERED / NOT VERIFIED. | Approved period and trigger schedule; strict minimisation; implemented and tested controls; archive/deletion method; no purge until separately approved. |
| D12 | Legal holds | **UNRESOLVED** — technical safeguard described; written procedure absent. | **PARTIAL — SOFTWARE/GOVERNANCE INTENT ONLY** — PR #51 C03/C07 implements hold interlocks/DPO controls; no approved SOP or operational hold/release evidence surfaced. | PR #51 exact head; operational SOP and exercise evidence NOT RECOVERED / NOT VERIFIED. | Written hold authority, intake/notice/release process, annual review, separation of duties, suspension/restart evidence and operational test. |
| D13 | Independent legal opinion and separate professional determinations | **PARTIAL** — reports exist; Owner acceptance required. | **PARTIAL** — L01–L07 supplied but marked NOT APPROVED and not executed; separate independent Legal revalidation and DPO determination pending. | L01–L07 supplied in conversation 22 Nov 2026 18:07:10 UTC; Endalkachew response 23 Nov 2026 06:21; Dr. Kebene Wodajo DPIA confirmation dated 14 Hidar 2019 E.C. Exact separate file paths/signature verification NOT RECOVERED / NOT VERIFIED. | Register entries identifying each report; verify reviewer identity/qualification/date/signature and scope; record Owner acceptance; obtain separate final Legal and DPO decisions. |
| D14 | Accounting, tax and commercial-correspondence retention | **PARTIAL** — legal periods determined; implementation and destruction workflow not evidenced. | **PARTIAL — LEGAL POSITION ONLY** — L01–L07 states EC-1/EC-2 ten-year positions under Commercial Code Proclamation 1243/2021 Arts. 66–67; triggering-date confirmation remains a counsel issue. No approved operational schedule surfaced. | L01–L07 provenance as above; C06 legal position. Approved schedule and destruction-certificate workflow NOT RECOVERED / NOT VERIFIED. | Approved schedule mapping record classes, statutory triggers, latest applicable deadlines, exceptions, custodians, destruction method and certificate workflow. |

## 2. D01 regulatory assessment

D01 is refined into two legally distinct ECA workstreams; the recovered historical category/status is preserved above as a source assessment and is not rewritten:

1. **Personal-data handler registration.** Personal Data Protection Proclamation No. 1321/2024, Article 33(1), requires a data controller or data processor to be registered with the Authority before processing personal data. Article 35(2) provides for a registration certificate valid for two years. ECA identifies itself as the national personal-data protection authority and provides a PDP registration service. The platform is expected to handle customer, sender, recipient, rider and delivery personal data; absent a contrary fact pattern, a registration analysis is mandatory. The legal role(s) and exact applicant entity still require confirmation.
2. **Courier-service licence.** ECA's official Postal Services licensing page states that no person may operate a postal service or express courier service without an ECA licence. ECA's IRIS portal offers a Domestic Express Mail (courier) Service licence for deliveries where sender and recipient are within Ethiopia. Whether MaaleNex itself is the courier operator, rather than a software marketplace arranging delivery through separately licensed operators, depends on its actual contracts, custody/control of consignments, dispatch/rider arrangements, pricing and service responsibility. Do not assume a platform-only label removes licensing obligations; obtain written ECA/counsel classification where the facts are borderline.

**Official sources checked (23 Nov 2026):**
- Personal Data Protection Proclamation No. 1321/2024, Arts. 33–35: https://pdp.eca.et/pdp-proclamation and https://pdp.eca.et/files/pdfs/pdp-proclamation/pdp_personal_data_protection_proclamation_No_1321_2024.pdf
- ECA role and PDP oversight: https://www.eca.et/about/
- ECA PDP registration guide: https://pdp.eca.et/pdp-guide
- ECA postal/courier licensing position: https://www.eca.et/services/
- ECA IRIS Domestic Express Mail (courier) licence service: https://iris.eca.et/

**Owner decision recorded:** C — Hybrid operating model. **Entity dependency:** Owner confirms MaaleNex Technologies PLC is not yet incorporated; incorporation is in process and TIN is not yet available. Application filing must wait for verified legal-entity formation and TIN. Split the service into (a) MaaleNex-operated deliveries and (b) independent partner-operated deliveries. For (a), ECA domestic express-courier licensing is the presumptive requirement and must be evidenced before operations. For (b), verify each partner's current licence and obtain written ECA/counsel confirmation of MaaleNex's platform/intermediary licensing boundary. The actual service-line allocation is not yet evidenced. PDP registration remains a separate workstream; applicant entity and TIN are not yet available because incorporation is in process; controller/processor roles are also not yet verified. D01 remains **PARTIAL** as an assessment and **UNRESOLVED** as a compliance gate; no processing or courier operations may be treated as authorised.

### D01 pre-filing preparation record

The Owner approved hybrid model C. The two service lines, partner licence verification controls and purpose-based controller/processor allocation are documented in [D01 Hybrid Service-Line, Partner Licence and Data-Role Map](D01-HYBRID-SERVICE-LINE-AND-DATA-ROLE-MAP.md). This is a planning record only. Actual partners/licences are not supplied or verified; contracts and operating facts are not yet reconciled; MaaleNex incorporation/TIN remain pending; and PDP/courier filing or operating authority is not established. The map identifies D03 DPIA and D04 inventory/flow reconciliation as dependencies. D01 remains PARTIAL as pre-filing assessment and UNRESOLVED as a compliance gate.

## 3. D02 Article 40 threshold assessment

D02 has a separate pre-appointment assessment in [D02 Article 40 DPO Threshold Assessment](D02-ARTICLE-40-DPO-THRESHOLD-ASSESSMENT.md). Article 40(1) contains three alternative triggers: government-body processing; core activities requiring regular and systematic monitoring on a large scale; or core activities involving large-scale processing of sensitive personal data. The proposed private PLC is in formation and no government-body processing arrangement is evidenced, so limb A is not triggered on current evidence. Monitoring and sensitive-data limbs remain UNDETERMINED because feature configuration, actual/forecast volumes, data categories and D03/D04 records are not yet verified. No DPO mandatory/not-required conclusion is made. D02 remains OPEN.

## 4. Reconciliation notes — do not silently harmonise

The two status columns represent different evidence snapshots and reviewer scopes:

- The 06:30 recovered reconciliation is the later detailed reviewer reconciliation that records D03, D04, D11, D13 and D14 as PARTIAL and the other items as UNRESOLVED.
- The PR #51 repository submission snapshot records a source-search result and distinguishes software/engineering-only evidence from documentary evidence. It records D03 and D04 as NOT LOCATED IN SOURCES SEARCHED, and D09, D10 and D12 as PARTIAL on software/engineering or governance-intent grounds.
- “Not located” is not proof that a document does not exist. “Software-only” is not documentary or operational closure.
- D03 is a material reconciliation discrepancy: the 06:30 record says a DPIA report exists and Dr. Kebene's DPIA confirmation exists; the PR #51 search did not surface a completed DPIA/approval record. Identify and verify the actual report before changing status.
- D13 must preserve the distinction between the Owner-supplied L01–L07 opinion (NOT APPROVED, unsigned/unexecuted in the source record), Endalkachew's legal response, and Dr. Kebene's DPIA confirmation. They are not interchangeable approvals.
- No item is marked CLOSED. The Owner's acceptance of D03/D13 reports has not been recorded in this package.

## 5. Source and evidence register

| Source ID | Record | Provenance / date | Use and limitation |
|---|---|---|---|
| SRC-01 | D01–D14 reconciliation | Library file `Pasted markdown(20261123-063002).md`, saved 23 Nov 2026 06:30 | Primary recovered category/status/closure-prerequisite structure; not a populated evidence-location register. |
| SRC-02 | Endalkachew legal response / C06 | Library file `Pasted markdown(20261123-062134).md`, saved 23 Nov 2026 06:21 | Legal retention determinations and submission protocol; D01–D14 item review was reserved pending register receipt. |
| SRC-03 | Separate 06:32 saved copy | Library file `Pasted markdown(20261123-063246).md` | Preserve as separate historical copy; do not overwrite or assume byte-identical without comparison. |
| SRC-04 | L01–L07 Ethiopian legal-validation opinion | Owner-supplied project conversation, 22 Nov 2026 18:07:10 UTC | Prior legal position and NOT APPROVED conclusion; reviewer identity/qualification/signature/date fields blank in the repository submission record. |
| SRC-05 | Dr. Kebene Wodajo DPIA confirmation | Dated 14 Hidar 2019 E.C. | Independent DPIA confirmation and safeguards; exact file reference and signature verification NOT RECOVERED / NOT VERIFIED. |
| SRC-06 | PR #51 formal revalidation submission comment | https://github.com/akefadaka-git/maalenex/pull/51 | Repository source-search reconciliation, C01–C08 dispositions, and reviewer requests. |
| SRC-07 | PR #51 exact-head CI run #691 | https://github.com/akefadaka-git/maalenex/actions/runs/45056584444 | Engineering verification for head `b81e788b55bb5c988d77412ce54f483106675e82`; not legal approval or production assurance. |
| SRC-08 | ECA official PDP authority / registration | https://www.eca.et/about/ and https://pdp.eca.et/pdp-guide | Confirms ECA's PDP regulator role and registration workflow; does not prove MaaleNex is registered. |
| SRC-09 | Personal Data Protection Proclamation No. 1321/2024 | https://pdp.eca.et/pdp-proclamation | Article 33 prior registration and Article 35 registration certificate; does not prove registration. |
| SRC-10 | ECA courier licensing | https://www.eca.et/services/ and https://iris.eca.et/ | ECA states express courier operators require a licence and lists domestic courier licensing; MaaleNex's operator classification remains fact-dependent. |

## 6. Closure rule

A D-item may be marked closed only after its exact evidence is identified, authenticity/version/authority are verified, applicable reviewer determination is recorded, Owner acceptance is documented where required, and operational tests are available where relevant. Do not close based solely on code, a summary, an unexecuted opinion, a category definition or a reviewer acknowledgement.

## 7. Owner decision

- Register accuracy: **PENDING OWNER REVIEW**
- D03/D13 report acceptance: **PENDING**
- External submission: **NOT AUTHORISED**
- D01–D14 closure: **NOT ESTABLISHED**


## 8. Source-to-implementation reconciliation — 23 November 2026

New controlled addenda:
- [D03 DPIA Source-to-Implementation Reconciliation](D03-DPIA-SOURCE-TO-IMPLEMENTATION-RECONCILIATION.md)
- [D04 Cargo Personal-Data Inventory and Processing-Flow Reconciliation](D04-CARGO-PERSONAL-DATA-INVENTORY-AND-FLOW-RECONCILIATION.md)
- [D02 Article 40 DPO Threshold Assessment](D02-ARTICLE-40-DPO-THRESHOLD-ASSESSMENT.md) — updated with the source-level implementation findings.

**D03 current reconciliation: PARTIAL / NOT VERIFIED-CLOSED.** The recovered independent DPIA confirmation is C06-focused and expressly states that the full D01–D14 register, privacy notices, DPIA screening record and direct technical schema review were not supplied. The complete DPIA report/version was not recovered. Source-level cargo features and risks are now mapped, but the full DPIA, operational configuration, actual/forecast scale, sensitive-file classification, risk scoring and reviewer/Owner closure remain outstanding.

**D04 current reconciliation: PARTIAL / NOT VERIFIED-CLOSED.** Candidate backend fields, tracking/proof flows and forecast arithmetic are now reconciled in D02–D04-FORECAST-TO-SOURCE-RECONCILIATION.md. The Owner-approved forecast is provisional, not actual. The cargo feature branches remain unmerged. Production runtime, mobile/client configuration, deduplicated subject counts, processor/hosting location evidence, partner contracts, actual operational volumes and sensitive-file content remain unverified. No live production processing or zero-volume conclusion is inferred.

**D02 impact:** staged source uses staff-authenticated event-based tracking with optional caller-supplied coordinate pairs; no continuous GPS polling was found in the inspected backend, but no per-dispatch event cap/rate limit or client/device configuration was verified. The approved forecast supports calculated lifecycle-event and named-role-entry envelopes, not deduplicated unique people. Delivery proof and PDF/JPEG/PNG uploads may contain sensitive information; the false-by-default sensitive flag is not a content assessment. Article 40 monitoring and sensitive-data limbs remain UNDETERMINED; no DPO-required or DPO-not-required conclusion is made.

**Preservation:** the historical 06:30 and PR #51 snapshot status columns above are retained unchanged. The new addenda are current source-level reconciliation records and do not rewrite the historical reviewer snapshots. The cargo increments are candidate branches and remain separate from main. No merge, deployment, hosted migration, production activation, external reviewer submission or A5 activity is authorised by these documentation additions.


## 9. Forecast-to-source reconciliation — 23 November 2026

The detailed source reconciliation is [D02–D04 Forecast-to-Source Reconciliation](D02-D04-FORECAST-TO-SOURCE-RECONCILIATION.md). It records the event-based tracking design, optional coordinate collection, absence of a code-level event ceiling, proof fields, file-validation limits, and the difference between named role appearances and deduplicated unique data subjects.

**Important counting qualification:** the calculated sender/recipient/receiver role-entry envelope is not a unique-person count. Stable person identifiers, cross-role deduplication, courier/driver roster counts and file-content classification are still missing. D02 remains IN PROGRESS / UNDETERMINED; D03 and D04 remain PARTIAL / NOT VERIFIED-CLOSED.


## 10. A2 client and integration inspection — 23 November 2026

The reviewed Cargo feature branches PR #45–#49 are backend-only. No Cargo mobile/web client was found in the current repository main tree or the changed-file sets for those Cargo PRs. The separate passenger Android/WebView application declares coarse/fine location permission and uses a one-shot passenger map location action; its source explicitly distinguishes this from driver tracking. Google Maps is therefore recorded as a passenger integration only. Cloudflare R2 is an optional private evidence-storage target and remains disabled by default in the inspected configuration; no live provider configuration or production runtime was inspected.

The proposed control baseline is [CARGO-TRACKING-COLLECTION-AND-SUBJECT-COUNTING-SPEC-v1.0.md](CARGO-TRACKING-COLLECTION-AND-SUBJECT-COUNTING-SPEC-v1.0.md). It defines user-initiated event-bound location capture, event/coordinate frequency ceilings, precision/source metadata, and HMAC-based pseudonymous subject-counting requirements. It is not active policy or A3 authorization. D02 remains UNDETERMINED for the monitoring and sensitive-data limbs; D03 and D04 remain PARTIAL.


## A2 mobility tracking addendum — 23 November 2026

The user's requirement for customer/verified-vehicle-owner tracking of the designated vehicle during an active fleet/ride trip is recorded in [A2-VEHICLE-TRIP-TRACKING-REQUIREMENT-RECONCILIATION.md](A2-VEHICLE-TRIP-TRACKING-REQUIREMENT-RECONCILIATION.md). Passenger app source has map/catalog and scheduled ETA only; no live vehicle location endpoint or customer tracking view was found. Vehicle model currently binds a vehicle to an operator organization and does not evidence an individual owner entitlement. Cargo dispatch-event tracking remains a separate profile. D02 monitoring implications remain UNDETERMINED; D03/D04 remain PARTIAL. No implementation change was made.
