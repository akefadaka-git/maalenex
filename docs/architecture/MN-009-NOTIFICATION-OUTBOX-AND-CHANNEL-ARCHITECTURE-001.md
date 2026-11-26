# MN-009 — Notification Outbox and Channel Architecture Reconciliation

**Artifact:** MN-009-NOTIFICATION-OUTBOX-AND-CHANNEL-ARCHITECTURE-001  
**Version:** 1.0.0  
**Assessment date:** 2026-11-26  
**Status:** DELIVERED — ARCHITECTURE RECONCILIATION; PROVIDER DELIVERY NOT IMPLEMENTED/ACTIVATED  
**Repository:** `akefadaka-git/maalenex`  
**Main baseline:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Method:** Static review of Passenger Notifications PR #38 and current A1/A2 records. No provider account, secret, workflow or production service was accessed or changed.

## 1. Executive disposition

MaaleNex already has a candidate passenger-owned in-app notification inbox and preference model on PR #38. The branch provides notification records, read/unread state, a unique deduplication key, passenger ownership checks and in-app preferences. Booking and account-security events are used to create notifications.

However, the inspected implementation is **not a complete provider-neutral transactional outbox and channel-delivery architecture**. The current service function inserts a `PassengerNotification` row directly through the request's SQLAlchemy session. No independent outbox event table, delivery-attempt ledger, dispatcher worker, provider adapter, retry/backoff policy or dead-letter workflow was evidenced in the inspected PR #38 files.

The canonical design should make the in-app inbox the durable user-facing record and use a transactional outbox to decouple business transactions from external delivery. Email and SMS remain disabled; WhatsApp Business is not selected or activated; Telegram remains optional and, if ever adopted, user-initiated.

## 2. Evidence baseline

