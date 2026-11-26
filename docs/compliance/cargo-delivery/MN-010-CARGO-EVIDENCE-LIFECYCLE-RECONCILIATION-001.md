# MN-010 — Cargo Evidence Lifecycle Legal and Technical Reconciliation

**Artifact:** MN-010-CARGO-EVIDENCE-LIFECYCLE-RECONCILIATION-001  
**Version:** 1.0.0  
**Assessment date:** 2026-11-26  
**Status:** DELIVERED — EVIDENCE RECONCILIATION; LEGAL/DPO CLOSURE PARTIAL  
**Repository:** `akefadaka-git/maalenex`  
**Main baseline:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Method:** Static reconciliation of Cargo PRs #45–#52, the controlled D01–D14 package, MN-005 Owner decisions and MN-006 findings. No production database, file store, workflow or deletion scheduler was accessed or activated.

## 1. Executive disposition

Cargo evidence lifecycle work has a substantial staged backend implementation: consignment and dispatch lifecycles, delivery proof, private evidence storage, lifecycle metadata, legal holds, deletion requests, retention controls, data-subject rights triage and DPO safeguards.

The implementation is not a production-ready or legally closed evidence-management service. Cargo PRs remain separate open branches. PR #50 and PR #51 contain competing migration descendants that both declare Alembic revision ID `0024_cargo_legal_retention` with different migration bodies. PR #51 has exact-head CI success; PR #50 does not have exact-head verification evidence in the reviewed record. That engineering difference does not resolve the design conflict or legal approval.

**Controlling Owner decision MN-005-D01:** Choice C — design a separately reconciled replacement Cargo retention model. Preserve PR #50 and PR #51 as competing historical evidence; do not merge either unchanged. The replacement must be designed and reviewed before any implementation.

## 2. Evidence inventory

| PR | Branch purpose | Exact head | Status/evidence |
|---|---|---|---|
| #45 | Consignment lifecycle | `c2debf278e682f850c13a9866722376548bc792f` | Open/draft; backend candidate |
| #46 | Dispatch and append-only tracking | `f0f221ce0ea2226c5f2fd2d8ec519c3b2e03a59b` | Open/draft; backend candidate |
| #47 | Carrier operations, delivery proof and exceptions | `7ca507c5fc6e5aec05e6039a869b170abb616990` | Open/draft; backend candidate |
| #48 | Private delivery-evidence storage | `ab89ae0b13e6b6091808ab8240a76fedd49069ea` | Open/draft; private storage candidate |
| #49 | Evidence lifecycle governance | `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | Open/draft; lifecycle/hold base |
| #50 | Retention alternative A | `73fee61613e533bd75d1e7e85db8689ee1a4799b` | Open/draft; exact-head CI NOT VERIFIED |
| #51 | Corrective retention alternative B | `b81e788b55bb5c988d77412ce54f483106675e82` | Open/non-draft; exact-head CI PASS |
| #52 | D01–D14/C06 controlled review package | `b7d025e2e23be9359e4f648b8b88c3dcb3e455e5` | Open/draft; documentation-only, not approved for external submission |

PR #51 Actions run #45056584444 reports SUCCESS on the exact PR #51 head and base. Its recorded checks include 155 backend tests passed, 9 skipped, API container build, empty-database migration upgrade, HTTPS/session/CORS smoke, Alembic metadata parity, downgrade and clean re-upgrade. This is engineering evidence only. It is not independent Legal or DPO approval, not proof of deployment, and not a reason to select PR #51 as the final design without the Owner-directed replacement review.

## 3. Lifecycle and data-boundary reconciliation

The staged code covers:

1. Consignment creation and lifecycle.
2. Dispatch offers, assignment and state transitions.
3. Append-only tracking/checkpoint events, including optional coordinates.
4. Carrier operational eligibility.
5. Delivery-proof submission and review.
6. Private PDF/JPEG/PNG evidence upload and verification.
7. Evidence lifecycle state, access grants and legal-hold metadata.
8. Deletion requests and retention-policy metadata.
9. Rights-request triage and DPO deletion-suspension controls.
10. Audit events and tombstone/audit retention metadata.

The staged Cargo branches do not establish a deployed Cargo service. No production data, hosted object-storage bucket, actual file contents, live operational volumes, partner client or production configuration was inspected. The source-level inventory cannot establish whether uploaded files contain identity documents, faces, signatures, addresses or sensitive personal data.

## 4. Competing migration collision

The two competing retention descendants share the same parent and revision identifier:

| Alternative | Migration sequence |
|---|---|
| PR #50 | `0024_cargo_legal_retention` → `0025_audit_tombstone_review` |
| PR #51 | `0024_cargo_legal_retention` → `0025_cargo_evidence_rights` → `0026_cargo_evidence_dpo_controls` |

Both declare `0024_cargo_legal_retention` with parent `0023_cargo_evidence_hold_review`, but the migration bodies differ. They cannot both exist unchanged in one Alembic graph.

**Required treatment:**

- Preserve PR #50 and PR #51 as historical evidence.
- Do not merge or combine either branch unchanged.
- Produce a replacement model reflecting the Owner's D1=C decision.
- Assign unique migration identifiers only during separately authorized A3 implementation, after exact parent and graph verification.
- Preserve existing migration history; no renumbering or database execution during this A2 reconciliation.
- Document downgrade behavior and populated-data safeguards before implementation.

