# MaaleNex Evidence Lifecycle Governance v1 — A3 Implementation Contract

**Status:** FROZEN — Owner policy decisions recorded  
**Stage:** A3 contract freeze only; implementation is not authorized  
**Repository baseline:** `akefadaka-git/maalenex`  
**Contract base:** PR #48 head `ab89ae0b13e6b6091808ab8240a76fedd49069ea`  
**PR #48:** https://github.com/akefadaka-git/maalenex/pull/48 — preserve unchanged  
**Decision date:** 2026-11-22  
**Owner authority:** Owner-approved policy decisions recorded in the governing project conversation

## 1. Owner-approved policy decisions

The following decisions are binding inputs to this contract:

1. **Retention:** retain ordinary delivery evidence for **24 months provisionally**, measured from delivery closure. This is an operational default pending legal validation; it is not represented as a statutory Ethiopian retention period.
2. **Access and deletion:** approve the proposed separation of carrier, platform reviewer, evidence custodian, Legal/Compliance, and DPO responsibilities. Manual deletion requires dual control: the requester and approver must be distinct authorized people, with the deletion action and outcome recorded.
3. **Legal hold:** the **Legal/Compliance Officer** is authorized to initiate and release legal holds, with **DPO oversight**. The evidence custodian implements the hold and ensures deletion is blocked. A hold does not itself grant additional evidence-read access.

No retention policy is to be activated in production by this contract. The 24-month period is a versioned policy value to be configurable and auditable.

## 2. Legal-validation caveats and mandatory pre-activation checks

This contract is an engineering specification, not a legal opinion. Before production activation, Legal/Compliance and the DPO must document a jurisdiction- and record-class-specific validation covering at least:

- **Personal Data Protection Proclamation No. 1321/2024:** validate purpose limitation, necessity, reasonable retention, security, processing records, data-subject rights, and secure destruction. Articles 15 and 50 are relevant to retention and destruction; Article 42 is relevant to technical/organizational safeguards and processing logs. Do not retain personal data indefinitely merely because storage is inexpensive.
- **Commercial Code Proclamation No. 1243/2021, Article 66:** books of account and accounting documents are subject to a 10-year retention requirement. Legal/Compliance must determine whether a particular delivery record or attachment is itself an accounting document or a supporting accounting record. **Do not automatically extend the 10-year rule to every photograph, scan, or ordinary delivery attachment.**
- Confirm whether transport, carriage, insurance, contractual, tax, limitation-period, dispute, investigation, or other sector-specific rules require a longer or different period for particular evidence classes.
- Validate the retention trigger (delivery closure), treatment of reopened/contested deliveries, orphan-upload cleanup grace period, legal-hold release consequences, and any cross-border processor/storage obligations.
- Approve the final retention schedule, destruction method, notices/instructions to processors, and exception register before enabling scheduled deletion.

Until those checks are documented and the policy is separately activated, the 24-month value remains a **provisional contract default only**. If a record is subject to a longer mandatory period or an active hold, deletion must be blocked. If applicable law requires earlier erasure, Legal/Compliance and the DPO must resolve the conflict before the ordinary schedule is applied.

## 3. Baseline and compatibility constraints

The implementation must build on, and must not rewrite, the verified PR #48 increment:

- Existing private S3-compatible storage integration and provider configuration.
- Existing `CargoDeliveryProof.evidence_reference` private object-key field and historical proof records.
- Existing dispatch/carrier scoping and upload verification behavior.
- Existing audit service and authorization framework.

Preserve historical proof metadata when evidence bytes are deleted. Do not expose raw object keys, presigned URLs, credentials, or storage endpoints in API responses or audit metadata. Use evidence-record identifiers in audit events.

## 4. A3 scope

### 4.1 Evidence lifecycle registry

Add a durable lifecycle record for each uploaded evidence object, including:

