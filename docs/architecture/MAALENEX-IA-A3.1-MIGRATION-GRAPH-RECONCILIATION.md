# MAALENEX-IA-A3.1 — Migration Graph Consolidation

**Status:** Implemented on integration branch; verification pending  
**Architecture baseline:** MAALENEX-IA-A1-SPEC-001 v1.0.0 (preserved)  
**A2 authority:** MAALENEX-IA-A2-CLOSURE-RECORD-001 v1.0.0  
**A3 authorization:** Owner authorization recorded 25 November 2026  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Base:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`

## 1. Problem confirmed

The frozen main branch contained the migration chain through `0007_operator_invites_support`. Two independently developed branches then added distinct revisions with the same numeric prefix:

- Passenger/wallet stream: `0008_wallet_double_entry_ledger`, followed by `0009_passenger_identity` through `0018_koybe_boarding_point`.
- MITP stream: `0008_mitp_tracking`, whose parent is `0007_operator_invites_support`.

The revision identifiers are distinct; the numeric filename prefix is not an Alembic identity. The conflict is a multiple-head graph, not a duplicate revision ID.

## 2. Controlled resolution

Preserved every source revision identifier and its existing parent relationship. Imported the passenger/wallet migration files from PR #43's head branch and the MITP migration from PR #53's head branch without renumbering or rewriting their historical revision definitions.

Added graph-only merge revision:

- File: `backend/migrations/versions/0019_merge_passenger_mitp.py`
- Revision: `0019_merge_passenger_mitp`
- Parents: `0018_koybe_boarding_point` and `0008_mitp_tracking`
- Upgrade/downgrade: no-op; the merge changes migration ancestry only and performs no schema or data mutation.

The result is intended to expose one Alembic head while retaining both complete migration histories.

## 3. Automated graph test added

Added `backend/tests/test_migration_graph.py` to assert:
1. Alembic reports exactly one head: `0019_merge_passenger_mitp`.
2. The merge revision retains both expected parent revisions.

## 4. Safety and compatibility boundaries

- No existing PR or source branch was changed.
- No migration was executed against any database.
- No production or external database history was inspected; deployed-database compatibility remains a separate required precondition before any migration execution.
- No schema/data mutation is performed by the merge revision itself.
- The imported migrations are not proof that the corresponding passenger/MITP application code has been integrated or verified.
- A3.1 is not marked VERIFIED-CLOSED until the Alembic graph test and clean-install/upgrade/downgrade/re-upgrade checks pass in an executable environment.

## 5. Required verification

- [ ] Run `python -m alembic heads`; expected only `0019_merge_passenger_mitp`.
- [ ] Run the migration graph pytest.
- [ ] Run empty-database `alembic upgrade head`.
- [ ] Run full downgrade and clean re-upgrade.
- [ ] Run `alembic check` against model metadata.
- [ ] Inspect any existing database's `alembic_version` rows before applying this graph to it.

**Disposition:** A3.1 implementation files are present on the integration branch. Verification remains pending; no migration execution, merge, or deployment is authorized by this record.
