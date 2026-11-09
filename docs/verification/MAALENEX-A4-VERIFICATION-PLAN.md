# MaaleNex Moto — A4 Full Verification and Remediation Plan

**Stage:** A4 — full verification and remediation  
**A4 branch:** `a4/full-verification-remediation`  
**Observed branch graph:** PR #10-derived A4 branch is not a fast-forward descendant of PR #9's recorded verified head. The compare endpoint reports A4 branch 18 commits ahead and 7 behind PR #9 head `456e181ffda82403dc6cc9a245f66d47f9a947f4`, with merge base `94a4ab968ee09f3c7dccf3d2665fc25f5fa160dd`.  
**Prior A4 workflow snapshot:** `791d95796a6d87e99b3299fe7f654001e8b2be92`; all three jobs passed in run [#42502705174](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42502705174).  
**Governance:** synthetic-only; no PR merge, deployment, production activation, live payments, location tracking, or commercial operation.

## 1. Purpose and baseline qualification

PR #3 records earlier passenger-foundation fixes for cross-challenge verification throttling, reverse-proxy Secure-cookie handling, and bounded PBKDF2 verifier parameters at `0a01631a21a823b720337d1d80aa690e5df347bc`, with workflow [#42453257303](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42453257303).

PR #9 records the shared-platform and identity baseline at `456e181ffda82403dc6cc9a245f66d47f9a947f4`. PR #10's later head `0181d48cf27ad3d566cb5a76c7372f12bd199fa7` is not a descendant of that exact PR #9 head: the branch comparison reports 14 commits ahead and 7 behind. Therefore, the prior A4 green run verifies the A4 branch snapshot, not a reconciled combination of the latest PR #9 and PR #10 heads.

A4 remains **PARTIAL** until the branch graph and code state are reconciled without merging PRs or changing the default branch. Do not describe PR #10 as including the latest PR #9 commits until ancestry is proven.

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

## 4. Exit criteria

A4 can be marked **VERIFIED-CLOSED** only when:
- the intended PR #9 and PR #10 code histories are reconciled in the A4 candidate and the exact commit graph is documented;
- every applicable automated gate passes on the same final exact HEAD;
- all findings are remediated and regression-verified or explicitly listed as accepted residual risks;
- the final report identifies checks not run and implications;
- the A4 evidence record is committed and that commit itself passes exact-HEAD CI.

A green CI run on a branch that omits commits from another required baseline is not sufficient. A5 remains a separate Owner authorization and operational readiness gate.
