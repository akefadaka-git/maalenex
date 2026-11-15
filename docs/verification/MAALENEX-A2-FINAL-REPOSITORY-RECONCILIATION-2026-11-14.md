# MaaleNex — A2 Final Repository Reconciliation and Integration Register

**Status:** A2 VERIFIED-CLOSED WITH RECORDED INTEGRATION GAPS  
**Audit date:** 2026-11-14  
**Repository:** `akefadaka-git/maalenex`  
**Authoritative baseline:** `main` at `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9`  
**Branch:** `docs/a2-final-repository-reconciliation`  
**Scope:** Read-only repository, branch, commit, PR, dependency, workflow-evidence and architecture reconciliation. This document is committed on a separate documentation branch; it does not modify `main`.

---

## 1. Executive disposition

The current repository contains a substantial, largely tested passenger platform foundation, a shared identity/platform layer, synthetic location/Move implementation, and two distinct Android implementation approaches. The implementation is not ready for bulk merge.

A2 is closed for repository inventory, dependency reconstruction, content reconciliation and an actionable integration/cleanup register. The closure is **with recorded gaps**: several branches require synchronization, PR #1 contains unsafe deletions, the Android package identifier is inconsistent, and the current A4 documentation tip is newer than its last exact-head workflow run.

### Audit facts

