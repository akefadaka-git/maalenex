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

## No-send masking validation

- Workflow: `.github/workflows/identity-key-mask-validation.yml`
- Workflow commit: `9f7cf570463afa1e1e784b9679cf8c715d5617ab`
- Trigger marker commit: `8d936a517337ede6d837811e9b327cf6e951d987`
- Intended side effects: none; no SMTP credentials, no recipient, and no email command.
- Runtime result: NOT YET VERIFIED in this record.

## Governance boundary

- PR #9 remains unmerged.
- PR #10 remains unmerged.
- Production email activation, merge, deployment, and commercial operation remain separate approval gates.
- This record closes only the controlled synthetic email E2E acceptance test; it does not declare all MaaleNex A3 work complete.