## 5. D01–D14 documentary status

The controlled register in PR #52 is explicitly a derivative review package, not the original populated evidence register. It preserves differing source assessments and labels unrecovered evidence accurately.

| ID | Subject | Current status from controlled register | Principal outstanding evidence |
|---|---|---|---|
| D01 | ECA PDP registration and hybrid courier-service licensing | UNRESOLVED | Incorporation/TIN, actual operator-role map, licences or written non-applicability determination |
| D02 | Data Protection Officer | UNRESOLVED | Article 40 threshold analysis, attributed written determination, appointment/registration if triggered |
| D03 | DPIA | PARTIAL | Complete versioned DPIA, scope reconciliation, Owner acceptance and DPO determination |
| D04 | Data inventory and processing flows | PARTIAL | Actual client/runtime, partner/processor flows, file contents, locations and measured volumes |
| D05 | Hosting/data residency | UNRESOLVED | Primary/backup/replica regions, provider terms and support-access evidence |
| D06 | International transfers | UNRESOLVED | Destination/access map, safeguards and any required ECA approval |
| D07 | Privacy notices, lawful bases and retention | UNRESOLVED | Approved notices, lawful-basis register and category-specific schedule |
| D08 | Processor agreements | UNRESOLVED | Executed agreements and subprocessor inventory |
| D09 | Data-subject rights | PARTIAL — SOFTWARE ONLY | Approved SOP, operational case evidence and exercise |
| D10 | Security controls | PARTIAL — ENGINEERING ONLY | Consolidated security assessment, key/backup/access/incident assurance and independent review |
| D11 | Tombstone/audit retention | PARTIAL | Approved periods/triggers, minimisation, implementation and operational tests |
| D12 | Legal holds | PARTIAL — SOFTWARE/GOVERNANCE INTENT | Written SOP, authority, annual review and operational exercise |
| D13 | Independent Legal/DPO determinations | PARTIAL | Verified reviewer identity/qualification/signature, Owner acceptance and separate final determinations |
| D14 | Accounting/tax/commercial correspondence retention | PARTIAL — LEGAL POSITION ONLY | Confirmed source dates/triggers, implementation and destruction workflow |

“Not located in sources searched” is not equivalent to “does not exist.” Missing source locations remain NOT RECOVERED / NOT VERIFIED until authenticated evidence is produced.

## 6. C06 retention determinations — qualifications preserved

The recovered professional determinations recorded in PR #52 describe:

- Cargo-evidence tombstones: 10 years from deletion of the underlying evidence, as a professional determination.
- Audit logs: 5 years from creation of each audit entry, as a professional recommendation.
- The cited provisions do not establish that these periods are universally statutory periods for all tombstones or audit logs.
- A valid written legal hold suspends the clock until written release.
- Tombstones must be strictly minimized; destruction certificates have their own personal-data implications.
- The destruction-certificate retention period is NOT DETERMINED / NOT VERIFIED.

These recommendations are not a final Owner-approved retention schedule or authority to activate purge.

## 7. Replacement design requirements (MN-005-D01=C)

The replacement Cargo evidence lifecycle specification must, at minimum:

1. Define evidence classes by purpose and legal category, with multi-characteristic personal-data overlays.
2. Record the authoritative event date and legal trigger for each retention class.
3. Apply the latest applicable mandatory deadline where categories overlap.
4. Keep residual operational retention distinct from statutory accounting/commercial retention.
5. Require documented lawful basis, purpose and DPIA/DPO review for residual retention.
6. Make deletion fail closed for incomplete classification, missing dates, active holds, pending rights requests, unresolved DPO review or unapproved policy.
7. Apply the same eligibility interlock to manual deletion, scheduled deletion and orphan cleanup.
8. Keep production purge and scheduler disabled until all documentary, legal and operational gates pass.
9. Separate Legal/Compliance hold issuance from DPO review and hold release.
10. Minimize audit/tombstone data and define their own retention with independent approval.
11. Include backup, replica and disaster-recovery deletion/restore semantics.
12. Preserve auditable evidence of eligibility, authorization, execution, failure and verification.
13. Include a safe dry-run, kill switch, idempotency and retry behavior.
14. Map each control to D01–D14 evidence and the responsible reviewer/Owner decision.

No retention period, statutory interpretation or deletion schedule may be invented to fill missing evidence.

## 8. Production and operational gates

The following remain disabled or unapproved:

- Production retention-policy activation.
- Production deletion or purge.
- Retention scheduler/automation.
- Hosted migration.
- Cargo commercial activation.
- Live GPS or public tracking.
- External reviewer submission of the D01–D14 package.
- Merge and deployment.

Legal and DPO revalidation, hosting/data-residency, transfer safeguards, privacy notices, processor agreements, rights-handling SOP, security assurance and Owner acceptance remain outstanding.

## 9. MN-010 disposition and governance

**MN-010: DELIVERED — CARGO LIFECYCLE EVIDENCE AND REPLACEMENT REQUIREMENTS RECONCILED.**  
**Cargo legal/privacy closure: PARTIAL / NOT CLOSED.**  
**PR #50/#51 migration collision: UNRESOLVED — replacement design required.**  
**Production deletion, purge and retention automation: DISABLED / NOT AUTHORIZED.**

This record does not amend Cargo source, select either competing implementation, create migrations, run tests, access production data, submit evidence externally, merge, deploy or authorize A5.