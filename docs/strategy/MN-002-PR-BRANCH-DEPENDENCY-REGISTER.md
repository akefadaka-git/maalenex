# MaaleNex MN-002 — Pull Request and Branch Dependency Register

**Record ID:** MN-002  
**Prepared:** 2026-11-26  
**Status:** READ-ONLY RECONCILIATION — PARTIAL, MATERIAL BLOCKERS RECORDED  
**Canonical repository:** `akefadaka-git/maalenex`  
**Main snapshot:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Method:** GitHub PR metadata, branch ancestry comparisons, exact PR base/head comparisons, changed-file inventories, selected source-file reads and exact-commit workflow-run lookups.  
**Mutations:** Documentation-only record on the existing PR #57 branch. No application source, migration, workflow, secret, provider, main branch, merge or deployment was changed.

## 1. Executive determination

The repository contains **57 pull requests** and multiple independently developed implementation tracks. The PR history is not one linear sequence and must not be integrated by merge order alone.

The current main snapshot is `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`. PR #1 and PR #3 are merged into main history. Most later work remains open/unmerged or is closed without merge. Several PRs are stacked on old branches; some child PR bases are behind their stated parent branch tips. Several branches have no corresponding PR targeting main.

The principal integration tracks are:

1. Historical G1/passenger foundation and its merged synchronization chain.
2. A3 shared platform identity/tenancy foundation and a separate Move/location-consent branch.
3. Passenger-only preview and a broad passenger/runtime chain.
4. Passenger Android/runtime siblings PR #42 and #43, with PR #44 and Cargo #45–#52 stacked from #43.
5. Independent MITP tracking PR #53.
6. A separate A3 canonical PostGIS integration branch and A4 evidence branches, not represented by a PR against main.
7. Independent documentation, brand, A5 security, and production-readiness work.

**Disposition:** MN-002 is **PARTIAL**. Exact PR refs and major branch dependencies are captured below. Migration graph, code-level overlap and CI evidence are not yet sufficient to recommend integration or close A2. No PR is approved for merge by this register.

## 2. Current main and historical baselines

| Reference | Exact SHA | Meaning |
|---|---|---|
| Current main | `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | Current repository snapshot used by PR #54, #55 and #57 |
| Earlier main snapshot | `78884c0f2609edbfc94a24e42d84824bff9eed20` | Base used by PR #24–#26 and several passenger-only branches |
| Earlier main snapshot | `72550a2e464f6517653580bb1ae4e7608f211f39` | Base used by historical product docs PR #2, #7 and #8 |
| Earlier main snapshot | `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | Base used by brand/identity and A2 report PRs #14, #18 and #19 |
| Earlier main snapshot | `1daf201bfb407280604534e28440b9fa83178efb` | Base of MITP PR #53; one commit behind current main |
| Earlier main snapshot | `25b1d66d3d565bf2462a37f4cc6d5f0c4536292e` | Base of merged main CI PR #23 |

Do not infer that an open PR's base is current main merely because its base branch is named `main`; use its exact recorded base SHA. Do not infer integration from an open PR's mergeable metadata.

## 3. Dependency graph — major tracks

### 3.1 Historical G1 and passenger foundation

```text
main (d7edb1e)
  └─ PR #1 G1 foundation (c1f74c1) — MERGED
       └─ main merge commit ac0e05f
            └─ PR #3 Passenger MVP (70a8608) — MERGED
                 ├─ PR #20 G1 synchronization (c1f74c1) — MERGED into passenger branch
                 ├─ PR #21 G1 integration candidate (933f307) — MERGED into passenger branch
                 └─ PR #22 passenger UX resilience (a6036d1) — MERGED into passenger branch
                      └─ PR #3 merge commit 25b1d66
                           └─ PR #23 main CI verification (a918fc5) — MERGED
                                └─ main snapshot 78884c0
```

PR #1 and PR #3 are merged; they are not pending integration. PR #20–#22 are also merged into the historical passenger chain. Their old PR base/head references should not be reused as current integration targets.

### 3.2 Shared platform identity and Move/location branch

```text
PR #3 historical passenger branch (base 0a01631)
  └─ PR #9 shared platform foundation (bfa9993) — OPEN/DRAFT
       └─ PR #10 synthetic email E2E (7848fa0) — OPEN/DRAFT
          [PR #10 base 94a4ab9 is 8 commits behind PR #9 head bfa9993]

Separate branch: feat/a3-location-consent-foundation
  └─ PR #17 Move/location-consent repair (51193cc) — OPEN/DRAFT
```

PR #9 adds service registry, service-scoped roles, general account identity/trust and related migrations. Its revision `0008_platform_service_registry` descends from `0007_operator_invites_support`. PR #17's parent branch contains a platform/identity/location/Move implementation stream, but the branch base is **diverged** from PR #9's head (51 commits on one side and 1 on the other from merge base `456e181...`). Do not treat PR #17 as a clean child of the latest PR #9 head.

