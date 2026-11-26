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
| A4-01 | Production application database identity and capability-role membership | **PARTIAL — CONTRACT DEFINED; LIVE IDENTITY/MEMBERSHIP MISSING** | The application uses the SQLAlchemy `DATABASE_URL` login; `backend/app/domains/geo/security.py` maps six permission codes to four static NOLOGIN capability roles. A dedicated evidence procedure and read-only SQL checks are documented in [A4-01 evidence record](A4-01-PRODUCTION-DB-IDENTITY-AND-MEMBERSHIP-EVIDENCE.md). The production login remains unidentified because no production target or secret reference is in the repository; current G1 settings prohibit production connections. | Identify the actual production cluster/database and runtime login from the hosting control plane/secret metadata; run the documented read-only catalogue checks; then separately authorize any required SET-only memberships. |
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


## 6. Read-only gate inspection — 26 November 2026

### A4-01 — Database principal and capability memberships

**Finding: NOT READY — PRODUCTION DATABASE IDENTITY IS NOT CONFIGURABLE IN THE CURRENT G1 SETTINGS.**

- `backend/app/core/config.py` defaults to `APP_ENV=development`, `SYNTHETIC_DATA_ONLY=true`, and `DATABASE_URL=postgresql+psycopg://localhost:5432/maalenex_dev`.
- Its settings validator rejects environments other than development/test, rejects non-synthetic mode, rejects remote database hosts, and rejects database names other than `maalenex_dev`.
- `backend/app/db/session.py` creates the SQLAlchemy engine directly from that validated `settings.database_url`.
- Migration `0023_geo_tenant_rls_permissions` defines NOLOGIN capability roles. It does not create or grant memberships to the runtime login.
- The A3.5/A3.6 records require out-of-band membership and explicitly state the actual runtime application login is unidentified.

**Disposition:** production principal identity, membership, SET OPTION semantics and negative privilege checks are **MISSING / NOT RUN**. No database connection was attempted. Do not bypass the development guard or provision a production login as part of this read-only check.

### A4-02 — Network and TLS boundary

**Finding: LOCAL-ONLY NETWORK BINDING VERIFIED; PRODUCTION INGRESS/TLS NOT VERIFIED.**

- `infra/martin/docker-compose.yml` publishes Martin as `127.0.0.1:3000:3000`; the container listens on `0.0.0.0:3000` internally. The host-side binding is loopback-only in the supplied Compose definition.
- `infra/martin/config.yaml` disables its web UI and CORS and lists only the six sanitized `geo_public` sources.
- `backend/app/core/config.py` exposes an explicit `secure_cookies` setting and uses HTTPS request scheme or that setting to select Secure cookies. However, the same settings validator prohibits a production environment and remote database.
- No production reverse-proxy configuration, certificate chain, TLS policy, trusted-proxy configuration, firewall/security-group evidence, public DNS, ingress test, or production Martin login was found in the inspected repository paths.

**Disposition:** local development binding is **PASS** as configured; production TLS/network boundary is **NOT RUN / UNVERIFIED**. No endpoint was exposed or probed.

### A4-03 — Official geographic-source and license leads

Read-only web research identified possible authoritative-source leads, but none is yet cleared for import or publication:

