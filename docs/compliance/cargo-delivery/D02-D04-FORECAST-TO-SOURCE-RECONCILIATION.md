# D02–D04 Forecast-to-Source Reconciliation — Tracking, Delivery Proof and Data Subjects

**Assessment date:** 23 November 2026  
**Status:** PARTIAL / NOT VERIFIED-CLOSED  
**Scope:** MaaleNex Cargo Delivery, hybrid service model C  
**Evidence boundary:** Source-level review of the relevant staged cargo PRs #45–#49 and #51. PR #50 is a separate parallel retention-remediation branch and is not in PR #51's ancestry or used as the tracking/proof baseline here. The reviewed feature PRs remain open and unmerged; the inspected code is not evidence of a deployed or operational production configuration.

## 1. Purpose and controlling forecast

This reconciliation tests the Owner-approved provisional planning scenario against the cargo backend design. The forecast is a capacity scenario, not actual activity, a legal threshold, a launch commitment or a DPO determination.

| Metric | Initial launch | Year 2 | Year 3 |
|---|---:|---:|---:|
| Average deliveries / operating day | 10 | 30 | 75 |
| Peak deliveries / operating day | 20 | 60 | 150 |
| Operating days / month | 26 | 26 | 26 |
| Average-basis deliveries / month | 260 | 780 | 1,950 |
| Average-basis deliveries / year | 3,120 | 9,360 | 23,400 |

The forecast is combined across SL-01 MaaleNex-operated and SL-02 partner-operated services. No split has been approved. Calculations below assume one completed dispatch per forecast delivery solely to make the planning arithmetic transparent; the source schema does not enforce one dispatch per consignment and actual retries/reassignments may increase dispatch and event counts.

## 2. Tracking configuration — source-verified design

### 2.1 What the inspected backend implements

- Tracking is exposed as a staff-authenticated POST endpoint for appending an event to a dispatch. The caller must have platform dispatch permission or assigned-carrier dispatch permission and pass CSRF validation.
- The payload accepts an event type, optional free-text description (maximum 300 characters), optional latitude and longitude, and an optional occurrence timestamp.
- Latitude and longitude must either both be supplied or both be absent. Coordinates are optional at the API schema level; the inspected backend does not automatically obtain them from a device location service.
- The normal dispatch lifecycle creates an initial `offered` event and records events for status transitions. A completed successful path ordinarily produces four system-created events per dispatch: `offered`, `accepted`, `picked_up`, and `delivered`.
- A caller can append additional events (including `checkpoint`, `arrived`, `departed`, and other allowed event types). No per-dispatch event maximum, polling interval, coordinate-frequency ceiling or endpoint rate limit was found in the inspected route.
- The submitted event occurrence time must be within the previous 30 days and no more than five minutes in the future. This is an input-validation window, not a retention period.
- Tracking history reads are paginated up to 250 items per response; that read limit does not cap event creation.
- The inspected backend does not show continuous GPS polling, a background location worker, a live map feed or an automated location sampling schedule. This is a source-level absence only: no complete mobile/web client, device permission configuration, external map SDK, telemetry integration or deployed runtime was reconciled.

### 2.2 Forecasted event-record envelope

Assuming one completed dispatch per forecast delivery and the normal four-event lifecycle:

| Metric | Initial launch | Year 2 | Year 3 |
|---|---:|---:|---:|
| Baseline lifecycle tracking events / month | 1,040 | 3,120 | 7,800 |
| Baseline lifecycle tracking events / year | 12,480 | 37,440 | 93,600 |

These are calculated baseline event records, not a maximum. Additional manual events, failed dispatches, reassignments and repeat dispatches can increase the totals. Because the API has no source-verified event-frequency cap, no defensible upper bound can currently be assigned.

### 2.3 Coordinate collection conclusion