| Evidence | Reference | Finding |
|---|---|---|
| Main | `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | Current A2 baseline |
| Passenger Notifications PR #38 | `046da5e6cb435f2c9baeb2228fc9918287bd584e` | Open/draft/unmerged implementation candidate |
| Notification model | `backend/app/domains/notifications/models.py`, blob `1b33831aeced08592345fce5e0e0d82c04b2828` | Passenger inbox and preference tables |
| Notification service | `backend/app/domains/notifications/service.py`, blob `22a930aba6e9a0c2e4c814ce5e0e0d82c04b2828` | Direct inbox row creation, dedupe and read operations |
| Notification migration | `0013_passenger_notifications.py`, blob `696c8b211994c21e35004265e59b1eb9de8b1ef7` | Inbox and preference schema |
| PR #38 backend run | #44914789288 | PASS: 51 passed, 9 skipped; migration/parity/downgrade/re-upgrade recorded |
| PR #38 frontend run | #44914789340 | PASS: frontend tests, typecheck, build and Android/PWA validation |

These are PR #38 branch results only. They do not prove that PR #38 is merged into main or integrated with the current main baseline.

## 3. Existing notification capabilities

### 3.1 Persistent in-app inbox

The inspected model contains:

- `PassengerNotification`: passenger owner, notification type, title, body, optional resource type/reference, unique dedupe key, read timestamp and creation timestamp.
- `PassengerNotificationPreference`: passenger owner and in-app/email/SMS preference flags.
- Passenger ownership foreign keys and owner-oriented indexes.
- Unique dedupe constraint on the notification key.

The service provides:

- `create_notification()`: checks in-app preference, returns an existing item for a duplicate key, otherwise adds a passenger-owned inbox item to the current database session.
- `list_notifications()`: returns the latest 50 items and unread count for the authenticated passenger.
- `mark_notification_read()`: locks the passenger-owned row, sets read timestamp and records an audit event.
- `get_preferences()`: returns or creates the passenger preference row.

The default preferences are in-app enabled, email disabled and SMS disabled.

### 3.2 Event sources described by PR #38

PR #38 records in-app notifications for:

- Help & Support case events.
- Reports/Complaints events.
- Successful sign-in.
- Repeated failed sign-in lock threshold.
- Session revocation/logout.
- Booking claim-time state, reservation confirmation, hold-expiry detection and cancellation.

The PR describes booking notifications as transactional and deduplicated. The inspected service code shows direct inbox-row creation with a unique dedupe key; it does not establish a separate general-purpose outbox/worker architecture.

### 3.3 Explicitly disabled or incomplete channels

- Email delivery is disabled.
- SMS delivery is disabled.
- No production contact-challenge delivery provider is configured by PR #38.
- No WhatsApp Business provider or approved business account is evidenced.
- Telegram is not an approved default delivery channel.
- No provider credentials, webhook endpoints, sender registration or delivery receipts are evidenced.

## 4. Target architecture

### 4.1 Transactional write path

When a business event requires a notification:

1. The business operation validates its domain state and authorization.
2. In the same database transaction, it writes the business mutation and one immutable outbox event.
3. The transaction commits once; either both the business event and outbox event exist or neither exists.
4. A separate dispatcher claims pending outbox events with bounded concurrency and lease/lock semantics.
5. The dispatcher resolves the passenger's channel preferences and applicable consent/purpose.
6. The in-app notification is created idempotently from the event.
7. External channel adapters are called only when separately enabled and consented.
8. Each delivery attempt and final outcome is recorded without logging message secrets or unnecessary personal data.

The outbox is the durable handoff between business transactions and notification delivery. Provider delivery must never be called as an unprotected side effect before the business transaction commits.

### 4.2 Required records

The implementation design should distinguish:

- **OutboxEvent:** immutable event ID, event type/version, aggregate type/ID, tenant/organization, recipient principal, occurred-at time, minimal structured payload/reference, dedupe key, created-at and processing state.
- **DeliveryAttempt:** outbox event, channel, provider adapter/version, attempt number, started/finished time, provider message reference, outcome/error class and next retry time.
- **InboxNotification:** passenger-owned user-facing message, read state and stable source event reference.
- **ChannelPreference/Consent:** recipient, channel, purpose, source, status, captured-at, revoked-at and evidence reference.

Do not store rendered message copies containing unnecessary personal data in the outbox. Prefer stable resource references and template identifiers; resolve authorized content at dispatch/render time.

### 4.3 State and idempotency

Recommended outbox states:

`pending → leased → delivered | retry_wait | dead_letter | suppressed`

Requirements:

- Unique event/dedupe key scoped to the originating business event.
- Idempotent inbox creation and provider request handling.
- Expiring worker lease to recover from worker termination.
- Exponential backoff with bounded retries and jitter.
- Explicit permanent/transient error classification.
- Dead-letter review and replay with audit.
- Provider idempotency key where supported.
- No duplicate booking, wallet, dispatch or account mutation from a notification retry.
- No claim of delivery based only on successful provider API submission; distinguish accepted, delivered, failed and unknown provider states.

## 5. Channel policy and activation boundary

| Channel | Architectural role | Current disposition |
|---|---|---|
| In-app inbox | Canonical user-facing notification record | Existing candidate implementation; not merged |
| Email | Optional provider adapter for approved transactional notices | DISABLED / PROVIDER NOT CONFIGURED |
| SMS | Optional provider adapter for time-sensitive notices and verified challenges | DISABLED / PROVIDER NOT CONFIGURED |
| WhatsApp Business | Optional future adapter subject to business account, templates, consent, cost and provider terms | NOT SELECTED / NOT ACTIVATED |
| Telegram | Optional user-initiated integration only if separately approved | NOT SELECTED |
| Push notification | Future platform capability; requires device-token lifecycle and privacy/security review | NOT IMPLEMENTED / NOT ACTIVATED |

The in-app inbox remains the reliable in-product record even if external delivery is delayed or unavailable. The product must not imply that an SMS/email was delivered when only an inbox row was created.

## 6. Consent, privacy and security controls

- Separate service/security/transactional notification purposes.
- Record channel consent or other approved lawful basis, source and timestamp; support revocation.
- Do not use marketing consent as a proxy for essential account-security notices.
- Minimize notification title/body and avoid exposing sensitive booking, identity, location or cargo details on lock screens.
- Re-check recipient ownership and authorization when resolving a resource link.
- Never place session tokens, OTPs, passwords, private evidence URLs or payment secrets in notification content.
- Verify provider callback signatures, timestamps and replay protection before recording delivery receipts.
- Store provider credentials only in an approved server-side secret store.
- Redact provider request/response payloads and recipient addresses from ordinary logs.
- Enforce tenant/recipient boundaries and rate limits.
- Provide accessible Amharic/English templates and explicit delivery/error states.

## 7. Acceptance criteria for a later A3/A4 increment

1. Business event and outbox event commit atomically.
2. Rollback leaves neither partial business mutation nor orphan outbox event.
3. Duplicate event delivery creates one inbox item.
4. Worker crash/lease expiry recovers without duplicate external side effects.
5. Retry/backoff, permanent failure and dead-letter behavior are tested.
6. Preference opt-out and consent revocation suppress the appropriate external channel.
7. Provider callbacks are authenticated and idempotent.
8. Cross-tenant and cross-passenger notification reads are rejected.
9. External provider outage does not block or roll back a valid booking/business transaction.
10. Logs and notification content pass privacy/security review.
11. Provider cost, service terms, availability and sender registration are reviewed before any activation.
12. No real channel is activated in development acceptance; use synthetic recipients and provider mocks.

## 8. MN-009 disposition and governance

**MN-009: DELIVERED — PROVIDER-NEUTRAL OUTBOX/CHANNEL ARCHITECTURE RECORDED.**  
**Existing in-app inbox: PARTIAL IMPLEMENTATION EVIDENCE.**  
**Transactional outbox/dispatcher: NOT EVIDENCED AS IMPLEMENTED.**  
**External delivery: DISABLED / NOT AUTHORIZED.**

This is an A2 architecture record. It does not modify PR #38, add migrations, implement a worker, configure a provider, create secrets, dispatch workflows, merge, or deploy. Provider choice and activation remain separate decisions and approvals.