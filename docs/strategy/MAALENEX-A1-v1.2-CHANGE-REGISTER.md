# MaaleNex Platform A1 v1.2 — Controlled Change Register

**Status:** DRAFT FOR OWNER REVIEW — NOT FROZEN  
**Prepared:** 2026-11-26  
**Applies to:** MaaleNex Platform Product Scope and Architecture A1 v1.1  
**Purpose:** Record proposed, evidence-linked amendments without editing, replacing, or reopening the frozen v1.1 document.

## 1. Source-of-truth and provenance

| Item | Verified reference | Treatment |
|---|---|---|
| Frozen platform A1 v1.1 | Commit `22813a4510d42d4295602075abaebabc7a83369e`; file `docs/MAALENEX-PLATFORM-A1-v1.1.md`; blob SHA `f7900e619f969e62d9f12c3c78457f99def23a05`; PR #6 | Immutable historical baseline. Preserve exactly. |
| A1 v1.1 approval record | PR #6 body records Owner approval/freeze on 2026-11-08; freeze commit above | Preserve approval provenance; do not restate as a new approval. |
| Historical A2 closure | PR #8, head `13c7e60df0712a11269c29a6884d33cb62aeecb0`; file `docs/A2-MAALENEX-PLATFORM-RECONCILIATION-v1.0.md`; blob SHA `683ea5b26b9867d333ef16366ce984661d2a5d06` | Preserve as a closed assessment of its stated historical baseline, main SHA `72550a2e464f6517653580bb1ae4e7608f211f39`. |
| Separate MaaleNex–IROKA A1 | Main file `docs/architecture/MAALENEX-IA-A1-SPEC-001.md`; blob SHA `061f24bb527bc5153f6f187989822ace7846f9ca`; document version 1.0.0, frozen | Distinct architecture baseline. Not the platform A1 v1.1 and not amended here. |
| Production-readiness A1/A2 | PR #55, head `0213953d474bf9a724237a853d4a8df8b04b21bc`; A1 draft and A2 partial | Separate, newer assessment against main `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`; does not retroactively invalidate the historical A2 closure. |
| Enhanced implementation strategy | PR #57, branch `docs/enhanced-implementation-strategy-a1-v1`, initial head `4cd1c31f824a2f2f0ec63241c80f5ab6357aea8f` | Owner-approved planning direction; not itself an A1 v1.2 freeze or A2 closure. |

**Repository continuity note:** The frozen v1.1 document's metadata names `akefadaka-git/maalenex-moto`, while the accessible historical commit and PR records are now retrievable in `akefadaka-git/maalenex`. The original file and freeze commit are preserved byte-for-byte in the current repository history. The historic label is retained as provenance; this register does not assume or assert an undocumented repository rename.

## 2. Amendment rules

1. v1.1 remains frozen and unchanged.
2. v1.2 is a proposed additive/clarifying amendment. It becomes a new baseline only after explicit Owner approval and a recorded freeze.
3. Each proposed change must be traceable to an existing v1.1 section, an Owner-approved reassessment direction, and current repository evidence.
4. A new technical preference is not represented as implemented, externally validated, or commercially approved.
5. Where evidence conflicts or is missing, the amendment records a gap or deferred decision rather than silently choosing an implementation.
6. No amendment authorizes merge, A3 implementation before A2 closure, provider activation, paid services, production data, commercial operations, or A5 deployment.

## 3. Proposed change register