**Coordinates are permitted but not required by the inspected API.** The code provides no configured coordinate percentage, purpose code, precision/accuracy requirement, device source, collection interval, event-level retention rule or explicit coordinate opt-in control. The approved low-monitoring planning intent (event-based updates; no continuous GPS polling; coordinates only for a documented operational need) is therefore not yet fully enforced by the source design.

- Planned coordinate-bearing event count: **UNKNOWN**.
- Planned coordinate-bearing percentage: **UNKNOWN**.
- Coordinate source and device permission behaviour: **NOT VERIFIED**.
- Frequency/duration and rate limiting: **NOT VERIFIED / NO CODE-LEVEL CEILING FOUND**.
- Continuous/background collection: **NOT FOUND IN INSPECTED BACKEND; CLIENT AND RUNTIME NOT REVIEWED**.

The four-event baseline should not be described as four GPS observations: the automatically generated lifecycle events do not populate coordinates in the inspected implementation. Coordinates can be added to additional caller-submitted events.

## 3. Delivery-proof content and evidence files

### 3.1 Structured proof fields

The inspected proof endpoint requires:
- `received_by_name` (1–160 characters);
- an evidence reference (8–255 characters on the legacy proof route; the lifecycle route links an evidence record);
- an occurrence timestamp with an explicit timezone offset.

Delivery notes are optional free text up to 500 characters. The proof model also stores dispatch/consignment references, submission actor, review actor, review reason and timestamps. One proof row is permitted per dispatch. The proof route is available to assigned-carrier users with the delivery-proof permission.

The consignment model separately requires sender name, recipient name, destination and cargo description; weight is optional. Exception descriptions and resolution notes are also free text. No sender/recipient natural-person identifier or cross-role identity key is present in the inspected consignment model.

**Control gap:** the dispatch transition route can mark a dispatch delivered without checking that a delivery-proof record exists. The presence of a proof endpoint does not establish that proof is mandatory for every completed delivery.

### 3.2 Uploaded evidence

- Permitted formats: PDF, JPEG and PNG.
- Maximum file size: 10 MiB.
- Upload intent: private, dispatch/carrier scoped, presigned for five minutes.
- Verification checks stored object size, declared content type and the leading file signature bytes.
- These checks validate file format and size; they do not inspect document contents, identify people, detect identity documents, classify sensitive information or establish that a file is necessary.
- The evidence metadata model initially records personal data as present, sensitive personal data as false by default, and classification status as unclassified with classification incomplete. A false default is not evidence that a file contains no sensitive data.
- Later classification fields and review references exist, but no automatic content classifier/OCR or verified pre-attachment content review was found. The lifecycle proof path can attach an uploaded file while its classification is still unclassified.
- Free-text notes, exception descriptions and uploaded files may contain additional individuals' names, signatures, faces, addresses, identity details or sensitive personal information.

Object storage and scheduler settings default to disabled, and synthetic-data-only defaults to true in the inspected configuration. No production configuration, bucket, live uploads or production database was examined.

## 4. Expected data-subject counts — what can and cannot be calculated

### 4.1 Named transaction-role appearances

For planning only, assume every forecast delivery creates one consignment with one sender-name and one recipient-name entry. If a proof is submitted, it can add one receiver-name entry per dispatch. These are **field/role appearances**, not unique people.

| Measure | Initial launch / month | Year 2 / month | Year 3 / month |
|---|---:|---:|---:|
| Required sender + recipient name entries (2 × deliveries) | 520 | 1,560 | 3,900 |
| Potential receiver-name entries (up to 1 × delivery, if proof for every dispatch) | 0–260 | 0–780 | 0–1,950 |
| Potential total named transaction-role entries | 520–780 | 1,560–2,340 | 3,900–5,850 |
| Required sender + recipient entries / year | 6,240 | 18,720 | 46,800 |
| Potential receiver-name entries / year | 0–3,120 | 0–9,360 | 0–23,400 |
| Potential total named transaction-role entries / year | 6,240–9,360 | 18,720–28,080 | 46,800–70,200 |

