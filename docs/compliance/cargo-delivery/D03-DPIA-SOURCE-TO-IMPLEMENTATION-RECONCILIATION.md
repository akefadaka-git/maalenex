# D03 — DPIA Source-to-Implementation Reconciliation

**Status:** PARTIAL — implementation evidence reconciled at source level; complete DPIA, operational configuration, actual volumes and reviewer closure remain unverified  
**Assessment date:** 23 November 2026  
**Scope:** MaaleNex Cargo Delivery, hybrid service model C (MaaleNex-operated and independently partner-operated deliveries)  
**Purpose:** Reconcile recovered DPIA material against actual staged cargo application features, fields, monitoring configuration and available scale evidence. This is an evidence addendum, not a replacement DPIA or legal opinion.

## 1. Executive finding

The recovered independent DPIA confirmation from Dr. Kebene Wodajo, dated 14 Hidar 2019 E.C., is **not a complete platform DPIA**. The reviewer expressly states that the populated D01–D14 register, privacy notices, DPIA screening record, direct log/tombstone schema review and operational testing evidence were not supplied. The reviewer also states that the assessment did not cover courier contracts, payment arrangements or employment-law aspects of worker monitoring. Its “no special-category data” position is an assumption, not a conclusion established by direct review of the current cargo implementation.

The source review now establishes that staged backend code includes:
- consignment creation and lifecycle;
- dispatch assignment and state transitions;
- append-only tracking events with optional latitude/longitude;
- carrier operational profiles;
- delivery-proof records and exception cases;
- private PDF/JPEG/PNG delivery-evidence upload;
- evidence lifecycle, retention, rights-request and legal-hold metadata;
- actor/action/resource audit events.

These features create identifiable processing involving senders, recipients, carrier staff, MaaleNex staff and potentially other persons represented in uploaded evidence. The code does **not** establish continuous GPS polling, a live map, public tracking links, automatic rider scoring, profiling, facial recognition or biometric identification. Those capabilities were not found in the inspected cargo branches; their absence from these branches is not proof that no other system or later configuration can perform them.

The repository contains no measured production volumes or Owner-approved operating forecast. The cargo increments are unmerged candidate branches, not a deployed cargo service. Consequently, the DPIA can now be grounded in the implemented data model and API behavior, but cannot yet make a defensible quantitative scale or operational residual-risk determination.

**D03 disposition: PARTIAL / NOT VERIFIED-CLOSED.** This addendum narrows the unknowns; it does not complete or approve the DPIA.

## 2. Source and implementation boundary

### 2.1 Recovered DPIA evidence

The recovered independent confirmation:
- identifies customer, recipient and courier identifiers, contact details, location data and delivery records as processing categories described to the reviewer;
- confirms certain C06 tombstone and audit-log retention recommendations subject to minimisation and other safeguards;
- assumes that no special-category data is processed;
- states that the reviewer did not receive the populated D01–D14 register, privacy notices, DPIA screening record or testing evidence;
- states that the reviewer did not directly review the log/tombstone schemas and did not assess courier contracts, payment-processing arrangements or employment-law aspects of monitoring;
- expressly corrects any impression that the reviewer assessed all fourteen internal D01–D14 references.

It is therefore evidence of a limited independent professional confirmation, not proof that the full D03 DPIA has been completed, version-controlled, accepted by the Owner or reconciled to the current code.

### 2.2 Candidate implementation branches

The following cargo increments were located as separate GitHub pull requests and branches. They are candidate backend implementation evidence only; they are not evidence of deployment or production processing.

| PR | Increment | Relevant scope |
|---|---|---|
| #45 | Cargo consignment lifecycle | Consignment records and staff API |
| #46 | Dispatch and append-only tracking | Dispatch assignment and manually appended tracking events |
| #47 | Carrier operations and delivery proof | Carrier profiles, recipient proof, exceptions and review |
| #48 | Private delivery-evidence storage | Dispatch-scoped private file upload and verification |
| #49 | Evidence lifecycle governance | Evidence metadata, holds, access grants, rights requests and retention policy metadata |
| #51 | Legal retention corrective implementation | Additional personal-data classification, legal-basis, transfer, sensitive-data and DPO-control fields |

