# MaaleNex A3 — Controlled Verification Email E2E Evidence

**Record date:** 2026-11-08  
**Scope:** One Owner-authorized synthetic verification-email end-to-end test.  
**Environment:** GitHub Actions, ephemeral PostgreSQL 16, test-only application configuration, Gmail SMTP.  
**Production status:** Not activated. No merge or deployment authorized by this record.

## Verified test

- **Implementation PR:** [#10](https://github.com/akefadaka-git/maalenex-moto/pull/10)
- **Implementation branch HEAD:** `c4c5ff31058afcae972078fd4a0a81fe83d7b79f`
- **Successful E2E workflow run:** [#42497547149](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42497547149)
- **Run-trigger commit:** `06c1618fbdc8b8532499852b916a75acc15bd7d1`

### Acceptance evidence

| Check | Result |
|---|---|
| Synthetic registration endpoint exercised | PASS |
| Exactly one verification message accepted by Gmail SMTP | PASS |
| Recipient mailbox receipt | PASS — Owner confirmed receipt |
| Challenge persisted as digest only | PASS |
| Verification token exposure disabled | PASS |
| Registration audit event | PASS |
| Delivery audit event and metadata | PASS |
| Recipient address/token omitted from audit metadata | PASS |
| Secrets/message body omitted from test output | PASS |
| Ephemeral PostgreSQL/test cleanup | PASS |

This closes the controlled one-message test. No further email send is authorized or required for this evidence record.

## Follow-up security hardening

The initial successful run exposed ephemeral test-only encryption and lookup keys in the Actions log. These were not Gmail credentials or production keys. The workflow was corrected to register both generated values with GitHub Actions masking before exporting them through `GITHUB_ENV`, and to remove the temporary key file.

- **Hardening commit:** [`ab9f26f089edcbb45ea6fa13c23d33778b7d28e0`](https://github.com/akefadaka-git/maalenex-moto/commit/ab9f26f089edcbb45ea6fa13c23d33778b7d28e0)
- **File:** `.github/workflows/identity-email-e2e.yml`
- **Static inspection:** PASS — both `::add-mask::` calls precede the corresponding `GITHUB_ENV` writes; temporary file is removed.
- **Runtime masking verification:** PENDING — a separate no-send workflow has been added so this can be checked without invoking the email-delivery path.

## No-send masking validation — VERIFIED PASS

- Workflow: `.github/workflows/identity-key-mask-validation.yml`
- Run: [#42499087307](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42499087307)
- Trigger marker commit: `8d936a517337ede6d837811e9b327cf6e951d987`
- Job `128787696391`: all five steps succeeded.
- Runtime log probes show both generated values redacted as `***`; temporary file removed.
- No SMTP credentials were supplied and no email command was invoked.
- Result: VERIFIED-CLOSED; no additional email was sent.

## Exact-HEAD PR verification and dependency security audit — VERIFIED PASS

### Final verified pull-request heads

- PR #9: `15348386fca41340a1ed2d27901e43f01da00ad1` — [PR](https://github.com/akefadaka-git/maalenex-moto/pull/9) — [CI run #42500056878](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42500056878)
- PR #10: `a80c56639142ebe6440ffdda12b7d37524c3474c` — [PR](https://github.com/akefadaka-git/maalenex-moto/pull/10) — [CI run #42500059996](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42500059996)

Both exact-HEAD CI runs passed backend compilation, Ruff, PostgreSQL migrations, idempotent seed, 41 backend/PostgreSQL tests, Alembic parity, downgrade/re-upgrade, 5 frontend tests, TypeScript typecheck and Vite production build.

### Dependency audit findings and remediation

The first dependency scan found 6 npm vulnerabilities (3 moderate, 1 high, 2 critical) in the Vite/Vitest test/build toolchain and Python advisories affecting `cryptography 46.0.7` and `pytest 8.4.2`.

Remediation on both PR branches:
- Vite upgraded to `^8.3.6`, Vitest to `^4.1.12`, and `@vitejs/plugin-react` to `^6.0.3`; frontend CI uses Node 24.
- `cryptography` constraint upgraded to `>=50,<51`; pytest constraint upgraded to `>=9.0.3,<10`.

Final exact-HEAD security audit: [run #42500072233](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42500072233). All four jobs passed: npm audit found 0 vulnerabilities for each PR head; pip-audit reported no known vulnerabilities for each PR head.

### Security review boundary

- Ephemeral key masking: runtime-verified.
- Python and npm dependency vulnerability scans: PASS on both final PR heads.
- The configured exact-HEAD CI gates passed.
- No CodeQL/SAST or independent third-party penetration test was run in this verification. Those are not claimed as passed.

### Final PR governance status

- PR #9 remains open/draft/unmerged; mergeable reported true.
- PR #10 remains open/draft/unmerged; mergeable reported true.
- No review threads or submitted PR reviews were returned by GitHub at verification time.
- No merge, production activation, or deployment was performed or authorized.

This closes the bounded E2E and exact-HEAD CI/dependency-scan verification record. It does not close all MaaleNex A3 implementation or independent security assurance.

## Governance boundary

- PR #9 remains unmerged.
- PR #10 remains unmerged.
- Production email activation, merge, deployment, and commercial operation remain separate approval gates.
- This record closes only the controlled synthetic email E2E acceptance test; it does not declare all MaaleNex A3 work complete.