| ID | v1.1 reference | Proposed v1.2 treatment | Basis / evidence | Status |
|---|---|---|---|---|
| CR-001 | §§1–3 Product vision, hierarchy and rollout | Retain all eight service lines and South Omo-first strategy. Clarify passenger/Transit first; Move follows; Delivery, Cargo, Market/Business and Pay remain sequenced, not simultaneous launch commitments. | Frozen v1.1; Owner-approved enhanced strategy PR #57. | PROPOSED |
| CR-002 | §3.1 Geographic sequence | Retain Koybe/Jinka pilot and Jinka–Wolaita Sodo–Addis Ababa corridor only as planning scope subject to operator-authorized route/stop evidence. Explicitly prohibit inferred route geometry or intermediate stops. | Frozen v1.1; current A2 PR #55 identifies route geometry/provenance gaps; Owner-provided Koybe boarding point reference. | PROPOSED |
| CR-003 | §4 Roles and authorization | Add a canonical authorization decision tuple: principal, organization/tenant, service, resource and action; require explicit membership, resource scope, least privilege and audit for privileged actions. Preserve guest passenger discovery/reservation behavior. | Historical A2 §3.2; PR #57 §2.4; current branch evidence remains to be reconciled. | PROPOSED |
| CR-004 | §§5–6 Service and shared capabilities | Retain eight service lines. Define shared platform capabilities as bounded domains (Identity, Trust, Organizations, Authorization, Audit, Geography, Files/Evidence, Notifications, Support, Analytics, Integration) with service-owned lifecycle/state machines. | Frozen v1.1; PR #57 target domain catalogue. | PROPOSED |
| CR-005 | §7.1 Starting architecture | Clarify modular monolith first; retain FastAPI, Python 3.11+, Pydantic Settings, SQLAlchemy 2, Alembic, PostgreSQL, React, TypeScript, Vite and Capacitor as current starting stack, subject to exact-branch verification. No premature microservices or wholesale passenger rewrite. | Frozen v1.1; PR #55 repository assessment; PR #57 §§2.1–2.3 and 2.7. | PROPOSED |
| CR-006 | §§6–7 Geography/maps | Prefer canonical PostGIS data and MapLibre rendering, with Martin as a candidate tile service. Separate verified public geography from restricted operational telemetry. Preserve provenance, license, attribution, freshness and verification status. Hosting, licensing, bandwidth, privacy and cost remain A2 decisions. | Frozen v1.1 deferred map decision; PR #55 §5; PR #57 §2.6. | PROPOSED / A2 VALIDATION REQUIRED |
| CR-007 | §§6, 8 Notifications/communications | Specify transactional outbox and durable in-app inbox as the source of truth. SMS, WhatsApp Business and email are provider adapters subject to consent, terms, cost and separate activation approval. Telegram remains optional, user-initiated if ever adopted. | PR #55 notification recommendation; PR #57 §2.8. | PROPOSED |
| CR-008 | §§7–8 Mobile, privacy and security | Preserve existing passenger web/PWA and Android implementation. Require API-origin, session/cookie, CSRF/CORS, offline/error recovery and physical-device acceptance. Require purpose-bound location consent, expiry/revocation, scoped access and telemetry replay protection. | Historical A2 Android limitation; PR #55; PR #57 §§2.7–2.9. | PROPOSED |
| CR-009 | §5.8 Pay | Clarify that ETB ledger foundations may be tested synthetically; provider adapters, real payment collection, settlement, payouts and money movement remain disabled pending separate legal, provider, security, finance and Owner gates. | Frozen v1.1 Pay requirements; PR #57 §§2.9 and 3.6. | PROPOSED |
| CR-010 | §§8, 10, 11 Acceptance and stages | Expand A4 evidence to include migration parity/rollback/re-upgrade, concurrency, tenant/resource isolation, independent security review, accessibility, physical Android, GIS provenance/licensing, backup restore, monitoring and incident readiness. Keep A5 as separate explicit approval. | Frozen v1.1 acceptance matrix; PR #55 A1 draft; PR #57 phases 10–11. | PROPOSED |
| CR-011 | §§11–12 Delivery and exclusions | Add explicit synthetic-preview boundary: preview is not production, does not authorize persistent real-user data, live providers, payments, GPS or commercial operation. No paid hosting/provider activation without separate approval. | PR #55 current runtime restrictions; PR #57 §7. | PROPOSED |
| CR-012 | §7 / intelligence integration | Reaffirm IROKA as a separate, governed, invisible intelligence backbone, disabled by default in MaaleNex integration, authenticated/audited/data-minimizing, advisory unless MaaleNex separately authorizes a defined action. It cannot authorize transactions. | Separate frozen MaaleNex–IROKA A1 v1.0; PR #57 §§1 and 2.8. | PROPOSED; PRESERVE SEPARATE BASELINE |
| CR-013 | §§10–12 Evidence and gates | Distinguish historical A2 closure (baseline main SHA `72550a2...`) from the current production-readiness A2 (baseline main SHA `c988b9d...`). The latter is PARTIAL / NOT CLOSED and must be completed read-only. Do not claim historic A2 was invalidated. | PR #8 historical closure; PR #55 current A2 report; PR #57 §4. | PROPOSED |
| CR-014 | §13 Owner decisions | Convert unresolved decisions into explicit decision records: identity/tenancy contract, canonical GIS, passenger/MITP map interfaces, PR stack disposition, notification provider selection (without activation), preview hosting boundary, Cargo evidence/retention, and acceptance KPIs. | PR #55 gaps; PR #57 MN-001–MN-012 register. | PROPOSED / DEFERRED TO A2 |
| CR-015 | §§11–14 Governance | Reaffirm A1 freeze → A2 read-only reconciliation → A3 implementation → A4 verification → A5 deployment. No main changes during A2, no merge or workflow dispatch without separate authorization, no paid activation, and A5 always separately approved. | Owner governance; PR #57 §7. | PROPOSED |

