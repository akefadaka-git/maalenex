# D04 — Cargo Personal-Data Inventory and Processing-Flow Reconciliation

**Status:** PARTIAL — source-level field inventory and candidate data flows mapped; runtime configuration, processors/locations, actual operational volumes and live validation remain missing  
**Assessment date:** 23 November 2026  
**Scope:** MaaleNex Cargo Delivery; hybrid service model C  
**Purpose:** Establish a code-grounded inventory of actual staged cargo application fields and flows for D03/D02 reconciliation. This is not a live-data inspection or a completed legal processing register.

## 1. Executive result

The recovered D04 status states that a technical inventory had been described but was not reconciled to the DPIA. The repository submission search did not locate a cargo-specific inventory/flow map. This document now provides the source-level reconciliation against the staged backend code.

The inventory is based on candidate branches associated with PRs #45–#51. The cargo increments are separate, unmerged pull requests and are not evidence of a deployed cargo service. No production database, production configuration, actual customer/recipient/courier records, hosted object-storage bucket, live logs or operational volumes were available for inspection.

**D04 disposition: PARTIAL / NOT VERIFIED-CLOSED.** Source fields and main backend flows are now identified. Actual data collection, end-user interfaces, production configuration, processor locations, partner flows, volumes and file-content categories remain unresolved.

## 2. Data-subject categories

| Data-subject group | Data linked in the staged model | Status / limitation |
|---|---|---|
| Sender / customer | Sender name; consignment and delivery references; destination; cargo description; linked status and event history | Direct name field verified. Phone/email and other contact channels were described in earlier processing materials but are not fields in the inspected consignment model; exact source and storage are not verified here. |
| Recipient / consignee | Recipient name; destination; delivery proof received-by name; delivery notes; evidence reference/file; event history | Direct name and delivery fields verified. Additional contact details are not present in the inspected cargo consignment model. |
| Courier / carrier staff | Staff-user ID references for dispatch offers/responses, tracking event recording, proof submission, exception reporting/resolution and review; linked staff display name/login identifier | Staff action linkability verified. Employment, device, location-source and worker-monitoring facts require operational evidence. |
| Partner carrier organisation | Organisation ID, display name/status, operational status, service area and operating notes | Organisation fields verified; natural-person contact details and contract data not included in the inspected organisation model. |
| MaaleNex platform staff | Staff-user identity, role, organisation membership and actor references in cargo/audit records | Staff-user model includes login identifier and display name; actor IDs and role snapshots appear in audit records. |
| Vehicle operator / associated persons | Optional vehicle ID on dispatch; vehicle reference and organisation link; compliance-document evidence references and reviewer IDs in fleet model | Vehicle association verified. The inspected vehicle schema does not itself establish a driver GPS feed or driver profile. Vehicle compliance files may contain additional personal data; exact file content is unknown. |
| Persons incidentally represented in evidence | Any person whose name, signature, face, address, identity document or other personal information appears in a PDF/JPEG/PNG or free-text field | Possible because evidence content is not semantically constrained by the file type. Actual occurrence and category are unknown. |
| Government-body personnel | No government-body customer or processing arrangement was evidenced in reviewed materials | Not established; reassess if a public-sector customer or processing instruction is introduced. |

## 3. Field-level inventory

### 3.1 Consignment and intake

**Source:** `backend/app/domains/cargo/models.py`, PR #45, blob `45844cac3a126389bd1127e66e7819cac7a1808c`.

| Field | Classification / subject link | Purpose evidenced by code | Open issue |
|---|---|---|---|
| `id` | Random UUID; record identifier | Consignment identity and relational linkage | Linkability through related tables |
| `organization_id` | Organisation identifier | Tenant/owner scoping | Controller/processor role per service line |
| `consignment_reference` | Business reference; potentially linkable | Operational lookup | Whether externally exposed |
| `idempotency_key` | Technical identifier | Duplicate request prevention | Ensure no user-entered identifier is reused |
| `sender_name` | Sender personal data | Identify sender | Lawful basis, notice and any contact linkage |
| `recipient_name` | Recipient personal data | Identify recipient | Recipient notice and accuracy |
| `destination` | Address/location information; may identify a residence/workplace | Delivery destination | Precision, address source and access |
| `description` | Free text; potentially personal/sensitive by content | Describe cargo/consignment | Data minimisation and prohibited-content rules |
| `weight_grams` | Usually non-personal operational data | Cargo handling | Context may reveal sensitive delivery type |
| `status`, `assigned_organization_id` | Operational metadata, linkable to parties | Lifecycle and assignment | Partner role/access |
| `created_by`, timestamps, `delivered_at` | Staff ID and activity metadata | Accountability and lifecycle | Retention and access controls |