The branch `a4/full-verification-remediation` also contains the PR #9 platform/identity code and its A4 verification plan, but is divergent from current main: 109 commits ahead and 71 behind, with merge base `0a01631...`. No PR with that branch as head was found in the repository PR search.

### 3.3 A5 security/deployment-readiness branch — preserve separately

```text
a5/deployment-readiness-assessment
  └─ PR #11 edge security hardening — OPEN/DRAFT
       ├─ PR #12 synchronization — MERGED into PR #11 branch
       └─ PR #13 provider-neutral deployment spec — MERGED into PR #11 branch
```

This branch is divergent from current main (144 commits ahead, 71 behind; merge base `0a01631...`). PR #12 and #13 are merged only into the PR #11 branch, not into main. This work includes A5-labelled security/deployment specifications and workflows. It is not authorization to perform A5 deployment. Preserve it for separate governance review; do not merge, dispatch, expose services or deploy under MN-002.

### 3.4 Brand, passenger-only preview and full-platform UI stream

```text
PR #14 brand / Android / maps / portal artifacts — OPEN/DRAFT
  └─ PR #15 emulator-backed acceptance — OPEN/DRAFT
     (PR #15 base is one commit behind PR #5 head; not a clean child of its latest tip)

PR #25 passenger-only guest preview — OPEN/DRAFT
  ├─ PR #27 keyboard/focus A4 assurance — OPEN/DRAFT
  │  (base is 6 commits behind PR #25 head)
  ├─ PR #28 initial UI draft — CLOSED, NOT MERGED; superseded
  ├─ PR #29 stacked full-platform draft — CLOSED, NOT MERGED; superseded
  └─ PR #30 full-platform clean candidate — OPEN/DRAFT
       └─ PR #31 mobile acceptance remediation — OPEN/DRAFT
            └─ PR #32 passenger identity — OPEN/DRAFT
                 └─ PR #33 journey search — OPEN/DRAFT
                      └─ PR #34 booking flow — OPEN/DRAFT
                           └─ PR #35 support — OPEN/DRAFT
                                └─ PR #36 reports/complaints — OPEN/DRAFT
                                     └─ PR #37 wallet — OPEN/DRAFT
                                          └─ PR #38 notifications — OPEN/DRAFT
                                               └─ PR #39 My Bookings/hold expiry — OPEN/DRAFT
                                                    └─ PR #40 scheduler/operations/RBAC — OPEN/DRAFT
                                                         └─ PR #41 password policy — OPEN/DRAFT
                                                              ├─ PR #42 Android API foundation — OPEN/DRAFT
                                                              └─ PR #43 Android/backend runtime + passenger map — OPEN/DRAFT
                                                                   └─ PR #44 IROKA contract — OPEN/DRAFT
                                                                        └─ PR #45 Cargo consignment — OPEN/DRAFT
                                                                             └─ PR #46 Cargo dispatch/tracking — OPEN/DRAFT
                                                                                  └─ PR #47 carrier operations/proof — OPEN/DRAFT
                                                                                       └─ PR #48 private evidence storage — OPEN/DRAFT
                                                                                            └─ PR #49 evidence lifecycle — OPEN/DRAFT
                                                                                                 ├─ PR #50 retention branch — OPEN/DRAFT
                                                                                                 └─ PR #51 retention remediation — OPEN
                                                                                                      └─ PR #52 D01–D14/C06 review package — OPEN/DRAFT
```

Important exact-base qualifications:
- PR #4's base is the older passenger branch SHA `0a01631...`; PR #5's base `24a5e3a...` is one commit behind PR #4's current head `b9e2359...`.
- PR #15's base `563bd5c...` is one commit behind PR #5's current head `2eb38d5...`.
- PR #10's base is eight commits behind PR #9's current head.
- PR #27's base `d4bf907...` is six commits behind PR #25's current head `bab7aa9...`.
- PR #28's base `8ce41b7...` is one commit behind PR #25's current head and is closed/unmerged.
- PR #29 is closed/unmerged; PR #30 is the open clean candidate. Do not resurrect PR #28 or #29 as integration candidates.
- PR #42 and #43 are siblings from the exact same PR #41 base SHA `5640e906...`. PR #43 does not include PR #42's commits.

### 3.5 MITP and canonical GIS integration

```text
main historical snapshot 1daf201
  └─ PR #53 MITP synthetic tracking / map PoC — OPEN/DRAFT
       └─ imported into A3 canonical GIS integration branch

PR #43 passenger map / route geometry / Koybe boarding point
       └─ imported into A3 canonical GIS integration branch

feat/a3-canonical-postgis-integration
  └─ A4 current-readiness evidence branch
       └─ A4-01 production DB identity evidence branch
            └─ PR #56 free pilot provider onboarding document
```

The branch `feat/a3-canonical-postgis-integration` is 196 commits ahead of current main with 69 changed files and merge base exactly current main SHA `c988b9d...`. It has no PR targeting main in the repository PR search. It contains the passenger/MITP migration merge and canonical PostGIS/Martin work.