The upper end assumes one proof per delivery, one dispatch per delivery, all names refer to natural persons and every role entry relates to a different person. Those assumptions are not verified. The lower end for receiver entries reflects that proof is supported but not enforced as a prerequisite to the delivered state.

### 4.2 Unique natural persons are not currently computable

No defensible unique sender, recipient, receiver, courier or total data-subject count can be derived from the forecast or inspected schema:

- Sender and recipient are stored as name strings, not linked to stable person/customer records.
- Receiver is stored as a name string; no person key links it to sender or recipient.
- The same person may appear in multiple consignments or in multiple roles; no deduplication key is present in these cargo fields.
- Dispatches link carrier organisations and optional vehicles, but the inspected dispatch/tracking schema has no dedicated assigned-driver/courier person identifier.
- Staff actor IDs are recorded for dispatch, tracking, proof and exception actions, but no actual staff/partner roster or distinct-actor count was supplied.
- Uploaded evidence may contain multiple additional people not represented in structured fields; their number cannot be bounded by delivery count.
- No actual database or live activity dataset was inspected.

Accordingly, the table above is a **transaction-role record envelope only**, not a count or estimate of unique data subjects. It must not be reported as the Article 40 subject population.

### 4.3 Required counting method before a final threshold conclusion

For a representative forecast and, once live, actual monthly and rolling-12-month measures, record:
1. distinct pseudonymous natural persons in sender, recipient and receiver roles, both by role and as a deduplicated union;
2. distinct couriers/drivers, partner-carrier staff and MaaleNex staff whose identities are processed or whose activity is monitored;
3. people represented in proof files, using a documented content-classification sample and category counts;
4. active and peak-period subjects, repeat frequency, geographic coverage and service-line split (SL-01 / SL-02);
5. data source, measurement period, extraction date, deduplication method, uncertainty and accountable approver.

Use stable pseudonymous subject keys for counting; do not place names or raw identifiers in the aggregate compliance report. Do not add role counts together without deduplicating overlap.

## 5. Article 40 preliminary assessment

| Article 40 limb | Reconciled evidence | Current assessment |
|---|---|---|
| Government-body processing | No government-body customer, mandate or processing arrangement evidenced in the reviewed records. | NOT TRIGGERED ON CURRENT EVIDENCE; reassess if a government-body arrangement arises. |
| Core activities requiring regular and systematic monitoring on a large scale | Event-based dispatch/tracking design and optional coordinates are present. Continuous/background GPS is not found in the inspected backend, but manual event frequency is uncapped in source; client/runtime and actual subject counts are missing. | UNDETERMINED. Do not conclude that event-based tracking is necessarily non-systematic or small-scale. |
| Core activities involving large-scale sensitive personal data | Proof files may contain sensitive information; upload validation does not classify contents; sensitive flag defaults false and classification begins unclassified. Actual file contents, sensitive categories and subject scale are unknown. | UNDETERMINED. Do not rely on the false default as a “no sensitive data” finding. |

**Overall D02 result: IN PROGRESS / UNDETERMINED.** The forecast improves capacity planning but does not settle either large-scale limb. No DPO-required or DPO-not-required conclusion, appointment, non-appointment or regulatory notification is made.

## 6. Required reconciliation actions