PR #51 exact head is `b81e788b55bb5c988d77412ce54f483106675e82`; exact-head Actions run #691 succeeded. This is engineering verification, not DPIA approval or proof of deployed operation. The earlier cargo PRs remain separate candidate increments; no hosted migration or cargo production activation is evidenced.

## 3. Reconciled processing features and fields

| Processing activity | Implemented fields / records evidenced | Data subjects and DPIA implications |
|---|---|---|
| Consignment intake | `sender_name`, `recipient_name`, `destination`, `description`, optional `weight_grams`, status, assigned organisation, `created_by`, timestamps, `delivered_at` | Sender and recipient are directly identifiable by name; destination and free-text description may reveal a home/work address, routine or sensitive context. Staff creator is identifiable through a staff-user reference. |
| Dispatch allocation and lifecycle | Carrier organisation, optional `vehicle_id`, dispatch reference, idempotency key, status, `offered_by`, `responded_by`, version and timestamps | Carrier organisation and staff actions are linkable to a person through staff-user records. Vehicle association may increase linkability to an operator/driver. |
| Tracking/checkpoint events | Event type, optional description, optional latitude/longitude pair, `occurred_at`, `recorded_at`, `recorded_by`, dispatch/consignment reference and sequence number | Coordinates linked to a dispatch can reveal a courier's or other person's movement depending on who generated the point and what it represents. The source and subject of each coordinate are not encoded in the field names and must be defined operationally. |
| Carrier profile | Organisation, operational status, service area, operating notes, `updated_by`, timestamps | Organisation data plus free-text operational notes and identifiable staff actions. |
| Delivery proof | `received_by_name`, `evidence_reference`, optional `delivery_notes`, `occurred_at`, `submitted_by`, `reviewed_by`, review reason/status/timestamps | Recipient identity and delivery confirmation. Notes and evidence can contain additional personal or sensitive information. |
| Delivery evidence file | Private object key, content type, content length, upload-intent creation/expiry, verification/attachment timestamps, lifecycle state | File contents are not represented by the database schema. A PDF, JPEG or PNG may contain names, signatures, faces, addresses, labels, identity documents or sensitive information. Actual file content categories are unknown. |
| Exceptions and resolution | Exception code, description, status, resolution code/notes, `reported_by`, `resolved_by`, timestamps | May reveal personal circumstances, disputes, allegations, injury/damage or other sensitive contextual details through free text. |
| Evidence governance | Personal-data-present flag; sensitive-personal-data flag; legal-basis and processing-justification fields; privacy-notice reference; transfer/safeguard references; sensitive-data approval reference; retention, rights-request and deletion-suspension metadata | These fields support governance but do not prove classification is accurate, populated or enforced. A default false sensitive-data flag is not evidence that uploaded content contains no sensitive data. |
| Audit trail | Event type, time, actor type/ID/role, organisation, resource type/ID, action, outcome, reason code, request/correlation IDs and redacted metadata | Identifiable staff activity and access/administrative events. Redaction reduces payload exposure but does not anonymise actor, resource or event metadata. |

Supporting source files and blob SHAs are listed in Section 9.

## 4. Monitoring configuration — what the code does and does not show

### 4.1 Tracking behavior actually evidenced

The tracking API is a staff-authenticated cargo endpoint. A tracking event is submitted as a discrete API request. The payload accepts:
- an event type from a bounded event vocabulary;
- optional free-text description (maximum 300 characters);
- optional latitude and longitude, which must be supplied together and are range-validated;
- an occurrence timestamp with an explicit timezone offset.

The event is associated with a dispatch and consignment, assigned a sequence number, recorded with a staff-user reference and appended to the event history. The route checks that the caller is an assigned carrier or platform dispatcher. An occurrence timestamp is restricted to the previous 30 days and not materially in the future.

**No continuous GPS polling, background location sampling interval, device location permission, live map feed, automatic coordinate ingestion, or public tracking endpoint was found in the inspected cargo backend branches.** The code supports coordinate-bearing events; it does not prove that coordinates are always collected or that a person is continuously tracked.

### 4.2 Monitoring unknowns requiring operational evidence

The application schema does not establish:
- whether a coordinate represents the courier, vehicle, consignment, checkpoint or another location;
- whether coordinates are entered manually or captured from a device;
- who is expected to submit them and how often;
- whether coordinates are required by an operating procedure, optional in practice or disabled by policy;
- whether partners submit events on the same schedule as MaaleNex-operated deliveries;
- whether location history is shown to customers or recipients outside the staff API;
- whether a separate mobile app, third-party system, webhook or integration sends additional location events;
- actual tracking duration per journey, number of points per dispatch, or retention/access behavior in a live environment.

