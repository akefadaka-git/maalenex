# MN-006 — Final Read-only A2 Reconciliation

**Artifact:** MN-006-FINAL-READ-ONLY-A2-RECONCILIATION-001  
**Version:** 1.0.0  
**Assessment date:** 2026-11-26  
**Status:** MN-006 DELIVERED — READ-ONLY; CURRENT MN-SERIES A2 INTEGRATION RECONCILIATION OPEN / NOT CLOSED  
**Canonical repository:** `akefadaka-git/maalenex`  
**Main baseline:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Assessment branch base:** `main` at the SHA above  
**Method:** Read-only inspection of repository metadata, branches, PRs, commit trees, migration files, model registries, workflow runs and recorded PR discussion.

## 1. Executive disposition

MN-006 refreshes and consolidates the evidence for MN-003, MN-004 and MN-005. It records the Owner's five MN-005 decisions, revalidates the relevant branch and PR heads, inspects the current migration revision identifiers and parent links, compares the branch-specific SQLAlchemy model registries, reconciles PR #43 subsystem evidence, and records the Cargo legal/privacy evidence gaps.

**MN-006 is delivered as a documentation-only A2 artifact. The current MN-series integration reconciliation remains OPEN / NOT CLOSED.** The evidence identifies a viable three-stream integration direction, but there is not yet one reconciled migration head and one verified hybrid model registry. The Cargo retention replacement has not received independent Legal/DPO validation. PR #43 remains only partially accepted by subsystem.

This report does not reopen, replace or amend the historical MaaleNex–IROKA A2 governance disposition. The recovered `MAALENEX-IA-A2-CLOSURE-RECORD-001 RECOVERY-001` records the earlier governance decision as **CLOSED — PARTIAL**, with its original recovery limitations. The current MN-003–MN-012 technical integration/production-readiness reconciliation is a separate workstream and remains open. The earlier 14-November repository reconciliation is a historical snapshot, not current evidence.

The frozen platform-wide MaaleNex–IROKA A1 architecture on current `main` remains preserved. The separate production-readiness A1 specification in PR #55 remains DRAFT / NOT FROZEN; it must not be silently treated as an approved amendment to the frozen architecture.

### Decision summary

| Area | MN-006 finding |
|---|---|
| Repository baseline | **VERIFIED** — current `main` is `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` |
| MN-005 Owner decisions | **RECORDED** — D1–D5 are carried forward below |
| Three-stream migration topology | **PARTIAL** — ancestry and known collision verified; final one-head graph not yet established |
| Cargo retention replacement | **UNRESOLVED** — replacement requirements can be specified; independent Legal/DPO approval remains outstanding |
| Hybrid model registry | **PARTIAL** — target pattern agreed; no complete combined manifest/registry has been verified |
| PR #43 | **PARTIAL** — exact-head push CI passes; PR-event coverage and subsystem acceptance gaps remain |
| Overall current MN-series A2 | **OPEN / NOT CLOSED** |
| A3 implementation | **NOT AUTHORIZED by this workstream** |
| A5 deployment | **NOT AUTHORIZED** |

## 2. Scope, baseline and governance

### 2.1 Canonical scope

This assessment applies only to repository `akefadaka-git/maalenex`. Evidence from other repositories or products is not imported into this record.

- Default branch: `main`.
- Exact main SHA: `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`.
- Main migration history: common revisions `0001` through `0007`.
- Main model registry blob: `ae151fbf72806225b12202bd2e807f51a686bdf3`.
- Main application remains a synthetic-only development/test baseline; production configuration and live service readiness are not established by this assessment.

### 2.2 Preserved stage boundaries

- No application source, migration, model, workflow, secret, environment file or database was changed.
- No workflow was dispatched or rerun.
- No production or hosted database was accessed.
- No provider was provisioned or activated.
- No branch was rebased, retargeted, merged or deleted.
- No merge, deployment, release, commercial activation or production data processing was performed.
- This report is a documentation-only A2 record on a separate branch. It does not modify `main`.

### 2.3 Historical A2 record distinction

The recovered governance record `docs/governance/approvals/MAALENEX-IA-A2-CLOSURE-RECORD-001-RECOVERY-001.md` records the earlier Owner-approved disposition as **CLOSED — PARTIAL** and explicitly notes that the full original body and original repository commit were not recovered. Preserve that historical record and its limitations.

The old `MAALENEX-A2-FINAL-REPOSITORY-RECONCILIATION-2026-11-14.md` was assessed against an earlier main SHA (`d7edb1e...`). Its branch/PR remains historical and unmerged. It is not the current source of truth for the November 26 branch graph.

PR #55's production-readiness A1/A2 documents explicitly define a separate assessment. Its A1 is DRAFT FOR OWNER REVIEW — NOT FROZEN; its A2 is PARTIAL / NOT CLOSED. This MN-006 record updates the evidence for that current integration reconciliation without changing the historical governance disposition.

