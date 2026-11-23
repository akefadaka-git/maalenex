# Cargo Tracking Collection and Pseudonymous Subject-Counting Specification v1.0

**Document ID:** MN-CARGO-TRACK-001  
**Version:** 1.0  
**Assessment stage:** A2 — read-only reconciliation and controlled specification  
**Status:** PROPOSED CONTROL BASELINE — FOR OWNER REVIEW; NOT ACTIVE  
**Applies to:** MaaleNex Cargo Delivery, including SL-01 MaaleNex-operated and SL-02 independent partner-operated delivery services  
**Authority:** This document specifies proposed controls only. It does not authorize A3 implementation, production processing, device-permission changes, vendor activation, merge, deployment, or a DPO conclusion.

## 1. Purpose and decision boundary

This specification translates the A2 source review into a bounded design for (a) event-based location collection, (b) tracking-event frequency, and (c) deduplicated pseudonymous data-subject counting.

The controls below are proposed for Owner review and technical/legal validation. They become operative only after the required A3 authorization, implementation, A4 verification, and any separate legal/DPO approvals. Until then, the current source behaviour and its gaps remain as recorded in D02–D04.

## 2. A2 source findings and scope

### 2.1 Cargo application evidence

The reviewed Cargo increments are backend-only:

- PR #45, feat/cargo-consignment-backend-v1: consignment model and API.
- PR #46, feat/cargo-dispatch-tracking-v1: dispatch state machine and append-only tracking events.
- PR #47, feat/carrier-operations-delivery-proof-v1: carrier operations, delivery proof and exceptions.
- PR #48, feat/cargo-delivery-evidence-storage-v1: private evidence upload and verification.
- PR #49, feat/cargo-evidence-lifecycle-governance-v1, and PR #51: evidence lifecycle, retention and deletion governance.

The changed-file lists for PRs #45–#49 contain backend, migration, test, workflow and documentation changes; they do not contain a Cargo mobile/web client. The current main tree contains a small passenger frontend, not a Cargo tracking client. No separate Cargo client repository, deployed client build, carrier mobile application, or client-side configuration was evidenced in the reviewed repository.

**Conclusion:** Cargo client-side collection behaviour is NOT VERIFIED because a Cargo client was not located. This is not proof that no separate client or external system exists.

### 2.2 Distinct passenger application behaviour