| Item | Result |
|---|---|
| Current `main` SHA | `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` |
| Branches | 22 |
| Pull requests | 18 |
| Merged PRs | 3 (#12, #13, #16) |
| Open PRs | 15 |
| PRs currently marked draft | 14 |
| Main changes made during this audit | NONE |
| Application code changes | NONE |
| Merges, branch deletions or deployments | NONE |

**Important:** historical reports that use `72550a2e464f6517653580bb1ae4e7608f211f39` as main are not current. That SHA is the common historical baseline for many branches, not the current default-branch head.

### Primary decisions

1. PR #1 must not be merged as-is: its current diff removes 13 files from current main, including deployment and identity/security workflows.
2. PR #3 must be synchronized with the current G1 branch. Its base SHA is stale and GitHub reports `mergeable=false`.
3. PRs #9 and #10 are already reconciled in the A4 branch. Use the A4 consolidated history rather than merging the two stale stacked PRs independently.
4. The location/Move branch is an A4 descendant. PR #17 adds the service-area and lifecycle repair on top of it.
5. The owner-approved A1 v1.1 platform scope in PR #6 supersedes the draft biker-first A1 v1.0 document found on the restructure branch.
6. The approved Android architecture is a native Android Activity with a packaged WebView using AndroidX WebViewAssetLoader and a future AndroidX WebMessageListener bridge. Capacitor and `addJavascriptInterface` are excluded by the Android A1/A2 architecture contract.
7. A5 security/deployment branches remain isolated from the application integration and mainline merge sequence.

---

## 2. Exact branch inventory

The following branch HEADs were retrieved from the live repository during this audit.

| Branch | Exact HEAD SHA |
|---|---|
| `main` | `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` |
| `feat/g1-foundation-completion` | `7e71bd98752fa22f62e32f0f52737db89e7828c2` |
| `feat/a3-passenger-mvp` | `0a01631a21a823b720337d1d80aa690e5df347bc` |
| `feat/a3-maalenex-shared-platform-foundation` | `456e181ffda82403dc6cc9a245f66d47f9a947f4` |
| `feat/a3-synthetic-email-e2e-test` | `0181d48cf27ad3d566cb5a76c7372f12bd199fa7` |
| `feat/a3-location-consent-foundation` | `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611` |
| `fix/critical-location-consent-ci` | `9f4683455faddadd9107e0bf34dd6052f1aa54a6` |
| `a4/full-verification-remediation` | `b14151cd013289afd4cb162acfddd02a09be22df` |
| `docs/maalenex-platform-restructure-guideline` | `f7b1b6d73fbcaaa14b27c8f0ce81578378343c7f` |
| `feat/biker-first-platform-a1-test-catalog` | `22813a4510d42d4295602075abaebabc7a83369e` |
| `docs/maalenex-platform-guideline` | `276fbb6d02d47421466199d477a4fe770c1f117e` |
| `docs/a2-maalenex-platform-reconciliation` | `59045e7238fa0c2050ea2f0518eb32024d6013a4` |
| `docs/product-scope-roadmap-v1` | `3bf77bdbf6d017331a5ec2ea64e2a36577f9c8b6` |
| `feat/android-debug-apk` | `24a5e3af527e7e306e29e4c613f36e08722ff50c` |
| `fix/android-device-acceptance` | `563bd5c9eba6e69c1de08a29f00b113679c19cc5` |
| `fix/android-device-acceptance-emulator` | `56673921d966c505e2cf43fcee5b4d8786237f11` |
| `feat/maalenex-brand-identity` | `8d422a7ff14978f6e9733f0213c712e8f9d16703` |
| `fix/canonical-maalenex-product-identity` | `67e6c49a5cd925b43db3356b063be53069f73df5` |
| `a5/deployment-readiness-assessment` | `4a88653b1caef2c594587e24c67f004967b9bc10` |
| `a5/a5-3-4-edge-security-hardening` | `904d9a570b9bdf1867e9597f132a6b6a440794f6` |
| `a5/a5-3-6-provider-neutral-deployment-spec` | `f06443685688b5b7f017b3868fa108a95b1387f6` |
| `infra/cloudflare-pages-direct-upload` | `53814ad9f8883a62cc6e0599a7fa07078ff401d1` |

---

## 3. Full G1 ↔ Passenger MVP reconciliation

### 3.1 Commit graph

| Reference | SHA |
|---|---|
| Common historical merge base | `50e38a94011eb24d06812acace7d09e4d8e81dc8` |
| Current G1 head | `7e71bd98752fa22f62e32f0f52737db89e7828c2` |
| Passenger MVP head | `0a01631a21a823b720337d1d80aa690e5df347bc` |
| Current main | `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` |

GitHub compare result, G1 → Passenger: **202 commits unique to Passenger and 35 commits unique to G1**, with the common merge base above. The compare reports divergence. PR #3 still targets the old G1 base SHA `50e38a94011eb24d06812acace7d09e4d8e81dc8`, while current G1 is `7e71bd98752fa22f62e32f0f52737db89e7828c2`. GitHub currently reports PR #3 as `mergeable=false`.

G1 itself is 39 commits ahead of current main and 0 behind. Passenger is 235 commits ahead of its old main ancestor and 29 commits behind current main. These are not mergeable snapshots of the same baseline.

### 3.2 Passenger-only work — 202 commits

The 202 commits on the Passenger side represent the complete passenger MVP implementation and remediation history, not just a small feature patch. The commit subjects classify broadly as:

- 87 feature commits: identity, organization, catalog, fleet, trips, fares, bookings, reservations, support, operator administration, maintenance and frontend journeys.
- 58 fixes: migration/model alignment, transaction and concurrency integrity, idempotency, authorization, session and cookie behavior, audit redaction, fare publication, API and frontend correctness.
- 22 test commits: PostgreSQL concurrency, booking access, staff authentication, support, manifests, reservation recovery, UI behavior and lifecycle regression.
- 8 A4 remediation commits: cross-challenge guest verification throttling, explicit Secure-cookie configuration and bounded password-verifier parameters, plus regression coverage.
- Additional CI, documentation, build, accessibility and maintenance commits.

The Passenger branch contains migration revisions 0002–0007 and the associated domain implementation. Its final recorded A4-remediated head is `0a01631a21a823b720337d1d80aa690e5df347bc`.

The 62-file comparison includes the following complete path set:

```text
.github/workflows/a3-verify.yml
README.md
backend/app/core/config.py
backend/app/db/model_registry.py
backend/app/domains/audit/__init__.py
backend/app/domains/audit/models.py
backend/app/domains/audit/service.py
backend/app/domains/bookings/__init__.py
backend/app/domains/bookings/access.py
backend/app/domains/bookings/maintenance.py
backend/app/domains/bookings/models.py
backend/app/domains/bookings/service.py
backend/app/domains/catalog/__init__.py
backend/app/domains/catalog/models.py
backend/app/domains/fares/__init__.py
backend/app/domains/fares/models.py
backend/app/domains/fares/service.py
backend/app/domains/fleet/__init__.py
backend/app/domains/fleet/models.py
backend/app/domains/identity/__init__.py
backend/app/domains/identity/authorization.py
backend/app/domains/identity/models.py
backend/app/domains/identity/security.py
backend/app/domains/identity/service.py
backend/app/domains/organizations/__init__.py
backend/app/domains/organizations/models.py
backend/app/domains/organizations/service.py
backend/app/domains/reservations/__init__.py
backend/app/domains/reservations/models.py
backend/app/domains/support/models.py
backend/app/domains/trips/__init__.py
backend/app/domains/trips/models.py
backend/app/main.py
backend/app/routers/admin.py
backend/app/routers/auth.py
backend/app/routers/bookings.py
backend/app/routers/passenger_catalog.py
backend/migrations/env.py
backend/migrations/versions/0002_identity_audit_organizations.py
backend/migrations/versions/0003_passenger_domains.py
backend/migrations/versions/0004_staff_auth_controls.py
backend/migrations/versions/0005_booking_access_challenges.py
backend/migrations/versions/0006_guest_access_rate_limits.py
backend/migrations/versions/0007_operator_invites_support.py
backend/pyproject.toml
backend/scripts/__init__.py
backend/scripts/booking_maintenance.py
backend/scripts/booking_maintenance_worker.py
backend/scripts/seed_synthetic_admin.py
backend/tests/test_admin_router.py
backend/tests/test_audit_redaction.py
backend/tests/test_guest_booking_access.py
backend/tests/test_health.py
backend/tests/test_identity_security.py
backend/tests/test_postgres_booking_concurrency.py
backend/tests/test_staff_auth.py
docs/A3-OPERATIONS-RUNBOOK-v1.0.md
frontend/src/App.test.tsx
frontend/src/App.tsx
frontend/src/styles.css
frontend/vite.config.ts
scripts/validate-a3.ps1
```

### 3.3 G1-only work — 35 commits

The 35 G1-side commits include the G1 technical foundation, but also SMTP/E2E/security-audit workflow history and the current-main reconciliation. Exact commit subjects and SHAs:

| SHA | Commit subject |
|---|---|
| `7a96058fba17cf804afa8f44bff8ac3a36676145` | ci: add isolated manual SMTP connectivity workflow |
| `417e18d3dbb15c04aeb2eee595d240b0e6854149` | Configure Gmail SMTP defaults for connectivity workflow |
| `28e15609c0535257b6e7a3e72c4b213bf5994498` | Fix Gmail SMTP connectivity workflow source checkout |
| `eb232aff69ac1e5e67ce39fa85ad50ab5f4ed8f0` | Fix manual Gmail SMTP check and harden workflow execution |
| `637f42b50f886504553866af2bbe71e0f1b3a232` | Run Gmail SMTP connectivity check on workflow revision updates |
| `5e516f172227f1a4ce68c9d65f776a7e61bf39c0` | Run Gmail SMTP diagnostics against corrected A3 implementation |
| `5f4f5e73c83ccdc5b344ebac4a9e8dd961db1e7f` | Pin SMTP check to corrected SNI-aware transport implementation |
| `8610cebc5a2dd55c751b9e958d34a48bd24dad49` | Pin Gmail connectivity test to normalized credential implementation |
| `7f03cfa04177fe0b7b57a48297d96c9889013992` | Add non-disclosing Gmail App Password format preflight |
| `c5892411247efae60bdf76f2d1d31a982a959020` | ci: add manual synthetic verification email E2E workflow |
| `a4e61504dfdcff7fc7b3d79494b67275e113efda` | ci: add controlled push trigger for synthetic email E2E |
| `06c1618fbdc8b8532499852b916a75acc15bd7d1` | ci: trigger one Owner-authorized synthetic email E2E run |
| `ab9f26f089edcbb45ea6fa13c23d33778b7d28e0` | security: mask ephemeral identity keys in E2E logs |
| `9f7cf570463afa1e1e784b9679cf8c715d5617ab` | test: add no-send ephemeral key masking validation workflow |
| `8d936a517337ede6d837811e9b327cf6e951d987` | test: trigger no-send identity key masking validation |
| `b6315dd87686ff1f7b0e4fdf577516b7d67a2365` | docs: close controlled synthetic email E2E evidence record |
| `f880052f6b1757e5c2f9d00812c2991f6c699f81` | security: add exact-HEAD dependency audit workflow |
| `6c3f25e614676ce8d55bb374e04cfa2730ad4316` | security: trigger exact-HEAD dependency audit |
| `bdfc02dd0dea4984dad4d5068373dd06a845bb89` | security: audit current PR heads and skip local editable package |
| `d7e34edb81bf520bdc7323885bb729ec035cc5e1` | security: rerun audits on updated exact PR heads |
| `8afbd71d585f903348aca7afcfeaf5bc7371713b` | security: audit declared Python dependency graph and use Node 24 |
| `24620f4de8febb7409ee784fa51016dc00090b65` | security: audit latest remediation heads |
| `031d865fdfb32adce79aebb9e7f8d5a357c5bd71` | security: trigger final exact-head dependency audits |
| `253630a438b0e99094fbf7fad031aac008a91ca7` | security: install pip-audit in exact-head scanner job |
| `210ff3b3c7331384da36111579f95089fae02ab5` | security: trigger corrected dependency audit |
| `ced172848502b07a6c7631a1a27db222492f11ac` | security: target Python dependency remediation heads |
| `599526453da876e8c3812759c3bc4ecee508611b` | security: trigger final vulnerability audit after Python upgrades |
| `7d0e1ffd99bfd3134de50bb4dc5d2e322b202ca9` | docs: record exact-head CI and dependency security verification |
| `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | Add guarded Cloudflare Pages Direct Upload workflow (#16) |
| `0022675dcf33df69c7b5c57fcad0bb9d570639d4` | merge(main): reconcile G1 foundation branch with current main |
| `b2af4252bed8b569c94ae2749e07b6ec4fe67890` | ci(g1): verify backend against ephemeral PostgreSQL |
| `fb9d16b4b260edf84d7202aefbcd9036d8921eb4` | style(g1): sort settings imports |
| `659265f8508175ca3ca64b4f54bca2472a54f0e7` | style(g1): fix Alembic revision typing and imports |
| `9968a3e0d7d2ecd96c906874f6cd974364dd1cb2` | test(g1): assert configured runtime environment in health response |
| `7e71bd98752fa22f62e32f0f52737db89e7828c2` | ci(g1): apply baseline before Alembic metadata check |

### 3.4 Critical G1 merge-safety finding

PR #1 source `feat/g1-foundation-completion` at `7e71bd98752fa22f62e32f0f52737db89e7828c2` has 38 changed files relative to its main base. Its PR changed-file list includes deletions of 13 files that exist on current main:

- `.github/e2e-triggers/identity-email-e2e/2026-11-08-owner-authorized-test.yml`
- `.github/e2e-triggers/identity-key-mask-validation/2026-11-08-validation.yml`
- `.github/security-triggers/a3-exact-head-audit/2026-11-08-final-2.yml`
- `.github/security-triggers/a3-exact-head-audit/2026-11-08-final-3.yml`
- `.github/security-triggers/a3-exact-head-audit/2026-11-08-final.yml`
- `.github/security-triggers/a3-exact-head-audit/2026-11-08-pr9-pr10.yml`
- `.github/security-triggers/a3-exact-head-audit/2026-11-08-rerun.yml`
- `.github/workflows/a3-exact-head-security-audit.yml`
- `.github/workflows/cloudflare-pages.yml`
- `.github/workflows/identity-email-e2e.yml`
- `.github/workflows/identity-key-mask-validation.yml`
- `.github/workflows/identity-smtp-connectivity.yml`
- `docs/verification/MAALENEX-A3-EMAIL-E2E-EVIDENCE.md`

This is not a harmless mergeability warning. In particular, merging PR #1 as-is would remove the guarded Cloudflare Pages workflow added to main by PR #16. The SMTP and security workflows/evidence also require explicit disposition rather than silent deletion.

**Required A3 correction:** preserve/restore these current-main files on the G1 integration candidate, or document an individually approved retirement for each one. Re-run G1 exact-head CI after the correction. Do not merge PR #1 in its current state.

---

## 4. Shared platform and synthetic email dependency reconciliation

### PR #9 — shared platform

- Source branch/head: `feat/a3-maalenex-shared-platform-foundation` / `456e181ffda82403dc6cc9a245f66d47f9a947f4`
- Target branch/base recorded by PR: `feat/a3-passenger-mvp` / `0a01631a21a823b720337d1d80aa690e5df347bc`
- It adds platform-service registry, service-area availability, service-scoped roles, general platform accounts, identifier verification, sessions, credential enrollment, password recovery, SMTP adapter contracts, resend throttling and migrations 0008–0012.
- Identity identifiers are encrypted with AES-GCM; lookup uses keyed digests. SMTP is disabled by default. SMS remains an adapter contract, not a live integration.
- The current branch includes the latest A3.7 changes. The PR body records exact tested head `cf3e86c72477a39320b90cff4c0488999e4fc177` and workflow #42480441967; the current branch has since advanced to `456e181...`.

### PR #10 — synthetic email E2E

- Source branch/head: `feat/a3-synthetic-email-e2e-test` / `0181d48cf27ad3d566cb5a76c7372f12bd199fa7`
- Target branch/base recorded by PR: shared-platform at `94a4ab968ee09f3c7dccf3d2665fc25f5fa160dd`
- It adds a manual-only isolated PostgreSQL/Gmail SMTP E2E workflow. The workflow enforces a fixed Owner-designated mailbox allowlist and sends one synthetic verification email if explicitly dispatched with authorized secrets.
- No live SMTP E2E send or inbox confirmation is evidenced by the current report. No secrets were changed or used by this audit.

### Existing A4 consolidation

The A4 branch already contains both exact PR heads:

- Compare PR #9 head → A4: PR #9 head is an ancestor of A4; 30 commits ahead on A4.
- Compare PR #10 head → A4: PR #10 head is an ancestor of A4; 23 commits ahead on A4.
- Reconciled A4 code candidate: `ae7546b29b755973623420d8a887c813c5521edf`.
- Combined A4 workflow #42557579829: SUCCESS, 3/3 jobs.
- Later A4 branch-tip workflow #43067522415: SUCCESS on exact SHA `3e91081885d4d54ede01b3e281e03ad30efbd256`.

**Disposition:** Do not merge PR #9 and #10 separately into main. Use the A4 reconciled history as the source for these two increments after synchronizing it with the corrected G1 foundation. Keep the manual SMTP E2E workflow manual-only; it is not a production email activation.

---

## 5. Deep inspection of the three unassociated branches

### 5.1 A4 branch — `a4/full-verification-remediation`

- Current branch HEAD: `b14151cd013289afd4cb162acfddd02a09be22df`.
- Verified A4 code candidate: `ae7546b29b755973623420d8a887c813c5521edf`.
- Exact branch-tip verification at `3e91081885d4d54ede01b3e281e03ad30efbd256`: workflow #43067522415 PASS.
- The current A4 branch tip is two documentation-only commits beyond `3e910...`; those two commits are not present on the location/Move branch:
  - `3745dc92ea5533524e81811d5a143ac7d1c0bb25` — Reconcile A4 closure with exact branch-tip Actions evidence.
  - `b14151cd013289afd4cb162acfddd02a09be22df` — Record exact-head A4 evidence-record verification.
- The A4 report records 41 backend/PostgreSQL tests, frontend tests/typecheck/build, npm audit, pip-audit and Bandit as passing on the reconciled candidate. Independent penetration testing and CodeQL remain NOT RUN. A4 current documentation tip has no exact-head run after the two documentation-only commits.

**Disposition:** This is not an orphan implementation. Preserve the A4 evidence updates. Carry the two documentation commits into the consolidated A3/A4 candidate before retiring the branch. Do not merge the whole A4 branch directly to main without the G1 synchronization described above.

### 5.2 Platform restructure guideline branch — `docs/maalenex-platform-restructure-guideline`

- Current branch HEAD: `f7b1b6d73fbcaaa14b27c8f0ce81578378343c7f`.
- It has 10 commits after Passenger head `0a01631a21a823b720337d1d80aa690e5df347bc`.
- Its 10-commit line is:
  - `85e6ac35b4e7b28533d30eb072861e3ba6ecd54a` — isolated synthetic backend configuration.
  - `f54d4284465b0d706ce15014ab0d99513fa08544` — deterministic synthetic route catalog seed.
  - `9920b8a46fd0db02be2d6e5169570e49bf7448bf` — biker-first mobility A1 draft.
  - `0c0ccf074445b41263f390526b1ed9cf3a9eb90a` — synthetic catalog PostgreSQL CI.
  - `415a5175e34422a082050ba5b29a47b05c906f9c` — synthetic bus inventory.
  - `d7d532222760e4b932ed40247acb3c6ee3fb8912` — synthetic departure search verification.
  - `b12fdc787065fb349ecc7514ce3620b68e98b8e3` — flush synthetic vehicle before seat layout.
  - `3e76a7b8637ee1ddeb8bfd240c0e94da23dac245` — flush synthetic organization before vehicle.
  - `09eb0baeaa2cb9978fa8518402dccd3096f1c728` — clarify combined biker/passenger primary service.
  - `f7b1b6d73fbcaaa14b27c8f0ce81578378343c7f` — add platform implementation guideline v1.0.

The branch's unique final guideline commit is a draft status revision. The equivalent guideline in PR #7 is materially more authoritative: its document says **Owner-approved implementation guideline; A1 v1.1 frozen 2026-11-08**. The two guideline files differ in nine lines, chiefly the approval status and next-stage statements.

PR #6's branch `feat/biker-first-platform-a1-test-catalog` at `22813a4510d42d4295602075abaebabc7a83369e` shares the synthetic catalog history and adds four commits after common commit `09eb0bae...`:

- `fb8371c0bdab857c5f88b0e7ad566347e362779f` — expand A1 into MaaleNex platform scope v1.1.
- `863087418cf73cd7f313fbf3e31820b8f61729ab` — publish expanded A1 v1.1.
- `f87befeae06f2a75e1334e13dd8ceac3bd3cd6b0` — replace obsolete biker-first A1 filename.
- `22813a4510d42d4295602075abaebabc7a83369e` — record Owner approval and freeze MaaleNex A1 v1.1.

PR #6 states A1 v1.1 is Owner-approved/frozen and its synthetic catalog workflow passed on the recorded exact commit. The older `BIKER-FIRST-PLATFORM-A1-v1.0.md` is a draft and is superseded by the approved full-platform A1 v1.1. Do not treat the draft as the controlling product scope.

**Disposition:** Preserve the shared synthetic catalog workflow, test configuration and seed through PR #6. Use the approved A1 v1.1 document from PR #6 and the Owner-approved implementation guideline from PR #7. Do not merge the draft biker-first A1 v1.0 as authoritative. Once those contents are preserved, retire the restructure branch.

### 5.3 Location-consent foundation — `feat/a3-location-consent-foundation`

- Current branch HEAD: `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611`.
- Common A4 base: `3e91081885d4d54ede01b3e281e03ad30efbd256`.
- It adds 23 commits and 17 changed files: scoped consent, time-bounded location sessions, synthetic-only samples, Move ride lifecycle, service-area authorization, authenticated ride API, dispatch permission, and lifecycle integration tests.
- Exact 23 commits:

| SHA | Commit subject |
|---|---|
| `59dd2cd6abc18035ea519e0d6ddd7d1520110b1a` | scoped consent and synthetic session foundation |
| `7f087b40c4503d8a4fe465bceb05393b56c25a03` | enforce consent expiry and migration parity |
| `d90f030c27f237a781d91a69fc8b4207a08fd59a` | use database clock for synthetic sample timestamps |
| `7f6312cc65766fb402c514cf25fae80fcb190aff` | advance database clock for expiry regression |
| `c7de983c7343b43bf445d6a4dc364feb5d716e91` | authoritative Move ride lifecycle foundation |
| `ea14b8059a05df69378be7c4d2ef3ab65d1e1013` | resolve active Move ride from authoritative record |
| `c1cb9912f1dad392b87ac2ed30da260ea2b2dfeb` | authoritative ride and location consent integration test |
| `b2373192a59693b0116bfee32b60402906d7a39f` | correct lifecycle service lint violations |
| `7837bd72367583d22a7a13b5c1eb7417ed712b89` | remove unused consent assignment in test |
| `f79f438fa0df4c4a0b7a836a3bab4630609b2f83` | terminate location sessions with ride lifecycle |
| `2bf302931ec1db79d2ad72ce357f43af981b336e` | verify ride completion closes location sessions |
| `638d977c7494756ef1112abcf236ac78dc890694` | authenticated synthetic ride API |
| `dff1b01775cfee42d57685dd55ca6dabdd841241` | register authenticated ride API |
| `1170c38ae605486545ef3e8ea99e7b37c3cc322c` | attribute dispatch assignments to staff |
| `a96e327fe3f2c6bbc0804119749e3414c26299a6` | provision explicit dispatch permission |
| `056badeb38a5385c0d656287c39d0806f69e864f` | cover API registration and authentication |
| `3dd43c9d2c85db520fcf5b89a1991a1b401ec5bf` | idempotent dispatcher permission seed |
| `6eaf1fc8032abbc9043a9cdd54a7ca64113ef4b8` | remove unused router import |
| `976f384cb4748c8b8fc30028f206bc825fe36763` | correct ride lifecycle and pending-account fixtures |
| `838b901135874266d1148b922342358f83b9f335` | expose participant location consent controls |
| `0d85f19ad46f3fbee4bee83fc7ac578232cad80b` | require verified service-authorized drivers |
| `9381939bd1c80e5e7d591e6f755b49718ceb8bcc` | enforce authoritative pickup and destination service areas |
| `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611` | constrain synthetic service areas to test environment |

The location migrations form a single chain:
- `0013_location_consent_sessions.py` revises `0012_challenge_resend`.
- `0014_move_rides.py` revises `0013_location_consent`.

**Disposition:** Preserve this branch as the parent of PR #17. Do not merge it separately to main; use PR #17's repaired descendant as the location/Move integration source after synchronizing the complete stack with corrected G1.

### PR #17 — 11 repair commits on top of location

PR #17 source `fix/critical-location-consent-ci` at `9f4683455faddadd9107e0bf34dd6052f1aa54a6` is 11 commits ahead of location head `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611`. It adds migration 0015 and repairs the Move API/service/ORM/fixtures.

The 11 commits are:

| SHA | Commit subject |
|---|---|
| `e58ba3adef40f8d2da14f9ae61e7f9826162beb0` | Fix location-consent ride fixture contract |
| `8eb6d5e149f52e605af75fd08f2bf735b8bf9e72` | Enable synthetic Move area fixtures in test mode |
| `b1b530fa3c36b2e66c7d672683cd192c7bc3ce02` | Run location-consent verification on remediation branch |
| `61279b55697acde91d067b98c08e3b7903029198` | Persist Move ride service-area fields in ORM model |
| `e90b2a4f3d769b36b8918011d71899d4bcf35516` | Persist correct lifecycle timestamps for Move ride transitions |
| `c073e67fb188c855ded2f592e2658d2476c99acf` | Require service-area scope when creating Move rides |
| `3b27bab0eb8225478f3e37fef88b0e9c4d71a5a9` | Align Move API authentication test with required request schema |
| `dfa6a447817218bd988783ee44fd1d1da1a15c0d` | Add reversible Move ride service-area migration |
| `8f7f69f3cee28d8a0abc85fc1fc8c1e28febc825` | Isolate location lifecycle fixtures from driver trust onboarding |
| `04881b95551c61813e566243fcfe00512837a62e` | Assert Move scope persistence and lifecycle timestamp behavior |
| `9f4683455faddadd9107e0bf34dd6052f1aa54a6` | Verify Move API requires explicit service-area scope |

Migration `0015_move_ride_service_areas` revises `0014_move_rides` and adds nullable FK-constrained pickup/drop-off service-area fields. Nullable fields avoid inventing service areas for historical synthetic rows.

Exact-head workflow #43275551265 passed on `9f468345...`: 54 backend tests, Ruff, Alembic metadata parity and full downgrade/re-upgrade passed.

---

## 6. Canonical Android architecture

### 6.1 Controlling architecture record

PR #14 / branch `feat/maalenex-brand-identity` currently points to `8d422a7ff14978f6e9733f0213c712e8f9d16703`.

The branch contains:
- `docs/architecture/ANDROID-NATIVE-BRIDGE-PLUGIN-A1.md`
- `docs/architecture/ANDROID-NATIVE-BRIDGE-PLUGIN-A2-RECONCILIATION.md`
- `docs/architecture/ANDROID-NATIVE-BRIDGE-PLUGIN-A2-CLOSURE.md`

The A2 closure record says Owner approval was received on 2026-11-14 and records A2 as VERIFIED-CLOSED for architecture and implementation-contract reconciliation. It explicitly does not claim the bridge/plugins have been implemented. The A1 baseline native-shell smoke run #43592760041 passed on exact SHA `f805fcca56cafd88fe4d1382affe83dc02c99720`. The current PR #14 head is later than that exact tested SHA; the latest branch-tip commit fixes Android workflow summary formatting, so a new exact-head run is still required before integration.

### 6.2 Canonical architecture decision

**Canonical v1 Android client: native Android Activity + AndroidX WebViewAssetLoader + packaged React/Vite frontend.**

- Native Android owns the WebView and serves packaged assets at `https://appassets.androidplatform.net/assets/www/index.html`.
- Keep AndroidX WebKit `1.12.1`; JavaScript and DOM storage are enabled for the packaged application.
- File access, content access and mixed content are disabled; cleartext traffic is disabled.
- Native navigation is restricted to the exact packaged HTTPS asset origin and path.
- The future JS/native bridge uses AndroidX `WebMessageListener`, not `addJavascriptInterface`.
- Bridge requests are JSON-only, versioned, bounded and schema-validated; sender origin and main-frame status are checked on every callback.
- Bridge session is bound to the WebView/document generation; a fresh handshake is required after navigation or renderer/lifecycle loss.
- No capability is available before READY; native capabilities are statically registered and individually authorized.
- If WebMessageListener is unavailable, native capabilities fail closed. The app may continue as a web-backed app without native capabilities.
- Capacitor migration, unrestricted JavaScript interfaces, reflection/plugin discovery, arbitrary intents, arbitrary filesystem paths and broad permission exposure are excluded by the A1/A2 contract.

The A2 addendum specifies exact-origin validation, CSP, a 30-second single-use handshake challenge, cancellation/idempotency semantics, strict JSON resource bounds, rate limits, just-in-time Android permission checks, Keystore-backed secure storage, BiometricPrompt policy, lifecycle-bound events and negative-test coverage BR-001 through BR-026.

### 6.3 Capacitor branch conflict and extraction plan

PRs #4, #5 and #15 are a separate Capacitor implementation chain:
- PR #4 introduces Capacitor 6.2.1 and a frontend-only debug APK.
- PR #5 adds touch navigation and API-origin diagnostics.
- PR #15 centralizes API calls through `frontend/src/api.ts`, requires HTTPS for non-local API origins, sends credentialed requests, exposes the non-secret booking CSRF token in the verification response, and adds emulator install/launch smoke.

PR #15's successful emulator run #42764549178 installed/launched package `com.maalenex.app` on Android API 30 x86_64. However, `VITE_API_BASE_URL` was empty, so this was shell/emulator smoke only; no real backend authentication, booking or CSRF journey was tested.

The native shell in PR #14 uses Gradle namespace/applicationId `com.maalenex.moto`. The Capacitor branch uses `com.maalenex.app`. This is a package-ID conflict that must be resolved before A3 Android integration or a signed release.

**Recommended A3 extraction:**
1. Keep the native WebView architecture as the canonical implementation.
2. Port PR #15's validated API-origin client, credentialed fetch and CSRF handling into the native WebView frontend.
3. Adapt the emulator acceptance script to install the native Gradle APK rather than a Capacitor-generated APK.
4. Retain the successful emulator evidence as historical evidence for the Capacitor shell only; do not treat it as acceptance of the native shell.
5. Freeze one package ID before the first signed release. Recommendation: `com.maalenex.app`, with namespace, Kotlin package, manifest, tests and workflow updated consistently. No signed production release is evidenced, so this is the appropriate time to remove the legacy Moto identifier. This recommendation is not yet implemented.
6. Implement the A1/A2 WebMessageListener bridge only under its separately gated A3 scope. No bridge or native plugin is claimed complete.

PR #14 also changes portal workspaces, map previews/provider interfaces, payment/fare specifications, role/page matrices and broader frontend styling. These are not all Android-shell changes. Split them into independently reviewable feature/documentation PRs rather than treating all 64 changed files as one Android merge.

---

## 7. Final PR-by-PR integration register

The SHAs below are the exact source and target/base SHAs returned by GitHub PR metadata at the time of this audit. For stacked PRs, the target is a feature branch, not main. The recommended integration target is described in the final column.

| PR | Source HEAD SHA | Current target/base SHA | State | Final disposition |
|---:|---|---|---|---|
| #1 | `7e71bd98752fa22f62e32f0f52737db89e7828c2` | main `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | Open, draft | Correct 13 deletions, preserve main workflows, rerun exact-head G1 CI, then integrate G1 first. Do not merge current head as-is. |
| #2 | `3bf77bdbf6d017331a5ec2ea64e2a36577f9c8b6` | main `72550a2e464f6517653580bb1ae4e7608f211f39` | Open | Rebase/update to current main; reconcile legacy MaaleNex Moto/ticketing language with canonical identity and current reservation-only implementation. Preserve approved product decisions. |
| #3 | `0a01631a21a823b720337d1d80aa690e5df347bc` | G1 `50e38a94011eb24d06812acace7d09e4d8e81dc8` | Open, draft; mergeable=false | Synchronize with corrected G1 head; rerun integrated backend/PostgreSQL/frontend checks; then target main after G1 lands. |
| #4 | `24a5e3af527e7e306e29e4c613f36e08722ff50c` | Passenger `0a01631a21a823b720337d1d80aa690e5df347bc` | Open, draft | Do not merge Capacitor architecture. Retain APK build evidence as historical; extract only useful, non-conflicting assets/workflow pieces if needed. |
| #5 | `563bd5c9eba6e69c1de08a29f00b113679c19cc5` | Android debug `24a5e3af527e7e306e29e4c613f36e08722ff50c` | Open, draft | Superseded by #15 for emulator acceptance; do not merge as a separate Capacitor layer. Preserve any unique UX/API-origin diagnostics after review. |
| #6 | `22813a4510d42d4295602075abaebabc7a83369e` | Passenger `0a01631a21a823b720337d1d80aa690e5df347bc` | Open, draft | Preserve owner-approved A1 v1.1 and synthetic catalog workflow/seed. Integrate once Passenger/G1 baseline is synchronized. |
| #7 | `276fbb6d02d47421466199d477a4fe770c1f117e` | main `72550a2e464f6517653580bb1ae4e7608f211f39` | Open, draft | Preserve as authoritative Owner-approved platform implementation guideline; update against current main and A1 v1.1. |
| #8 | `59045e7238fa0c2050ea2f0518eb32024d6013a4` | main `72550a2e464f6517653580bb1ae4e7608f211f39` | Open, draft | Historical A2 report is stale; supersede with this final A2 closure document after review/merge. |
| #9 | `456e181ffda82403dc6cc9a245f66d47f9a947f4` | Passenger `0a01631a21a823b720337d1d80aa690e5df347bc` | Open, draft | Already included in A4 reconciliation; do not merge independently. Preserve through consolidated A4/A3 candidate. |
| #10 | `0181d48cf27ad3d566cb5a76c7372f12bd199fa7` | Shared platform `94a4ab968ee09f3c7dccf3d2665fc25f5fa160dd` | Open, draft | Stale stacked base; already included in A4 reconciliation. Do not merge separately. Keep email E2E manual-only; live SMTP E2E not evidenced. |
| #11 | `904d9a570b9bdf1867e9597f132a6b6a440794f6` | A5 readiness `4a88653b1caef2c594587e24c67f004967b9bc10` | Open, draft | Keep isolated in A5. F-04 production-edge acceptance remains operationally pending. No main merge. |
| #12 | `c64191b50d0ff4424bea1203f683075df9798bfd` | A5 security `683aa18b46a7ddd59265c5931403f1ece5ab78b3` | Merged to A5 branch | Preserve A5 branch history. Merge commit `dc8462d7d4fedba91292eeb53a2bf9d56241ccd4`; not a main merge. |
| #13 | `f06443685688b5b7f017b3868fa108a95b1387f6` | A5 security `38be5af657f26335209bf908e3765a6b2e27c67a` | Merged to A5 branch | Preserve provider-neutral deployment specification and synthetic edge harness. Merge commit `0698dcbe19f71fdaac4793e248ae34f7237f8efa`; not a main merge. |
| #14 | `8d422a7ff14978f6e9733f0213c712e8f9d16703` | main `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | Open, draft | Split native Android shell/A1-A2/brand assets from portal, maps, payment and broad UI changes. Keep native WebView architecture; resolve package ID before A3. |
| #15 | `56673921d966c505e2cf43fcee5b4d8786237f11` | Android acceptance `563bd5c9eba6e69c1de08a29f00b113679c19cc5` | Open, draft | Do not merge Capacitor implementation. Port API client/CSRF/HTTPS validation and adapt emulator acceptance to native shell. |
| #16 | `53814ad9f8883a62cc6e0599a7fa07078ff401d1` | main `7d0e1ffd99bfd3134de50bb4dc5d2e322b202ca9` | Merged to main | Already merged by main commit `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9`. Both changed-file blob SHAs match main; no re-merge. Retire source branch after final content check. |
| #17 | `9f4683455faddadd9107e0bf34dd6052f1aa54a6` | Location `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611` | Open, draft | Preserve as repaired location/Move descendant; integrate after G1 synchronization and A4 consolidation, then target main. |
| #18 | `67e6c49a5cd925b43db3356b063be53069f73df5` | main `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | Open, draft | Preserve documentation-only canonical MaaleNex identity correction; merge after review and synchronize dependent documents. |

### PR state interpretation

- PR #12 and #13 are merged only into the A5 security branch, not main.
- PR #16 is merged into main; its merge commit is the current main head.
- A PR marked `mergeable=true` is not necessarily safe to merge. PR #1 demonstrates why file-level deletion review is mandatory.
- Stacked PRs #3, #4, #5, #6, #9, #10, #15 and #17 must be integrated through their actual dependency graph, not treated as independent mainline PRs.

---

## 8. Proposed integration order and exact target baselines

This is the recommended A3 integration plan. It is not an instruction to merge now.

### Stage A — G1 preservation and integration

- Source: G1 `7e71bd98752fa22f62e32f0f52737db89e7828c2`.
- Target baseline: current main `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9`.
- First restore/preserve the 13 deleted files or explicitly approve their retirement individually.
- Verify G1 runtime restrictions, local PostgreSQL guard, empty Alembic baseline, health/OpenAPI and frontend shell.
- Run backend/PostgreSQL, migration, frontend/typecheck/build gates on the corrected exact head.
- Only after review should the corrected G1 increment be merged to main.

### Stage B — Passenger MVP synchronization

- Source starting head: `0a01631a21a823b720337d1d80aa690e5df347bc`.
- Historical base: `50e38a94011eb24d06812acace7d09e4d8e81dc8`.
- Synchronize the corrected G1/main history into Passenger. Resolve model/config/migration/workflow conflicts.
- Preserve migration revisions 0002–0007 and the A4 remediations.
- Run full PostgreSQL upgrade, metadata parity, downgrade/re-upgrade, concurrency, backend and frontend tests.
- Do not rely on the old PR #3 mergeable flag; obtain a new exact-head result.

### Stage C — A1 v1.1 and synthetic catalog

- Source: PR #6 `22813a4510d42d4295602075abaebabc7a83369e`.
- Target baseline: synchronized Passenger branch after Stage B.
- Preserve the eight-service A1 v1.1 frozen scope and deterministic synthetic catalog.
- Preserve PR #7's Owner-approved implementation guideline.
- Do not promote the superseded biker-first A1 v1.0 draft.

### Stage D — Shared platform, email and A4

- Use the reconciled A4 history containing PR #9 head `456e181...` and PR #10 head `0181d48...`.
- Reconcile A4 with corrected G1 and synchronized Passenger.
- Preserve migrations 0008–0012, identity/session lifecycle, service roles, SMTP adapter, resend controls and synthetic E2E workflow.
- Carry A4 evidence-only commits `3745dc9...` and `b14151c...`.
- Re-run A4 verification after the G1 synchronization. The prior A4 success is not a substitute for a newly integrated exact-head run.

### Stage E — Location and Move

- Source: PR #17 `9f4683455faddadd9107e0bf34dd6052f1aa54a6`.
- Parent: location foundation `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611`.
- Preserve migration chain 0013 → 0014 → 0015 and the 54-test exact-head verification.
- Run the complete integrated suite after adding this descendant to the synchronized A4 candidate.

### Stage F — Android and documentation

- Android: split PR #14 into native shell/A1-A2/brand, portal/UI, maps and payment documentation units.
- Extract PR #15 API-origin/CSRF client and emulator evidence; adapt to native WebView.
- Merge PR #18 canonical identity correction and update PR #2 product documents.
- Merge PR #7 approved guideline and PR #6 A1 v1.1/catalog after current-main synchronization.
- Replace PR #8's stale A2 report with this current closure record.

### Stage G — A4 integrated acceptance

Required integrated evidence:
- G1 and all migrations upgrade from empty PostgreSQL and downgrade/re-upgrade cleanly.
- Backend unit/integration and concurrency suites pass.
- Frontend tests, typecheck and production build pass.
- Synthetic seed scripts are idempotent.
- Android native Gradle build, navigation policy tests, CSP verification and emulator startup/DOM checks pass on the selected canonical package ID.
- HTTPS API-origin, cookie/CORS/CSRF and booking journey are tested against an approved non-production API before claiming server-backed Android acceptance.
- Independent security, WCAG 2.2 AA and physical-device acceptance remain separate evidence gates.

A5 deployment/security acceptance remains separate. No production activation is implied by this A2 record.

---

## 9. Branch cleanup register

No branch is deleted by this A2 work. The table states the earliest safe disposition after its unique work has been preserved and merged/reconciled.

| Branch | Cleanup disposition |
|---|---|
| `main` | RETAIN permanently; authoritative source of truth. |
| `feat/g1-foundation-completion` | RETAIN until corrected PR #1 is integrated and exact-head verification passes. |
| `feat/a3-passenger-mvp` | RETAIN until synchronized Passenger MVP is integrated. |
| `feat/a3-maalenex-shared-platform-foundation` | RETAIN until its work is preserved through the reconciled A4 candidate and integrated. |
| `feat/a3-synthetic-email-e2e-test` | RETAIN until A4 integration and manual-only email test policy are preserved; then retire. |
| `a4/full-verification-remediation` | RETAIN until its two latest evidence commits are carried into the final integrated report; then retire. |
| `docs/maalenex-platform-restructure-guideline` | RETIRE after synthetic catalog work is preserved by PR #6 and its draft guideline is superseded by approved PR #7. |
| `feat/biker-first-platform-a1-test-catalog` | RETAIN until A1 v1.1 and synthetic catalog are integrated; then retire. |
| `docs/maalenex-platform-guideline` | RETAIN until Owner-approved guideline PR #7 is integrated; then retire. |
| `docs/a2-maalenex-platform-reconciliation` | SUPERSEDE after this final A2 closure document is reviewed and merged; then retire. |
| `docs/product-scope-roadmap-v1` | RETAIN until its approved product decisions are reconciled with current identity and service boundaries; then retire. |
| `feat/a3-location-consent-foundation` | RETAIN until PR #17's repaired descendant is integrated; then retire. |
| `fix/critical-location-consent-ci` | RETAIN as the location/Move repaired source until integrated and verified; then retire. |
| `feat/android-debug-apk` | RETAIN only until any reusable assets/build evidence are extracted; do not merge Capacitor architecture. |
| `fix/android-device-acceptance` | RETAIN only until unique navigation/API diagnostics are reviewed and preserved; then retire. |
| `fix/android-device-acceptance-emulator` | RETAIN until API client/CSRF and emulator acceptance evidence are ported to native shell; then retire. |
| `feat/maalenex-brand-identity` | RETAIN until native shell, architecture docs and brand assets are split into accepted PRs; then retire. |
| `fix/canonical-maalenex-product-identity` | RETAIN until PR #18 is integrated; then retire. |
| `a5/deployment-readiness-assessment` | RETAIN separately for A5; do not merge into main as part of A3/A4 consolidation. |
| `a5/a5-3-4-edge-security-hardening` | RETAIN separately for A5; operational acceptance remains pending. |
| `a5/a5-3-6-provider-neutral-deployment-spec` | RETAIN until its merged content is confirmed in the A5 security branch; then retire within A5 only. |
| `infra/cloudflare-pages-direct-upload` | PR #16 is merged. Both changed-file blob SHAs match main; branch is cleanup-ready after final branch-tree equivalence check. |

---

## 10. Remaining recorded gaps and final A2 closure

| Item | Status |
|---|---|
| Exact 22-branch inventory and HEADs | PASS |
| PR #1–#18 source/base SHA register | PASS |
| G1 ↔ Passenger commit graph and file-diff review | PASS |
| G1 deletion conflict | BLOCKER for PR #1 merge; recorded |
| PR #9/#10 shared-platform/E2E ancestry | VERIFIED in A4 branch |
| Three unassociated branch histories/content | INSPECTED |
| Location/Move migration and PR #17 dependency | VERIFIED |
| Android A1/A2 architecture selection | VERIFIED-CLOSED by existing Owner-approved architecture record |
| Android package ID `.moto` vs `.app` | OPEN decision for A3 |
| A4 current documentation tip exact-head CI | NOT RUN after two docs-only commits |
| Physical Android device acceptance | NOT RUN |
| Android HTTPS API/auth/booking/CSRF end-to-end | NOT RUN |
| Live SMTP connectivity/E2E email delivery | NOT RUN |
| Independent penetration test | NOT RUN |
| Independent WCAG 2.2 AA audit | NOT RUN |
| Production TLS/edge/origin-isolation acceptance | NOT RUN |
| Production deployment/activation | NOT AUTHORIZED by this document |

### Final A2 determination

**A2 VERIFIED-CLOSED WITH RECORDED GAPS.**

The repository baseline, exact branch/PR dependencies, unique branch work, canonical Android architecture and ordered integration/cleanup register have been reconciled. The remaining gaps are explicit A3/A4 integration and acceptance tasks, not unknown branch ownership or undocumented dependencies.

This closure document does not merge PRs, alter application code, delete branches, run SMTP sends, change secrets, deploy, or activate commercial services. `main` remains at `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` as of the audit snapshot.
