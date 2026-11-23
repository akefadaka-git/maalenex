# A2 Vehicle Trip-Tracking Requirement and Client/Integration Reconciliation

**Document ID:** MN-MOBILITY-TRACK-002  
**Version:** 1.0  
**Date:** 23 November 2026  
**Stage:** A2 — read-only source reconciliation and controlled requirement clarification  
**Status:** EVIDENCE RECORDED; PROPOSED DESIGN ONLY  
**Implementation:** NOT AUTHORIZED

## 1. User-stated product requirement

The user states that a verified vehicle owner, or a customer who ordered a fleet service or ride, must be able to track the designated vehicle from trip start to destination and see its estimated and actual arrival time.

This is recorded as a product requirement, not as evidence of an implemented capability:

- **Customer access:** the customer who owns the active booking/order can see only the vehicle assigned to that booking/order and only for the relevant active trip.
- **Vehicle-owner access:** a verified owner or authorized fleet representative can see the vehicle(s) they are entitled to manage during an active service trip. Ownership and delegation must be established by authoritative records, not by a user-supplied vehicle identifier.
- **Partner access:** an approved partner operator can access only its own assigned vehicles and trips, subject to the documented controller/processor arrangement.
- **Trip window:** tracking begins when the trip is operationally started and ends at arrival, cancellation or another terminal trip state. It must not become off-duty or unrelated private-use tracking.
- **Customer display:** designated vehicle, map position, trip status, last-update time, estimated arrival time (ETA), and actual arrival time. A stale or unavailable location must be clearly labelled; the system must not fabricate a current position or arrival time.

## 2. A2 repository and client discovery

### 2.1 Accessible repository and branch search

The connected GitHub account returned 11 repositories owned by the account; the MaaleNex application repository was the relevant project repository. No separate Cargo driver app, fleet-owner tracking app, or partner tracking repository was identified in that returned inventory.

Within the MaaleNex repository, branch searches returned Cargo branches for consignment, dispatch tracking, evidence storage, evidence lifecycle governance, legal-retention remediation, and documentation. The Cargo increments PR #45–#49 have backend, migration, tests, workflow and documentation changes. They do not contain a Cargo mobile/web client. Their tracking contract expressly describes a backend-only increment and excludes a frontend, GPS polling, live map, public tracking links and external carrier webhooks.

This is a repository evidence boundary. It does not prove that no private, partner-owned, separately hosted or deployed client exists.

### 2.2 Passenger Android/WebView client

PR #43 (branch feat/passenger-backend-connectivity-foundation, head 20c855b881e30aacf97dbb0d8fbb85755eb7bdf5, open and unmerged) contains the reviewed passenger application files.

Relevant source pins:

| Component | Path | Blob SHA |
|---|---|---|
| Passenger map | frontend/src/PassengerGoogleMap.tsx | 79f633b828544747eaefd4a56ce4df11969ea4ad |
| Passenger app | frontend/src/App.tsx | 71b9a7e4a064803fec43ddec6fe9e8cdc4fe5f6e |
| Passenger API client | frontend/src/passenger-api.ts | e01afb46229e11d148aad415783b7c279933db90 |
| Passenger bookings | frontend/src/MyBookings.tsx | 10336b59f572a351786a372c9c63bde47199ca34 |
| Android manifest | android/app/src/main/AndroidManifest.xml | f081d76de41d86e3654c19a941a0c7bb091f7bca |
| WebView geolocation policy | android/app/src/main/java/com/maalenex/moto/WebViewGeolocationPolicy.kt | 3e95eeeadba01f211a6b63efb644c251cb4f1c90 |
| Passenger catalog API | backend/app/routers/passenger_catalog.py | 4be8a5bcf99e073aebabae3e886a29e2d5254fff |

**Observed behaviour:**