1. **Ministry of Agriculture National Ag Datahub — Ethiopian Woreda Boundary.** The catalogue describes a Woreda boundary dataset with source attributed to CSA and downloadable WFS/GeoJSON/Shapefile resources. Its metadata shows dataset reference date 2020-04-25 and last catalogue update 2025-09-03. Critically, it states **No License Provided** and the access-constraints field says the original author did not specify a license. It is a candidate for a formal source request and content/version verification, not an approved production source: https://data.moa.gov.et/dataset/ethiopian-woreda-boundary2
2. **Ministry of Agriculture National Ag Datahub — Ethiopian Administrative Boundary.** The catalogue identifies SSGI as organization and exposes WFS/GeoJSON/Shapefile resources, but states **No License Provided**. This is another candidate lead only: https://data.moa.gov.et/dataset/ethiopian-administrative-boundary
3. **Ethiopian Roads Administration i-RAMS.** ERA describes GIS-based Federal Road Network information and road inventory/condition systems. The public information page does not establish a downloadable Maale rural-road dataset or a reuse/redistribution license. Its stated Federal Road Network scope is not proof of complete Woreda/local-road coverage: https://irams.era.gov.et/about
4. **Current South Ethiopia LLRP-II procurement notice.** A notice published 17 November 2026 seeks route selection, survey, feasibility and detailed design services for access roads and bridges in several woredas, including a Tikiboko Bezo River bridge in Maale. This is evidence of planned survey/design work, not a completed Maale road-network dataset or a license to reuse derived geometry: https://etgs.co/tenders/procurement-of-consultancy-service-for-feasibility-study-detail-design-26csqcbs
5. **Ministry of Agriculture Woreda Participatory Land Use Planning toolkit.** The published toolkit describes use of CSA administrative maps as a guide and topographic maps / satellite imagery to prepare a Woreda base map; it is methodological guidance, not itself a Maale geometry dataset: https://www.moa.gov.et/wp-content/uploads/2024/11/201811_Woreda-Participatory-Land-Use-Planning-WPLUP-in-Pastoral-and-Agro-Pastoral-Areas-Volume-2-Toolkit-Worksheets.pdf

The public catalogue evidence does not establish that the selected boundary layer contains the current Maale Woreda boundary, nor does it establish a usable license. No source file was downloaded, modified, imported, or added to the repository. No road dataset was acquired.

**Disposition:** authoritative Maale boundary **UNRESOLVED**; authoritative road network **MISSING**; reuse/publication rights for the candidate boundary dataset **MISSING**; road-network license/access terms **MISSING**. Keep the A3.8 publication-eligibility gate closed.

### A4-04 — IROKA endpoint and trust configuration

PR #44 remains **OPEN / DRAFT / UNMERGED**, head `e2e997e1a6d48f8aeb041cd50339bebe4d434a60`. Its recorded scope is a versioned strict request/decision contract and disabled-by-default fail-closed adapter. The PR description explicitly says that no deployed IROKA HTTP service or stable endpoint has been verified and that production credentials, trust roots, key provisioning and real IROKA calls are absent. Exact-head CI run [#574](https://github.com/akefadaka-git/maalenex/actions/runs/45034367684) completed successfully on that same head SHA (one backend/PostgreSQL job). This verifies the synthetic contract implementation and tests; it does not verify a deployed endpoint, transport security, service identity or live trust.

**Disposition:** contract boundary **PARTIAL**; deployed endpoint identity **MISSING**; production trust roots/key lifecycle **MISSING**; live end-to-end integration **NOT RUN**. Do not invent an endpoint or connect to an unverified service.

## 7. Current gate summary after inspection

| Gate | Updated status |
|---|---|
| A4-01 Runtime DB principal and role membership | **MISSING / NOT RUN** — current application settings remain local development/test only |
| A4-02 Production network/TLS | **PARTIAL** — local loopback binding verified; production ingress/TLS not evidenced |
| A4-03 Maale authoritative geography and licensing | **UNRESOLVED / MISSING** — catalogue leads found, no confirmed current Maale source or cleared license |
| A4-04 IROKA endpoint/trust/live integration | **PARTIAL** — fail-closed contract only; no deployed endpoint or live trust |

The A3.8 code and synthetic CI tests passing do not change the missing real-world source, legal-rights or production-operations evidence above.


## 8. A4-01 detailed evidence record

The application-to-database capability mapping and read-only verification procedure are recorded in [A4-01 — Production Database Identity and Least-Privilege Evidence](A4-01-PRODUCTION-DB-IDENTITY-AND-MEMBERSHIP-EVIDENCE.md).

**Updated disposition:** **PARTIAL — CONTRACT ESTABLISHED; PRODUCTION LOGIN AND MEMBERSHIP NOT VERIFIED.** Repository inspection establishes the logical application DB identity boundary and exact four-role capability mapping. It does not establish the real production principal. No production cluster is identified, no secret metadata was accessed, and no database connection or grant was performed.

The A4-01 record defines the required catalogue checks, role-attribute expectations, SET-membership checks, unexpected-membership check, and negative privilege tests. Provisioning remains a separately approved action.