## 4. Explicitly unchanged v1.1 decisions

The following remain unchanged unless a later evidence-backed amendment is separately approved:

- MaaleNex is the master product identity and the eight service lines remain Move, Transit, Delivery, Cargo, Market, Fleet, Business and Pay.
- South Omo is the initial operating priority; no fabricated coverage, operator availability or route data.
- Amharic-first, mobile-first and low-bandwidth usability.
- Safety, trust, transparency, service-specific operating/legal gates and tenant/resource isolation.
- Modular FastAPI backend, PostgreSQL/Alembic data foundation and React/TypeScript/Vite frontend direction.
- Synthetic-only public development/test fixtures; no real personal data or secrets in source control.
- No silent location tracking, live payments, commercial operation, or unapproved provider activation.
- Existing passenger MVP and repository history must be preserved.
- A5 deployment remains a separate explicit Owner approval.

## 5. Open questions and evidence required before v1.2 freeze

| ID | Question / evidence gap | Required resolution | Current status |
|---|---|---|---|
| OQ-01 | Confirm exact continuity between historical `maalenex-moto` source metadata and current `maalenex` repository history. | Preserve original commit/file provenance and record any repository transfer/rename evidence if available. | PARTIAL — source commit is retrievable; rename history not asserted. |
| OQ-02 | Reconcile current PR #32–#44, #53–#57 and all relevant dependencies against current main. | Exact base/head SHAs, changed files, branch ancestry, workflow statuses and conflict/disposition register. | PARTIAL — A2 PR #55. |
| OQ-03 | Establish the combined Alembic graph and model registry. | Full revision inventory, database `alembic_version` state where safely available, registry parity, disposable DB upgrade/downgrade/re-upgrade evidence. | PARTIAL — competing heads identified; no live migration. |
| OQ-04 | Finalize identity/tenancy authorization contracts. | Principal/org/service/resource/action matrix; tenant isolation and guest access regression evidence. | OPEN. |
| OQ-05 | Select GIS implementation contract. | PostGIS/MapLibre/Martin feasibility, licensing, attribution, hosting, bandwidth, cost and public-vs-restricted data boundary. | OPEN. |
| OQ-06 | Verify passenger API and Android runtime connectivity. | Exact API origin, cookie/session/CSRF/CORS tests, physical-device acceptance. | MISSING / NOT RUN. |
| OQ-07 | Complete notification design and provider assessment. | Outbox/inbox contract, consent, channel comparison, provider policy/cost/sandbox review. No provider activation. | PARTIAL. |
| OQ-08 | Reconcile Cargo evidence and retention lifecycle. | Custody/evidence provenance, access, retention, deletion/legal-hold and claims requirements. | OPEN. |
| OQ-09 | Establish synthetic preview boundary. | Separate runtime/database identity, synthetic-only enforcement, no production secrets/data, no paid activation. | OPEN. |
| OQ-10 | Close security, privacy, regulatory and operations evidence. | Threat model, independent review, privacy/retention, insurance/regulatory checklist, backup/restore and incident readiness. | MISSING / UNKNOWN by topic. |

## 6. Stage disposition

- **Historical A1 v1.1:** VERIFIED-CLOSED / FROZEN. Do not edit.
- **Proposed A1 v1.2:** DRAFT / NOT FROZEN. This register is not an Owner freeze record.
- **Historical A2 v1.0:** VERIFIED-CLOSED WITH RECORDED GAPS for its historical baseline only.
- **Current production-readiness A2:** PARTIAL / NOT CLOSED; continue read-only reconciliation.
- **A3:** NOT AUTHORIZED TO START under the current stage sequence until the applicable A1 v1.2 decision is frozen and current A2 closure is accepted.
- **A4:** NOT RUN for the integrated platform.
- **A5:** NOT AUTHORIZED; separate explicit Owner approval required.

## 7. Change history

| Version | Date | Change | Approval |
|---|---|---|---|
| 0.1-draft | 2026-11-26 | Initial traceable register prepared from frozen v1.1, historical A2 closure, current PR #55 and Owner-approved strategy PR #57. | Not yet approved |

**Disposition:** Controlled draft for Owner review. No source baseline was modified.
