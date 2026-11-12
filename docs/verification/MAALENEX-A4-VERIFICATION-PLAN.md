# MaaleNex — A4 Full Verification and Remediation Plan

**Stage:** A4 — full verification and remediation  
**A4 branch:** `a4/full-verification-remediation`  
**Reconciled code candidate:** `ae7546b29b755973623420d8a887c813c5521edf`; PR #9 head `456e181ffda82403dc6cc9a245f66d47f9a947f4` and PR #10 closure head `0181d48cf27ad3d566cb5a76c7372f12bd199fa7` are both ancestors of this A4 commit. The A4 merge commit has the prior A4 line as first parent and PR #9 as second parent; PR #10 is retained in the prior A4 line.  
**Reconciled candidate verification:** run [#42557579829](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42557579829), all three jobs passed on exact SHA `ae7546b29b755973623420d8a887c813c5521edf`.  
**Evidence-record verification:** run [#42557700677](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42557700677), all three jobs passed on exact SHA `239253f55bbc8b4936f62fbf06b8601f62cc6b06`.  
**Current A4 branch-tip verification:** run [#43067522415](https://github.com/akefadaka-git/maalenex/actions/runs/43067522415), all three jobs passed on exact SHA `3e91081885d4d54ede01b3e281e03ad30efbd256`.  
**Governance:** synthetic-only; no PR merge, deployment, production activation, live payments, location tracking, or commercial operation.

## 1. Purpose and baseline qualification

PR #3 records earlier passenger-foundation fixes for cross-challenge verification throttling, reverse-proxy Secure-cookie handling, and bounded PBKDF2 verifier parameters at `0a01631a21a823b720337d1d80aa690e5df347bc`, with workflow [#42453257303](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42453257303).

**Historical pre-reconciliation state:** PR #9's verified head was `456e181ffda82403dc6cc9a245f66d47f9a947f4`. PR #10's then-current head `0181d48cf27ad3d566cb5a76c7372f12bd199fa7` was not a descendant of that exact PR #9 head; the pre-reconciliation comparison reported 14 commits ahead and 7 behind. That divergence explains why the earlier A4 snapshot could not be treated as verification of both latest histories together. It is a historical graph observation, not the status of the reconciled candidate.

**Post-reconciliation state:** the A4-only merge commit `ae7546b29b755973623420d8a887c813c5521edf` makes both PR heads ancestors of the candidate. GitHub comparisons report PR #9 → A4 as 21 commits ahead / 0 behind and PR #10 → A4 as 14 commits ahead / 0 behind. The five PR #9-changed shared files were compared at PR #9, PR #10 and A4 refs and have identical blob SHAs. PR #10 identity/E2E additions and A4 verification files are retained. No original PR was merged.

The prior A4 workflow snapshot `791d95796a6d87e99b3299fe7f654001e8b2be92` passed all three jobs in run [#42502705174](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42502705174), but it predates the reconciled code candidate and is not used as the final combined-history evidence.

## 2. A4 verification gates

1. **Source graph integrity:** identify exact heads and ancestry for PR #3, #9, #10 and A4; establish a controlled A4 integration candidate that includes the intended commits from both shared-platform and email-E2E branches. Preserve PRs and default branch unchanged.
2. **Exact source integrity:** every check must execute against one final exact A4 commit; record SHA and workflow run.
3. **Backend correctness:** compile, focused Ruff correctness checks, complete pytest suite.
4. **Database integrity:** isolated PostgreSQL 16, full Alembic upgrade, registry seed idempotency, model/migration parity, full downgrade and clean re-upgrade.
5. **Frontend correctness:** clean lockfile install, complete Vitest suite, TypeScript typecheck and production build.
6. **Dependency security:** npm audit at moderate severity or higher; pip-audit against authoritative `pyproject.toml` runtime and development dependencies including resolved transitive dependencies.
7. **Static security:** Bandit high-severity scan of backend application code.
8. **Identity/platform regression:** tests must exercise identity lifecycle, service registry, service-scoped role boundaries, SMTP adapter behavior, resend throttles, audit redaction and failure handling without sending external email.
9. **Remediation discipline:** document each failure or actionable finding, fix only on the A4 branch, and rerun affected gates against the resulting exact HEAD.

## 3. Safety and execution constraints

- CI uses disposable PostgreSQL and synthetic test data only.
- Do not invoke the manual SMTP E2E workflow; it sends an external email.
- Do not provision production secrets, use production databases, or enable real customer processing.
- SMS, payment collection, refunds, ticket issuance, boarding, live GPS, and commercial operation remain disabled/out of scope.
- No independent third-party review is required as a prerequisite per the Owner's explicit direction; this does not imply one was performed.
- CodeQL, full secrets-history scanning, independent penetration testing and WCAG 2.2 AA independent audit are not represented as completed unless separately evidenced.
- PRs #3, #9 and #10 remain separate and unmerged. A4 does not authorize merge or A5 deployment.

## 4. Exit criteria and disposition

A4 can be marked **VERIFIED-CLOSED** only when:
- the intended PR #9 and PR #10 code histories are reconciled in the A4 candidate and the exact commit graph is documented;
- every applicable automated gate passes on the same final exact code HEAD;
- all findings are remediated and regression-verified or explicitly listed as accepted residual risks;
- the final report identifies checks not run and implications;
- the evidence record is committed and the evidence-record commit is checked by exact-head CI.

The reconciled code-candidate requirement is satisfied by run #42557579829 on `ae7546b29b755973623420d8a887c813c5521edf`. The evidence-record requirement was satisfied for `239253f55bbc8b4936f62fbf06b8601f62cc6b06` by run #42557700677. The current A4 branch tip `3e91081885d4d54ede01b3e281e03ad30efbd256`, including the later report/plan corrections, was then checked by exact-head run #43067522415; all three jobs passed. The backend job reported 41 passed tests, Alembic parity, and full downgrade/re-upgrade success.

A5 remains a separate Owner authorization and operational readiness gate.