### 3.2 Dispatch and tracking

**Sources:** `backend/app/domains/cargo/dispatch.py`, blob `5455798cf5288b9ae3fb874e0a3cf172f859e114`; `backend/app/routers/cargo_dispatch.py`, blob `fb3f90c1bf46c787470ec4827c83f59cf12b19f0`; PR #46.

| Field | Classification / subject link | Purpose evidenced by code | Open issue |
|---|---|---|---|
| `dispatch_reference`, dispatch UUID | Operational identifiers | Dispatch lookup | External exposure and linkability |
| `consignment_id` | Link to sender/recipient/delivery record | Join dispatch to consignment | Joined-data access |
| `carrier_organization_id` | Partner/operator organisation identifier | Carrier assignment and access scope | Contract and role allocation |
| `vehicle_id` | Link to fleet vehicle | Optional vehicle assignment | Whether driver identity/location is linked elsewhere |
| `status`, `version`, timestamps | Operational/activity metadata | Dispatch lifecycle | Retention and reporting uses |
| `offered_by`, `responded_by` | Staff-user identifiers | Accountability for dispatch actions | Worker activity monitoring and access |
| `event_type`, sequence number, idempotency key | Tracking/event metadata | Append-only progress history | Event taxonomy and event rate |
| `description` | Free text | Checkpoint or event description | May contain unnecessary personal/sensitive information |
| `latitude`, `longitude` | Precise coordinate pair, potentially personal data when linkable | Optional event location | Coordinate subject, source, precision, frequency and duration not specified |
| `occurred_at`, `recorded_at` | Time/location-linked event metadata | Distinguish occurrence from recording time | Time-series reconstruction and retention |
| `recorded_by` | Staff-user identifier | Event accountability | Staff activity monitoring |

The API requires latitude and longitude together, validates geographic bounds and accepts discrete event submissions. The inspected route restricts event submission to assigned carriers/platform dispatchers and limits occurrence timestamps to the previous 30 days and not materially in the future. No continuous GPS polling or sampling configuration was found.

### 3.3 Carrier operations, delivery proof and exceptions

**Sources:** `backend/app/domains/cargo/carrier_operations.py`, blob `1cb5dbbf06977d424a14d4efebcc4cd5734346f1`; `backend/app/routers/cargo_carrier_operations.py`, blob `de8b00cc625838f2e42ba1455cfcb38f98ebb1d6`; PR #47.

| Field | Classification / subject link | Purpose evidenced by code | Open issue |
|---|---|---|---|
| Carrier `service_area`, `operating_notes`, status | Organisation and free-text operational metadata | Carrier setup and eligibility | Notes minimisation and personal data in text |
| `received_by_name` | Recipient/receiver personal data | Delivery proof | Identity verification method not established |
| `evidence_reference` | Opaque reference to private evidence | Link proof to file | Keep URL, object key and access credentials out of logs/public APIs |
| `delivery_notes` | Free text | Delivery context | Content minimisation and sensitive data |
| `occurred_at` | Delivery timestamp | Evidence of delivery event | Timezone/accuracy and retention |
| `submitted_by`, `reviewed_by` | Staff-user identifiers | Proof accountability | Access/worker monitoring |
| `review_reason`, proof status | Free text and decision metadata | Review and acceptance/rejection | Avoid unnecessary personal detail |
| `exception_code`, `description` | Operational code and free text | Record failed/exceptional delivery | Descriptions may reveal personal circumstances |
| `resolution_code`, `resolution_notes` | Decision and free text | Resolve exception | Content and retention review |
| `reported_by`, `resolved_by` | Staff-user identifiers | Accountability | Worker activity monitoring |

### 3.4 Private delivery-evidence files and lifecycle metadata

**Sources:** `backend/app/domains/fleet/object_storage.py`, blob `5c612e050bd965904b6013f66405cc93963cf811`; `backend/app/domains/cargo/evidence_lifecycle.py`, PR #49 blob `3de847294781b845bddd1e52b5d453e60ec92ea9` and PR #51 branch blob `022feb4e3d45a1174eaf8b1ed24689b2749d0e65`.

**Upload behavior:** only PDF, JPEG and PNG are accepted; maximum object size is 10 MiB; the presigned URL expires after 300 seconds; the object key is scoped to the carrier organisation and dispatch; the stored object is checked for content type, size and file signature. The code uses private S3-compatible object storage and supports the R2 provider; object storage is disabled by default in the inspected configuration.

