# MN-005 — Canonical Integration Contract (A2 Candidate)
Version: 1.0.0-draft
Status: PROPOSED / NOT OWNER-APPROVED / NOT IMPLEMENTATION AUTHORITY
Prepared: 2026-11-26
Repository: `akefadaka-git/maalenex`
Baseline: `main` at `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`

## 1. Purpose and governance

This document translates the MN-003 PR #43 review and MN-004 revision/model-registry inventory into a candidate integration contract. It is an A2 reconciliation artifact only. It does not authorize A3 implementation, migration edits, model refactors, branch retargeting, merges, workflow dispatches, database access, provider activation, or deployment.

The contract preserves the frozen product and architecture baselines. It does not amend A1 v1.1, approve proposed A1 v1.2, change the passenger-first scope, or make IROKA a public MaaleNex service. IROKA remains an invisible, governed intelligence backbone and cannot authorize transactions independently.

Owner decisions are explicitly separated from technical recommendations. No unresolved choice is silently treated as approved.

## 2. Evidence baseline and immutable references

| Evidence item | Ref / SHA | Current interpretation |
|---|---|---|
| Main | `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | Canonical repository baseline for this reconciliation |
| PR #43 | `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | Passenger runtime, Android WebView and map integration candidate; open/draft |
| PR #43 base | `5640e9067aef5c8a1cb9fada32bf5123aa693162` | `fix/passenger-password-minimum-six` |
| PR #9 platform foundation | `bfa99939f220502d1d680f29044bc59aff602af2` | Independent platform identity/account branch |
| PR #17 Move/location | `51193cc7635853f9da3da0de1ba34eb12771185e` | Divergent platform identity + location/Move descendant |
| Passenger/MITP/GIS integration | `3c3eeb7a211e4978f95140e36f7f4da5d9e52c67` | Passenger and MITP joined; GIS/PostGIS revisions added |
| PR #53 MITP | `6d6a2de592381cd751c52f40824a9da1dd17b07a` | Independent MITP root and model stream; synthetic/PoC evidence only |
| Cargo pre-retention base | `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | Cargo lifecycle branch through evidence-hold review |
| PR #50 retention alternative | `73fee61613e533bd75d1e7e85db8689ee1a4799b` | Alternative A; duplicate revision ID collision |
| PR #51 retention alternative | `b81e788b55bb5c988d77412ce54f483106675e82` | Alternative B; duplicate revision ID collision and subsequent rights/DPO revisions |

These references are evidence snapshots, not a claim that the branches remain unchanged. Revalidate branch tips, PR bases and file blobs before any future implementation.

## 3. Canonical migration architecture — candidate

### 3.1 Common foundation

The shared ancestry begins with:

`0001_g1_foundation` → `0002_identity_audit_organizations` → `0003_passenger_domains` → `0004_staff_auth_controls` → `0005_booking_access_challenges` → `0006_guest_access_rate_limits` → `0007_operator_invites_support`.

The current `main` is at `0007_operator_invites_support`. Do not rewrite or renumber these established revisions as part of this reconciliation.

### 3.2 Passenger and GIS stream

Passenger revisions continue from the common foundation through:

- `0008_wallet_double_entry_ledger`
- `0009_passenger_identity`
- `0010_passenger_support_cases`
- `0011_passenger_reports_complaints`
- `0012_passenger_wallet`
- `0013_passenger_notifications`
- `0014_verified_booking_ownership`
- `0015_scheduler_operations_rbac`
- `0016_fleet_compliance`
- `0017_passenger_map_geometry`
- `0018_koybe_boarding_point`

MITP has a separate `0008_mitp_tracking` root. The GIS integration branch joins the passenger and MITP paths at `0019_merge_passenger_mitp`, followed by:

`0020_canonical_postgis_schema` → `0021_mitp_tracking_to_geo` → `0022_geo_publication_views` → `0023_geo_tenant_rls_permissions` → `0024_geo_provenance_licensing`.

Candidate treatment: retain this passenger/MITP/GIS ancestry as a single stream. Do not copy MITP migrations into the passenger chain or create a second revision with the same IDs. Verify all migration file contents and parent metadata again immediately before any future integration.

### 3.3 Platform identity, location and Move stream

The platform branch independently continues from `0007_operator_invites_support`:

`0008_platform_service_registry` → `0009_service_scoped_role_assignments` → `0010_general_accounts_trust` → `0011_account_identity_lifecycle` → `0012_account_challenge_resend_limits` → `0013_location_consent_sessions` → `0014_move_rides` → `0015_move_ride_service_areas`.

Candidate treatment: preserve the platform identity and Move work as a distinct ancestry until a deliberate Alembic merge node is designed. Do not rename these revisions to force them into the passenger sequence. The existing GIS merge revision joins passenger and MITP only; it does not join this platform/Move stream.

### 3.4 Cargo stream and unresolved retention alternatives

Cargo branches from the passenger ancestry after `0018_koybe_boarding_point` and adds:

`0019_cargo_consignments` → `0020_cargo_dispatch_tracking` → `0021_carrier_operations_delivery_proof` → `0022_cargo_evidence_lifecycle` → `0023_cargo_evidence_hold_review`.

Two competing descendants then exist:

- Alternative A / PR #50: `0024_cargo_legal_retention` followed by `0025_audit_tombstone_review`.
- Alternative B / PR #51: `0024_cargo_legal_retention` followed by `0025_cargo_evidence_rights` and `0026_cargo_evidence_dpo_controls`.

Both alternatives declare revision ID `0024_cargo_legal_retention` with parent `0023_cargo_evidence_hold_review`, but the migration contents differ. This is a confirmed Alembic revision-ID collision.

**Hard rule:** PR #50 and PR #51 must not be merged or combined unchanged. A single Owner-selected retention design must be produced after legal, privacy, audit, records-retention and operational review. If the selected design reuses work from the other branch, its migration history must be rewritten/rebased under new unique revision identifiers through an explicitly reviewed migration plan; do not retain duplicate revision IDs.

### 3.5 Candidate final merge topology

After all three domain streams have been reconciled and the Cargo retention alternative has been selected, the target should have one Alembic head. The recommended topology is a new, explicitly named merge revision whose parents are:

1. The verified GIS head (`0024_geo_provenance_licensing`, or its newly verified successor).
2. The verified platform/Move head (`0015_move_ride_service_areas`, or its newly verified successor).
3. The single selected and reconciled Cargo head (PR #50 or PR #51 lineage after resolving the collision).

This is a topology recommendation only. The exact merge revision identifier, filename, parent list and implementation sequence must be derived from the revalidated final migration files and reviewed before A3. The proposed parent list must not be copied into a migration until every parent exists in the chosen integration branch and the complete graph is checked for duplicate IDs, missing parents, cycles and unintended multiple heads.

No database migration has been executed as part of MN-003/MN-004. No production `alembic_version` state is known.

## 4. Canonical SQLAlchemy model-registry target

The inspected registry snapshots are distinct branch-specific states:

| Stream | Registry blob SHA | Module imports |
|---|---|---:|
| Main | `ae151fbf72806225b12202bd2e807f51a686bdf3` | 10 |
| PR #43 passenger | `bb72ab9926c06d2085bbd9e5c70b48c1ce6c262b` | 16 |
| PR #9 platform | `8156d005d77d0244bcc25d93106f7689a5213b29` | 12 |
| PR #17 Move/location | `48c78442410b81af0456a674c93321ee54144be6` | 14 |
| GIS/A4 | `de92fc96e010bfe5dac05aa8832d2cdffca77bf9` | 13 |
| PR #53 MITP | `e21faebffae043e9dd43346d9042ba086a9812dd` | 11 |
| Cargo | `c24eb5c6231c3aabc6559e3bfde38e0c4ae0928c` | 20 |

The import counts are not table counts and do not prove metadata completeness. The final registry must be derived from the selected canonical source tree and must import every mapped SQLAlchemy model exactly once, without relying on import side effects or leaving models undiscovered.

Candidate model families to reconcile:

- Core: audit, identity, organizations, platform accounts/trust, catalog, fleet, trips, fares, bookings, reservations and support.
- Passenger: passenger identity, passenger support, reports/complaints, notifications and wallet/ledger.
- Operations: scheduler and operations/RBAC.
- Location/Move: location consent/session and Move ride/service-area models.
- GIS/MITP: tracking, geometry, publication, tenant access and provenance/licensing models.
- Cargo: consignments, dispatch, carrier operations, delivery proof, evidence lifecycle, legal retention, evidence rights, DPO controls and audit/tombstone review.

The final registry should have an explicit module manifest, import-order policy, duplicate table/class check, metadata completeness test and migration-to-model coverage matrix. The chosen registry must be validated against every selected migration branch. Do not copy one branch's registry wholesale and assume it includes all other branches.

## 5. PR #43 integration contract and acceptance boundaries

PR #43 is open/draft at `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5`, based on `fix/passenger-password-minimum-six` at `5640e9067aef5c8a1cb9fada32bf5123aa693162`.

Exact-head push evidence observed:

- Android verification run 45033264442: success.
- Backend verification run 45033264304: success.

These were push-triggered runs, not pull-request-triggered runs. The workflow branch filters do not include PR #43's actual base branch, so exact-head PR-event coverage remains unresolved. CI success is not transferable to sibling branches or later SHAs.

Before PR #43 can be accepted into the canonical integration path:

1. Correct its stale PR body, which still cites the former head SHA and says exact-head checks are pending.
2. Ensure workflow pull-request filters cover the actual target branch and the intended integration target.
3. Replace mutable third-party Action tags with reviewed immutable commit pins; document the update process.
4. Review the Android workflow's conditional `contents: write` metadata-writeback capability and keep it disabled or narrowly constrained unless separately approved.
5. Complete native geolocation prompt lifecycle tests, denial/revocation behavior, concurrent prompt behavior, and origin/navigation boundary tests.
6. Validate secure cookie/session behavior against the actual API origin, with the WebView navigation and CSP policy reviewed as one security boundary.
7. Tighten map provenance acceptance: publication state, coordinate bounds and non-empty source labels do not establish authoritative source or licence approval. Require separately governed provenance/licensing evidence before presenting data as source-verified.
8. Preserve synthetic-only and no-commercial-operation boundaries until legal, security, privacy, insurance, provider and operational gates are passed.

PR #43's green CI does not demonstrate a live production API, live map data, production credentials, or commercial readiness.

## 6. Candidate integration sequence (no implementation authorized)

| Order | Candidate work package | Entry criteria | Exit evidence |
|---:|---|---|---|
| 1 | Freeze evidence inventory | Revalidate all branch tips, PR bases, migration blobs and registry blobs | Signed/reviewable evidence manifest |
| 2 | Decide Cargo retention design | Owner decision informed by legal/privacy/records review | One selected model; other alternative explicitly superseded or archived |
| 3 | Reconcile platform/Move with passenger/GIS | Domain contracts and ownership reviewed | Explicit multi-head migration merge design; no duplicate revisions |
| 4 | Reconcile Cargo with canonical graph | Selected Cargo branch and ancestry revalidated | Unique revision IDs and one final migration head |
| 5 | Produce unified model manifest | Every selected model file and table inventoried | One registry manifest with duplicate/missing-model checks |
| 6 | Review migration/model parity | Full migration graph and model manifest available | Automated graph validation and metadata parity evidence |
| 7 | PR #43 integration readiness | Workflow/security/map blockers addressed | Exact-head PR-event CI and review evidence |
| 8 | A3 implementation authorization | Owner approves this contract and the exact implementation scope | Explicit A3 approval record |

Any database execution, migration, seed, data mutation, credential use, paid service, provider activation or deployment requires separate authorization and applicable safety gates. A5 remains separately gated.

## 7. Owner decisions required before A2 closure

| Decision ID | Decision required | Current status |
|---|---|---|
| MN-005-D01 | Select Cargo retention alternative A (PR #50 lineage) or B (PR #51 lineage), or approve a separately designed replacement | OPEN — Owner decision required |
| MN-005-D02 | Approve the proposed three-stream merge topology (GIS + platform/Move + selected Cargo), subject to verified ancestry | PROPOSED |
| MN-005-D03 | Confirm the canonical model-domain ownership and module manifest | OPEN |
| MN-005-D04 | Confirm PR #43 workflow/security remediation acceptance criteria | OPEN |
| MN-005-D05 | Confirm whether the candidate unified branch is the sole A3 integration target after A2 closure | OPEN |

This document intentionally does not answer those Owner decisions on the Owner's behalf.

## 8. Explicit exclusions and non-actions

This A2 artifact does not:

- Modify or merge `main`, PR #43, PR #50, PR #51 or any other PR.
- Edit application source, migration files, model files, workflows, environment files or secrets.
- Choose a Cargo retention alternative.
- Run Alembic, seed data, connect to any database or inspect production database state.
- Dispatch, rerun or modify GitHub Actions.
- Provision domains, hosting, API services, map providers or paid services.
- Enable commercial passenger operations, payments, ticketing, boarding, live tracking or deployment.
- Authorize A3 or A5.

## 9. A2 status

**MN-005: DOCUMENTATION DRAFT — PROPOSED.**

**MN-003: DELIVERED / PARTIAL ACCEPTANCE.** Exact-head push CI passed; PR-event workflow coverage and security/provenance acceptance remain open.

**MN-004: DELIVERED / PARTIAL.** Branch revision and model-registry inventories completed; unified graph and registry remain unresolved.

**Overall A2: OPEN / NOT CLOSED.** Closure requires the Owner decisions above, a verified evidence refresh, and a reconciled single-head migration/model target. A3 and A5 remain unauthorized until separately approved.
