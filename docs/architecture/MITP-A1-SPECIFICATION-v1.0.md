# MaaleNex Proprietary Integrated Tracking Platform (MITP)
## A1 Assessment, Architecture and Requirements Specification

| Field | Value |
|---|---|
| Document ID | MN-MITP-A1-001 |
| Version | 1.0 — Owner decisions incorporated |
| Date | 2026-11-23 |
| Stage | A1 — Assessment and specification |
| Status | VERIFIED-CLOSED — A1 scope only |
| Repository | `akefadaka-git/maalenex` |
| Authorization | A1 closure and A2 read-only reconciliation only; no A3/A4/A5 authorization |

## 1. Purpose and executive summary

MaaleNex shall pursue a proprietary, hardware-independent vehicle tracking platform that MaaleNex owns and operates. The platform will receive vehicle positions primarily from GPS/GNSS trackers installed in vehicles, use authorized driver-phone location only as a temporary fallback, process tracking data on MaaleNex-controlled infrastructure, and provide tracking through MaaleNex applications.

MaaleNex shall not require a third-party fleet-tracking platform subscription. Hardware suppliers may provide compatible trackers and cameras, but shall not control MaaleNex's tracking platform, customer experience, data model, access policy or data export.

This is a future-state specification. It does not claim that the repository currently contains GPS ingestion, live tracking, camera integration, map hosting or production-ready infrastructure.

## 2. Owner decisions — controlled requirements

The following decisions were supplied by the Owner and are incorporated without alteration:

| ID | Owner decision | Controlled requirement | Status |
|---|---|---|---|
| D01 | Mandatory | Every MaaleNex-operated vehicle must have a registered, approved and functioning installed GPS tracker. Driver-phone GPS is fallback only. | DECIDED |
| D02 | Road | Initial camera scope is road-facing cameras only. Cabin cameras are excluded from initial scope. | DECIDED |
| D03 | Hybrid | Self-hosted road maps plus a separately approved satellite imagery layer. | DECIDED |
| D04 | Review (initial decision) | Initially retained A1 for review and withheld A2. Superseded by the explicit Owner approval recorded in §21. | SUPERSEDED BY §21 |

These decisions establish product direction. They do not authorize hardware procurement, paid subscriptions, supplier engagement, code changes, schema changes, migrations, merges, production activation or deployment.

## 3. Objectives

1. Establish MaaleNex ownership and operational control of its tracking platform.
2. Require installed vehicle GPS hardware for every MaaleNex-operated vehicle.
3. Support multiple compatible tracker manufacturers through protocol adapters.
4. Provide authorized live tracking during active trips.
5. Integrate customer and driver applications with clear location-source indicators.
6. Provide self-hosted road maps and a legally approved satellite imagery layer.
7. Provide location history, route playback, ETA and arrival status.
8. Support road-facing camera integration as a separate security capability.
9. Enforce privacy, security, auditability and data minimization.
10. Avoid mandatory recurring third-party fleet-platform subscriptions.

## 4. Scope boundaries

### 4.1 In scope

- Vehicle GPS/GNSS tracker standard and compatibility register.
- Device registration, authentication, assignment and revocation.
- Direct device communication with MaaleNex-controlled infrastructure where supported.
- Authorized driver-phone fallback.
- Trip-bound location collection and customer tracking.
- Location history, stale-data handling, ETA and route presentation.
- Self-hosted road-map evaluation and approved satellite imagery integration.
- Road-facing camera integration design.
- Security, privacy, audit, retention, backup and cost controls.

### 4.2 Out of initial scope

- Cabin-facing cameras.
- Public or guessable live-tracking links.
- Third-party hosted fleet-management platform dependency.
- GPS tracker or camera manufacturing.
- Satellite constellation or mobile network operation.
- Remote engine immobilization or remote vehicle control.
- Unrestricted continuous video streaming to customers.
- Production deployment or commercial operation without subsequent approvals.

## 5. Architecture principles

- **MaaleNex ownership:** MaaleNex controls application code, APIs, data, device registry, access policies and infrastructure.
- **Mandatory installed GPS:** No MaaleNex-operated vehicle enters commercial operation under this tracking policy without an approved, functioning installed tracker.
- **Hardware independence:** Support multiple manufacturers through documented protocols and isolated adapters.
- **No mandatory tracking SaaS:** The system must not require a third-party fleet-management platform subscription.
- **Direct ingestion:** Devices should send telemetry to MaaleNex-controlled infrastructure.
- **Phone fallback:** Driver-phone location is a clearly labelled temporary fallback, never silently substituted for installed-device data.
- **Privacy by design:** Collection and disclosure must be purpose-limited and authorized.
- **Source transparency:** Every location has a source, timestamp, receipt time and available accuracy/quality information.
- **Offline resilience:** Delayed or stale coordinates must never be represented as current.
- **Modular expansion:** Shared tracking infrastructure may serve passenger and cargo products while preserving separate business rules and authorization scopes.