**Metadata inventory:**
- evidence ID, carrier organisation ID, dispatch ID, optional delivery-proof ID;
- private object key, content type and content length;
- upload-intent creation/expiry, verification and attachment timestamps;
- lifecycle state and retention-policy version/start/expiry;
- classification status and reviewer/classifier references;
- personal-data and sensitive-personal-data flags;
- accounting/commercial classification fields;
- personal-data legal basis, processing justification and privacy-notice reference;
- international-transfer flag, safeguard reference and sensitive-data ECA approval reference;
- operational retention basis/justification and DPIA reference;
- rights-request status, deletion suspension, storage-deletion timestamp and failure code;
- legal-hold, access-grant, deletion-request and rights-request records.

**Important limitation:** file metadata does not describe the actual bytes. A file may include receiver names, signatures, faces, labels, addresses, ID documents or sensitive content. File-type validation is not content classification. The default false value for the sensitive-data flag is not proof that the file contains no sensitive personal data.

### 3.5 Identity, organisation, vehicle and audit linkages

| Record | Source fields | Relevance |
|---|---|---|
| Staff user | `staff_users.login_identifier`, `display_name`, status and timestamps; PR #46 blob `d487c9dfd682523b4bf0a40ea3a4586af0991cd6` | Resolves staff-user IDs stored on cargo records |
| Organisation | `organization_type`, `display_name`, status and timestamps; PR #46 blob `1220bfe4021bc825b04af4f7c64242df0f81452a` | Resolves operator/carrier organisations |
| Vehicle | Organisation ID, `vehicle_reference`, status and review status; PR #46 blob `175eb6a2eabdb3e7707db065dd5cf87032b6fd8d` | Optional dispatch vehicle linkage |
| Audit event | Event type/time, actor type/ID/role, organisation, resource type/ID, action, outcome, reason code, request/correlation IDs and redacted metadata; PR #51 blob `a87acb1a78be538272ed8ebe386fb484521f3ec1` | Captures staff actions and resource access/change metadata |
| Audit redaction | Redacts keys associated with phone, email, credentials, object/evidence references, GPS, coordinates, signatures, consignee, address, location and driver; PR #51 blob `219fbfb6341dd928cc96f2dcd0a5bf23443e955c` | Reduces sensitive payload logging; actor/resource metadata remains linkable |

## 4. End-to-end candidate data-flow map

The following is the flow evidenced by source structure. It must be validated against the final deployed architecture and actual contracts.

1. **Sender/customer or MaaleNex staff → consignment API/database.** Sender name, recipient name, destination, description and optional weight are entered. A staff-user ID and organisation/tenant context are linked.
2. **MaaleNex dispatch staff → dispatch API/database.** A consignment is assigned to an approved carrier organisation and optionally a vehicle. Offer/response and status transitions are recorded with staff identifiers.
3. **Assigned carrier staff → tracking API/database.** Discrete status/checkpoint events are appended. Optional coordinates and event descriptions may be attached. Events link to dispatch and consignment records.
4. **Assigned carrier staff → private object storage.** A short-lived upload intent is created for one dispatch; a PDF/JPEG/PNG evidence file is uploaded to a private object key. The API verifies type, size and signature and stores an evidence reference/metadata.
5. **Assigned carrier staff → delivery-proof API/database.** Receiver name, evidence reference, notes and occurrence time are submitted. Platform reviewer accepts or rejects proof; accepted proof closes dispatch/consignment and appends a delivery event.
6. **Carrier staff → exception API/database.** Exception code/description and later resolution details are stored; actor identifiers and audit events are recorded.
7. **Platform operations, Legal/Compliance and authorised reviewers → evidence governance endpoints/database.** Classification, legal basis, transfer references, holds, rights requests, access grants and deletion approvals are recorded.
8. **Audit service → audit database.** Actor, role, organisation, resource, action, outcome, request/correlation and redacted metadata are recorded.

### 4.1 External processors and data locations

| System / recipient | Evidence | Current status |
|---|---|---|
| PostgreSQL application database | SQLAlchemy models and Alembic migrations | Database technology evidenced; production provider, region, backups, replicas and support-access locations NOT VERIFIED |
| Private S3-compatible object storage / Cloudflare R2 support | Object-storage code accepts R2-compatible endpoint and private bucket configuration | Provider capability evidenced; actual provider, contract, region, account, backup and access location NOT VERIFIED; disabled by default |
| MaaleNex-operated service line | Owner-approved hybrid service-line model | Proposed role documented; actual contracts and processing activity not evidenced |
| Independent courier partners | Carrier-scoped API permissions and partner organisation model | Partner access capability evidenced; actual partners, contracts, instructions, independent controller/processor status and sub-processors NOT VERIFIED |
| ECA / public authorities | Regulatory and rights obligations may require disclosures | No live data-sharing integration or government processing contract evidenced |
| Analytics, maps, tracking or messaging providers | No cargo-specific integration identified in reviewed branches | NOT IDENTIFIED in inspected source; cannot exclude separate systems or future integrations |