The A4 branch sequence is documented by branch ancestry comparisons:
- `a4/current-readiness-evidence-2026-11-26` is 4 commits / 1 document ahead of `feat/a3-canonical-postgis-integration`.
- `a4/01-production-db-identity-evidence` is the parent of PR #56 and is 203 commits ahead of current main.
- `a4/free-pilot-provider-onboarding` is 3 commits / 1 document ahead of its declared A4-01 base; PR #56 changes only `docs/operations/FREE-PILOT-PROVIDER-ONBOARDING-A4.md` relative to that base.
- The current-readiness branch and free-pilot branch comparison shows the latter 6 commits / 3 documents ahead of the former.

Thus PR #56 is a one-file A4 documentation increment **on top of a large unmerged A3/A4 integration branch**. It is not a standalone one-file change against current main. The parent integration branch and A4 evidence branches have no corresponding PR to main in the search results.

Separate branch `a4/full-verification-remediation` is another divergent A3/A4 implementation stream; it contains the PR #9 identity/tenancy branch and is not the same as the canonical PostGIS branch.

## 4. PR inventory — exact refs and current state

The table records the PR base/head SHAs returned by GitHub at the time of this assessment. SHAs are full 40-character values. “Merged” means the PR itself is merged; it does not mean a child branch or an entire service line is production-ready.

