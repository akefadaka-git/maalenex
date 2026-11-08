# MaaleNex Moto — Biker-First Mobility Platform A1

**Status:** Owner-requested direction; A1 specification draft for review.  
**Product hierarchy:** (1) Biker mobility and dispatch, (2) passenger transport, (3) intercity bus connections.  
**Current implementation baseline:** Passenger MVP only. This document does not claim new capabilities are implemented.

## 1. Product vision

Build an Amharic-first, mobile-first mobility platform that helps motorcycle riders/operators earn safely and helps passengers find, verify, contact, follow and pay for a ride. The Jinka → Wolaita Sodo → Addis Ababa bus corridor is the second major service line, not the primary product.

## 2. Biker-first capability domains

- **Biker onboarding and trust:** identity/document review, motorcycle registration, license and insurance expiry tracking, operator approval, emergency contacts and auditable status changes.
- **Dispatch and jobs:** nearby ride requests, accept/decline, pickup/drop-off, fare estimate, trip state machine, cancellation, support and dispute evidence.
- **Navigation and maps:** map-based pickup/drop-off, route guidance, landmarks, low-bandwidth fallback and location-freshness indicators. Never imply GPS precision or tracking when permission/network is unavailable.
- **Live trip location:** explicit opt-in; foreground/background permission disclosure; authenticated, encrypted, short-lived location sessions; visibility only to matched passenger and authorized safety/support staff; retention limits, revoke/stop controls, audit events and abuse controls.
- **Call-to-verify:** in-app call action to matched biker/passenger, masked/relay calling where lawful provider support exists; show verified trip code and vehicle/biker details. A call alone is not proof of identity or trip completion.
- **Biker operations:** earnings ledger, commission statements, payout status, service history, maintenance reminders, safety/SOS workflow and offline-tolerant job-state recovery.

## 3. Passenger service

- Amharic-first ride request, pickup/drop-off map selection, fare estimate, matched biker profile and vehicle details.
- One-tap call-to-verify, trip PIN/QR confirmation, live trip map after consent, trip sharing and SOS/help.
- Transparent fare, cancellation/refund policy, payment status, receipts and support/dispute pathway.
- Accessibility, low-bandwidth behavior, clear offline state, and no false claim that a booking/payment succeeded while offline.

## 4. Intercity bus service — second product line

- Search and compare operator-published trips for Jinka ↔ Wolaita Sodo ↔ Addis Ababa, including intermediate stops, departure/arrival estimates, seat availability, fares, boarding terminal and operator identity.
- Reservation, passenger manifest and operator check-in remain distinct lifecycle states. No ticket/boarding claim until implemented and verified.
- Route, timetable and fare data must be operator-authorized; synthetic data must be visibly labelled TEST.

## 5. Payments and company commission

Provider integration targets: Telebirr, CBE Birr and supported Ethiopian mobile-bank transfer rails, subject to provider onboarding, merchant credentials, API documentation, commercial agreement and regulatory review.

- Provider adapter per rail; server-side payment intents and immutable transaction references.
- Verify signed provider callbacks/server-to-server status; never trust a client success screen or uploaded receipt as final settlement proof.
- Never collect/store banking PINs, OTPs, passwords or full payment credentials.
- Double-entry ETB ledger with gross fare, provider fee, company commission, biker/operator payable, refunds, chargebacks and reconciliation references.
- Commission is an explicit, versioned policy (percentage/fixed amount, effective dates, service/operator scope), disclosed before confirmation and auditable. No rate is assumed or activated by this specification.
- Payment integrations stay in sandbox/mock mode until provider credentials, security review, legal/compliance review and explicit release approval exist.

## 6. Architecture direction

- Android-first PWA/Capacitor client; offline-safe read cache and retryable idempotent commands, with clear sync state.
- Modular FastAPI domains for identity/trust, bikers/operators, dispatch, trips, geospatial location sessions, maps/routing, communication, payments, ledger/commission, bus catalog/reservations, support and audit.
- Authenticated WebSocket or managed pub/sub with per-trip authorization, heartbeat/expiry, replay protection and rate limits. Persist only required location samples under a retention policy.
- PostgreSQL; geospatial extension or validated coordinate/index strategy after infrastructure compatibility assessment; immutable financial journal; transactional outbox for provider callbacks/notifications.
- Least privilege, consent, device/session revocation, encryption in transit/at rest, secrets outside source, abuse detection, audit trail and incident response.
- Amharic default, English fallback; Ethiopian calendar support where dates are shown; ETB; low-bandwidth and intermittent-network behavior.

## 7. Non-functional acceptance criteria

- No location sharing before explicit consent and an active matched trip; revoked/ended trips stop updates promptly.
- Only authorized participants can read a trip's live location; cross-user/cross-trip access tests fail closed.
- Stale GPS is visibly marked with last-updated time; no fabricated live position.
- Payment state is server-verified and idempotent; duplicate callbacks cannot double-credit or double-charge.
- Ledger totals reconcile exactly; commission is traceable to a policy version and transaction.
- No real money, real identity documents or production GPS traces in CI; synthetic-only fixtures.
- Core biker and passenger flows pass Android device acceptance under intermittent connectivity.

## 8. Phased delivery proposal

- **A1:** approve product scope, role matrix, service lifecycle, privacy model, payment/commission framework, map/GPS assumptions, bus-service boundary and acceptance criteria.
- **A2:** read-only reconciliation of current repo; identify reusable passenger, identity, booking, fleet and support capabilities; map missing domains and migration dependencies.
- **A3.1:** biker/operator identity, vehicle and trust foundation.
- **A3.2:** dispatch, trip lifecycle, fare estimate and call-to-verify.
- **A3.3:** consent-based live location, maps, SOS and privacy controls.
- **A3.4:** biker earnings and commission ledger using synthetic transactions only.
- **A3.5:** provider sandbox adapters for Telebirr/CBE Birr/bank transfer only after provider docs and credentials are available.
- **A3.6:** intercity bus corridor search/reservation improvements as second service line.
- **A4:** security, concurrency, payment reconciliation, privacy, accessibility, performance and physical-device verification.
- **A5:** separately authorized production hosting, provider activation, pilot and deployment; no automatic merge/deploy.

## 9. Current blockers and exclusions

- Existing backend config intentionally permits development/test, local PostgreSQL and synthetic data. Do not weaken these safeguards to expose a public API.
- No approved reachable HTTPS test API host is configured; GitHub Actions CI can validate an ephemeral API but cannot serve as a persistent backend for an installed APK.
- Current schema has no production GPS stream, payment provider, commission ledger, biker dispatch or call relay domain. These must be designed and implemented, not implied by UI controls.
- No provider API credentials/agreements or confirmed commission rate have been supplied. Do not invent either.
- No real payments, live location collection, production operator onboarding, commercial service, deployment or merge are authorized by this specification.
