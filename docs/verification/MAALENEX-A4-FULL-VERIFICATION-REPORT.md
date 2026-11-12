# MaaleNex — A4 Full Verification Report

**Audit date:** 2026-11-11  
**Repository:** `akefadaka-git/maalenex` (historical workflow links may display `maalenex-moto`)  
**A4 branch:** `a4/full-verification-remediation`  
**Reconciled code candidate:** `ae7546b29b755973623420d8a887c813c5521edf`  
**Final evidence-record candidate before this correction:** `239253f55bbc8b4936f62fbf06b8601f62cc6b06`  
**Current A4 branch tip:** `3e91081885d4d54ede01b3e281e03ad30efbd256`  
**Current A4 branch-tip verification:** [run #43067522415](https://github.com/akefadaka-git/maalenex/actions/runs/43067522415), PASS — 3/3 jobs on the exact branch-tip SHA  
**Prior A4 evidence-record branch head:** `d54b0291a58499891baaac5d5106ea8eed85a96b`

## 1. Executive disposition

**A4 bounded automated verification: PASS on the reconciled code candidate.**  
**A4 evidence record: corrected in this revision; exact-head CI for this documentation revision must be checked separately.**

The original A4 report contained contradictory statements. In particular, its verification table still said the combined PR #9 + PR #10 exact-head run was NOT RUN / UNRESOLVED, and its ancestry section repeated pre-reconciliation divergence after the report had already declared that reconciliation complete. Those statements were stale and have been removed or explicitly qualified below.

A4's reconciliation commit `ae7546b29b755973623420d8a887c813c5521edf` includes both required histories:
- PR #9 verified head: `456e181ffda82403dc6cc9a245f66d47f9a947f4`.
- PR #10 closure head: `0181d48cf27ad3d566cb5a76c7372f12bd199fa7`.

The GitHub compare API confirms both PR heads are ancestors of the reconciled A4 candidate:
- PR #9 → A4: 21 commits ahead, 0 behind; merge base equals PR #9 head.
- PR #10 → A4: 14 commits ahead, 0 behind; merge base equals PR #10 head.

The earlier PR #9 ↔ PR #10 comparison (14 ahead / 7 behind, merge base `94a4ab968ee09f3c7dccf3d2665fc25f5fa160dd`) described their **pre-reconciliation divergence**. It is not the status of the reconciled A4 branch. The A4-only merge commit brought both lines together without merging either original PR or changing `main`.

## 2. Exact-head automated verification

| Exact commit checked out | Workflow run | Result | Scope |
|---|---|---|---|
| `ae7546b29b755973623420d8a887c813c5521edf` | [#42557579829](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42557579829) | **PASS — 3/3 jobs** | Reconciled code candidate |
| `239253f55bbc8b4936f62fbf06b8601f62cc6b06` | [#42557700677](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42557700677) | **PASS — 3/3 jobs** | Evidence-record commit; workflow logs confirm exact checkout SHA |
| `3e91081885d4d54ede01b3e281e03ad30efbd256` | [#43067522415](https://github.com/akefadaka-git/maalenex/actions/runs/43067522415) | **PASS — 3/3 jobs** | Current A4 branch tip; exact checkout SHA confirmed |

The workflow logs for both runs show the exact SHA fetched and checked out. All three jobs completed successfully: backend/PostgreSQL/migrations; frontend tests/typecheck/build/npm audit; and Python dependency audit/high-severity Bandit scan.

### Gate results

| Gate | Result |
|---|---|
| Python compilation and focused Ruff checks | PASS |
| PostgreSQL 16 migrations and service-registry seed idempotency | PASS |
| Backend/PostgreSQL integration suite | PASS — 41 tests reported |
| Alembic metadata parity | PASS |
| Full migration downgrade and clean re-upgrade | PASS |
| Frontend clean install and tests | PASS — 5 tests reported |
| TypeScript typecheck and Vite production build | PASS |
| npm audit | PASS — zero vulnerabilities reported |
| pip-audit | PASS — no known vulnerabilities reported |
| Bandit high-severity scan | PASS — no issues identified |
| Combined PR #9 + PR #10 ancestry in A4 candidate | VERIFIED |
| Combined PR #9 + PR #10 automated verification on reconciled candidate | PASS — run #42557579829 |

**Evidence qualification:** run #42557579829 is the primary code-verification run on the reconciled candidate. Run #42557700677 verifies the subsequent evidence-record commit. The two runs must not be conflated: they checked out different exact SHAs.

## 3. Branch ancestry and content reconciliation

The dedicated A4 merge commit reconciles PR #9 and PR #10 histories. It has the prior A4 line and PR #9 verified head as parents; the prior A4 line retains PR #10's closure head. Git ancestry comparisons independently confirm both PR heads are included.

The A4 report's earlier claim that PR #9 was not included was based on the graph before the reconciliation merge. That historical observation remains true for the old A4 snapshot, but it does not describe the reconciled candidate `ae7546b29b755973623420d8a887c813c5521edf`.

The five shared files changed by PR #9 were previously compared at PR #9, PR #10 and A4 refs and recorded as identical in content. PR #10 identity/E2E additions and A4 verification additions are retained. No original PR branch was rewritten.

## 4. Inherited passenger foundation evidence

PR #3 records earlier passenger-foundation fixes for:
1. Cross-challenge guest verification throttling.
2. Explicit Secure-cookie handling behind a TLS-terminating proxy.
3. Bounded PBKDF2 verifier iteration and salt/digest dimensions.

Recorded remediation HEAD: `0a01631a21a823b720337d1d80aa690e5df347bc`.  
Recorded workflow: [#42453257303](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42453257303).  
Recorded result: 28 backend/PostgreSQL tests passed plus migration and frontend gates. These inherited results are not a substitute for the A4 reconciled-candidate verification above.

## 5. Warnings and residual assurance limits

- Backend tests report a Starlette deprecation warning concerning the current `starlette.testclient` integration with `httpx`; tests pass.
- Frontend tooling emits upstream Node deprecation warnings, including `punycode` and `url.parse()`; tests and build pass.
- PostgreSQL logs include the expected append-only-trigger rejection exercised by the trust-review immutability test.

| Activity | Status |
|---|---|
| npm dependency audit | PASS — zero reported vulnerabilities |
| Python dependency audit | PASS — no known vulnerabilities reported |
| Bandit high-severity static scan | PASS — no issues identified |
| Independent third-party security review | WAIVED as prerequisite by Owner; not performed |
| Independent penetration test | NOT RUN |
| CodeQL analysis | NOT RUN |
| Full secrets-history scan | NOT RUN |
| WCAG 2.2 AA independent audit | NOT RUN |
| Production TLS proxy / key lifecycle exercise | NOT RUN |

## 6. Operational and product boundaries

The verified runtime remains development/test and synthetic-data-only. This A4 work does not activate production accounts, personal-data processing, SMS, payments/refunds, live GPS, ticket issuance, boarding, commercial operation, production keys, deployment, pilot or release.

The controlled email E2E was not rerun by the A4 verification workflow; no external email was sent by these CI runs. Existing user-confirmed delivery evidence remains the sole mailbox acceptance evidence.

PRs #3, #9 and #10 remain unmerged. The default branch was not changed. No deployment was performed.

## 7. Final A4 disposition

**PR #9 / PR #10 source-history reconciliation:** VERIFIED.  
**Reconciled code candidate `ae7546b29b755973623420d8a887c813c5521edf`:** VERIFIED — run #42557579829, all three jobs passed.  
**Evidence-record commit `239253f55bbc8b4936f62fbf06b8601f62cc6b06`:** VERIFIED — run #42557700677, all three jobs passed.  
**Reconciled A4 code candidate:** VERIFIED — run #42557579829, all three jobs passed on the exact code SHA.  
**Prior evidence-record candidate:** VERIFIED — run #42557700677, all three jobs passed on exact SHA `239253f55bbc8b4936f62fbf06b8601f62cc6b06`.  
**Current A4 branch tip `3e91081885d4d54ede01b3e281e03ad30efbd256`:** VERIFIED — exact-head run #43067522415, all three jobs passed. Backend/PostgreSQL: 41 tests passed; frontend tests, typecheck, build and npm audit passed; Python dependency audit and Bandit high-severity scan passed; Alembic parity and full downgrade/re-upgrade passed.  
**A4 automated evidence closure:** VERIFIED for the current A4 branch tip and the bounded automated gates listed above. This does not certify external penetration testing, WCAG conformance, live infrastructure or production readiness.  
**Production readiness:** NOT READY / NOT ASSESSED FOR LIVE OPERATION.  
**A5:** NOT AUTHORIZED.

This A4 assessment is limited to the documented automated verification scope. It is not production approval, independent security certification, regulatory approval, accessibility conformance certification, merge authorization or deployment authorization.