- PassengerGoogleMap loads the Google Maps JavaScript API from maps.googleapis.com using VITE_GOOGLE_MAPS_API_KEY.
- It draws published catalog locations and published route geometry returned by the passenger catalog API.
- The “Use my location” action calls navigator.geolocation.getCurrentPosition once, only after the passenger presses the button. It pans the passenger's map to that passenger device location and displays the message “This is not driver tracking.”
- The one-shot call uses enableHighAccuracy true, a 10-second timeout and maximumAge 60000. This is passenger-device positioning, not vehicle telematics.
- The Android manifest declares ACCESS_COARSE_LOCATION and ACCESS_FINE_LOCATION. No ACCESS_BACKGROUND_LOCATION declaration was found in the inspected manifest.
- The WebView policy permits geolocation only for the packaged appassets origin and accepts coarse or fine Android location permission.
- MyBookings shows booking reference, departure, estimated arrival, passenger count, fare and booking status. It does not display a live vehicle position or live vehicle tracking history.
- PassengerTrip returned by passenger-api.ts contains trip ID, departure, estimated arrival, boarding model, seat availability and fare flags. It does not contain vehicle position, location timestamp, live ETA, or a tracking subscription endpoint.
- The inspected passenger API client exposes catalog, trip-search, seat and booking operations; no passenger live-vehicle-location endpoint was found in that client.
- The passenger catalog backend returns published static locations, route geometry and scheduled trip information. The trip search returns arrival_estimate_at, not a live ETA computed from current vehicle position.

**Conclusion:** a passenger Android/WebView client exists, but the reviewed client provides a route/catalog map and a passenger-initiated location fix only. It does not implement the stated customer-to-designated-vehicle live-tracking requirement.

### 2.3 Vehicle, trip and booking data model

Relevant source pins:

| Model | Path | Blob SHA | Observed relationship |
|---|---|---|---|
| Vehicle | backend/app/domains/fleet/models.py | 175eb6a2eabdb3e7707db065dd5cf87032b6fd8d | Vehicle belongs to an operator organization; no individual owner identity field in this model |
| Trip | backend/app/domains/trips/models.py | e3f7b95ab15763a42e0aedef80af3511d4b502ab | Trip has vehicle_id, departure, scheduled arrival estimate and status; no current position or location-update model |
| Booking | backend/app/domains/bookings/models.py | d6d0e075d97bed48070131272430736298d79a36 | Booking links to trip and optional passenger account; no tracking entitlement or live-location reference |

The existing model can associate a scheduled trip with a vehicle, but the inspected Vehicle model associates the vehicle to an organization rather than a verified natural-person owner. There is no evidenced owner-to-vehicle entitlement suitable for owner-facing live tracking. A verified ownership/delegation source and access-control contract remain design dependencies.

### 2.4 Cargo client and backend

Cargo PR #46 head f0f221ce0ea2226c5f2fd2d8ec519c3b2e03a59b includes:

- backend/app/domains/cargo/dispatch.py — blob 5455798cf5288b9ae3fb874e0a3cf172f859e114
- backend/app/domains/cargo/dispatch_service.py — blob 212c0d26c6eb327fde8d0b153ecdc35d1c3042d3
- backend/app/routers/cargo_dispatch.py — blob fb3f90c1bf46c787470ec4827c83f59cf12b19f0
- docs/backend/cargo-dispatch-tracking-v1.md — blob 4680c55b22782cfd0ca6e560bfc554df12974519

The Cargo route is staff-authenticated. Assigned-carrier staff or platform dispatchers append events; dispatch participants can read the event history. Events support optional paired latitude/longitude and operator-reported occurrence time. The event model is append-only and idempotent, but no live customer location feed, public tracking link, location polling loop or server-side event-frequency ceiling is present in the reviewed increment.

**Conclusion:** Cargo backend event history is not a customer-facing live vehicle-tracking service. No separate Cargo client was located in the reviewed Cargo branches.

## 3. External provider and integration reconciliation