## 6. GPS hardware standard

### 6.1 Mandatory capabilities

| Capability | Minimum / preferred requirement |
|---|---|
| Positioning | GNSS receiver; GPS support mandatory |
| Other constellations | Additional GNSS constellations preferred |
| Connectivity | 4G LTE preferred; coverage and carrier compatibility to be tested |
| Power | Vehicle electrical supply |
| Backup | Internal backup battery preferred |
| Identity | Unique, stable device identifier |
| Authentication | Per-device credentials or equivalent secure identity |
| Transport security | Encrypted communication supported by device or secure gateway |
| Reporting | Configurable periodic and event-based reporting |
| Offline | Local buffering and later forwarding |
| Time | Device timestamp plus server receipt timestamp |
| Tamper | Power-loss/disconnection alert preferred |
| Diagnostics | Device health and firmware/version reporting preferred |
| Protocol | Documented protocol and test access required |

### 6.2 Optional capabilities

Ignition state, motion/accelerometer, SOS, driver identification, fuel, door sensors, temperature, CAN/OBD, tire-pressure monitoring and camera event triggers may be evaluated as optional extensions.

### 6.3 Device acceptance gate

A device is not accepted based solely on marketing claims. Technical acceptance must verify:

- Protocol documentation and direct connectivity to MaaleNex.
- Position accuracy and timestamp behavior.
- Authentication, encryption and credential rotation.
- Offline buffering and recovery behavior.
- Duplicate/replay handling.
- Device reset, replacement and credential revocation.
- Firmware update and vulnerability-management process.
- Tamper/power-loss behavior.
- Warranty, replacement availability and lifecycle support.
- Total cost of hardware, installation, SIM and maintenance.

A device compatibility register shall record tested model, firmware, protocol, configuration, test evidence and approval status.

## 7. Maps and satellite imagery

### 7.1 Distinguish positioning from map imagery

GNSS calculates the vehicle's geographic position. Road maps and satellite imagery display that position in geographic context. Satellite imagery is not a live vehicle-position source.

### 7.2 Road maps

The preferred direction is self-hosted road-map infrastructure using suitable open geographic data, including OpenStreetMap-compatible data subject to the applicable licence, attribution and database obligations.

Evaluate:
- Data import and update process.
- Tile generation, rendering and caching.
- Server/storage/bandwidth requirements.
- Coverage and quality in MaaleNex operating areas.
- Offline regional map packages.
- Attribution and licence compliance.

Public community tile servers must not be treated as unrestricted free commercial hosting or as an unlimited production tile service.

### 7.3 Satellite imagery

Use a selectable satellite imagery layer only after verifying:
- Commercial-use rights.
- Hosting, caching and redistribution permissions.
- Attribution requirements.
- Coverage and resolution for intended operating areas.
- Refresh/update frequency.
- Offline and derivative-use restrictions.
- Bandwidth and storage costs.

No paid imagery subscription or commercial licence is approved by this document. If suitable imagery cannot be used lawfully within the cost constraint, the road-map layer remains the baseline and satellite imagery is deferred.

### 7.4 Map interface requirements

- Road/satellite layer switch where imagery rights permit.
- Vehicle, pickup and destination markers.
- Route and direction display.
- Current/last-known/stale location state.
- Timestamp and source indicator.
- Historical route playback.
- Amharic-first interface with English option.
- Offline map support where technically and legally feasible.

## 8. Device protocols and telemetry

Candidate transports include HTTPS/REST, MQTT over TLS and documented TCP-based tracker protocols. Selection depends on verified hardware support, security and operational cost.

Each accepted telemetry message should include, where supported:

- Device identifier.
- Latitude and longitude.
- Device-generated timestamp.
- Server receipt timestamp.
- Speed and heading.
- Ignition/movement state.
- Position accuracy or quality.
- Power/battery status.
- Event type and sequence identifier.

The ingestion layer must validate device identity, schema, coordinate range, timestamp, assignment and message integrity. Unknown, malformed, unauthorized, replayed or suspicious messages must be rejected or quarantined.