The separate passenger application contains frontend/src/PassengerGoogleMap.tsx (PR #43 branch, blob 79f633b828544747eaefd4a56ce4df11969ea4ad). Its “Use my location” action calls navigator.geolocation.getCurrentPosition once, with enableHighAccuracy true, a 10-second timeout and maximumAge 60000; the returned point is passed to the Google Maps map's panTo method. The component says this is the passenger's device location and is not driver tracking.

The Android manifest (PR #43 branch, blob f081d76de41d86e3654c19a941a0c7bb091f7bca) declares ACCESS_COARSE_LOCATION and ACCESS_FINE_LOCATION. The WebView geolocation policy (blob 3e95eeeadba01f211a6b63efb644c251cb4f1c90) accepts the packaged app-assets origin only. No ACCESS_BACKGROUND_LOCATION declaration was found in that manifest.

These are passenger-map facts. They must not be attributed to Cargo drivers, couriers or recipients. The passenger Google Maps SDK is an external integration that requires separate vendor, transfer, notice and contractual review if the passenger feature is in scope; it is not evidence of a Cargo tracking feed.

### 2.3 Cargo backend behaviour

The inspected Cargo tracking model and API provide append-only, dispatch-linked events, a monotonically increasing sequence, idempotency key, event type, optional free-text description, optional paired latitude/longitude, occurrence time, server record time and recording staff-user ID. Coordinates are range-validated but have no recorded accuracy, device source, collection-purpose code or explicit per-event collection receipt.

The inspected route accepts caller-submitted events from authorized platform dispatchers or assigned-carrier staff. The normal completed dispatch path generates four lifecycle events (offered, accepted, picked_up, delivered). Additional supported event types include departed, checkpoint, arrived, failed, cancelled and exception. No per-dispatch event ceiling, per-actor rate limit, coordinate frequency ceiling or background polling control was found in the Cargo backend.

The source documentation explicitly excludes continuous GPS polling, live maps, public tracking links and external carrier webhooks from the Cargo tracking increment. The API's 30-day occurrence-time validation window is not a retention period.

### 2.4 External integration inventory

| Integration | Evidence | Cargo relevance / disposition |
|---|---|---|
| Google Maps JavaScript API | Passenger map loads maps.googleapis.com and Google map assets; build expects VITE_GOOGLE_MAPS_API_KEY. | Passenger map only in reviewed code. Not a Cargo tracking integration. Vendor processing, key restrictions, transfer and contract evidence remain D05/D06/D08 work. |
| Cloudflare R2 / S3 API | Cargo evidence upload adapter supports R2-compatible private storage; runtime setting object_storage_enabled defaults to false; credentials and endpoint are required to activate. | Potential Cargo evidence processor/storage provider, not a live integration established by this review. No live R2 account, bucket, credential or region was inspected. |
| SMS / email | Repository README states no SMS/email provider is connected in the reviewed passenger development baseline. | No Cargo messaging provider or delivery-notification integration was identified in reviewed Cargo branches. Separate systems cannot be excluded. |
| Carrier webhooks / telemetry | Cargo tracking design and PR descriptions explicitly exclude external carrier webhooks and continuous GPS. | None identified in reviewed Cargo source. No separate partner system was inspected. |
| IROKA | MaaleNex–IROKA integration is a separate disabled-by-default contract. | No Cargo tracking or location processing through IROKA is evidenced. |

No production configuration, vendor account, processor agreement, hosting region, support-access location, external telemetry account or live database was inspected. D05, D06 and D08 therefore remain open.

## 3. Proposed coordinate-collection controls

### 3.1 Default collection mode

1. **No continuous or background location collection.** Do not implement periodic GPS polling, background location workers, route replay, geofencing, passive device tracking, vehicle telemetry ingestion or automatic location sampling for Cargo.
2. **User-initiated, event-bound capture only.** A permitted courier/carrier staff user may explicitly request a single location fix while submitting a specific Cargo event. The interface must explain the purpose and show that location is optional unless a separately approved legal/operational requirement establishes otherwise.
3. **No silent collection.** Do not request device location at sign-in, app launch, dispatch assignment, or merely because a user opens a tracking screen.
4. **No coordinates by default.** If the user does not request or the device cannot provide a location fix, submit the event without coordinates. Do not block a delivery update solely because location permission is denied or unavailable.
5. **No reuse for unrelated purposes.** Coordinates collected for delivery progress must not be repurposed for staff productivity scoring, route surveillance, attendance, behavioural profiling, marketing or unrelated analytics without a separately assessed and authorized purpose.

An explicit UI action is a collection safeguard; it is not, by itself, proof that consent is the appropriate lawful basis. The lawful basis, notice, controller/processor roles and any worker-related obligations must be determined separately for SL-01 and SL-02.

### 3.2 Permitted event types and limits

Coordinates may be attached only to these event contexts, if the event is operationally necessary:

- picked_up — at most one pickup coordinate.
- checkpoint — at most two manually submitted checkpoint coordinates per dispatch.
- arrived — at most one arrival coordinate, where used as a distinct event.
- delivered — at most one delivery coordinate.
- exception — at most one coordinate when needed to document a material delivery exception.

Do not attach coordinates to offered, accepted, rejected, routine departed, or cancelled events by default. Any additional event type requires a documented purpose and controlled specification revision.

Proposed frequency ceilings:

| Control | Proposed limit |
|---|---:|
| Operator-added supplemental tracking events | Maximum 8 per dispatch |
| Operator-added events for one dispatch | No more than 1 in any 5-minute interval |
| Coordinate-bearing events | Maximum 4 per dispatch, including no more than 2 checkpoint coordinates |
| Coordinate-bearing events for one dispatch | At least 15 minutes between coordinate captures |
| Location fix per event | One single-shot fix; no watch/stream subscription |
| Per-actor API event submissions | Maximum 60 per rolling hour across dispatches, subject to operational validation |
| Normal completed-dispatch lifecycle events | Four expected state-transition records; valid lifecycle transitions must remain state-machine constrained |

The eight supplemental events are in addition to the finite, state-machine-generated lifecycle events. Repeated attempts with the same idempotency key must not create additional records. A rate-limit rejection must not erase or suppress a safety-critical exception; provide a separate auditable exception path that does not permit unlimited location submissions.

These are conservative proposed defaults, not measured operational requirements. Operations must validate them against the actual route duration, exception profile, connectivity constraints and service-line model before A3. Any proposed increase requires a written rationale, updated DPIA/Article 40 review and Owner approval.

### 3.3 Precision, source and payload

- Prefer approximate/coarse device location for Cargo. Do not request fine/high-accuracy location by default.
- Proposed stored precision: round latitude and longitude to **three decimal places** (approximately 100 metres in latitude; longitude distance varies by latitude). Do not store raw higher precision in ordinary Cargo event records.
- Record location accuracy in metres, source (device_coarse, device_fine_exception, or user_selected_map_point), capture time, event ID, dispatch ID, submitting actor pseudonym and purpose code.
- If the device reports accuracy worse than 100 metres, omit the coordinate or mark it as low-confidence; do not silently present it as a verified delivery location.
- device_fine_exception may be used only after a documented necessity assessment and separate Owner approval. The reason must be recorded; no blanket fine-location permission.
- Never put coordinates, precise addresses, recipient identity details or evidence contents in free-text descriptions, URLs, analytics events or routine application logs.
- Keep the event occurrence time and server-recorded time distinct. A device timestamp must not be represented as a server-verified capture time.

The current schema does not contain all proposed metadata fields. This section describes a future design requirement, not an assertion that the fields or controls have been implemented.

### 3.4 Notice, access and user controls

Before any Cargo client captures a location, provide a concise Amharic-first and English notice identifying the event purpose, data captured, recipient/access roles, retention reference, optionality and how to proceed without location. Request the platform/device permission only after the user initiates the relevant action.

Access must remain dispatch-scoped and role-based. No public tracking URL or anonymous map endpoint is proposed. Partner access must be limited to the relevant service line and assigned dispatch. Coordinates must be excluded from general-purpose audit payloads, support exports and customer-facing screens unless a separately approved purpose requires them.

A user must be able to decline location capture and still submit a valid event where location is not a separately justified mandatory field. Permission revocation must stop future capture; it does not automatically erase previously lawfully recorded events, which remain subject to the approved retention and rights process.

## 4. Proposed pseudonymous data-subject counting standard

### 4.1 Counting objective

The purpose is to produce defensible, deduplicated counts of natural persons whose personal data is processed, including people who appear in more than one transaction role. Counts must support monthly, rolling-12-month, annual and peak-period assessment, and must separately expose the population associated with location monitoring and sensitive evidence.

Do not equate any of the following:
- delivery count;
- database row count;
- tracking-event count;
- name-field/role appearance count;
- distinct natural-person count.

The existing sender, recipient and receiver fields are name strings, not stable person identifiers. The current schema cannot reliably deduplicate a person who appears in several roles or consignments. Do not infer identity from name similarity, phone suffixes, addresses or other weak matching.

### 4.2 Approved pseudonymous key design required before measurement

The future counting process must:

1. Resolve a person to a verified, canonical internal person identifier through an authorized identity/party registry. Do not use a name string as the canonical key.
2. Generate a stable, non-reversible reporting token using keyed HMAC-SHA-256 over the canonical identifier, with a secret key held outside source control in an approved secrets manager/KMS. Do not use an unkeyed hash of names, phone numbers, email addresses or national identifiers.
3. Use domain-separated keys/namespaces for controller, legal entity and service line. Cross-controller or partner-level linking is prohibited unless the role allocation, lawful basis, purpose, contract and access are separately documented and approved.
4. Keep the canonical-identity-to-pseudonym mapping separately access-controlled. Analysts and ordinary operations users must not receive the mapping or the HMAC secret.
5. Version the key and document controlled rotation/re-keying so that rotation does not silently split one person's counts or make historical counts incomparable.
6. Treat pseudonymized records as personal data wherever re-identification remains reasonably possible. Pseudonymization is a safeguard, not anonymization.

If no verified canonical person identifier exists, classify the person record as **UNRESOLVED FOR DEDUPLICATION**. Report the unresolved count and its role/source; do not invent a match or include the record in a claimed deduplicated unique-person total.

### 4.3 Required subject dimensions and measures

The counting register must cover, where applicable:

- sender/customer;
- recipient/consignee;
- person receiving the delivery;
- courier/driver and other carrier staff;
- MaaleNex staff;
- partner-organization staff and individual contacts;
- people identifiable in delivery-proof files, signatures, photographs, notes or exception records;
- any other natural person whose personal data is processed through support, complaints or operational communications.

For each period, produce:

| Measure | Required output |
|---|---|
| Distinct natural persons | Deduplicated union across all applicable roles, with unresolved records reported separately |
| Role-specific distinct persons | Unique persons by sender, recipient, receiver, courier/driver, partner staff, MaaleNex staff and file-content subject |
| Location-linked persons | Distinct persons whose data is associated with at least one coordinate-bearing event |
| Monitoring exposure | Coordinate-bearing events per person, first/last event dates, active days and longest observed tracking window |
| Sensitive-data population | Distinct persons represented in files/records classified as sensitive, with unclassified files reported separately |
| Service-line split | SL-01 and SL-02 separately; consolidated total only where the counting method and controller roles permit |
| Activity profile | Monthly distinct, rolling-12-month distinct, annual distinct, peak-day distinct and active/peak concurrent population where measurable |
| Data quality | Matched, unmatched, duplicate-resolution, missing-identifier and estimated/forecast counts, each separately identified |

Report both the deduplicated union and the unresolved population. Never sum role-specific totals to claim the unique-person total. Never combine SL-01 and SL-02 into a single controller population without first validating the actual controller/processor allocation and lawful data-sharing arrangement.

### 4.4 Reporting evidence and governance

Every count report must record:
- measurement window and as-of timestamp;
- source systems, tables and extracts;
- code/query version and pseudonym-key version;
- identity-resolution and deduplication method;
- role taxonomy and service-line allocation;
- matched/unmatched totals and data-quality exceptions;
- exclusions, assumptions and uncertainty;
- observed values separately from forecasts and planning scenarios;
- preparer, reviewer, approval date and evidence reference.

Do not place direct identifiers or HMAC secrets in the report. Preserve a restricted audit trail for the counting run. Any manual identity resolution must be authorized, reason-coded and independently reviewable.

### 4.5 Forecast treatment

The Owner-approved delivery-volume scenario remains a planning assumption only. The existing sender/recipient/receiver role-entry envelope is not a unique-person count. Forecasts must not be converted into unique-person estimates by applying an assumed ratio or deduplication factor without an evidenced, Owner-approved methodology and uncertainty range.

## 5. Retention, disclosure and security dependencies

1. Coordinate-specific retention must be explicitly set in the approved category-based schedule (D07) after purpose and legal requirements are assessed. The 30-day event-time validation window in the current API is not a retention period.
2. Keep location history no longer than necessary for the documented purpose, subject to valid legal holds and applicable statutory obligations. Separate coordinate minimization/deletion from any independently justified event/audit metadata retention.
3. Restrict location access to authorized dispatch participants and approved platform reviewers. Log access without duplicating precise coordinates in audit payloads.
4. Encrypt coordinates in transit and at rest under the approved security architecture. Review backups, replicas, support access and key custody.
5. No coordinates or pseudonymous subject-count datasets may be sent to Google Maps, R2, IROKA, analytics, telemetry, messaging or another vendor for Cargo purposes unless that integration is separately specified, assessed, contractually governed and approved.
6. Private evidence upload remains a separate data flow. File type/signature/size checks do not classify file contents. The evidence workflow must identify and minimize incidental third-party data and sensitive information before live use.

## 6. Required A3 design and A4 verification evidence

Before A3 implementation is considered ready, the Owner-approved scope must include:

- Cargo client/repository identification and exact release-candidate SHA;
- client permission and UI notice design for one-shot, user-initiated location capture;
- API enforcement of event caps, actor/dispatch throttles and idempotency;
- event taxonomy and coordinate eligibility validation;
- coordinate precision, accuracy, source, purpose and capture-time metadata;
- denial, timeout, offline, permission-revocation and low-accuracy behaviour;
- separate SL-01/SL-02 identity and access treatment;
- canonical person identifier and protected pseudonym service design;
- deduplication query specification and repeatable report evidence;
- approved lawful basis, privacy notice, retention schedule and processor/transfer assessments;
- DPIA and Article 40 reassessment based on actual intended configuration and scale.

A4 tests must demonstrate that background collection is absent; no location is captured without the user's explicit action; denied permission does not block non-location events; event and coordinate caps are enforced server-side; idempotent retries do not inflate counts; role duplicates collapse to one pseudonymous person within the permitted controller namespace; unresolved identities are not guessed; and no coordinates leak into logs, URLs or unauthorized responses.

## 7. Open evidence and legal consequences

This specification does not close the following gaps:

- No Cargo mobile/web client was located in the reviewed repository. Separate client repositories, partner apps and deployed builds remain unverified.
- No production database, runtime configuration, live GPS data, actual event counts or measured subject counts were inspected.
- The passenger Google Maps integration is not Cargo tracking and requires its own vendor/transfer review if passenger processing remains in scope.
- R2 is disabled by default in the inspected configuration; live activation and hosting location are not established.
- Actual SL-01/SL-02 partner allocation, courier/driver roster, staff population and partner controller/processor roles remain unverified.
- Sensitive file contents and the number of people represented in those files remain unclassified/unmeasured.

Accordingly, D04 remains **PARTIAL / NOT VERIFIED-CLOSED**. D03 remains **PARTIAL / NOT VERIFIED-CLOSED**. D02's government-body limb remains not triggered on current evidence; the regular/systematic large-scale monitoring and large-scale sensitive-data limbs remain **UNDETERMINED**. This specification does not establish that Article 40 requires or does not require a DPO, and it does not authorize appointment, non-appointment or notification.

## 8. Source pins

| Source | Ref / SHA | Relevance |
|---|---|---|
| Cargo dispatch/tracking model | PR #46, 5455798cf5288b9ae3fb874e0a3cf172f859e114 | Event fields, optional coordinates, sequence and idempotency |
| Cargo dispatch/tracking API | PR #46, fb3f90c1bf46c787470ec4827c83f59cf12b19f0 | Event payload, authorization and append route |
| Cargo dispatch service | PR #46, 212c0d26c6eb327fde8d0b153ecdc35d1c3042d3 | Lifecycle and event taxonomy |
| Cargo dispatch tracking contract | PR #46, 4680c55b22782cfd0ca6e560bfc554df12974519 | Backend-only scope and no continuous GPS |
| Passenger Google Maps client | PR #43, 79f633b828544747eaefd4a56ce4df11969ea4ad | Separate passenger one-shot geolocation |
| Android location manifest | PR #43, f081d76de41d86e3654c19a941a0c7bb091f7bca | Coarse/fine permission declarations |
| Android WebView geolocation policy | PR #43, 3e95eeeadba01f211a6b63efb644c251cb4f1c90 | Trusted app-assets origin |
| Cargo delivery evidence storage | PR #48, 5c612e050bd965904b6013f66405cc93963cf811 | Private storage adapter |
| Runtime configuration | PR #49, ce49e4bf571b47fd2222d0ca630eb18b01bc9831 | Storage disabled by default |

## 9. Change control and approval

- This document is a controlled A2 proposal only.
- It does not change application code, database schema, migrations, workflows, client permissions, vendor configuration or production behaviour.
- It does not supersede the historical source assessments; it adds a proposed future control baseline.
- Any amendment to the numerical limits, coordinate precision, eligible events, identity-linking model or vendor scope requires a versioned change record and Owner approval.
- A3 implementation, A4 verification, merge, A5 deployment and production activation each remain separate gates.

**Disposition:** A2 source inspection recorded; tracking specification proposed for Owner review; implementation not authorized by this document.