1. **Tracking product specification:** confirm whether client apps will request device location; whether any background permission, periodic polling, map SDK, analytics SDK or third-party telemetry exists; and exactly which user action triggers each coordinate event.
2. **Enforce the approved low-monitoring boundary:** if Owner retains the no-continuous-GPS design, add an explicit product/API control for coordinate purpose and collection mode, cap events per dispatch or apply a justified rate limit, and reject coordinates outside the approved use case. This is a recommendation for a separately approved implementation change, not an instruction to change code now.
3. **Proof minimisation:** define acceptable proof examples; prohibit unnecessary identity documents and sensitive content; establish redaction and exception handling; decide whether proof is mandatory for delivery completion; and require content classification before attachment or within a controlled review window.
4. **Subject-count model:** define pseudonymous person keys and deduplication across sender/recipient/receiver/courier/staff roles; produce a forecasted distinct-person estimate with explicit repeat/overlap assumptions.
5. **Service-line allocation:** provide forecast shares for SL-01 and SL-02 only when the Owner approves them; do not infer a split.
6. **Actual validation:** after an authorised pilot, measure monthly and peak-day delivery, dispatch, event, coordinate, proof, file and distinct-subject counts. Until then, retain the figures as forecasts only.

## 7. Source evidence and version pins

All references below are source snapshots from open, unmerged PRs; they are not deployed code.

| Source | PR head SHA | Relevant file blob SHA |
|---|---|---|
| Consignment fields (PR #45) | `c2debf278e682f850c13a9866722376548bc792f` | `backend/app/domains/cargo/models.py` — `45844cac3a126389bd1127e66e7819cac7a1808c` |
| Tracking schema/route (PR #46) | `f0f221ce0ea2226c5f2fd2d8ec519c3b2e03a59b` | `backend/app/domains/cargo/dispatch.py` — `5455798cf5288b9ae3fb874e0a3cf172f859e114`; `backend/app/routers/cargo_dispatch.py` — `fb3f90c1bf46c787470ec4827c83f59cf12b19f0` |
| Proof fields/routes (PR #47) | `7ca507c5fc6e5aec05e6039a869b170abb616990` | `backend/app/domains/cargo/carrier_operations.py` — `1cb5dbbf06977d424a14d4efebcc4cd5734346f1`; `backend/app/routers/cargo_carrier_operations.py` — `de8b00cc625838f2e42ba1455cfcb38f98ebb1d6` |
| Private upload validation (PR #48) | `ab89ae0b13e6b6091808ab8240a76fedd49069ea` | `backend/app/domains/fleet/object_storage.py` — `5c612e050bd965904b6013f66405cc93963cf811` |
| Runtime defaults/evidence lifecycle (PR #49) | `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | `backend/app/core/config.py` — `ce49e4bf571b47fd2222d0ca630eb18b01bc9831`; `backend/app/domains/cargo/evidence_lifecycle.py` — `d8cd6d25316fff4102c70abdbd9920167c723482` |
| Sensitive-data metadata/audit redaction (PR #51) | `b81e788b55bb5c988d77412ce54f483106675e82` | `backend/app/domains/cargo/evidence_lifecycle.py` — `3de847294781b845bddd1e52b5d453e60ec92ea9`; `backend/app/domains/audit/service.py` — `a5b5be2882d799de0f4a16c48246299acb70559d` |

## 8. Legal source

Article 40(1)(a)–(c) of Ethiopia's Personal Data Protection Proclamation No. 1321/2024 sets out the three alternative DPO appointment triggers discussed above. Official Federal Negarit Gazette text: https://justice.gov.et/wp-content/uploads/2025/04/seasiisia-seusiNse%C2%A1-1321-2016.pdf (English text, Article 40, PDF pages 41–42). The Ministry of Justice law catalogue lists Proclamation No. 1321/2024 as in force: https://justice.gov.et/en/law/personal-data-protection-proclamation/.

## 9. Governance disposition

This is a documentation-only source reconciliation. It does not modify application code, migrations, workflow configuration or production settings. PRs #45–#51 remain unmerged; PR #52 remains a draft. No live data processing, pilot, partner operation, DPO appointment, filing, merge or deployment is authorised by this record.

**D02:** IN PROGRESS / UNDETERMINED.  
**D03:** PARTIAL / NOT VERIFIED-CLOSED.  
**D04:** PARTIAL / NOT VERIFIED-CLOSED.