| PR | State | Base branch / SHA | Head branch / SHA | Notes |
|---:|---|---|---|---|
| #1 | CLOSED / MERGED | `main` / `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | `feat/g1-foundation-completion` / `c1f74c1e2ac81080f356d2a11bce8453a7beea38` | G1 foundation; merge `ac0e05fba50e375a106ca3eaa33d66aee700fb2b` |
| #2 | OPEN | `main` / `72550a2e464f6517653580bb1ae4e7608f211f39` | `docs/product-scope-roadmap-v1` / `d913080aa643f493ef4c4ea6ed753acdad5a117e` | Historical product docs |
| #3 | CLOSED / MERGED | `main` / `ac0e05fba50e375a106ca3eaa33d66aee700fb2b` | `feat/a3-passenger-mvp` / `70a86089d16acfa5a4476b813a6f215c4e3dfaf7` | Passenger MVP; merge `25b1d66d3d565bf2462a37f4cc6d5f0c4536292e` |
| #4 | OPEN / DRAFT | `feat/a3-passenger-mvp` / `0a01631a21a823b720337d1d80aa690e5df347bc` | `feat/android-debug-apk` / `b9e235999d8e21772893cd3e8022218c97b3029c` | Child base is historical |
| #5 | OPEN / DRAFT | `feat/android-debug-apk` / `24a5e3af527e7e306e29e4c613f36e08722ff50c` | `fix/android-device-acceptance` / `2eb38d57979e3c8fa883a567ca72d21e44ef77c9` | Base one commit behind #4 head |
| #6 | OPEN / DRAFT | `feat/a3-passenger-mvp` / `0a01631a21a823b720337d1d80aa690e5df347bc` | `feat/biker-first-platform-a1-test-catalog` / `ba2f70ea578ea0c92875dc0ee6d2aed951a39821` | A1 v1.1 source + synthetic catalog |
| #7 | OPEN / DRAFT | `main` / `72550a2e464f6517653580bb1ae4e7608f211f39` | `docs/maalenex-platform-guideline` / `d4efd866358abcc50760bd234ffbf911ba19aa19` | Platform guideline |
| #8 | OPEN / DRAFT | `main` / `72550a2e464f6517653580bb1ae4e7608f211f39` | `docs/a2-maalenex-platform-reconciliation` / `13c7e60df0712a11269c29a6884d33cb62aeecb0` | Historical A2 closure report |
| #9 | OPEN / DRAFT | `feat/a3-passenger-mvp` / `0a01631a21a823b720337d1d80aa690e5df347bc` | `feat/a3-maalenex-shared-platform-foundation` / `bfa99939f220502d1d680f29044bc59aff602af2` | Shared identity/platform foundation |
| #10 | OPEN / DRAFT | `feat/a3-maalenex-shared-platform-foundation` / `94a4ab968ee09f3c7dccf3d2665fc25f5fa160dd` | `feat/a3-synthetic-email-e2e-test` / `7848fa0ff06ead91705648dafed674976ca49ee6` | Base 8 commits behind #9 head |
| #11 | OPEN / DRAFT | `a5/deployment-readiness-assessment` / `4a88653b1caef2c594587e24c67f004967b9bc10` | `a5/a5-3-4-edge-security-hardening` / `3c9d407f0d441ca9b7a8243afc16c90867e07673` | A5 security stream; no deployment |
| #12 | CLOSED / MERGED | `a5/a5-3-4-edge-security-hardening` / `683aa18b46a7ddd59265c5931403f1ece5ab78b3` | `a5/deployment-readiness-assessment` / `c64191b50d0ff4424bea1203f683075df9798bfd` | Merged into #11 branch; merge `dc8462d7d4fedba91292eeb53a2bf9d56241ccd4` |
| #13 | CLOSED / MERGED | `a5/a5-3-4-edge-security-hardening` / `38be5af657f26335209bf908e3765a6b2e27c67a` | `a5/a5-3-6-provider-neutral-deployment-spec` / `f06443685688b5b7f017b3868fa108a95b1387f6` | Merged into #11 branch; merge `0698dcbe19f71fdaac4793e248ae34f7237f8efa` |
| #14 | OPEN / DRAFT | `main` / `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | `feat/maalenex-brand-identity` / `adf02dc2ad9ee578bdb6dba5226e63e328b9c361` | Brand, Android, portal and maps docs/UI |
| #15 | OPEN / DRAFT | `fix/android-device-acceptance` / `563bd5c9eba6e69c1de08a29f00b113679c19cc5` | `fix/android-device-acceptance-emulator` / `71a6937f049f4367caf54e2a68f31db5255f4e3a` | Base one commit behind #5 head |
| #16 | CLOSED / MERGED | `main` / `7d0e1ffd99bfd3134de50bb4dc5d2e322b202ca9` | `infra/cloudflare-pages-direct-upload` / `53814ad9f8883a62cc6e0599a7fa07078ff401d1` | Guarded Cloudflare workflow; merge `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` |
| #17 | OPEN / DRAFT | `feat/a3-location-consent-foundation` / `f5fd9a0c0a894b1dc5810e61eb23d21b44c2b611` | `fix/critical-location-consent-ci` / `51193cc7635853f9da3da0de1ba34eb12771185e` | Move/location stream; parent branch diverged from #9 |
| #18 | OPEN / DRAFT | `main` / `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | `fix/canonical-maalenex-product-identity` / `67e6c49a5cd925b43db3356b063be53069f73df5` | README identity correction |
| #19 | OPEN / DRAFT | `main` / `d7edb1eb3ab8d7f0784a7c9eba598c4ce36f79f9` | `docs/a2-final-repository-reconciliation` / `9138b3942b46cb65ae3ea7a460a0839d128ae205` | Historical A2 report |
| #20 | CLOSED / MERGED | `feat/a3-passenger-mvp` / `0a01631a21a823b720337d1d80aa690e5df347bc` | `feat/g1-foundation-completion` / `c1f74c1e2ac81080f356d2a11bce8453a7beea38` | G1 sync into passenger branch; merge `94d22da7b2c90659e692585b901a466b043b8031` |
| #21 | CLOSED / MERGED | `feat/a3-passenger-mvp` / `0a01631a21a823b720337d1d80aa690e5df347bc` | `integration/passenger-g1-sync-candidate` / `933f307beb6ba7d70e8d6f21a56500e4461f3d06` | Integration candidate; merge `8e40cb9c31b5758f4480b64188db15fc9b56bd7d` |
| #22 | CLOSED / MERGED | `feat/a3-passenger-mvp` / `8e40cb9c31b5758f4480b64188db15fc9b56bd7d` | `feat/passenger-ux-resilience` / `a6036d1900c2584969882fa8423374ea57fb64bb` | Passenger UX resilience; merge `70a86089d16acfa5a4476b813a6f215c4e3dfaf7` |
| #23 | CLOSED / MERGED | `main` / `25b1d66d3d565bf2462a37f4cc6d5f0c4536292e` | `ci/main-branch-verification` / `a918fc549734ac232b0f7777197067061e1520f6` | Main push verification; merge `78884c0f2609edbfc94a24e42d84824bff9eed20` |
| #24 | OPEN / DRAFT | `main` / `78884c0f2609edbfc94a24e42d84824bff9eed20` | `docs/a1-owner-approved-closure` / `9cad97251576beac3394c8276281ebc0f3b08489` | Passenger-first A1 closure record |
| #25 | OPEN / DRAFT | `main` / `78884c0f2609edbfc94a24e42d84824bff9eed20` | `feat/a3-passenger-only-integration` / `bab7aa9f6eb202a58415e54ad0c6aae67a995a66` | Passenger-only preview / Android integration |
| #26 | OPEN / DRAFT | `main` / `78884c0f2609edbfc94a24e42d84824bff9eed20` | `docs/a1-expanded-product-scope-amendment` / `9b447fe6b7090ac11d0e65b2302fff9991f710e5` | Expanded scope proposal; its own status is pending Owner approval |
| #27 | OPEN / DRAFT | `feat/a3-passenger-only-integration` / `d4bf907556430b6aab5d886ee381a06d7ec64d18` | `a4/passenger-keyboard-assurance` / `79adb87a8845373d3481db15034e9e74d6b77c2d` | Base 6 commits behind #25 head |
| #28 | CLOSED / NOT MERGED | `feat/a3-passenger-only-integration` / `8ce41b7c06830cc7138b5de2b08af08e67526c71` | `feat/maalenex-nexus-welcome-iroka-ui` / `7cd39a95627848ebfa2e192b9ccf5f032a5331c2` | Superseded UI draft |
| #29 | CLOSED / NOT MERGED | `feat/a3-passenger-only-integration` / `bab7aa9f6eb202a58415e54ad0c6aae67a995a66` | `feat/full-platform-experience` / `84a43b4b1bcdd5b99f6dcbf8bb3a849ef85a582e` | Superseded stacked implementation draft |
| #30 | OPEN / DRAFT | `feat/a3-passenger-only-integration` / `bab7aa9f6eb202a58415e54ad0c6aae67a995a66` | `feat/full-platform-clean` / `ec5f8060855869c7eba8905e87216d5c8ada93b9` | Full platform clean candidate |
| #31 | OPEN / DRAFT | `feat/full-platform-clean` / `ec5f8060855869c7eba8905e87216d5c8ada93b9` | `feat/acceptance-remediation` / `9ece201039df2ad2426637e0f8aa93310baa6b00` | Acceptance remediation |
| #32 | OPEN / DRAFT | `feat/acceptance-remediation` / `9ece201039df2ad2426637e0f8aa93310baa6b00` | `feat/passenger-identity-service` / `83bb469057a8246f0a330430573646377d5b11f1` | Passenger identity |
| #33 | OPEN / DRAFT | `feat/passenger-identity-service` / `83bb469057a8246f0a330430573646377d5b11f1` | `feat/passenger-journey-search` / `d457ba117780a92207ea3c55e45b430f157ffc27` | Journey search |
| #34 | OPEN / DRAFT | `feat/passenger-journey-search` / `d457ba117780a92207ea3c55e45b430f157ffc27` | `feat/passenger-booking-flow` / `58d82cb072864c7ba1fe84b15a9bdc88f665b997` | Booking |
| #35 | OPEN / DRAFT | `feat/passenger-booking-flow` / `58d82cb072864c7ba1fe84b15a9bdc88f665b997` | `feat/passenger-support-service` / `42527e41445ba11f3e3f0d5062c72f3ec538327b` | Support |
| #36 | OPEN / DRAFT | `feat/passenger-support-service` / `42527e41445ba11f3e3f0d5062c72f3ec538327b` | `feat/passenger-reports-complaints` / `9fc6b2ea4789d29f1a3108a96bf2587ed7b68f97` | Reports/complaints |
| #37 | OPEN / DRAFT | `feat/passenger-reports-complaints` / `9fc6b2ea4789d29f1a3108a96bf2587ed7b68f97` | `feat/passenger-wallet-service` / `94d15c8af349bc5b9c3fd9e9eef4a09859e93c45` | Wallet/ledger foundation |
| #38 | OPEN / DRAFT | `feat/passenger-wallet-service` / `94d15c8af349bc5b9c3fd9e9eef4a09859e93c45` | `feat/passenger-notifications-service` / `046da5e6cb435f2c9baeb2228fc9918287bd584e` | In-app notifications |
| #39 | OPEN / DRAFT | `feat/passenger-notifications-service` / `046da5e6cb435f2c9baeb2228fc9918287bd584e` | `feat/my-bookings-hold-expiry-notifications` / `63b85d65a2c6224f17c873a9dd6afbb6025cb58b` | My Bookings/hold expiry |
| #40 | OPEN / DRAFT | `feat/my-bookings-hold-expiry-notifications` / `63b85d65a2c6224f17c873a9dd6afbb6025cb58b` | `feat/scheduler-operations-rbac-dashboards` / `65fdbe86ad2054f11c2b341643957039ae48d286` | Scheduler/operations/RBAC |
| #41 | OPEN / DRAFT | `feat/scheduler-operations-rbac-dashboards` / `65fdbe86ad2054f11c2b341643957039ae48d286` | `fix/passenger-password-minimum-six` / `5640e9067aef5c8a1cb9fada32bf5123aa693162` | Password policy |
| #42 | OPEN / DRAFT | `fix/passenger-password-minimum-six` / `5640e9067aef5c8a1cb9fada32bf5123aa693162` | `feat/passenger-backend-functional-foundation` / `d3011e288c7487ebdca824d8c4dcd998ad3cfc7b` | Android API connectivity |
| #43 | OPEN / DRAFT | `fix/passenger-password-minimum-six` / `5640e9067aef5c8a1cb9fada32bf5123aa693162` | `feat/passenger-backend-connectivity-foundation` / `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | Android/backend runtime + map |
| #44 | OPEN / DRAFT | `feat/passenger-backend-connectivity-foundation` / `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | `feat/iroka-integration-contract-v1` / `e2e997e1a6d48f8aeb041cd50339bebe4d434a60` | IROKA contract |
| #45 | OPEN / DRAFT | `feat/iroka-integration-contract-v1` / `e2e997e1a6d48f8aeb041cd50339bebe4d434a60` | `feat/cargo-consignment-backend-v1` / `c2debf278e682f850c13a9866722376548bc792f` | Cargo consignment |
| #46 | OPEN / DRAFT | `feat/cargo-consignment-backend-v1` / `c2debf278e682f850c13a9866722376548bc792f` | `feat/cargo-dispatch-tracking-v1` / `f0f221ce0ea2226c5f2fd2d8ec519c3b2e03a59b` | Cargo dispatch/tracking |
| #47 | OPEN / DRAFT | `feat/cargo-dispatch-tracking-v1` / `f0f221ce0ea2226c5f2fd2d8ec519c3b2e03a59b` | `feat/carrier-operations-delivery-proof-v1` / `7ca507c5fc6e5aec05e6039a869b170abb616990` | Carrier/proof |
| #48 | OPEN / DRAFT | `feat/carrier-operations-delivery-proof-v1` / `7ca507c5fc6e5aec05e6039a869b170abb616990` | `feat/cargo-delivery-evidence-storage-v1` / `ab89ae0b13e6b6091808ab8240a76fedd49069ea` | Evidence storage |
| #49 | OPEN / DRAFT | `feat/cargo-delivery-evidence-storage-v1` / `ab89ae0b13e6b6091808ab8240a76fedd49069ea` | `feat/cargo-evidence-lifecycle-governance-v1` / `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | Evidence lifecycle |
| #50 | OPEN / DRAFT | `feat/cargo-evidence-lifecycle-governance-v1` / `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | `fix/cargo-evidence-legal-retention-c01-c08` / `73fee61613e533bd75d1e7e85db8689ee1a4799b` | Retention variant A |
| #51 | OPEN | `feat/cargo-evidence-lifecycle-governance-v1` / `3662887098211ac9f0b6c4ee3c4eb2401529f74b` | `feat/cargo-evidence-legal-retention-remediation-v1` / `b81e788b55bb5c988d77412ce54f483106675e82` | Retention variant B; #50 sibling |
| #52 | OPEN / DRAFT | `feat/cargo-evidence-legal-retention-remediation-v1` / `b81e788b55bb5c988d77412ce54f483106675e82` | `docs/cargo-d01-d14-controlled-review-package` / `b7d025e2e23be9359e4f648b8b88c3dcb3e455e5` | Cargo compliance review docs |
| #53 | OPEN / DRAFT | `main` / `1daf201bfb407280604534e28440b9fa83178efb` | `feat/a3-mitp-tracking-foundation` / `6d6a2de592381cd751c52f40824a9da1dd17b07a` | Independent MITP tracking |
| #54 | OPEN / DRAFT | `main` / `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | `feat/priority1-passenger-about` / `34e4aab8d84561828fb0a1bc8bdce9f914bc32ca` | About/API origin/Android docs |
| #55 | OPEN / DRAFT | `main` / `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | `docs/production-readiness-a1-a2` / `0213953d474bf9a724237a853d4a8df8b04b21bc` | Current production-readiness A1/A2 docs |
| #56 | OPEN / DRAFT | `a4/01-production-db-identity-evidence` / `c2782177693975c95bf8f895f19756c5f773aa0d` | `a4/free-pilot-provider-onboarding` / `9656ae29c210cfd132eb3a7f1a2b821ad98acc39` | One doc on top of 203-commit unmerged A4 stack |
| #57 | OPEN / DRAFT | `main` / `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | `docs/enhanced-implementation-strategy-a1-v1` / `11182288951393eb35344ad99753ff58d852e973` | Strategy, A1 v1.2 proposal and MN-001 register |