## 3. Refreshed branch and PR evidence

The following refs were re-read from GitHub on 2026-11-26. PR states are current at inspection; branch heads are exact commit SHAs.

| Workstream | PR / branch | Base SHA | Head SHA | State / exact evidence |
|---|---|---|---|---|
| Passenger/API runtime | [PR #43](https://github.com/akefadaka-git/maalenex/pull/43) | `5640e9067aef5c8a1cb9fada32bf5123aa693162` | `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | OPEN / DRAFT / UNMERGED |
| MITP tracking | [PR #53](https://github.com/akefadaka-git/maalenex/pull/53) | `1daf201bfb407280604534e28440b9fa83178efb` | `6d6a2de592381cd751c52f40824a9da1dd17b07a` | OPEN / DRAFT / UNMERGED; base snapshot predates current main |
| Shared platform | [PR #9](https://github.com/akefadaka-git/maalenex/pull/9) | `0a01631a21a823b720337d1d80aa690e5df347bc` | `bfa99939f220502d1d680f29044bc59aff602af2` | OPEN / DRAFT / UNMERGED |
| Move/location repair | [PR #17](https://github.com/akefadaka-git/maalenex/pull/17) | `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611` | `51193cc7635853f9da3da0de1ba34eb12771185e` | OPEN / DRAFT / UNMERGED |
| Cargo lifecycle base | [PR #49](https://github.com/akefadaka-git/maalenex/pull/49) | `ab89ae0b13e6b6091808ab8240a76fedd49069ea` | `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | OPEN / DRAFT / UNMERGED |
| Cargo retention alternative A | [PR #50](https://github.com/akefadaka-git/maalenex/pull/50) | `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | `73fee61613e533bd75d1e7e85db8689ee1a4799b` | OPEN / DRAFT / UNMERGED; exact-head CI not evidenced |
| Cargo retention alternative B | [PR #51](https://github.com/akefadaka-git/maalenex/pull/51) | `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | `b81e788b55bb5c988d77412ce54f483106675e82` | OPEN / non-draft / UNMERGED |
| Production readiness A1/A2 | [PR #55](https://github.com/akefadaka-git/maalenex/pull/55) | `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | `0213953d474bf9a724237a853d4a8df8b04b21bc` | OPEN / DRAFT / UNMERGED |
| MN-005 integration contract | [PR #58](https://github.com/akefadaka-git/maalenex/pull/58) | `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | `b390969d225a1b98f66161153237a9be27d8d987` | OPEN / DRAFT / UNMERGED |

Additional current refs:
- Passenger/MITP/GIS candidate branch: `feat/a3-canonical-postgis-integration` at `3c3eeb7a211e4978f95140e36f7f4da5d9e52c67`.
- Platform/Move branch: `fix/critical-location-consent-ci` at `51193cc7635853f9da3da0de1ba34eb12771185e`.
- Cargo pre-retention base: `feat/cargo-evidence-lifecycle-governance-v1` at `3662887098211ac9f0b6c4ee3c4eb2401529f74b).

**Freshness and PR-description defects:**
- PR #43's PR body still names former head `409a7d03efe3e07f71523f12b64d4e0109c54c1e`; actual PR head is `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5`.
- PR #9's body cites later account-lifecycle SHAs, including `43099450d6ea32a6ff7b69dbf8db4b82b1f71ce9`, while current PR metadata reports head `bfa99939f220502d1d680f29044bc59aff602af2`. Treat the PR body as stale for current-tip claims.
- PR #17's body cites earlier verification SHA `9f4683455faddadd9107e0bf34dd6052f1aa54a6`; current head is `51193cc7635853f9da3da0de1ba34eb12771185e`. A separate push run on the current head is available below.
- PR #53's base snapshot is `1daf201bfb407280604534e28440b9fa83178efb`, while current `main` is `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`. Revalidate its base relationship before any future integration.
- PR #58 remains a draft proposal. Owner decisions are recorded in its text, but the document itself still labels itself proposed/not Owner-approved. Do not infer that the PR has been accepted or merged.

## 4. Alembic migration graph reconciliation

### 4.1 Common main ancestry

Current `main` contains the common foundation:

`0001_g1_foundation` → `0002_identity_audit_organizations` → `0003_passenger_domains` → `0004_staff_auth_controls` → `0005_booking_access_challenges` → `0006_guest_access_rate_limits` → `0007_operator_invites_support`.

Do not rewrite or renumber this established history.

### 4.2 Passenger and MITP/GIS ancestry

The passenger wallet migration is:

- `0008_wallet_double_entry_ledger`
- `down_revision = 0007_operator_invites_support`
- File blob at PR #43 head: `c2905288a21ad33ab8636444e094ea32e18fd47b`.

The MITP migration is a separate child:

- `0008_mitp_tracking`
- `down_revision = 0007_operator_invites_support`
- File blob at PR #53 head: `1b107288a1dca52e78e926b9fe82da00524ef4e2`.

These are two distinct revision IDs and distinct domain histories. They are not a duplicate-ID collision. They are parallel children of revision 0007 and must be joined by an explicit graph merge.

The passenger branch continues through `0018_koybe_boarding_point`. The inspected migration confirms:
- Revision: `0018_koybe_boarding_point`.
- Parent: `0017_passenger_map_geometry`.
- Owner/operator-confirmed Koybe boarding-point reference: latitude `5.7678630`, longitude `36.7985890`, provenance `operator_confirmed_terminal_pin`.
- It does not establish a route trace, destination terminal, intermediate stop sequence or operating schedule.

The GIS integration branch contains the graph-only merge:

`0019_merge_passenger_mitp`

with exact parent tuple:

`("0018_koybe_boarding_point", "0008_mitp_tracking")`.

It is followed by:

`0020_canonical_postgis_schema` → `0021_mitp_tracking_to_geo` → `0022_geo_publication_views` → `0023_geo_tenant_rls_permissions` → `0024_geo_provenance_licensing`.

The merge revision's upgrade/downgrade functions are no-ops; it merges history without schema/data mutation. The inspected GIS head is `0024_geo_provenance_licensing`.

### 4.3 Platform/Move ancestry

The platform/Move branch is a separate child of the common foundation:

`0008_platform_service_registry` → `0009_service_scoped_role_assignments` → `0010_general_accounts_trust` → `0011_account_identity_lifecycle` → `0012_account_challenge_resend_limits` → `0013_location_consent_sessions` → `0014_move_rides` → `0015_move_ride_service_areas`.

Verified endpoints:
- `0008_platform_service_registry` parent: `0007_operator_invites_support`.
- `0015_move_ride_service_areas` parent: `0014_move_rides`.

The branch remains open/unmerged. Its exact migration ancestry must be included in the eventual unified graph; do not rename its revisions to force a linear sequence.

### 4.4 Cargo ancestry and confirmed duplicate revision collision

The Cargo lifecycle branch begins after the passenger Koybe revision:

`0019_cargo_consignments` → `0020_cargo_dispatch_tracking` → `0021_carrier_operations_delivery_proof` → `0022_cargo_evidence_lifecycle` → `0023_evidence_hold_review`.

Verified:
- `0019_cargo_consignments` parent: `0018_koybe_boarding_point`.
- `0023_evidence_hold_review` parent: `0022_cargo_evidence_lifecycle`.

PR #50 and PR #51 both define the same Alembic revision identifier:

- Revision: `0024_cargo_legal_retention`.
- Parent: `0023_evidence_hold_review`.

The two migration files have different paths and different contents:
- PR #50: `0024_cargo_legal_retention.py`, blob `0af064ccfcdb210066532e10221307cd3a4450a0`; followed by `0025_audit_tombstone_review`.
- PR #51: `0024_cargo_evidence_legal_retention.py`, blob `e0c5bda100293c294ce6838c79a7a20256165591`; followed by `0025_cargo_evidence_rights` and `0026_cargo_evidence_dpo_controls`.

**This is a confirmed duplicate Alembic revision-ID collision.** PR #50 and PR #51 must not be merged or combined unchanged. Their shared parent and same revision ID are directly verified from the migration source, not inferred from filenames.

PR #51 has exact-head CI success, but this does not resolve the duplicate revision ID or provide legal approval. PR #50 has no exact-head CI evidence in the inspected repository metadata.

### 4.5 Candidate final topology — not implemented

The conditional Owner-approved direction is a single final merge revision after the Cargo retention replacement has been designed and its migration history assigned unique IDs. Candidate parent streams:

1. Verified passenger/MITP/GIS head: `0024_geo_provenance_licensing` or its reviewed successor.
2. Verified Platform/Move head: `0015_move_ride_service_areas` or its reviewed successor.
3. One replacement Cargo head after the duplicate revision collision is eliminated.

This three-parent topology is an architectural candidate, not an existing migration. No final merge revision has been created. No single final integration branch has been established. No complete graph validation against the selected replacement Cargo lineage has been run. No database was accessed and no migration was executed.

### 4.6 Migration disposition

| Finding | Status |
|---|---|
| Common 0001–0007 ancestry | **VERIFIED** |
| Passenger wallet 0008 parent | **VERIFIED** |
| MITP 0008 parent | **VERIFIED** |
| Passenger/MITP merge revision 0019 and parents | **VERIFIED** |
| Platform/Move 0008–0015 lineage | **VERIFIED as branch ancestry** |
| Cargo 0019–0023 lineage | **VERIFIED as branch ancestry** |
| PR #50/#51 duplicate 0024 revision ID | **CONFIRMED BLOCKER** |
| Replacement Cargo migration lineage | **UNRESOLVED / NOT IMPLEMENTED** |
| Final three-parent merge revision | **DESIGN ONLY / NOT IMPLEMENTED** |
| One final Alembic head on a unified branch | **NOT VERIFIED** |
| Applied database revision state | **UNKNOWN — NO DATABASE ACCESS PERFORMED** |

## 5. SQLAlchemy model-registry reconciliation

The current snapshots have separate registry files and import sets. Import counts below are module imports, not model/table counts.

| Stream | Registry blob SHA | Import count |
|---|---|---:|
| Main | `ae151fbf72806225b12202bd2e807f51a686bdf3` | 10 |
| PR #43 passenger/runtime | `bb72ab9926c06d2085bbd9e5c70b48c1ce6c262b` | 16 |
| PR #9 platform foundation | `8156d005d77d0244bcc25d93106f7689a5213b29` | 12 |
| PR #17 Move/location | `48c78442410b81af0456a674c93321ee54144be6` | 14 |
| Passenger/MITP/GIS candidate | `de92fc96e010bfe5dac05aa8832d2cdffca77bf9` | 13 |
| PR #53 MITP | `e21faebffae043e9dd43346d9042ba086a9812dd` | 11 |
| Cargo lifecycle | `c24eb5c6231c3aabc6559e3bfde38e0c4ae0928c` | 20 |

### 5.1 Observed ownership coverage

- PR #43 registry contains the passenger/runtime set: audit, bookings, catalog, fares, fleet, identity, passenger identity, notifications, operations, organizations, reservations, support, passenger support, passenger reports, trips and wallet.
- PR #53 registry adds the tracking model import to an older baseline registry; it does not contain the full PR #43 passenger-specific import set.
- Platform/Move registry adds platform accounts, platform models, location and Move models, but does not contain the full passenger-specific set.
- Cargo registry includes cargo models, dispatch, carrier operations and evidence lifecycle plus passenger-related imports; it does not provide the tracking and Platform/Move union.
- The GIS candidate registry includes GIS-related passenger/ledger/scheduler imports but is not itself proof that all tracking, Platform/Move and Cargo models are registered.

The branch registries overlap and differ. A flat copy of any one registry is not a safe canonical target. A blind concatenation is also not sufficient because duplicate model classes/table registrations and ownership overlap must be detected.

### 5.2 Owner-approved hybrid registry requirement

MN-005-D03 selects **domain-owned model manifests feeding one central registry**. The target must:
1. Give each domain an explicit manifest of its mapped model modules.
2. Import each mapped model exactly once before Alembic reads `Base.metadata`.
3. Detect duplicate table names and duplicate mapped classes.
4. Verify metadata completeness and model-to-migration coverage.
5. Preserve all passenger, platform, Move/location, MITP/GIS and Cargo model families selected for the final integration.
6. Include tests for missing imports, duplicate registration and metadata parity on the final integration candidate.

The inspected `backend/tests/test_model_registry_migration_coverage.py` in the GIS branch checks a defined set of migration-backed tables and columns. It is useful partial evidence, not proof of the complete final hybrid registry.

**Disposition:** target architecture direction **RECORDED**; unified manifest **NOT CREATED**; complete import-once/duplicate/missing-model validation **NOT RUN**; final registry **NOT VERIFIED**.

## 6. Cargo retention replacement requirements and legal/privacy evidence

### 6.1 Owner decision

MN-005-D01 selects **C — design a separately reconciled replacement**. Neither PR #50 nor PR #51 is selected as the canonical retention lineage. Preserve both as competing historical evidence. No retention migration implementation is authorized by MN-006.

### 6.2 Requirements for the replacement proposal

The replacement design must explicitly reconcile the following multi-characteristic record classes and overlays. These are requirements to be validated, not an independent legal opinion:

- **EC-1 — accounting records:** records supporting accounting, receivables, invoices or tax liabilities. The Owner-supplied legal-validation opinion cited a ten-year position under Commercial Code Proclamation No. 1243/2021, Article 66; counsel must confirm the current provision, record scope, trigger date, exceptions and calculation.
- **EC-2 — commercial correspondence:** the supplied opinion cited a ten-year position under Article 67, measured from the correspondence date; counsel must confirm the current law, scope and exceptions.
- **EC-3 — residual operational evidence:** the supplied opinion identified no minimum statutory period for pure operational evidence. A 24-month period is conditional only where the record is not EC-1/EC-2 and a documented lawful basis, purpose justification and DPO-reviewed DPIA support the period. It is not a universal or statutory default.
- **EC-4 — personal-data overlay:** Personal Data Protection Proclamation No. 1321/2024 requirements must be assessed across the record classes, including lawful processing, purpose limitation, transparency, rights, security, localisation and international transfers, as confirmed by qualified reviewers.
- **EC-5 — legal-hold overlay:** a valid hold suspends ordinary expiry/deletion until release through documented authority, conclusion evidence and separation of duties.

The replacement specification must also define:
- Multi-characteristic classification and explicit precedence for overlapping categories.
- Source dates and category-specific statutory trigger dates; do not hard-code a trigger until Legal confirms it.
- Treatment of overlapping EC-1/EC-2 records, including the latest applicable confirmed statutory deadline.
- Lawful basis, purpose, privacy notice and DPIA references where required.
- DPO review and independent deletion-suspension authority.
- One fail-closed eligibility interlock across manual deletion, scheduled deletion and orphan cleanup.
- Rights-request triage and lawful early-erasure review.
- Hold placement, review, release evidence and role separation.
- Separate evidence, audit-log and tombstone retention schedules; do not infer one schedule from another.
- No audit/tombstone purge until periods, justification, archival/disposal method and approvals are independently accepted.
- A disabled/unactivated policy state until Legal, DPO and Owner gates are satisfied.

### 6.3 Existing engineering evidence is not compliance approval

PR #49 records the Cargo lifecycle foundation at `3662887098211ac9f0b6c4ee3c4eb2401529f74b`; its exact-head run [#638](https://github.com/akefadaka-git/maalenex/actions/runs/45045926865) passed the reported backend/lint/container/storage/migration/metadata/downgrade-re-upgrade checks.

PR #51 exact-head run [#691](https://github.com/akefadaka-git/maalenex/actions/runs/45056584444) completed successfully on exact head `b81e788b55bb5c988d77412ce54f483106675e82` and exact base `3662887098211ac9f0b6c4ee3c4eb2401529f74b`. Its formal PR submission reports 155 backend tests passed, 9 skipped, lint, API container build, local S3-compatible service, empty-database migration, HTTPS/session/CORS smoke, metadata parity, downgrade and clean re-upgrade all passing. This is engineering verification for PR #51 only.

PR #50 exact-head workflow/status evidence was not returned. It remains unverified.

PR #51 C06 remains **PARTIAL**: tombstone/audit retention metadata exists, but final periods and justifications are not approved and no purge mechanism is present. Do not infer or activate a purge schedule.

### 6.4 Compliance evidence register

The formal PR #51 Legal/DPO submission records a search of project-accessible sources and identifies the Owner-supplied L01–L07 legal-validation opinion from 22 November 2026 at 18:07:10 UTC. That opinion concluded **NOT APPROVED**; reviewer identity, qualification, signature and date were blank. Do not ask the Owner to resend it. The opinion is supplied source material, not an executed independent Legal approval.

| ID | Required evidence | Reconciled status |
|---|---|---|
| D01 | ECA registration/authorisation or reasoned non-applicability determination | **NOT LOCATED IN SOURCES SEARCHED** |
| D02 | DPO appointment, authority, independence and any required registration | **NOT LOCATED IN SOURCES SEARCHED** |
| D03 | Completed and approved DPIA | **NOT LOCATED IN SOURCES SEARCHED** |
| D04 | Cargo data inventory and processing-flow map | **NOT LOCATED IN SOURCES SEARCHED** |
| D05 | Hosting/data-residency, backup-location and support-access evidence | **NOT LOCATED IN SOURCES SEARCHED** |
| D06 | International-transfer assessment, safeguards/contracts and any required ECA approval | **NOT LOCATED IN SOURCES SEARCHED** |
| D07 | Approved privacy notices, lawful-basis register and communicated retention schedule | **NOT LOCATED IN SOURCES SEARCHED** |
| D08 | Signed processor agreements and confidentiality/security obligations | **NOT LOCATED IN SOURCES SEARCHED** |
| D09 | Rights-request SOP, operational records and tested handling | **PARTIAL — SOFTWARE ONLY** |
| D10 | Consolidated security-control evidence and independent security assessment | **PARTIAL — ENGINEERING EVIDENCE ONLY** |
| D11 | Approved tombstone/audit retention schedule and disposal/archival method | **PARTIAL — SOFTWARE METADATA ONLY** |
| D12 | Approved legal-hold SOP and operational hold/release evidence | **PARTIAL — SOFTWARE/GOVERNANCE INTENT ONLY** |
| D13 | Supplied L01–L07 opinion plus separate executed Legal and DPO determinations | **SUPPLIED OPINION NOT APPROVED; INDEPENDENT DETERMINATIONS PENDING** |
| D14 | Approved accounting/tax and commercial-correspondence schedule with trigger dates/exceptions | **PARTIAL — LEGAL POSITION ONLY** |

“Not located in sources searched” does not prove non-existence. Any later evidence must be added with title, issuer, version/date, scope, approver and exact reference before status changes.

**Disposition:** replacement requirements can be documented; legal interpretation, independent Legal approval, DPO determination and documentary evidence remain unresolved. No Cargo retention lineage is selected.

## 7. PR #43 subsystem reconciliation

PR #43 is open/draft and based on PR #41, not current `main`. Its broad scope must be accepted by subsystem; a pass in one subsystem is not acceptance of another.

### 7.1 Exact-head CI evidence

Exact head: `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5`.

- Android workflow [run #45033264442](https://github.com/akefadaka-git/maalenex/actions/runs/45033264442): **SUCCESS**, event `push`, exact head SHA.
- Backend workflow [run #45033264304](https://github.com/akefadaka-git/maalenex/actions/runs/45033264304): **SUCCESS**, event `push`, exact head SHA.
- The Android run's OSV dependency-scan job completed successfully; the generated Gradle metadata writeback job was skipped; an additional scanner check was neutral.
- The commit check-run list contains successful backend and Android jobs, but the commit status endpoint returned no status entries and aggregate state `pending`.
- The workflow-run lookup found push-triggered runs, not PR-triggered runs.

This corrects the earlier A2 wording that described PR #43 exact-head CI as wholly missing. **Exact-head push CI is PASS; PR-event CI is NOT EVIDENCED.** These runs do not establish a live API, production credentials, live map data or production readiness.

### 7.2 Workflow trigger and write-permission findings

- PR #43 base branch is `fix/passenger-password-minimum-six`.
- The backend workflow's `pull_request.branches` filter does not include that base branch. The Android workflow's `pull_request.branches` filter also does not include it.
- Both workflows have a push trigger for the PR #43 feature branch, explaining the successful push runs.
- The Android workflow contains a conditional `commit-gradle-verification-metadata` job with `contents: write` when a PR targets `main`. PR #43 does not currently target main, so that job was skipped; the write capability still requires review and explicit governance before a future main-targeted run.
- The workflow uses version tags for third-party actions; immutable SHA pinning and an update policy remain security-review items.

### 7.3 Android geolocation and WebView lifecycle

**Verified in code:**
- Android manifest declares INTERNET, network-state, coarse-location and fine-location permissions.
- WebView geolocation is enabled.
- The origin policy permits only the packaged `https://appassets.androidplatform.net` origin.
- The code stores one pending geolocation origin/callback and resolves it on Android permission result; `onDestroy` denies a still-pending callback.
- Current unit tests cover trusted-origin matching and coarse/fine permission helper logic.

**Remaining gaps:**
- The single pending-callback fields are overwritten if another geolocation prompt arrives before the first is resolved; concurrency/lifecycle behavior needs explicit handling and tests.
- No complete evidence was found for concurrent prompts, navigation while a prompt is pending, cancellation/revocation, denial/retry UX or physical-device permission behavior.
- The policy unit tests are not equivalent to Android permission lifecycle acceptance.

### 7.4 CSP, map provider and provenance

PR #43 implements a Google Maps JavaScript passenger renderer and permits Google map domains in CSP. Its CSP patch also permits inline styles. The Android build consumes `VITE_GOOGLE_MAPS_API_KEY`; key availability, restrictions, billing status and provider approval are not verified. No paid provider or billing activation is authorized.

The frozen platform architecture's self-hosted-first target is MapLibre rendering, PostGIS in the primary platform database and Martin as a candidate vector-tile service. PR #53's MapLibre/Martin/PostGIS work is a separate synthetic proof of concept with a local map database; it does not yet establish the canonical primary-database GIS model, authoritative data or production hosting. Google Maps and the isolated MapLibre proof of concept are not yet one integrated architecture.

The Koybe boarding-point pin is the only specifically recorded operator-confirmed geographic input in this scope. It does not establish the Koybe route trace, destination terminal, intermediate stops, route distance or schedule. Route geometry must remain unpublished until authoritative operator/source evidence and licensing are reconciled.

### 7.5 PR #43 disposition by subsystem

| Subsystem | Status | Reason |
|---|---|---|
| Backend production-runtime candidate | **PARTIAL** | Exact-head push CI pass; no verified live host/database/credentials |
| Android build/emulator | **PASS — CI SCOPE ONLY** | Exact-head push run passed; no physical-device acceptance |
| API origin/CORS/cookie/CSRF | **PARTIAL** | Synthetic/local HTTPS smoke only; no verified external API origin |
| Geolocation permission lifecycle | **PARTIAL** | Policy tests exist; concurrency, denial/revocation and device behavior remain |
| Workflow PR-event coverage | **NOT EVIDENCED** | Actual PR base omitted from branch filters |
| Workflow writeback capability | **UNRESOLVED** | Conditional contents-write job requires separate review |
| CSP/security boundary | **PARTIAL** | Google domains and inline-style allowances require review |
| Passenger map/provider | **UNRESOLVED** | Google Maps implementation conflicts with self-hosted-first target |
| Map source/licensing/route provenance | **MISSING** | No verified authoritative route trace or licence package |
| Independent security acceptance | **NOT RUN** | Requires independent reviewer and evidence |

PR #42 is a sibling based on the same PR #41 parent. Its green checks are not transferable to PR #43 and it must not be integrated as a separate sibling on top of PR #43. PR #43 remains the broader candidate, subject to the subsystem gates above.

## 8. Other current engineering evidence

These results are exact-commit evidence for their stated branches only:

| Workstream | Exact-head workflow evidence | Limit |
|---|---|---|
| PR #9 shared platform | [Run #45141611565](https://github.com/akefadaka-git/maalenex/actions/runs/45141611565) and [run #45141611563](https://github.com/akefadaka-git/maalenex/actions/runs/45141611563), both SUCCESS on `bfa99939f220502d1d680f29044bc59aff602af2` | Push-triggered evidence; branch remains stacked/unmerged; PR body contains stale later SHA |
| PR #17 Move/location | [Run #45141770337](https://github.com/akefadaka-git/maalenex/actions/runs/45141770337), SUCCESS on `51193cc7635853f9da3da0de1ba34eb12771185e` | Push-triggered evidence; branch remains stacked/unmerged |
| PR #53 MITP | [Run #45155547829](https://github.com/akefadaka-git/maalenex/actions/runs/45155547829), [run #45155547922](https://github.com/akefadaka-git/maalenex/actions/runs/45155547922), [run #45155547849](https://github.com/akefadaka-git/maalenex/actions/runs/45155547849), all SUCCESS on `6d6a2de592381cd751c52f40824a9da1dd17b07a` | PR-event CI for synthetic branch; no real OSM PBF import or browser/field map acceptance |
| PR #49 Cargo lifecycle | [Run #45045926865](https://github.com/akefadaka-git/maalenex/actions/runs/45045926865), SUCCESS on `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | Engineering verification only; retention policy remains provisional |
| PR #51 Cargo corrective branch | [Run #45056584444](https://github.com/akefadaka-git/maalenex/actions/runs/45056584444), SUCCESS on exact head and base | Engineering verification only; legal/DPO gates remain |
| PR #50 Cargo alternative A | No exact-head run/status evidence returned | **NOT VERIFIED** |

These checks do not establish a unified integrated release candidate. They must not be combined into a claim that one final branch passed all checks.

## 9. Consolidated MN-series A2 evidence matrix

| ID | Requirement / finding | Status | Evidence-backed disposition |
|---|---|---|---|
| MN-006-01 | Canonical repository and current main baseline | **PASS** | `akefadaka-git/maalenex`, main SHA `c988b9d...` |
| MN-006-02 | Preserve historical A1/A2 governance records | **PASS** | Historical recovery record retained; current MN-series assessment distinguished |
| MN-006-03 | Refresh exact branch/PR refs | **PASS** | Relevant current heads and PR states re-read |
| MN-006-04 | Reconcile passenger/MITP/GIS migration ancestry | **PASS — STATIC GRAPH** | Both 0008 children and 0019 graph merge inspected |
| MN-006-05 | Reconcile Platform/Move ancestry | **PASS — STATIC BRANCH EVIDENCE** | 0008–0015 lineage identified |
| MN-006-06 | Reconcile Cargo ancestry and unique revision IDs | **BLOCKED** | PR #50/#51 duplicate 0024 ID confirmed |
| MN-006-07 | Specify replacement Cargo retention requirements | **PARTIAL** | Requirements recorded; legal interpretation and independent approval outstanding |
| MN-006-08 | Reconcile hybrid model registry | **PARTIAL** | Branch registries inventoried; final manifest/union and completeness tests absent |
| MN-006-09 | Verify PR #43 exact-head evidence | **PASS — PUSH CI** | Backend and Android push runs pass; PR-event coverage absent |
| MN-006-10 | PR #43 Android permission lifecycle | **PARTIAL** | Helper tests pass; lifecycle/concurrency/device evidence absent |
| MN-006-11 | PR #43 map architecture and provenance | **UNRESOLVED** | Google Maps vs MapLibre; authoritative route/license evidence absent |
| MN-006-12 | Independent security acceptance | **NOT RUN** | Independent review not present |
| MN-006-13 | Production host/runtime/database identity | **NOT VERIFIED** | No live host, production DB, production identity or credentials verified in this read-only A2 |
| MN-006-14 | Notification delivery architecture | **PARTIAL** | In-app inbox exists in unmerged stack; provider/outbox/channel delivery not evidenced as complete |
| MN-006-15 | Legal/privacy/operational documentary evidence | **PARTIAL / NOT LOCATED** | D01–D14 register above |
| MN-006-16 | One final integrated migration head and model registry | **NOT VERIFIED** | No final integration branch, final merge migration or complete registry |
| MN-006-17 | Applied database migration state | **UNKNOWN** | No database access was performed or authorized |
| MN-006-18 | Production deployment and commercial operation | **NOT AUTHORIZED** | Separate A5 and legal/operational gates remain |

## 10. Owner decisions carried forward

The following MN-005 decisions are the controlling architecture direction for this reconciliation:

| Decision | Owner choice | Effect |
|---|---|---|
| MN-005-D01 Cargo retention | **C — separately designed replacement** | Preserve PR #50/#51 as competing evidence; do not merge either unchanged |
| MN-005-D02 Alembic topology | **A — conditionally approve three-stream topology** | Passenger/MITP/GIS + Platform/Move + one reconciled Cargo stream, subject to exact ancestry and graph validation |
| MN-005-D03 model registry | **C — hybrid domain-owned manifests + central registry** | Import-once, duplicate detection, metadata completeness and migration/model coverage required |
| MN-005-D04 PR #43 acceptance | **C — split by subsystem** | Accept only independently evidenced subsystems; no CI transfer between subsystems or branches |
| MN-005-D05 A3 target | **A — one candidate integration branch after A2 closure** | No branch creation/retargeting or A3 work before closure and separate authorization |

These decisions are recorded; they do not establish that their technical or documentary conditions have been satisfied.

## 11. A2 closure recommendation

**Recommendation: DO NOT CLOSE the current MN-series A2 reconciliation yet.** MN-006 has completed the evidence refresh and documented the unresolved conditions. A2 closure would currently overstate the state of the migration graph, Cargo retention decision, hybrid model registry and PR #43 acceptance.

Minimum remaining A2 closure conditions:

1. Produce the replacement Cargo retention design against D1, with exact migration identity strategy and a reviewable legal/privacy requirement map. Do not implement it in A2.
2. Obtain and record the independent Legal and DPO determinations and the documentary evidence needed to validate the replacement retention requirements. Keep “not located in sources searched” distinct from “does not exist.”
3. Finalize the static three-stream Alembic graph specification with unique revision identifiers, exact parent list, downgrade implications and one intended head. Preserve existing history; no database execution is part of this A2 report.
4. Complete the hybrid domain-manifest ownership/coverage matrix, including duplicate-table and missing-model checks as explicit acceptance requirements.
5. Close the PR #43 A2 integration contract gaps: accurate PR metadata, correct PR-event trigger coverage, reviewed workflow writeback permissions, geolocation lifecycle requirements, map-renderer alignment and authoritative data/licensing requirements.
6. Reconcile MN-007 through MN-011 work packages and their outputs into the same evidence register.
7. Prepare MN-012 as the consolidated A2 closure package for Owner review. Only then request an explicit A2 closure decision.

A2 closure does not itself authorize A3. The single candidate A3 integration branch may be designated only after A2 closure; A3 implementation, migration edits, PR merges and workflow dispatches require their own explicit authorization. A5 remains separately gated.

## 12. MN-007 through MN-012 sequence

The planned sequence carried forward is:

| Package | Scope | Output |
|---|---|---|
| MN-007 | Reconcile passenger/MITP map interfaces | Shared map contract, renderer boundary, data ownership and provenance requirements |
| MN-008 | Reconcile web/Android API flows | Passenger end-to-end acceptance plan for API origin, sessions, CORS/CSRF, offline/error behavior and Android |
| MN-009 | Reconcile notification outbox and channels | Provider-neutral notification architecture, consent and delivery/failure contract |
| MN-010 | Reconcile Cargo evidence lifecycle | Legal/technical package for retention, rights, holds, DPO controls and independent review |
| MN-011 | Reconcile synthetic hosted-preview boundary | Runtime/database identity specification; no provider provisioning or database access implied |
| MN-012 | Final A2 closure | Consolidated evidence matrix, unresolved-risk disposition and Owner-reviewable closure decision |

**Immediate next package:** MN-007 — passenger/MITP shared map contract. This is still read-only architecture reconciliation; it does not authorize map-provider activation, paid services, implementation, migration, merge or deployment.

## 13. Final disposition

- **MN-006:** DELIVERED — read-only evidence refresh and A2 reconciliation record.
- **Current MN-series A2:** OPEN / NOT CLOSED.
- **Historical MaaleNex–IROKA A2 governance disposition:** PRESERVED as CLOSED — PARTIAL; not reopened by this report.
- **Frozen platform-wide A1:** PRESERVED.
- **Production-readiness A1 in PR #55:** DRAFT / NOT FROZEN.
- **A3:** NOT AUTHORIZED by this record.
- **A5:** NOT AUTHORIZED.

No application implementation, migration, database access, workflow dispatch, provider activation, merge, deployment or commercial operation was performed.
