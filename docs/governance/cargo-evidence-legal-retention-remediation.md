# Cargo Delivery Evidence Lifecycle — Legal Retention Remediation

**Scope:** C01–C08 corrective implementation  
**Legal input:** Owner-supplied Ethiopian legal-validation opinion, determination: Not approved  
**Status:** Implemented on an isolated branch for technical verification; not approved for production.

## Governing safeguards

This implementation translates the supplied legal-review schedule into fail-closed application controls. It is not a legal opinion and does not independently establish the accuracy or applicability of the supplied legal interpretations.

### Evidence classification and retention

A record can carry multiple legal characteristics simultaneously:

- EC-1 accounting document: ten years from the accounting record date.
- EC-2 commercial correspondence: ten years from the correspondence date.
- EC-1 + EC-2: the later of the two mandatory expiry dates.
- EC-3 residual operational evidence: 24 calendar months from delivery closure, only with a DPIA reference and documented retention justification.
- EC-4 personal or sensitive personal data: privacy overlay and documented processing basis; sensitive-data classification requires a DPIA reference before independent DPO review.
- EC-5 legal hold: active hold blocks all automated and manual deletion pathways.

The classifier requires timezone-aware commencement dates for statutory categories. Missing dates fail closed. The classifier and DPO reviewer are separate actors. Statutory categories are marked `statutory` and are excluded from ordinary retention deletion.

### Deletion interlocks

All deletion paths must pass the shared `deletion_block_reason` policy:
- no active legal hold;
- no DPO deletion suspension;
- no pending data-subject rights request;
- no EC-1 or EC-2 statutory category;
- ordinary EC-3 classification only;
- independent DPO review and DPIA evidence;
- retention expiry reached;
- retention policy explicitly active.

Orphan cleanup uses the same interlocks and additionally requires an expired upload intent, an approved positive grace period, a reviewed EC-3 classification and no statutory category. It remains disabled by default.

### Legal holds

Release requires recorded DPO review, a separate Legal/Compliance releaser, confirmation that the underlying proceeding has concluded, and a conclusion reference. Hold records are retained as lifecycle history.

### Data-subject rights

Rights requests are recorded by reference, triaged by request type, and reviewed separately. Erasure is blocked where a mandatory statutory retention category, active legal hold, DPO suspension or incomplete DPO review applies. A DPO-approved erasure request for residual EC-3 evidence can override its ordinary retention expiry, but execution still requires a separate deletion request and distinct second-person approval. A reviewed request is not itself proof that a requested action has been fulfilled.

### Audit and tombstone minimization

Evidence audit events omit dispatch identifiers from metadata and redact GPS, coordinates, signatures, consignee, address, location, driver and storage-object fields. Audit and tombstone retention periods require separate Legal/Compliance proposals and independent DPO review. No automatic audit-log or tombstone purge is enabled by this change.

## External production gates — not implemented by code

The following require documentary evidence and remain production blockers:
1. ECA controller/processor registration.
2. DPO appointment and registration.
3. Completed and approved DPIA.
4. Verified Ethiopian hosting/localisation.
5. Subprocessor inventory and cross-border transfer safeguards or required ECA approval.
6. Signed legal revalidation of the corrected schedule and deployment conditions.

## C01–C08 traceability

| ID | Corrective control |
|---|---|
| C01 | Multi-flag evidence classification with overlapping EC-1/EC-2 categories and EC-4 privacy overlay |
| C02 | Ten-year statutory expiry calculations and conditional 24-month EC-3 calculation |
| C03 | Active-hold interlocks in manual deletion, retention worker and orphan cleanup |
| C04 | Shared fail-closed deletion decision function; DPO suspension and pending-rights blocks |
| C05 | Data-rights intake/review and DPO deletion suspension |
| C06 | Separate audit/tombstone retention proposals, DPO review and minimized audit metadata |
| C07 | Hold release conclusion reference and three-party separation between issuer, DPO reviewer and releaser |
| C08 | Unit tests for statutory schedules, overlapping categories and deletion interlock reasons |

## Safety boundary

No production policy activation, production migration, scheduler activation, object deletion, merge or deployment is authorized by this implementation. The new branch is intended for CI and review only. The original PR #49 baseline must remain unchanged.