These facts must be resolved before concluding whether courier or customer monitoring is regular and systematic. A recurring checkpoint process can still constitute structured monitoring even without continuous GPS.

### 4.3 Other monitoring and profiling

No implementation of automatic rider performance scoring, worker ranking, behavioural profiling, automated route optimization, fraud-risk scoring or facial/biometric identification was found in the reviewed cargo files. Exception codes and manual review are present; that is not equivalent to an automated profile. Any later addition of these capabilities is a material DPIA and Article 40 reassessment trigger.

## 5. Data collection, storage and access controls evidenced

- Cargo write and review endpoints use authenticated staff context, CSRF protection for mutations and permission checks, including carrier-organisation-scoped permissions.
- Tracking events are append-only, sequence-numbered and idempotency-protected.
- Delivery-proof review is performed by a platform role; accepting proof advances dispatch/consignment status.
- Delivery-evidence upload uses a short-lived (300-second) presigned private object-storage URL scoped to a carrier and dispatch. Accepted types are PDF, JPEG and PNG; maximum size is 10 MiB; the stored object's type, size and file signature are checked.
- The storage client requires explicit enablement and a configured R2-compatible endpoint. The default configuration has object storage disabled.
- The inspected configuration defaults `scheduler_enabled` to false, `object_storage_enabled` to false and `synthetic_data_only` to true. Development/test runtime requires synthetic-only mode and a local database. Production requires explicit non-synthetic configuration, secure cookies and a remote TLS PostgreSQL connection.
- Audit metadata redaction includes keys associated with phone, email, credentials, object keys, evidence references, GPS, coordinates, signatures, consignee, address, location and driver. Actor/resource/event metadata remains identifiable or linkable.
- Evidence governance includes classification and deletion interlocks; it does not establish that production retention, purge or deletion automation is active.

These are source-level controls and defaults. No live production environment, runtime environment variables, object-storage account, database, backup/replica configuration or operational logs were inspected in this reconciliation.

## 6. Sensitive-data reconciliation

The earlier “no special-category data” statement cannot be adopted as a verified fact on the current source evidence.

1. Routine sender/recipient names and ordinary destination information are personal data but are not automatically sensitive merely because they identify a person.
2. Precise coordinates are personal data where linkable to a person; they are not automatically a statutory sensitive category solely because they are precise. Context and inferences matter.
3. Delivery-proof PDFs/images and free-text fields are open-content channels. They may incidentally contain health, disability, identity, religious, political, ethnic or other sensitive information. The schema does not constrain the semantic contents of those files or notes.
4. The PR #51 evidence model includes a sensitive-personal-data flag defaulting to false and fields for sensitive-data review and prior ECA approval references. The existence of these fields is a control-design indicator, not evidence that files are classified or that the flag is accurately populated.
5. No biometric template extraction, facial recognition, fingerprint matching, voiceprint identification or other unique biometric identification operation was found in the reviewed cargo branches. A photograph containing a face is not, without more, proof of biometric identification processing.
6. No evidence currently establishes large-scale processing of sensitive personal data. Equally, the open-content evidence channel and unverified operational data mean the reviewer’s assumption has not been validated.

**Required control before live operation:** define prohibited and permitted evidence content; minimise or redact unnecessary sensitive content; establish a reliable classification and escalation process; record any actual sensitive category and legal basis; and obtain any required prior ECA approval before processing begins. Counsel must confirm the statutory classification against the authoritative text.

## 7. DPIA risk register — implementation-informed, not final