Each manufacturer protocol shall be isolated behind an adapter. Protocol adapters shall not have unrestricted access to customer identity, booking, financial or unrelated business data.

## 9. Server and application architecture

### 9.1 Logical layers

1. **Sources:** Installed vehicle trackers; authorized driver-phone fallback; customer applications; road-facing cameras.
2. **Secure ingestion:** Device authentication, protocol adapters, validation, rate controls and device-health monitoring.
3. **Tracking domain services:** Device registry, vehicle binding, trip binding, location processing, history, ETA, geofencing and trip lifecycle.
4. **Data infrastructure:** Relational records, partitioned/time-series location events, object storage for authorized video, audit records and backups.
5. **Interfaces:** Customer, driver, vehicle-owner, fleet-operator and MaaleNex operations interfaces.

### 9.2 Repository and architecture boundary

The MITP design must be reconciled with the existing MaaleNex repository architecture before implementation. It must not silently introduce a microservice architecture or bypass established domain boundaries. The existing project architecture documentation identifies a modular-monolith direction; A2 must determine the appropriate integration boundary and whether tracking belongs as a bounded domain/module within that architecture.

This A1 document does not assert that any of these tracking components currently exist or are implemented.

### 9.3 MaaleNex-controlled assets

MaaleNex shall control source code, device identities and credentials, API contracts, data schemas, access policies, infrastructure configuration, backups and data export procedures.

## 10. Tracking lifecycle and source hierarchy

### 10.1 Source hierarchy

1. Installed vehicle GPS tracker — primary and required source.
2. Authorized driver-phone GPS — temporary fallback only.
3. No valid source — report location unavailable.

Customer-phone location is for customer pickup coordination and navigation. It is not a substitute for vehicle location.

Fallback must be visibly identified as driver-phone GPS, with its own timestamp and freshness. The interface must not label it as installed-device GPS.

### 10.2 Lifecycle

1. Register vehicle and installed tracker.
2. Verify device identity and vehicle assignment.
3. Confirm tracker is online and reporting.
4. Assign authorized booking/dispatch and driver.
5. Start tracking at the authorized trip-start event.
6. Process authenticated positions during the active trip.
7. Expose the vehicle only to authorized roles.
8. Stop active-trip collection at terminal trip state, subject to separately justified vehicle-security functions.
9. Apply approved retention and deletion rules.

### 10.3 Candidate reporting intervals

For engineering evaluation only:
- Moving: approximately 30 seconds.
- Stationary: approximately 2 minutes.
- Material safety/operational event: immediate transmission where supported.

These are provisional values, not production settings. Validate against network coverage, device capabilities, data costs, storage, privacy and operational needs.

### 10.4 Stale and missing location

The system must distinguish current, last-known, delayed, estimated and unavailable positions. A last-known position must display its timestamp and must not be animated or presented as live. Loss of GPS or mobile connectivity must be visible.

### 10.5 ETA

ETA is an estimate, not a promise. Show calculation time and source where available. Scheduled arrival, estimated arrival and actual arrival must remain distinct.

## 11. Road-facing camera integration

Road-facing cameras are the only camera type in initial scope.

Initial capabilities to evaluate:
- Camera/device registration and vehicle binding.
- Recording/health status.
- Event metadata.
- Incident-triggered clip retrieval.
- Secure clip storage and playback.
- Access logging.
- Retention and deletion controls.

Cabin-facing cameras are excluded from initial scope. They require a separate Owner decision, purpose assessment, legal/privacy review and updated specification before any implementation.

Customers do not receive continuous camera access by default. Vehicle owners, fleet operators and MaaleNex operations may access only authorized security information for vehicles and responsibilities within their scope. Public or guessable media links are prohibited.

Remote immobilization and engine cut-off are excluded.

## 12. Security requirements

- Encrypted device communication.
- Unique device identity and per-device credentials.
- Secure credential storage, rotation and revocation.
- Resource-scoped role-based access control.
- Strong authentication and MFA for privileged access.
- Strict customer-to-booking-to-vehicle authorization.
- Driver access limited to assigned active trips.
- Owner access limited to registered/verified vehicles and authorized information.
- Organization-scoped operator access.
- Logged, justified and limited operations access.
- Input validation, protocol isolation and rate limiting.
- Replay/duplicate detection where technically supported.
- Encryption of sensitive stored data and backups.
- Secure firmware and dependency maintenance.
- Development, test and production separation.
- Security monitoring, incident response and recovery testing.
- Reassignment must revoke prior access and prevent cross-tenant leakage.