Do not infer that R2 is the active production provider or that data is stored in Ethiopia. Hosting/data residency and international transfer questions remain D05/D06 dependencies.

## 5. Processing purposes and role allocation — provisional

| Purpose | Likely data used | Candidate actor/role | Required confirmation |
|---|---|---|---|
| Accept and manage a consignment | Sender/recipient names, destination, cargo description, weight, status | MaaleNex and/or contracted operator, depending on service line | Who determines collection purpose, required fields, notices and retention |
| Allocate and perform delivery | Carrier, staff and vehicle identifiers; dispatch status | MaaleNex-operated team or partner carrier | Who controls dispatch, staff instructions and delivery execution |
| Provide progress updates | Event type/time, optional coordinates, consignment linkage | MaaleNex platform and carrier staff | Whether customer/recipient sees tracking; coordinate source and monitoring purpose |
| Verify delivery | Receiver name, proof file, notes and time | Carrier submits; platform reviews | Whether receiver is informed and whether signature/photo is necessary |
| Resolve delivery exceptions | Exception code, descriptions and resolution notes | Carrier and platform operations | Lawful basis, content restrictions and partner disclosure |
| Secure and govern evidence | Evidence bytes/metadata, actor and audit data | MaaleNex; object-storage provider if configured | Processor contract, location, sub-processors, access and deletion |
| Compliance and legal hold | Classification, retention, rights and hold metadata | MaaleNex Legal/Compliance and authorised reviewers | Authority, DPO role, access, retention and separation of duties |

This table is a provisional functional map, not a final legal controller/processor determination. Apply the D01 purpose-based role map to executed contracts, actual decision-making and service-line conduct. A partner does not automatically become a processor merely because it receives an API account; the role depends on who determines purposes and essential means.

## 6. Monitoring and configuration inventory

| Control / feature | Source-level result | Runtime / operational result |
|---|---|---|
| Continuous GPS polling | NOT FOUND in inspected cargo branches | NOT VERIFIED across separate mobile apps/integrations |
| Manual/discrete tracking events | IMPLEMENTED; optional coordinate pair and event timestamp | Actual event frequency and use NOT PROVIDED |
| Coordinate precision | Latitude/longitude numeric values validated to geographic bounds | Device accuracy, rounding, source and retention NOT PROVIDED |
| Event recency | API accepts occurrence time within previous 30 days and not materially future | Operational event latency NOT MEASURED |
| Public tracking link | NOT FOUND in inspected cargo backend | Other frontends/integrations NOT VERIFIED |
| Rider scoring/profiling | NOT FOUND in inspected cargo backend | Other systems and manual performance processes NOT VERIFIED |
| Facial/biometric identification | NOT FOUND | Evidence-file contents and any external identity process NOT VERIFIED |
| Analytics/automated risk scoring | NOT FOUND in inspected cargo branches | External analytics or manual analysis NOT VERIFIED |
| Scheduler | Default `scheduler_enabled=false`; worker exits when disabled | No live worker configuration inspected; production activation not evidenced |
| Object storage | Default `object_storage_enabled=false`; explicit endpoint/credentials required | No active production bucket/configuration inspected |
| Synthetic-data boundary | `synthetic_data_only=true` default; development/test requires synthetic-only mode | Production runtime values and any real-data processing NOT INSPECTED |

The default settings are source defaults, not proof of the values in any hosted environment. PR #51 states no hosted migration, deployment, production policy activation, production deletion or scheduler activation occurred.

## 7. Operational volumes and scale evidence

**No numeric operational volume or forecast was recovered.** The current evidence does not provide measured or approved values for any of the following:

| Metric | Required breakdown | Current status |
|---|---|---|
| Unique senders/customers | Monthly/yearly; deduplicated natural persons | MISSING |
| Unique recipients | Monthly/yearly; deduplicated natural persons | MISSING |
| Couriers/riders and partner staff | Active and occasional; by service line/partner | MISSING |
| MaaleNex staff/admin users | Active users by role and access scope | MISSING |
| Active carrier partners | Count, service area, operating days | MISSING |
| Consignments and dispatches | Average day, peak day, monthly, annual | MISSING |
| Tracking events | Total and per dispatch; event-type distribution | MISSING |
| Coordinate-bearing events | Count/percentage, source, frequency and per-person duration | MISSING |
| Delivery proofs and uploads | Count, file type, average/max size and storage growth | MISSING |
| Exceptions | Count, category and linked people | MISSING |
| Geographic scope | Routes, towns/woredas, regions, cross-border activity | MISSING |
| Retention exposure | Active/archived evidence, event history, audit data and backups | MISSING |
| Growth forecast | Launch year and 36-month base/low/high assumptions | MISSING |

