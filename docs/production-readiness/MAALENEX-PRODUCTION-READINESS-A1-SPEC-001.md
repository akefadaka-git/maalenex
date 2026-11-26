# MAALENEX-PRODUCTION-READINESS-A1-SPEC-001

**Version:** 1.0.0-draft  
**Status:** DRAFT FOR OWNER REVIEW — NOT FROZEN  
**Assessment date:** 2026-11-26  
**Repository baseline:** `main` at `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Product scope:** MaaleNex passenger platform, API and user experience  
**Priority:** Passenger MVP first; preserve the existing passenger application

## 1. Purpose and boundary

Define the production-readiness target for the existing MaaleNex API and passenger UI. This specification supplements, and does not amend or replace, the frozen `MAALENEX-IA-A1-SPEC-001 v1.0.0` platform-wide MaaleNex–IROKA architecture.

The objective is a secure, reliable, Amharic-first passenger service with a polished, dynamic and responsive interface. Build on existing workflows and reconcile existing feature branches; do not replace the passenger app with a demo or parallel implementation.

This is an architecture and acceptance baseline only. It does not authorize application implementation, migration execution, provider activation, production data processing, merge or deployment.

## 2. Owner constraints carried forward

1. Preserve the current passenger journey and all unrelated work.
2. Passenger experience and end-to-end booking lifecycle take priority over expansion of driver, agent and administrator surfaces.
3. Keep synthetic-only development/test boundaries. Never place real passenger/operator data, credentials, identity documents or production secrets in this public repository.
4. No paid provider, account, service, map API, CI billing or top-up is to be activated without separate authorization.
5. No payment collection, wallet movement, ticket issuance, boarding validation or commercial operation until separate legal, security, operational and Owner gates are satisfied.
6. A5 deployment is separate and requires explicit authorization. No merge or deployment is authorized by this specification.
7. Preserve the existing frozen MaaleNex–IROKA A1 baseline and the previous A2 closure record; this production-readiness assessment is a separate work item.

## 3. Product and UX target

### 3.1 Passenger-first scope

The first production candidate must complete and verify, end to end:

- Amharic-first and English passenger entry.
- Account registration, sign-in, session recovery and secure sign-out where account flows are included.
- Published trip discovery, route/date/passenger search and accurate availability timestamps.
- Seat selection, inventory revalidation, idempotent reservation hold and expiry.
- Contact verification through an explicitly configured and tested delivery path.
- Booking recovery, reservation confirmation, passenger-owned booking access and support.
- Clear distinction between a reservation reference/QR and a travel ticket or boarding authorization.
- Clear unavailable/offline/error states and safe retry behavior.

Do not expand role-specific operational interfaces ahead of the passenger acceptance gate. Preserve the existing staff/operations workspaces as separate implementation streams.

### 3.2 Visual system and interaction

Target a modern MaaleNex NEXUS experience: deep evergreen/midnight surfaces, restrained mint/cyan accents, legible hierarchy, crisp cards and status indicators, responsive navigation, useful motion and high-quality mobile interaction.

Amharic is the default language. Use locally bundled Noto Sans Ethiopic, locale-aware dates/numerals and Ethiopian Calendar presentation where applicable; preserve English as an alternative. Support narrow Android screens, touch targets, scalable text, keyboard focus, semantic controls and reduced-motion preferences. Target WCAG 2.2 AA; automated checks alone do not constitute accessibility certification.

The NEXUS design-system document found on an unmerged branch is a candidate reference, not proof that the design is implemented or approved. Reconcile it with the current main UI before adoption. Keep all visible service status, map provenance, booking/payment limitations and operational states truthful.

### 3.3 UI architecture

Use the existing React/TypeScript/Vite application as the starting point. Introduce feature boundaries and reusable shell/components incrementally; retain existing passenger workflow state and API contracts unless a controlled change is approved. Avoid a wholesale rewrite.

The UI must support loading, empty, stale, offline, validation, authorization, conflict, retry and success states. Server-side authorization and validation remain authoritative; hiding a control is not a security boundary.

## 4. API and data architecture

- Retain the FastAPI modular-monolith API under `/api/v1`.
- PostgreSQL is the operational system of record. Use transactional boundaries for booking, inventory, notification creation and audit events.
- Preserve the existing idempotency, row-locking and seat-allocation invariants; extend them with concurrency and retry tests rather than weakening them.
- Keep authentication, authorization, tenant/organization scoping, CSRF protection, audit records and rate limits server-enforced.
- Production configuration must fail closed: explicit environment, secure cookies, exact HTTPS CORS origins, remote PostgreSQL with verified TLS, managed secrets, trusted proxy configuration and no development defaults.
- Provide distinct liveness and dependency-aware readiness endpoints. Disable interactive API documentation in production unless an explicitly approved access control is in place.
- Run migrations as a controlled one-off release task, not concurrently from each API replica.
- Run schedulers and asynchronous workers as separate, explicitly enabled processes with durable leases, idempotency and bounded retries.
- Add structured, redacted logs, metrics, alerts, error reporting, backup/restore evidence, retention controls and incident/recovery runbooks before production activation.

## 5. Geographic and map architecture

The target is the previously selected self-hosted-first direction: MapLibre rendering, Martin as a candidate vector-tile service, and PostGIS in the primary PostgreSQL platform database. The approved logical schema direction is `geo`, `geo_public`, `geo_internal` and `geo_audit`, with tenant-scoped authorization and database-level controls. Public/internal access must be enforced in API and database queries, not by hiding map layers.

Reconcile the passenger map implementation, the MITP tracking proof of concept and all Alembic histories before implementation. Do not accept competing Google Maps, JSON-only route geometry or isolated map databases as the canonical design without an explicit amendment.

Only publish routes and boarding points supported by authoritative/approved evidence. Retain source, license, capture date, verification status and revision history. The Koybe boarding point coordinates remain the Owner-provided reference; do not infer or fabricate route traces or intermediate stops. Route geometry must remain unpublished until its original stop sequence and source trace are reconciled.

## 6. Notification architecture and channel recommendation

### 6.1 Source of truth

The authenticated in-app inbox is the canonical notification record and history. Business events must be committed independently of external message delivery. A provider outage must never roll back, duplicate or block a booking or other core business transaction.

Use a transactional outbox written in the same database transaction as the triggering business event, with a separately operated worker. The delivery subsystem must support provider adapters, idempotent message keys, bounded exponential retries, delivery state transitions, webhook verification, dead-letter handling, rate limits, redacted audit evidence, bilingual templates and operator-visible delivery diagnostics.

### 6.2 Channel priority

- **WhatsApp Business — preferred outbound passenger channel** for opted-in transactional updates where approved templates and provider policy permit it.
- **SMS — OTP/contact verification and fallback/urgent delivery**, subject to consent, local deliverability, security and cost validation.
- **Email — formal confirmations, account/security notices and durable correspondence** where a verified address exists.
- **Telegram — optional, user-initiated linked channel only**; not a required dependency.
- **In-app — always the source of truth**, with unread/read state and delivery-independent history.

No provider has been selected or activated. WhatsApp requires compliant opt-in, a WhatsApp Business Account and approved message templates where applicable. Provider selection must compare Ethiopian reach, sender identity, delivery receipts, API/webhook security, data processing terms, support, pricing and sandbox availability. Do not enter credentials, start a paid account or send live messages under this A1.

### 6.3 Consent and preference controls

Store explicit, channel-specific consent/opt-in evidence, purpose, source, timestamp, locale, destination verification and revocation. Essential security/OTP messages must be separated from optional marketing/preferences. Respect provider policy, Ethiopian privacy/telecommunications requirements and user withdrawal. Never treat a phone number or Telegram/WhatsApp account as consent by itself.

## 7. Security, privacy and operational controls

Before production acceptance, verify:

- Threat model and independent application/API/mobile security review.
- Session/token storage, rotation, revocation, expiry and CSRF/origin protections.
- Password hashing, account enumeration resistance, login and OTP rate limits, brute-force controls and recovery.
- Authorization and tenant-isolation tests for every sensitive resource.
- SQL injection, XSS, CSRF, SSRF, upload validation, dependency/supply-chain and secret scanning.
- Encryption in transit and at rest, key management/rotation, least privilege and secret separation.
- Privacy notice, purpose limitation, retention/deletion, data-subject request process and incident response.
- Database backups with a witnessed restore test, recovery objectives, monitoring, alerting and capacity/load testing.
- Exact production origins, trusted reverse-proxy IPs, HTTPS, secure cookies, database TLS and production API connectivity from web and Android clients.

## 8. Delivery gates and acceptance

| Gate | Required outcome | Status |
|---|---|---|
| A1 | Architecture, UX, security, notification and operational target specified | Draft; Owner freeze pending |
| A2 | Read-only reconciliation of main, stacked PRs, migrations, CI and external dependencies | In progress; gaps recorded separately |
| A3 | Bounded implementation on controlled branches after separate authorization | Not authorized by this record |
| A4 | Exact-SHA backend/frontend/Android, migration, security, end-to-end and device acceptance | Not run as a complete production acceptance |
| A5 | Production provisioning, migration, release and live operation | Separate explicit authorization required |

Passenger release acceptance requires successful exact-SHA tests, PostgreSQL migration parity and rollback/re-upgrade, end-to-end passenger journey against the intended API, cross-origin cookie/CSRF/CORS checks, Android installation and physical-device checks, accessibility review, operational backup/restore and monitoring evidence, and independent security review.

Payment, wallet movement, ticketing, boarding and commercial activation remain separately gated.

## 9. Change control

This document remains a draft until the Owner explicitly approves and freezes it. Amendments must identify the requirement, evidence, impact, security/privacy consequences, decision and version. The existing frozen `MAALENEX-IA-A1-SPEC-001` must not be silently edited or reopened.

**Disposition:** DRAFT FOR OWNER REVIEW — NOT FROZEN.  
**Next:** Complete A2 evidence reconciliation; no A3 implementation is implied.