| Provider / integration | A2 evidence | Reconciliation |
|---|---|---|
| Google Maps JavaScript API | Passenger map loads maps.googleapis.com; API key comes from VITE_GOOGLE_MAPS_API_KEY. | Passenger map rendering only in inspected source. No evidence of a Cargo or driver location feed, traffic-aware live ETA, or Google Routes/Directions integration. |
| Device geolocation | Passenger one-shot navigator.geolocation.getCurrentPosition; Android coarse/fine permission declarations. | Passenger's own location only. Not a driver app, vehicle GPS device or partner tracking integration. |
| Cloudflare R2 / S3-compatible storage | Cargo evidence adapter supports R2; runtime object_storage_enabled defaults to false; live credentials/endpoint are required. | Delivery-proof file storage only. Not a location or telemetry provider. No live bucket/account/region was inspected. |
| Carrier webhooks / telematics | Cargo tracking contract excludes external carrier webhooks and continuous GPS. | No partner GPS/telematics integration identified in reviewed Cargo source. Separate partner systems remain unverified. |
| SMS / email | No Cargo messaging provider identified in the reviewed Cargo increments; passenger baseline records messaging delivery as unavailable/not connected. | No evidenced provider for live-location notifications or ETA alerts. |
| IROKA | No Cargo tracking/location integration evidenced in reviewed source. | Not in scope for live vehicle telemetry on current evidence. |

No production configuration, partner system, vendor account, contract, traffic API credential, hardware tracker, SIM/IoT provider, data-hosting region, support access location or deployed client was inspected. Vendor and transfer assessments remain open.

## 4. Reconciliation against Cargo Tracking Collection Specification v1.0

The Cargo specification v1.0 is designed for dispatch-event evidence and deliberately prohibits continuous/background GPS by default. It proposes a maximum of four coordinate-bearing events per dispatch and at least 15 minutes between coordinate captures.

Those limits are **not sufficient** for the newly stated live vehicle-tracking requirement. Do not weaken or silently reinterpret the Cargo limits. Treat the two capabilities as distinct data-processing profiles:

1. **Cargo dispatch-event profile:** sparse, event-bound optional coordinates for cargo operational evidence; keep the v1.0 limits unless a controlled Cargo-specific revision is approved.
2. **Mobility live-trip profile:** bounded, active-trip-only vehicle telemetry for an assigned fleet/ride booking. This profile needs its own purpose, lawful-basis, client/device, frequency, retention, access and vendor assessment.

The mobility profile must not collect outside the active trip. It must not become all-day driver surveillance or expose a vehicle's location to the public.

## 5. Proposed mobility live-trip profile — for Owner review only

The following is a proposed starting design, not an approved implementation contract:

### 5.1 Trip lifecycle and location cadence

- Start collection only after the trip is explicitly marked started by an authorized operator/driver workflow and the designated vehicle is bound to the trip.
- While moving, consider one location update every 30 seconds; while stationary, reduce to one update every 2 minutes. Apply server-side rate limits and deduplicate repeated device samples.
- Emit explicit trip-start, pickup/boarding, material delay/exception, destination-arrival and trip-end events. Do not rely only on GPS points to infer legal or operational state transitions.
- Stop collection immediately at arrival, cancellation or another terminal trip state. Any post-trip investigation/retention must use a separately approved purpose and access path.
- Show last successful update time and a stale/offline indicator. Never interpolate or display a stale point as the current location.
- Recalculate ETA using an approved routing/traffic source and current location; label ETA as an estimate and show when it was last calculated. Preserve scheduled ETA and actual arrival as distinct fields.
- If location is unavailable or denied, continue the trip with status-only updates and clearly indicate that live location is unavailable; do not invent coordinates or block a safety-critical trip update.

### 5.2 Access and authorization