- Stable evidence-record identifier.
- Carrier organization and dispatch identifiers.
- Private storage object key (server-side only).
- Upload-intent creation and expiry timestamps.
- Object verification timestamp and verified metadata (size, media type, checksum/signature evidence as appropriate).
- Optional association to the relevant delivery-proof record.
- Lifecycle state sufficient to distinguish pending, verified/unattached, attached, held, deletion-requested, deleted, and deletion-failed states.
- Retention-policy version, retention-start timestamp, and calculated expiry timestamp.
- Legal-hold state and hold metadata (case/dispute reference, basis/reason, issuing officer, issue date, review date, release authority/date).
- Deletion request, approver, executor, reason, attempt/completion timestamps, and outcome.
- Tombstone/history fields sufficient to preserve the evidence record and audit trail after object bytes are removed.

Support identification and cleanup of uploaded objects that expire without being attached to a delivery proof. Do not orphan or silently lose lifecycle state for legacy proof records; provide a safe reconciliation/backfill strategy.

### 4.2 Retention and cleanup

- Implement a versioned, configurable retention policy. The provisional default for ordinary attached delivery evidence is 24 months after delivery closure.
- Persist the policy version and computed expiry for each applicable evidence record; do not infer expiry solely from current configuration at deletion time.
- Do not activate production deletion or assume the provisional default has passed legal validation.
- Legal hold always blocks automated deletion.
- Records classified as accounting documents or otherwise subject to a longer mandatory period must use the legally validated schedule.
- Expired unattached uploads must be identified and cleaned after a separately configured, legally validated grace period following upload-intent expiry.
- Retention evaluation and cleanup must be idempotent, bounded, observable, and safe to retry.
- If no valid policy applies, fail closed: do not delete.

### 4.3 Authorized private evidence access

Implement a dedicated authenticated evidence-read flow that returns only a short-lived private download authorization after server-side authorization. No public bucket, public URL, or permanent download URL.

Proposed distinct permissions:

- `operator.cargo.delivery_proof.evidence.read`
- `platform.cargo.delivery_proof.evidence.read`
- `platform.cargo.delivery_proof.evidence.hold.manage`
- `platform.cargo.delivery_proof.evidence.delete`

Authorization rules:

- Carrier users may read only evidence for dispatches belonging to their own carrier organization and only when assigned/otherwise authorized for that dispatch.
- Platform reviewers may read only cases explicitly assigned/authorized to them; review permission alone does not imply evidence-read.
- Evidence custodians may perform their separately granted custody functions; custody does not imply unrestricted access to all evidence.
- Legal/Compliance access is limited to documented legal cases and a separately granted evidence-read permission.
- DPO oversight does not create blanket read access; access must be justified and separately authorized.
- Submission, review, operations-management, and exception-management permissions do not implicitly grant evidence-read or delete.
- Every request must verify evidence ID, proof/dispatch association, carrier ownership, lifecycle state, retention state, and hold state.
- Expired or deleted evidence must not be downloadable. A legal hold blocks deletion but does not bypass access checks.
- Storage failures must be distinguishable from invalid client evidence and remain retryable where appropriate.

### 4.4 Hold workflow

- Legal/Compliance Officer may initiate and release a hold with a recorded legal/dispute basis and case reference.
- DPO provides oversight of privacy, necessity, scope, and review cadence; record the DPO review/oversight outcome.
- Evidence Custodian applies the hold state and verifies that retention workers cannot delete held objects.
- Each hold records affected evidence/dispatch scope, reason/legal basis, issuing officer, issue timestamp, review date, and release authority/timestamp.
- Holds must be periodically reviewed; do not allow unreviewed indefinite holds by default.
- Release requires an authorized Legal/Compliance Officer action and recorded DPO oversight. On release, recalculate eligibility using the applicable validated schedule; do not automatically delete without a fresh eligibility check and any required dual-control approval.
- Owner/Board escalation is reserved for exceptional disputes or overrides only where legally permissible; it is not a routine prerequisite for every hold.

### 4.5 Controlled deletion

