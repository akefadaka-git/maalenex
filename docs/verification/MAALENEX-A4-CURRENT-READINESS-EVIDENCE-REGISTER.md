# MaaleNex — A4 Current Readiness Evidence Register

**Record date:** 2026-11-26  
**Repository:** `akefadaka-git/maalenex`  
**Assessment branch:** `a4/current-readiness-evidence-2026-11-26`  
**Assessment base:** `feat/a3-canonical-postgis-integration` at `3c3eeb7a211e4978f95140e36f7f4da5d9e52c67`  
**Last code CI evidence:** G1 workflow run [#822](https://github.com/akefadaka-git/maalenex/actions/runs/45720048934), exact tested code SHA `9750d2cba123a7c2567ef5c9bce3511f9ce0382e`  
**Scope:** Documentation and read-only A4 operational readiness assessment. No production access, migration execution, merge, deployment, or live service activation.

## 1. Governance and baseline provenance

- A1 baseline remains frozen at `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`.
- The Owner-approved A2 disposition remains **CLOSED — PARTIAL**, based on the original 25 November 2026 conversation approvals.
- The original A2 body and its original repository commit were not recovered. The separately labelled recovery reissue is committed at [`1b170187ece989493a91c3b1f5bcc0330da5530c`](https://github.com/akefadaka-git/maalenex/commit/1b170187ece989493a91c3b1f5bcc0330da5530c), blob `842307910c58b5590a77316b88c19e492f66bc9a`. It is not the verbatim original.
- A3 was subsequently authorized separately and implemented on the integration branch. The historical A2 reissue's statement that A3 had not yet been authorized is time-scoped to the original A2 approval and does not override the later authorization.
- G1 run #822 passed backend/PostGIS and frontend jobs on exact code SHA `9750d2cba123a7c2567ef5c9bce3511f9ce0382e`. Recorded results: 38 backend tests passed, 31 skipped; Ruff, A3.2–A3.8 integration checks, migration parity, full downgrade/re-upgrade, and frontend build/tests passed.
- The current integration branch tip `3c3eeb7a211e4978f95140e36f7f4da5d9e52c67` is a later documentation commit. Run #822 is evidence for its stated exact tested code SHA, not a claim that #822 checked out this later documentation SHA.

## 2. Ordered A4 operational gates

| Order | Gate | Current status | Evidence / finding | Required closure evidence |
|---|---|---|---|---|
| A4-01 | Production application database identity and capability-role membership | **MISSING / UNVERIFIED** | A3.5 defines NOLOGIN least-privilege roles and transaction-local tenant context. A3.6 explicitly states the actual runtime application DB login is unidentified and out-of-band membership is deferred. CI tests do not prove production login membership. | Identify the intended runtime principal through an approved deployment record; verify its non-owner/non-superuser attributes and exact SET memberships for only required capability roles; verify negative grants. No credentials should be committed. |
| A4-02 | Production network and TLS boundary | **NOT RUN / UNVERIFIED** | Martin config listens on container port 3000; Compose publishes it only on `127.0.0.1:3000`. This is local-development binding, not evidence of a production ingress boundary. No production reverse proxy, certificate chain, TLS policy, trusted proxy configuration, firewall/security-group rule set, or external exposure test is recorded. | Document target host and ingress topology; verify TLS termination, certificate validity/renewal, secure-cookie behavior, trusted proxy handling, internal-only Martin access, firewall rules, and external negative reachability. Do not expose services during this assessment. |
| A4-03 | Authoritative Maale Woreda boundaries, road network, provenance and licenses | **MISSING — SOURCE EVIDENCE** | A3.8 adds fail-closed provenance/license-review fields and source-evidence records. Run #822 records CI checks for A3.8. The A3.8 architecture record explicitly says no authoritative Maale Woreda boundary, road-network source, or external license has been added. Existing synthetic fixtures are not production geography. | Identify authoritative source/provider and version; obtain source files and checksum; document collection method, CRS, authority, license terms, attribution and redistribution rights; complete independent license review and geometry/ground-truth validation before publication eligibility. |
| A4-04 | IROKA endpoint, trust configuration and live integration | **PARTIAL — FAIL-CLOSED CONTRACT ONLY** | PR [#44](https://github.com/akefadaka-git/maalenex/pull/44) is open and draft, head `e2e997e1a6d48f8aeb041cd50339bebe4d434a60`. It defines a versioned request/decision contract and disabled-by-default fail-closed adapter. Its PR record explicitly states no deployed IROKA HTTP service or stable endpoint has been verified, and no production credentials, trust roots, keys or live calls exist. | Verify an authorized IROKA deployment and stable endpoint; approve endpoint identity and protocol; provision and validate trust roots/key rotation/revocation; define service identity, authentication, authorization, timeouts, replay protection and audit receipt verification; conduct synthetic end-to-end integration tests before any live connection. |

## 3. Related open work that must remain separate

- PR #44 — IROKA contract: open, draft, unmerged; no live service integration.
- PR #53 — MITP synthetic GPS/map proof of concept: open, draft, unmerged. Its PR description records that the OSM PBF import and browser map rendering had not yet been run at that PR snapshot. Do not treat that older PR description as overriding the later A3 integration-branch CI evidence; authoritative Maale production geography remains absent.
- PR #54 — passenger About/creator profile: open, draft, unmerged; frontend tests are authored but the PR description says exact-head CI had not yet run. This is a separate passenger increment and is not a production-readiness gate for the four operational checks above.
- Existing open PRs and branches are preserved. No PR was merged or modified by this evidence register.

## 4. Status semantics and decision boundary

- **PASS:** exact evidence demonstrates the stated acceptance criterion.
- **MISSING:** required source, identity, configuration, or evidence does not exist in the inspected repository record.
- **UNVERIFIED / NOT RUN:** evidence is insufficient or the operational test has not been executed.
- **PARTIAL:** only a bounded subset, such as code contract or CI tests, is verified.
- **UNRESOLVED:** a material question remains open.

A successful CI run proves only the tested commit and automated scope. It does not prove production database membership, deployed TLS/network controls, legal rights to publish real geographic data, or a reachable and trusted IROKA service.

## 5. Overall A4 disposition

**A4 operational readiness: PARTIAL — OPEN.**  
**Production readiness: NOT READY.**  
**A5 deployment: NOT AUTHORIZED.**

The four gates above are assessed in order. Work remains read-only unless a separate implementation or operational action is explicitly authorized. No production credentials, secrets, real passenger data, production database access, migration execution, PR merge, deployment, or commercial activation is authorized by this register.