| Risk | Evidence basis | Current treatment / residual gap |
|---|---|---|
| Worker/courier movement surveillance | Optional coordinate-bearing events linked to dispatch, carrier and staff IDs | No continuous polling found. Coordinate source, purpose, frequency, access and worker notice/consultation remain unknown. |
| Recipient privacy and address exposure | Recipient name, destination and delivery proof | Restrict access by role and dispatch; define customer/recipient disclosure and notice; no complete notice evidence located. |
| Sensitive content in evidence files | PDF/JPEG/PNG upload and free-text fields | Private, scoped upload and size/type checks exist; content classification, malware/content review and sensitive-data handling are not evidenced by the reviewed code. |
| Overcollection through free text | Consignment, delivery, carrier and exception descriptions/notes | Length limits only; no semantic minimisation or sensitive-content filter demonstrated. |
| Partner access and role confusion | Hybrid service lines; carrier-scoped permissions and shared platform review | Actual contracts, controller/processor allocations, partner instructions, access reviews and partner volumes remain unverified. |
| Excessive audit/behavioral retention | Actor and event metadata retained in audit records | Redaction exists; approved operational retention schedule, access review and live log schema verification remain open. |
| Re-identification through joined datasets | Consignment, dispatch, coordinate, recipient, evidence and staff identifiers are relationally linked | Purpose-bound access and minimisation require operational validation; no scale or threat-model evidence is available. |
| Data restoration after deletion | Evidence lifecycle and legal-hold/retention metadata | Reviewer requires backup/replica treatment, dry-run and kill switch; no production deletion/purge activation is evidenced or authorised. |

This table is a source-informed risk register, not a completed likelihood/impact assessment. The full DPIA must assign inherent and residual likelihood/impact, affected populations, controls, owners, target dates and acceptance/consultation outcomes using actual operational facts.

## 8. Scale and operational volume evidence

No measured production delivery volume, live cargo dataset, actual active courier/partner count, or Owner-approved forecast was found in the recovered D03/D04 material or inspected repository evidence. CI/test records are synthetic engineering evidence and must not be treated as an operational sample.

The following are **MISSING**, not zero:
- monthly and annual unique senders, recipients, couriers, partner staff and MaaleNex staff;
- consignments and dispatches per day/month/year, including peak-day and peak-month volumes;
- tracking events per dispatch and per day/month/year;
- count and percentage of tracking events carrying coordinates;
- average and maximum tracking duration and event frequency per journey;
- delivery proofs and evidence uploads per day/month/year, plus storage bytes and retention;
- exception cases and support interactions per day/month/year;
- number of active partner carriers, vehicles, service areas, routes, woredas/regions and operating days;
- forecast growth and the assumptions behind the forecast;
- proportion of natural persons subject to repeated location or behavioral monitoring.

For a defensible forecast, Operations must supply an Owner-approved launch-year and 36-month scenario with monthly average and peak-day figures, service-line split (MaaleNex-operated vs partner-operated), geography, active partner/rider counts, event rates and assumptions. Counts must distinguish transactions from unique natural persons and deduplicate people who act as both sender and recipient. Record both measured values (where they exist) and forecast values, with dates and source evidence.

No numeric “large scale” threshold is prescribed in this record. The forecast is evidence for contextual legal analysis, not an automatic threshold calculation.

## 9. Source evidence index

