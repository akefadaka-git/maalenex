# C06 Determinations and Production Activation Gate

**Disposition:** FOR OWNER REVIEW — NOT APPROVED FOR EXTERNAL SUBMISSION  
**Status:** C06 PARTIAL; production activation NOT AUTHORISED  
**Source records:** Endalkachew response (23 Nov 2026 06:21 Library record); Dr. Kebene Wodajo DPIA confirmation (14 Hidar 2019 E.C.); PR #51 C06 disposition.

## 1. Separate professional determinations

### 1.1 Cargo-evidence tombstones — ten years

Endalkachew's response records a **10-year period from deletion of the underlying cargo evidence**. The response expressly characterises this as a professional determination, not a period directly prescribed by statute for every tombstone. It cites Civil Code Article 1845 and Commercial Code Proclamation 1243/2021 Articles 66–67 as rationale. Do not state that those provisions universally prescribe ten years for all tombstones.

Dr. Kebene Wodajo independently aligns with a ten-year tombstone period measured from execution of deletion, conditionally, as a professional determination. The exact report file path and signature verification were not recovered in the source set used for this package.

### 1.2 Audit logs — five years

Endalkachew records a **5-year period from creation of each audit-log entry**. This is a professional recommendation, **not a statutory period**. The response notes that Personal Data Protection Proclamation 1321/2024 Article 46(4)(e) empowers the Authority to set log-retention periods, and states that no Authority determination had been issued as of the response date.

Dr. Kebene independently aligns with the five-year period from creation. Do not present this recommendation as an Authority-mandated retention period.

### 1.3 Time computation and legal holds

- The periods are continuous calendar periods.
- Ordinary access does not reset the clock.
- A valid legal hold suspends the clock from written notification until written release.
- Held/statutory archive records must be restricted, access-controlled, read-only and audit-logged.
- The source determinations are not, by themselves, Owner approval of a production schedule or authority to activate purge.

## 2. Data minimisation and access safeguards

### 2.1 Tombstone fields

Dr. Kebene's confirmation calls for strict minimisation. Permitted minimal fields described in the report:

- Cryptographic hash of the record key.
- Evidence category.
- Deletion timestamp.
- Reason code.
- Authorising role (avoid the individual's name).
- Legal-basis/request reference.

Exclude names, phone numbers, addresses, GPS, delivery content, payment references, free text and direct identifiers. Keep hash salt/key separate; restrict access to read-only roles; log access; exclude tombstones from analytics, reporting and external APIs.

### 2.2 Audit-log fields

- Event metadata only.
- No payload, message bodies, GPS or free text.
- Pseudonymise actor IDs where feasible.
- Restrict access and log access.

### 2.3 Destruction certificates

The DPIA confirmation notes that a destruction certificate is itself personal data. It therefore needs purpose limitation, access restrictions and its own separately defined retention period. That period is **NOT DETERMINED / NOT VERIFIED** in the recovered source record and must not be invented.

## 3. Other required safeguards

The DPIA confirmation identifies the following controls:

- Annual legal-hold review.
- Written erasure-reconciliation procedure.
- Dry-run and kill switch.
- Idempotent and fail-safe deletion behaviour.
- Backup, replica and disaster-recovery restore safeguards.
- DPIA change triggers and reassessment when processing changes.

These are review requirements; this document does not assert that each has been operationally implemented or tested.

## 4. Production activation conditions

Production deletion, purge and retention automation must remain disabled until all conditions below are evidenced, reviewed and approved:

1. Complete category retention schedule with authoritative triggers and exceptions.
2. Written legal-hold procedure, authority, release process and suspension evidence.
3. Approved destruction method and destruction-certificate workflow, including the certificate's own retention.
4. Confirmed lawful bases and published privacy notices.
5. ECA registration/authorisation or reasoned non-applicability; hosting/data-residency and transfer position resolved.
6. Data-subject-rights reconciliation rule documented and operationally tested.

The DPIA reviewer requires the Project Owner's written approval after the DPIA reviewer confirms the conditions are evidenced. This package is not that approval.

## 5. Current production gate

| Control | Current state |
|---|---|
| Production deletion | **DISABLED** |
| Production purge | **DISABLED** |
| Retention scheduler / automation | **DISABLED** |
| Retention policy activation | **NOT AUTHORISED** |
| C06 final period approval | **PENDING** |
| Destruction-certificate retention period | **NOT DETERMINED / NOT VERIFIED** |
| Owner activation approval | **NOT GIVEN** |
| A5 / deployment | **NOT AUTHORISED** |

No purge mechanism is implemented or enabled according to the PR #51 formal submission record. Do not infer an activation schedule from the C06 metadata fields.

## 6. Reviewer and Owner actions

- Legal reviewer: confirm the legal basis, statutory interpretation, trigger dates, overlap and exceptions; distinguish statutory periods from professional recommendations.
- DPIA/DPO reviewer: confirm proportionality, minimisation, safeguards, deletion/hold controls and residual risks.
- Project Owner: accept or reject the reports and approve any schedule only after documentary and operational gates are evidenced.
- Repository implementer: do not activate deletion, purge, scheduler, retention policy, production migration or deployment as part of this documentation task.

## 7. Review disposition

C06 remains **PARTIAL**. This record does not close D11 or D14, approve any retention schedule, authorise purge, or constitute a Legal/DPO approval.