## 5. Material overlap and integration blockers

### 5.1 PR #42 and PR #43 are siblings with overlapping files

Both use exact base SHA `5640e9067aef5c8a1cb9fada32bf5123aa693162`. Their exact PR diffs are:
- PR #42: 4 files, 4 commits.
- PR #43: 33 files, 50 commits.

They overlap on four paths:
- `.github/workflows/android-shell-verification.yml`
- `.github/workflows/g1-backend-verification.yml`
- `android/app/src/main/AndroidManifest.xml`
- `backend/tests/test_passenger_identity.py`

PR #42 exact-head CI:
- Android shell run [#45002401214](https://github.com/akefadaka-git/maalenex/actions/runs/45002401214) — completed success.
- Backend run [#45002401119](https://github.com/akefadaka-git/maalenex/actions/runs/45002401119) — completed success.

PR #43 exact-head PR-triggered workflow lookup returned no runs. PR #42 green runs do not prove PR #43. Before any integration, reconcile the four overlapping paths and run the required tests on the selected exact candidate SHA through an authorized normal PR workflow; do not dispatch or rerun workflows under this read-only assessment.

### 5.2 Cargo PR #50 / #51 contain a confirmed Alembic revision-ID collision

PR #50 and PR #51 are siblings from PR #49 head `3662887098211ac9f0b6c4ee3c4eb2401529f74b`.

Both files declare:
- Alembic revision ID: `0024_cargo_legal_retention`
- Parent revision: `0023_evidence_hold_review`

But the migration bodies and schemas differ:
- PR #50 file: `0024_cargo_legal_retention.py`, blob `0af064ccfcdb210066532e10221307cd3a4450a0`.
- PR #51 file: `0024_cargo_evidence_legal_retention.py`, blob `e0c5bda100293c294ce6838c79a7a20256165591`.

PR #51 then adds `0025_cargo_evidence_rights` and `0026_cargo_evidence_dpo_controls`; PR #52 is stacked on PR #51. This is a **duplicate Alembic revision identifier with divergent migration content**, not merely two filenames sharing the same numeric prefix. Do not combine PR #50 and #51. Select/reconcile one source of truth, design a controlled migration history for the chosen semantics, and test from a disposable database before any A4 closure or migration execution. No database migration was run in this assessment.

### 5.3 Multiple independent migration roots start after revision 0007

The main A2 record identifies main's migration chain through `0007_operator_invites_support`. At least these separate branches then start from that same parent:
- PR #9: `0008_platform_service_registry` → `0009_service_roles` → identity/trust/service-role migrations.
- Passenger chain in PR #30/#32–#43: `0008_wallet_double_entry_ledger` → passenger/support/wallet/notification/booking/scheduler/fleet/map revisions through `0018_koybe_boarding_point`.
- PR #53: `0008_mitp_tracking`.

These revision IDs are distinct but form multiple Alembic heads. The canonical GIS integration branch contains a graph-only merge revision `0019_merge_passenger_mitp` with parents `0018_koybe_boarding_point` and `0008_mitp_tracking`, followed by canonical PostGIS revisions `0020`–`0024`. The inspected A3.1 document explicitly says verification is pending and no database migration was executed.

That merge resolves only the passenger/MITP histories. It does not establish that PR #9's separate platform service registry/identity history, or PR #17's Move/location history, is incorporated. A complete graph inventory and model-registry comparison is still required.

### 5.4 PR #53 exact-head evidence and base freshness

PR #53 exact head `6d6a2de592381cd751c52f40824a9da1dd17b07a` has 32 changed files. Its base `1daf201bfb407280604534e28440b9fa83178efb` is one commit behind current main. Exact-head runs:
- Backend run [#45155547829](https://github.com/akefadaka-git/maalenex/actions/runs/45155547829) — success.
- Cloudflare Pages workflow [#45155547922](https://github.com/akefadaka-git/maalenex/actions/runs/45155547922) — success.
- MITP map PoC run [#45155547849](https://github.com/akefadaka-git/maalenex/actions/runs/45155547849) — success.

These are synthetic/PoC workflow results on PR #53's exact head. They do not establish production GPS, real geography, production map hosting or A4 acceptance. The PR remains open/draft/unmerged.

### 5.5 A4 integration branch is not represented by a PR to main

`feat/a3-canonical-postgis-integration` is 196 commits ahead of current main, 0 behind, 69 changed files. It contains the passenger/MITP merge and PostGIS/Martin integration work. The A4 readiness branch adds evidence documents on top. The branch `a4/01-production-db-identity-evidence` is 203 commits ahead of main; PR #56 is three commits / one document beyond that branch.

No PR with `feat/a3-canonical-postgis-integration`, `a4/current-readiness-evidence-2026-11-26`, or `a4/01-production-db-identity-evidence` as its head was returned by the repository PR search. Therefore the integrated A3/A4 work is **not currently exposed as a normal PR against main**. The A4 readiness register records:
- A4-01 production DB identity and capability membership: MISSING / UNVERIFIED.
- A4-02 production network/TLS: local loopback binding verified; production ingress/TLS NOT RUN.
- A4-03 authoritative Maale geography and licensing: MISSING / UNRESOLVED.
- A4-04 IROKA endpoint/trust/live integration: PARTIAL contract only.

A4 status remains PARTIAL / OPEN and production readiness NOT READY. The branch's green G1 run #822 applies to exact code SHA `9750d2cba123a7c2567ef5c9bce3511f9ce0382e`, not automatically to later branch tips.

### 5.6 Distinct A1/A2 documentation records must not be collapsed

The repository contains multiple documents with different scopes and baselines:
- PR #6: platform A1 Product Scope and Architecture v1.1, explicitly marked Owner-approved/frozen 2026-11-08. Source blob `f7900e619f969e62d9f12c3c78457f99def23a05`.
- PR #8: historical platform A2 closure report, tied to main SHA `72550a2...`; its PR remains open/unmerged.
- PR #24: separate Owner-approved A1 closure record dated 2026-11-15, with passenger-first initial release decisions, based on main `78884c0...`; PR remains open/unmerged.
- PR #26: expanded product scope amendment proposal dated 2026-11-15; its own document explicitly says approval pending. Do not represent it as frozen.
- Main `MAALENEX-IA-A1-SPEC-001 v1.0.0`: frozen MaaleNex–IROKA invisible-intelligence architecture at current main SHA `c988b9d...`; distinct from product-scope A1 v1.1.
- PR #55: production-readiness A1 draft and A2 partial report against current main; it explicitly supplements and does not replace the frozen MaaleNex–IROKA A1.
- PR #57: enhanced strategy and proposed platform A1 v1.2; proposal remains draft/not frozen.

The different A1 records are not interchangeable. The active product scope, passenger-first release sequencing and full eight-service target need a single explicit cross-reference/authority matrix before A1 v1.2 freeze. This is an A1 change-control question, not a reason to silently rewrite frozen source records.

## 6. Integration disposition

| Workstream | Disposition | Required next action |
|---|---|---|
| G1 + passenger foundation PR #1/#3 | **VERIFIED MERGED** | Preserve main history; use current main SHA for future work |
| Historical product/A1/A2 docs #2/#6/#7/#8 | **OPEN / UNMERGED** | Preserve provenance; do not assume docs are on main |
| Shared platform identity PR #9/#10 | **OPEN / STALE-BASE** | Reconcile with Move and passenger migration graph |
| Move/location PR #17 | **OPEN / DIVERGED** | Compare against current platform identity and migration graph |
| A5 PR #11–#13 | **SEPARATE / NOT AUTHORIZED FOR DEPLOYMENT** | Keep isolated; no dispatch, merge or deployment |
| Brand/Android PR #14/#15 | **OPEN / STALE-BASE** | Reconcile only relevant design/Android artifacts with selected passenger stack |
| Passenger-only/full platform PR #25–#41 | **OPEN STACK** | Preserve dependency chain; no wholesale replacement of current main |
| Android PR #42/#43 | **SIBLING OVERLAP** | Resolve four common files; #43 exact-head CI evidence missing |
| IROKA PR #44 | **CONTRACT ONLY** | No live endpoint/trust evidence |
| Cargo PR #45–#49 | **STACKED OPEN** | Preserve chain; perform service/legal evidence review |
| Cargo PR #50/#51 | **BLOCKED — REVISION-ID COLLISION** | Select one retention model and reconcile migrations |
| Cargo PR #52 | **DEPENDENT ON #51** | No independent integration; legal/compliance review still needed |
| MITP PR #53 | **OPEN / EXACT-HEAD CI PASS** | Reconcile with canonical GIS branch; no live tracking |
| Passenger About PR #54 | **OPEN** | Separate passenger UI increment; API connectivity remains separately gated |
| Current readiness docs PR #55 | **OPEN / A2 PARTIAL** | Continue read-only A2 evidence closure |
| Free-pilot docs PR #56 | **ONE DOC ON UNMERGED A3/A4 STACK** | Do not treat as standalone main integration |
| Strategy/A1 amendment PR #57 | **OPEN / DOCUMENTATION ONLY** | Owner review; no merge or A1 freeze implied |

## 7. Required remaining MN-002/A2 checks

1. Inspect exact diffs for overlapping PR #42/#43 files and relevant parent commits; establish whether any semantic change is lost if one sibling is selected.
2. Inventory every Alembic revision across PR #9, #17, #30–#53 and the canonical A3 integration branch; compare all revision IDs, parent relationships, model imports and migration ownership.
3. Compare PR #17's location/Move migration ancestry against PR #9 and the canonical GIS integration branch; identify whether any schema/model changes are absent from the A4 branch.
4. Inspect exact-head workflow evidence for the remaining candidate PRs; distinguish PR-triggered runs from stale branch runs and synthetic CI from device/production acceptance.
5. Verify current model registry and router/config integration on each candidate integration branch; no source edits during A2.
6. Establish the parent A3/A4 integration branch's PR path and governance disposition; do not create a PR or retarget any branch without a separate explicit decision.
7. Reconcile Cargo retention variant #50/#51 with a documented selected migration design and legal/retention requirements.
8. Produce the current-scope A2 closure package only after the above evidence is reconciled. A2 closure remains Owner-reviewed.

## 8. Governance and non-actions

- No main modification.
- No PR merge, retarget, close, branch deletion or force push.
- No application code or migration edits.
- No migration execution or database connection.
- No workflow dispatch or rerun.
- No provider, billing, paid service or external endpoint activation.
- No production data, real passenger identity, live GPS, payment or commercial operation.
- A3 entry remains gated by the applicable A1 freeze and current A2 closure.
- A5 deployment requires separate explicit Owner approval.

## 9. Final MN-002 status

**MN-002: PARTIAL — branch graph and PR refs reconciled; material integration blockers confirmed.**

**Immediate next work:** complete MN-003 exact-head PR #43 review and MN-004 full Alembic/model-registry inventory. Keep both read-only. The Cargo revision collision and unsubmitted A3/A4 integration branch must remain visible blockers; neither is resolved by this report.