| Source | Branch / PR | Blob SHA | Use |
|---|---|---|---|
| `backend/app/domains/cargo/models.py` | PR #45 / `feat/cargo-consignment-backend-v1` | `45844cac3a126389bd1127e66e7819cac7a1808c` | Sender, recipient, destination, description, weight and lifecycle fields |
| `backend/app/domains/cargo/dispatch.py` | PR #46 / `feat/cargo-dispatch-tracking-v1` | `5455798cf5288b9ae3fb874e0a3cf172f859e114` | Dispatch and tracking-event schema |
| `backend/app/routers/cargo_dispatch.py` | PR #46 | `fb3f90c1bf46c787470ec4827c83f59cf12b19f0` | Tracking payload, coordinate validation, event endpoint/access behavior |
| `backend/app/domains/cargo/carrier_operations.py` | PR #47 / `feat/carrier-operations-delivery-proof-v1` | `1cb5dbbf06977d424a14d4efebcc4cd5734346f1` | Carrier, delivery-proof and exception fields |
| `backend/app/routers/cargo_carrier_operations.py` | PR #47 | `de8b00cc625838f2e42ba1455cfcb38f98ebb1d6` | Proof submission/review and exception operations |
| `backend/app/domains/fleet/object_storage.py` | PR #48 / `feat/cargo-delivery-evidence-storage-v1` | `5c612e050bd965904b6013f66405cc93963cf811` | Private upload types, size and scope |
| `backend/app/domains/cargo/evidence_lifecycle.py` | PR #49 / `feat/cargo-evidence-legal-retention-remediation-v1` | `3de847294781b845bddd1e52b5d453e60ec92ea9` | Evidence lifecycle and initial classification fields |
| `backend/app/domains/cargo/evidence_lifecycle.py` | PR #51 branch / `fix/cargo-evidence-legal-retention-c01-c08` | `022feb4e3d45a1174eaf8b1ed24689b2749d0e65` | Corrective personal/sensitive-data, legal-basis, transfer and DPO metadata |
| `backend/app/domains/audit/models.py` | PR #51 branch | `a87acb1a78be538272ed8ebe386fb484521f3ec1` | Audit-event fields |
| `backend/app/domains/audit/service.py` | PR #51 branch | `219fbfb6341dd928cc96f2dcd0a5bf23443e955c` | Audit metadata redaction |
| `backend/app/core/config.py` | cargo evidence governance branch | `ce49e4bf571b47fd2222d0ca630eb18b01bc9831` | Synthetic-only, scheduler and object-storage defaults |
| `backend/app/jobs/scheduler_worker.py` | PR #49 evidence branch | `f23a6750d541372e26da7e6225d18e43efb0c43f` | Scheduler fail-closed disabled behavior |
| `backend/app/domains/identity/models.py` | PR #46 branch | `d487c9dfd682523b4bf0a40ea3a4586af0991cd6` | Staff identity references |
| `backend/app/domains/organizations/models.py` | PR #46 branch | `1220bfe4021bc825b04af4f7c64242df0f81452a` | Carrier organisation and membership references |
| `backend/app/domains/fleet/models.py` | PR #46 branch | `175eb6a2eabdb3e7707db065dd5cf87032b6fd8d` | Vehicle linkage and compliance-document references |

## 10. Required closure actions

| ID | Required evidence/action | Current status |
|---|---|---|
| D03-01 | Recover the actual complete DPIA, screening record, version, author and scope | MISSING / NOT RECOVERED |
| D03-02 | Confirm the DPIA explicitly covers the PR #45–51 feature set and the hybrid SL-01/SL-02 model | PARTIAL — source features mapped here; full DPIA reconciliation pending |
| D03-03 | Complete end-to-end D04 data inventory and data-flow map | PARTIAL — source fields mapped; processors, live destinations and actual configuration unknown |
| D03-04 | Obtain measured or Owner-approved forecast volumes and monitoring metrics | MISSING |
| D03-05 | Determine the source, purpose, frequency, duration and subject of every coordinate-bearing event | MISSING |
| D03-06 | Review representative evidence-file categories and free-text controls; establish sensitive-data classification | MISSING |
| D03-07 | Reconcile controller/processor roles, partner access, hosting, transfers, notices and lawful bases | UNRESOLVED |
| D03-08 | Complete risk scoring, mitigation ownership, residual-risk acceptance and any required consultation | NOT RUN / NOT EVIDENCED |
| D03-09 | Obtain qualified reviewer’s attributed written D03 conclusion and Owner acceptance | NOT OBTAINED |

**Closure rule:** D03 remains PARTIAL until the complete DPIA is recovered or prepared, the above evidence is reconciled, actual/forecast operational scale is recorded, residual risks are assessed and the qualified reviewer and Owner decisions are documented. No DPO conclusion is made by this addendum.


## Owner-approved provisional operating-volume scenario — 23 November 2026

The Project Owner approved a staged capacity-planning scenario recorded in [Cargo Operational-Volume Planning Baseline](CARGO-OPERATIONAL-VOLUME-PLANNING-BASELINE.md): initial launch average 10 deliveries/operating day (peak 20), Year 2 average 30 (peak 60), and Year 3 average 75 (peak 150), using 26 operating days/month. Approximate average-basis monthly volumes are 260, 780 and 1,950; annualised estimates are 3,120, 9,360 and 23,400.

**Evidence classification:** OWNER-APPROVED PROVISIONAL PLANNING ASSUMPTIONS — NOT ACTUAL VOLUMES. These figures are not a regulatory threshold, not a legal safe harbour and not a DPO determination. They do not supply unique-subject counts, tracking-event frequency/duration, coordinate-bearing proportions, evidence-file volumes/content classifications or the SL-01/SL-02 split. D03 remains PARTIAL / NOT VERIFIED-CLOSED; measured operational evidence and complete DPIA/reviewer closure remain outstanding.