- Support reasoned deletion requests and policy-driven expiry deletion.
- Manual deletion requires a distinct requester and approver (dual control); the executor must be authorized and the complete chain auditable.
- Reject deletion while retention is active, a legal hold is active, or another legal/contractual preservation rule applies.
- Make deletion idempotent and retryable. A storage error must never be recorded as successful deletion.
- Preserve the lifecycle tombstone, delivery-proof metadata, dispatch/consignment records, and audit history after object deletion.
- Do not delete or overwrite proof metadata to simulate evidence removal.
- Never silently replace a rejected proof or alter proof acceptance rules.

### 4.6 Audit and privacy

Record auditable events for upload registration/verification/attachment, retention evaluation, hold creation/review/release, access granted/denied, deletion requested/approved/completed/failed, and orphan cleanup.

Audit entries must identify actor, organization, evidence-record ID, related dispatch/proof, action, outcome, reason where required, and timestamp. Do not include raw object keys, presigned URLs, credentials, or unnecessary personal data. Access logs must support investigation of who accessed what, when, and why, consistent with the applicable law and approved retention schedule for logs.

## 5. Migration and legacy-data requirements

- Add additive migrations only; do not destructively alter or remove existing proof records.
- Reconcile existing `CargoDeliveryProof` rows and their private object references into lifecycle records without changing the established evidence reference or proof status.
- Backfill unknown historical upload/verification/closure dates as explicitly unknown; do not fabricate dates or silently assign an expiry.
- Mark legacy records requiring manual classification or legal review; fail closed for deletion until reconciled.
- Ensure downgrade behavior is safe and documented. Do not make a downgrade delete evidence objects or lifecycle/audit history.

## 6. Required verification and acceptance criteria

A3 is complete only when automated tests and exact-head CI demonstrate:

1. Correct lifecycle registration and proof association, including idempotency.
2. Legacy evidence reconciliation with unknown dates preserved as unknown.
3. Carrier same-organization access succeeds only for authorized dispatches; cross-carrier and cross-dispatch access is denied.
4. Platform evidence access requires explicit evidence-read permission and case authorization.
5. Submission/review permissions alone cannot read or delete evidence.
6. Evidence cannot be downloaded after expiry or deletion; no public URL is emitted.
7. Retention uses the persisted policy version and closure timestamp; no-policy and unknown-classification cases fail closed.
8. Active legal holds block automated and manual deletion; hold release is auditable and does not bypass retention checks.
9. Manual deletion enforces distinct requester/approver identities.
10. Successful deletion removes object bytes but preserves tombstone, proof metadata, and audit history.
11. Storage outages produce retryable failures and never false deletion success.
12. Orphan uploads are found and cleaned only after the approved grace period, with idempotent retries.
13. Audit events contain no raw object keys, presigned URLs, credentials, or unnecessary personal data.
14. Existing PR #48 upload-intent and verification tests remain passing.
15. Migration upgrade/downgrade and metadata parity checks pass without destructive evidence loss.

## 7. Explicit exclusions and release gates

Out of scope:

- Any modification to PR #48 or its branch.
- Frontend, mobile, or public-facing UI.
- Storage-provider change, public bucket, public evidence URL, or permanent download URL.
- Change to delivery-proof acceptance/rejection rules.
- Deletion of delivery-proof, dispatch, consignment, or audit metadata.
- Production retention activation, production deletion, hosted migration, deployment, or production service activation.
- Billing, paid services, or provider upgrades.
- Autonomous evidence decisions.

**Separate authorization required:** This document freezes the A3 implementation contract only. It does not authorize A3 implementation, merge, deployment, hosted migration, production retention activation, or production deletion. Those actions remain behind their own Owner approval gates.

## 8. Freeze record

The A3 contract is considered frozen at this revision because the three required Owner policy choices have been explicitly resolved. Any change to the approved retention period, access/deletion role separation, or legal-hold authority requires an explicit Owner-approved contract revision. Legal validation may refine the schedule before production activation, but must not silently weaken the approved access, dual-control, audit, or hold safeguards.

**Baseline protection:** PR #48 remains the unchanged technical baseline at head `ab89ae0b13e6b6091808ab8240a76fedd49069ea`. This contract is recorded on a separate documentation branch based on that exact head.