## 13. Privacy and data governance

MITP may process vehicle coordinates, driver identity, customer/booking references, pickup and destination, owner/operator information, camera recordings, device identifiers and access logs.

| Role | Permitted access principle |
|---|---|
| Customer | Exact vehicle assigned to that customer's authorized active booking |
| Driver | Assigned active trip and necessary operational information |
| Verified vehicle owner | Own registered vehicles and specifically authorized trip information |
| Fleet operator | Authorized vehicles and trips belonging to its organization |
| MaaleNex operations | Scoped operational access, logged and auditable |
| Public | No unrestricted live tracking |

A vehicle owner does not automatically receive a customer's phone location. Customer access to a vehicle does not grant camera access.

Controls required:
- Clear notices for customers and drivers.
- Defined purposes and appropriate lawful basis.
- Data minimization and least privilege.
- Separate location and video retention rules.
- Restricted access to historical routes and clips.
- Data access/export and deletion procedures.
- Access audit trails and incident response.
- Legal assessment under applicable Ethiopian requirements before production.

No conclusion about whether a Data Protection Officer is required shall be made without assessment of actual processing scale, frequency and applicable law.

## 14. Cost controls

The platform shall avoid mandatory third-party fleet-platform subscriptions.

Preferred cost model:
- Open-source software where technically suitable.
- MaaleNex-controlled/self-hosted services.
- Direct device-to-MaaleNex telemetry.
- Open and documented device protocols.
- Open geographic data and self-hosted road maps.
- Satellite imagery only under verified suitable rights and approved cost.
- Multiple compatible hardware manufacturers.
- Configurable reporting intervals and event-based updates.
- Location/video retention and storage lifecycle controls.
- Bandwidth, storage and per-vehicle connectivity monitoring.

Expected costs that cannot be assumed to be zero include one-time tracker/camera hardware, installation, SIM/mobile data, server/storage/bandwidth, map operations, imagery licensing where applicable, maintenance and security operations.

No procurement, paid subscription, commercial licence or supplier commitment is authorized.

## 15. Reliability and operations

Design and test for mobile-network outages, GNSS loss, vehicle power loss, device tampering, delayed/duplicate telemetry, device replacement, vehicle reassignment, driver changes, server failure and database recovery.

The platform must preserve event ordering where possible, retain device and server timestamps, expose data freshness, and prevent stale positions from appearing live. Backup restoration and export must be demonstrated before production approval.

## 16. Future acceptance criteria

- AT-01: Approved installed tracker sends authenticated positions to MaaleNex.
- AT-02: Unknown devices cannot submit trusted positions.
- AT-03: Device assignment and revocation are secure and auditable.
- AT-04: Customer access is restricted to the exact authorized booking.
- AT-05: Driver-phone fallback is separately labelled and never misrepresented.
- AT-06: Stale coordinates are never shown as current.
- AT-07: Location history and route playback preserve timestamps.
- AT-08: Road map and legally approved satellite imagery layers display correctly.
- AT-09: Unauthorized users cannot access camera footage.
- AT-10: Privileged access and security-relevant actions are logged.
- AT-11: Backup restoration and data export are demonstrated.
- AT-12: Reporting, bandwidth and storage costs are measurable.
- AT-13: Vehicle/device reassignment revokes former access.
- AT-14: Tracking operates without a third-party fleet-platform subscription.
- AT-15: Every MaaleNex-operated vehicle passes the installed-tracker compliance check before commercial operation.

These are future acceptance criteria; none is claimed as tested or passed.

## 17. A2 assessment register — unresolved items preserved

The following items cannot responsibly be marked resolved from product preference alone. A2 must gather evidence and produce recommendations without changing code or configuration.

