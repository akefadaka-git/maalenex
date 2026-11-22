# MaaleNex Carrier Operations, Delivery Proof and Exceptions v1

## Scope
Backend-only carrier operational eligibility, dispatch-scoped proof-of-delivery submission and review, and auditable exception resolution. No frontend, payment, external carrier webhook, public tracking, autonomous dispatch or production activation.

## Carrier operations
One operational profile per approved operator organization. Statuses are pending, active, restricted and suspended. Platform operations roles manage status; carrier staff may read/manage only through the assigned organization permission. The profile is an operational control, not a substitute for licensing, insurance or regulatory verification.

## Delivery proof
One proof record per dispatch. Carrier staff submit recipient name, server/private evidence reference, optional notes and timezone-aware delivery occurrence time. Platform operations reviews and accepts or rejects the proof. Dispatch completion is blocked until a proof is accepted. Evidence bytes are not uploaded by this API; evidence_reference must identify an object in an independently governed private evidence store.

## Exceptions
Supported classifications include failed delivery, recipient unavailable/refused, cargo damaged/missing, delay, documentation issue and other. Cases transition open -> investigating -> resolved -> closed, with resolution code, notes, actor and timestamps. Every mutation emits an audit event. Idempotency keys are scoped to dispatch.

## Migration and boundary
Migration 0021 follows 0020 and is additive. It is tested by the existing clean PostgreSQL migration workflow. No hosted migration is performed. Evidence retention, legal admissibility, carrier licensing and insurance remain separate operational/compliance gates.
