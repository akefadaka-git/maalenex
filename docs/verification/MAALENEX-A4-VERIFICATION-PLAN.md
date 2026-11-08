# MaaleNex Moto — A4 Full Verification and Remediation Plan

**Stage:** A4 — full verification and remediation  
**Baseline:** A3-verified implementation on PR #10 head `0181d48cf27ad3d566cb5a76c7372f12bd199fa7`, which includes PR #9 and the PR #3 passenger foundation.  
**A4 branch:** `a4/full-verification-remediation`  
**Baseline governance:** synthetic-only; no merge, deployment, production activation, live payments, location tracking, or commercial operation.

## 1. Purpose

PR #3 contains an earlier, bounded A4 code-level review. It records three passenger-foundation findings (cross-challenge verification throttling, reverse-proxy cookie Secure handling, and bounded PBKDF2 verifier parameters) as remediated and regression-tested at `0a01631a21a823b720337d1d80aa690e5df347bc`.

This stage extends verification across the later shared-platform and general-account identity implementation in PRs #9 and #10. The earlier PR #3 closure is retained as inherited evidence; it is not substituted for verification of the later code.

## 2. A4 verification gates

1. **Exact source integrity:** all checks must execute against the A4 branch commit; record the full SHA and workflow run.
2. **Backend correctness:** compile, focused Ruff correctness checks, and complete pytest suite.
3. **Database integrity:** isolated PostgreSQL 16, full Alembic upgrade, registry seed idempotency, model/migration parity, full downgrade and clean re-upgrade.
4. **Frontend correctness:** clean lockfile install, complete Vitest suite, TypeScript typecheck and production build.
5. **Dependency security:** npm audit at moderate severity or higher; pip-audit against direct dependencies parsed from the authoritative `pyproject.toml` metadata (including transitive resolution).
6. **Static security:** Bandit high-severity scan of backend application code.
7. **Identity and platform regression coverage:** existing integration suite must exercise the implemented identity lifecycle, service registry and role/tenant boundaries, SMTP adapter behavior, resend throttles, audit redaction and failure handling. The suite must not send an external email.
8. **Remediation discipline:** any failure or actionable finding is documented, fixed on this A4 branch only, and the affected gates rerun against the resulting exact HEAD.

## 3. Safety and execution constraints

- CI uses disposable PostgreSQL and synthetic test data only.
- Do not invoke the manual SMTP E2E workflow; it sends an external email.
- Do not provision production secrets, use production databases, or enable real customer processing.
- SMS, payment collection, refunds, ticket issuance, boarding, live GPS, and commercial operation remain disabled/out of scope.
- No independent third-party review is required as a prerequisite per the Owner's explicit direction; this does not imply one was performed.
- CodeQL and independent penetration testing are not represented as completed by this stage.
- PRs #3, #9 and #10 remain separate and unmerged. A4 does not authorize merge or A5 deployment.

## 4. Exit criteria

A4 can be marked **VERIFIED-CLOSED** only when:
- every applicable automated gate above passes on the same final exact HEAD;
- all findings discovered in this A4 scope are either remediated and regression-verified or explicitly listed as accepted residual risks with rationale;
- the final report identifies checks not run and their implications;
- the A4 evidence record is committed on this branch and its commit is itself covered by successful exact-HEAD CI.

A green CI run alone is not a production-readiness declaration. A5 remains a separate Owner authorization and operational readiness gate.