| ID | Item | Current disposition | Evidence/action required |
|---|---|---|---|
| R01 | Exact GPS hardware model and minimum acceptance profile | OPEN | Compare protocol, GNSS, LTE bands, power, buffering, security, warranty and cost; bench-test candidate devices |
| R02 | Supported device protocols and adapters | OPEN | Inspect current repository and candidate device protocol documentation; prove direct ingestion feasibility |
| R03 | Satellite imagery source and commercial rights | OPEN | Verify provider/source terms, redistribution, caching, coverage, attribution and cost |
| R04 | Self-hosted road-map stack and update method | OPEN | Evaluate map data/licence, tile generation, storage, compute, bandwidth and regional quality |
| R05 | Hosting topology and budget | OPEN | Reconcile current infrastructure and estimate telemetry, map, video, backup and availability costs |
| R06 | Production reporting intervals | PROVISIONAL | Validate through device/network tests and cost/privacy analysis |
| R07 | Location and video retention periods | OPEN | Determine legal purpose, operational need, storage impact and deletion policy |
| R08 | Road-facing camera model and integration | OPEN | Evaluate recording, event clips, storage, connectivity, security and compatibility |
| R09 | Privacy/legal assessment | OPEN | Assess applicable Ethiopian law, notices, lawful basis, data-subject rights and DPO threshold |
| R10 | SIM/mobile-data arrangements | OPEN | Assess carrier coverage, data plans, APN/private connectivity options, roaming and per-vehicle cost |
| R11 | Driver-phone fallback rules | PROVISIONAL | Define permission, background operation, user notice, fallback activation, expiry and source labelling |
| R12 | Availability, recovery and support targets | OPEN | Define service objectives after operating model and hosting constraints are known |

**Resolution rule:** An item may be closed only with documented evidence or an explicit Owner decision. Unknown licensing, hardware, legal, coverage or cost facts must not be guessed or silently marked resolved.

## 18. Future workstreams (not authorized)

- W01 — GPS hardware and protocol compatibility assessment.
- W02 — Road-map and satellite imagery assessment.
- W03 — Device registry and secure ingestion design.
- W04 — Vehicle and trip tracking service design.
- W05 — Location history, ETA and route presentation.
- W06 — Customer, driver and owner application integration.
- W07 — Road-facing camera integration.
- W08 — Security, privacy and audit.
- W09 — Infrastructure, backup and monitoring.
- W10 — Performance, connectivity and cost validation.

## 19. Stage-gate governance

- **A1:** Assessment and specification. Current stage; remains open for Owner review.
- **A2:** Read-only reconciliation of existing repository, applications, backend, architecture, dependencies, security and tests. Requires separate explicit authorization. No code, schema, migration, workflow or configuration changes.
- **A3:** Implementation; requires separate explicit authorization.
- **A4:** Verification; requires evidence and separate stage approval.
- **A5:** Deployment; requires separate explicit authorization.

This document does not authorize A2, A3, A4 or A5. It does not authorize procurement, supplier engagement, payment, merge, production activation or deployment.

## 20. A1 closure conditions

A1 can be closed only when the Owner:
1. Approves the MITP ownership and independence principles.
2. Confirms mandatory installed GPS, road-facing camera-only initial scope, and hybrid road/satellite map direction.
3. Reviews the unresolved register and accepts its items for evidence-based A2 assessment.
4. Explicitly authorizes A1 closure and A2 read-only reconciliation.

**Current controlled status: OPEN — OWNER REVIEW.**

**Owner decisions incorporated:** D01 mandatory installed GPS; D02 road-facing camera only; D03 self-hosted road maps plus approved satellite imagery; D04 review only.

**No A2/A3/A4/A5, procurement, merge or deployment authorization is implied.**


## 21. Owner approval and A1 closure record

**Approval date:** 23 November 2026  
**Approval evidence:** Explicit Owner instruction in the controlling project conversation: “Approved.” This approval followed the request to approve A1 closure and authorize A2 read-only reconciliation.

**Governance determination:**
- A1 — **VERIFIED-CLOSED for specification and assessment scope only**.
- A2 — **AUTHORIZED, READ-ONLY RECONCILIATION ONLY**.
- A3 — NOT AUTHORIZED.
- A4 — NOT AUTHORIZED.
- A5 — NOT AUTHORIZED.

The Owner's later approval supersedes the earlier D04 review-only hold. The technical decisions D01–D03 remain unchanged: mandatory installed GPS tracker for every MaaleNex-operated vehicle; road-facing cameras only in initial scope; self-hosted road maps plus a legally approved satellite imagery layer.

A2 may inspect existing repository files, branches, commits, pull requests, workflows, tests and architecture. A2 must not modify application code, schemas, migrations, runtime configuration, workflows, existing branches or deployment state. No procurement, supplier engagement, paid service, merge, production activation or deployment is authorized.

**A1 closure boundary:** This closure freezes the MITP A1 direction and requirements. It does not certify technical implementation, legal compliance, provider/imagery licensing, hardware compatibility, security readiness, operating cost or production readiness. Those remain evidence items for A2 and later separately approved stages.