The absence of records in this repository search is not a zero-volume result. Test fixtures and CI results are not a production sample. No database query or production telemetry was available.

### 7.1 Forecast dataset required

Operations should produce an Owner-approved forecast with:
- monthly average and peak-day values for launch year and years 2–3;
- MaaleNex-operated versus partner-operated split;
- active partner, vehicle, courier and staff counts;
- unique sender/recipient/courier counts, with deduplication methodology;
- deliveries per courier and operating days;
- tracking events per dispatch, percentage carrying coordinates, average and maximum event frequency, and tracking duration;
- proof/evidence upload counts and bytes per delivery;
- exception and support-contact rates;
- service-area expansion assumptions and peak-season factors;
- source, author, date, confidence and approval for every assumption.

Keep observed values, forecasts and scenarios separate. Do not create an assumed numeric threshold for “large scale”.

## 8. D04 completeness and gap register

| ID | Gap | Status | Closure evidence |
|---|---|---|---|
| D04-01 | Source-level cargo field inventory | PARTIAL — mapped in Sections 2–3 | Recheck against exact release candidate and any UI/mobile/third-party integration |
| D04-02 | End-to-end source data-flow | PARTIAL — candidate backend flow mapped in Section 4 | Architecture diagram, deployed endpoint list, actual integrations and contracts |
| D04-03 | Data subjects and source of each field | PARTIAL | Confirm actual intake screens, field provenance, optional/required behavior and notices |
| D04-04 | Location monitoring source/configuration | MISSING | Device/source, purpose, sampling, frequency, precision, subject, duration, access and retention |
| D04-05 | Uploaded-file content categories and sensitive-data classification | MISSING | Representative content taxonomy, content minimisation and classification/approval procedure |
| D04-06 | Processor/subprocessor and hosting locations | MISSING | Hosting contract, region, backup/replica/DR, support-access map, object-storage contract and processor agreements |
| D04-07 | Actual and forecast operational volumes | MISSING | Owner-approved measured/forecast volume dataset and assumptions |
| D04-08 | Service-line controller/processor allocation | PARTIAL — D01 map exists | Executed partner contracts and actual decision-making/data-sharing practices |
| D04-09 | Retention and access by category | PARTIAL — technical metadata exists | Approved schedule, production configuration, tested access and retention behavior |
| D04-10 | Reconciliation to privacy notices and lawful bases | MISSING | Published notices and approved purpose/lawful-basis register |

## 9. Source index

The principal source blobs are listed in D03 Section 9. Additional source files directly relevant to D04:
- `backend/app/domains/identity/models.py` — PR #46, blob `d487c9dfd682523b4bf0a40ea3a4586af0991cd6`.
- `backend/app/domains/organizations/models.py` — PR #46, blob `1220bfe4021bc825b04af4f7c64242df0f81452a`.
- `backend/app/domains/fleet/models.py` — PR #46, blob `175eb6a2eabdb3e7707db065dd5cf87032b6fd8d`.
- `backend/app/domains/audit/models.py` — PR #51 branch, blob `a87acb1a78be538272ed8ebe386fb484521f3ec1`.
- `backend/app/domains/audit/service.py` — PR #51 branch, blob `219fbfb6341dd928cc96f2dcd0a5bf23443e955c`.
- `backend/app/core/config.py` — cargo evidence governance branch, blob `ce49e4bf571b47fd2222d0ca630eb18b01bc9831`.
- `backend/app/jobs/scheduler_worker.py` — PR #49 evidence branch, blob `f23a6750d541372e26da7e6225d18e43efb0c43f`.

## 10. D04 closure rule

D04 may be closed only after this source-level inventory is reconciled to the release candidate, actual UI/mobile and external integrations, executed service-line/partner contracts, hosting and processor evidence, published notices, approved lawful bases, retention/access configuration and actual/forecast operational volumes. The resulting inventory must be signed/versioned and used as the authoritative input to the completed D03 DPIA and D02 Article 40 assessment.

**Current D04 status: PARTIAL — source fields and candidate backend flows mapped; live configuration, processors/locations, operational volumes and complete legal/operational reconciliation remain MISSING or UNVERIFIED.**