- Customer: access only through an authenticated passenger/customer account or a strongly verified guest-booking entitlement, bound to the exact active booking/order and assigned vehicle.
- Vehicle owner: access only after authoritative vehicle ownership or delegated fleet-management entitlement is verified; scope access to vehicles and active trips belonging to that owner/operator.
- Partner staff: scope access to their approved organization and assigned vehicles/trips.
- No anonymous, guessable or publicly shareable tracking URL by default. If a share feature is later requested, it needs a separate short-lived token, revocation, expiry and privacy review.
- Reassignment of a vehicle or trip must revoke the previous customer's and partner's access according to the updated booking/dispatch relationship.
- Driver/operator must receive an Amharic-first and English notice, visible tracking-active indication, purpose, recipients, active-trip boundary and contact/rights route. Legal basis and employment/contract implications require separate legal review; a UI acknowledgement is not automatically the lawful basis.

### 5.3 Proposed subject-counting additions

Extend the v1.0 pseudonymous counting method to cover distinct natural persons whose data is linked to live trip tracking:

- assigned driver/courier;
- customer who ordered the ride/fleet service;
- passengers/occupants where identifiable;
- verified vehicle owner or delegated fleet contact;
- partner and MaaleNex operations staff who access location data.

Count a person once within the permitted controller namespace across these roles. Keep driver, customer, passenger, owner and staff role-specific counts as well as the deduplicated union. Count active-trip location-exposed persons separately from Cargo event-only subjects. Vehicle IDs also require a separate pseudonymous asset key; a vehicle key must not be substituted for a person key. Unresolved identities remain separately reported and are not guessed.

### 5.4 Dependencies before implementation

- identify the actual driver app, in-vehicle tracker or partner telematics source;
- establish verified vehicle ownership and delegated access;
- define the authoritative trip-start, trip-end, arrival and vehicle-reassignment state transitions;
- choose and assess a routing/traffic ETA provider or an internally operated routing engine;
- specify location precision, accuracy, update cadence, stale-state behaviour and offline buffering;
- assess driver notice, lawful basis, passenger notice, partner/controller roles and DPIA;
- specify location retention, deletion, legal holds, vendor hosting/transfer and access logging;
- test customer/owner/partner authorization against cross-trip and cross-organization access.

## 6. Article 40 and DPIA impact

If implemented at scale, active-trip location telemetry can constitute regular and systematic monitoring of identifiable drivers and potentially passengers/vehicle owners. Its Article 40 implications cannot be dismissed merely because tracking stops at trip end. The monitoring limb remains **UNDETERMINED** until the actual trip frequency, duration, number of vehicles, distinct drivers/customers, coverage, location cadence, service-line split and operational purpose are measured and assessed. Sensitive-data and government-body limbs remain subject to the existing D02 evidence requirements.

The proposed active-trip boundary and lower stationary cadence are minimization controls, not a legal conclusion. D02 remains open; D03/D04 remain partial.

## 7. A2 disposition

- Passenger Android/WebView client: **IDENTIFIED**; passenger map only, no live designated-vehicle tracking evidenced.
- Cargo mobile/web client in reviewed repository/branches: **NOT LOCATED**.
- Separate partner driver app / telematics device / hosted tracking service: **NOT VERIFIED**.
- Customer-to-vehicle live tracking: **NOT IMPLEMENTED IN REVIEWED CLIENT/API EVIDENCE**.
- Vehicle-owner access entitlement: **NOT EVIDENCED** in the inspected Vehicle model.
- Google Maps: passenger map rendering only; live traffic ETA integration not evidenced.
- R2: optional evidence storage, disabled by default in inspected config; not a location provider.
- No code, schema, migrations, permissions, vendor settings, CI workflows or production configuration changed in this assessment.

**Overall:** A2 source reconciliation is PARTIAL. The user's live-trip tracking requirement is now recorded as a separate mobility capability requiring a controlled design and legal/privacy assessment. No A3 implementation is authorized by this document.
