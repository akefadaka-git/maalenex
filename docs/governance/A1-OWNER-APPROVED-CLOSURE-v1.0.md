# MaaleNex A1 — Owner-Approved Closure Record

- **Document ID:** MNX-GOV-A1-CLOSE-001
- **Version:** 1.0.0
- **Status:** VERIFIED-CLOSED — A1 assessment, specification and freeze
- **Approval date:** 2026-11-15
- **Repository:** `akefadaka-git/maalenex`
- **Closure branch:** `docs/a1-owner-approved-closure`
- **Closure branch base / unchanged main SHA:** `78884c0f2609edbfc94a24e42d84824bff9eed20`
- **Scope:** Documentation and governance record only

## 1. Owner approval and decision

The Owner explicitly instructed on 2026-11-15:

> Reconcile the existing A1 decisions and artifacts, identify only genuine omissions, and produce an Owner-approved A1 closure record.

This record memorializes that approval. It does not represent a cryptographic signature or an approval by any third party.

**Decision:** A1 is **VERIFIED-CLOSED (100% of A1 stage scope), WITH RECORDED GAPS**. The A1 deliverables—product direction, planning baseline, requirements and governance baselines, architecture/dependency assessment, security and privacy threat model, synthetic acceptance scenarios, migration/rollback strategy, and explicit stage gates—are present and reconciled sufficiently to freeze the planning baseline.

This closure does **not** certify implementation completeness, operational readiness, legal compliance, security certification, production readiness, or deployment readiness. Recorded gaps below remain binding inputs to A2, A3, A4 and A5.

## 2. Stage boundary

A1 covers assessment, requirements and architecture planning, specification, dependency analysis, risk identification, acceptance planning, and baseline freeze.

- **A1:** closed by this record.
- **A2:** read-only reconciliation and detailed design verification remain separately controlled; no application-code or schema changes are authorized by this record.
- **A3:** implementation remains subject to a separately approved, bounded scope.
- **A4:** verification remains subject to exact-head evidence and acceptance criteria.
- **A5:** deployment, pilot activation and commercial operation remain separate Owner approval gates.

No merge, deployment, release, production activation, real operator onboarding, live payment collection, real passenger-data processing, ticket issuance for real travel, or commercial operation is authorized here.

## 3. Reconciled and frozen A1 decisions

The following decisions form the controlling A1 product baseline:

1. **Canonical product identity:** The product/platform name is **MaaleNex**. “MaaleNex Moto” is a legacy project label retained in historical planning documents and existing Android package identifiers until separately reviewed. New user-facing product copy should use MaaleNex.
2. **Initial market and product:** Passenger mobility is the first delivery domain, with a Jinka-first controlled-pilot direction. This is a product direction, not evidence that Jinka operators, terminal permissions, routes, schedules or fares have been verified.
3. **Initial boarding boundary:** Jinka Bus Terminal is the initial planning baseline. Intermediate boarding points are excluded unless individually verified and approved for the relevant operator and trip.
4. **Route status:** Jinka–Wolaita Sodo and Jinka–Addis Ababa are candidate priorities only. Neither is represented as an active, verified or bookable service by A1.
5. **Freight and other services:** Freight is a later, separately scoped domain. Motorcycle-driver, heavy-load-driver and other non-passenger roles appearing in prototype UI material are not part of the initial passenger release. They are future-scope placeholders only.
6. **Architecture direction:** Preserve the FastAPI + React/TypeScript/Vite + PostgreSQL/Alembic foundation and a modular-monolith approach with explicit domain ownership. Do not introduce microservices or additional infrastructure without a separate architecture decision.
7. **Localization and delivery:** Amharic-first, English-capable and mobile-first experience is the product direction.
8. **Data and environment boundary:** Development and automated acceptance remain synthetic-only. Real passenger/operator personal data, financial data and production secrets are prohibited in development/test.
9. **Financial boundary:** Payment collection, provider selection, custody, commissions, subscriptions, settlements and refunds remain disabled/unapproved until their separate legal, commercial, security and Owner gates are met. The initial pilot baseline assumes no platform revenue.
10. **Operational boundary:** Real operator onboarding, public trip publication, live booking, live ticketing/boarding, and commercial pilot activation require separately verified authority, evidence, agreements, support ownership and explicit approval.
11. **Android boundary:** The native Android shell may host the packaged web application. The A1 bridge/plugin document is a design specification only; no privileged native bridge or plugin implementation is authorized by its A1 freeze.

The Owner-approved Passenger MVP Requirements Baseline v1.0 and the approved A2 decisions D01–D07 / Implementation Specification v1.0 take precedence over inconsistent or older draft wording in the PRD and onboarding proposal.

## 4. Source artifact register

The source artifacts below were inspected at their exact GitHub branch revisions. Their blob SHAs are recorded to make the closure auditable. These artifacts are not all present on `main`; their source PRs remain unmerged as noted.

| Artifact | Source branch / PR | Exact blob SHA | Reconciliation disposition |
|---|---|---|---|
| Product Scope and Phased Roadmap v1.0 — `docs/PRODUCT-SCOPE-ROADMAP-v1.md` | `docs/product-scope-roadmap-v1`, PR #2 | `0f0fb082db129d5b81ebb4f5c302aa9d64b1f7c5` | Controlling approved product direction and phased roadmap |
| Passenger MVP Requirements Baseline v1.0 — `docs/PASSENGER-MVP-REQUIREMENTS-BASELINE-v1.0.md` | PR #2 | `3af3ba0345eb29bf18b87b494043d96566ecd41c` | Controlling approved working requirements baseline |
| Jinka Pilot Governance Decision Register v1.0 — `docs/JINKA-PILOT-GOVERNANCE-DECISION-REGISTER-v1.0.md` | PR #2 | `561b9ab763a498117171a460460cd29e424a45ea` | Approved governance baseline; accountable-party assignments remain open |
| Passenger MVP A1 Implementation Plan v1.0 — `docs/PASSENGER-MVP-A1-IMPLEMENTATION-PLAN-v1.0.md` | PR #2 | `86184d7b9435012b43a0b210ed5598e9bbe0743b` | A1 assessment, dependency graph, backlog, threat model, synthetic scenarios, migration/rollback and evidence gates; stale findings superseded by §5 |
| Passenger Mobility PRD v0.1 — `docs/PASSENGER-MOBILITY-PRD-v0.1.md` | PR #2 | `1f480edd62ab376fcc87721e962b92d0ef6fdf06` | Draft/reference only; its open decisions and earlier assumptions do not override v1.0 baseline |
| Jinka Operator Onboarding v0.1 — `docs/JINKA-OPERATOR-ONBOARDING-v0.1.md` | PR #2 | `bd1d317b486f11012ddace5328437dde0f46ad00` | Draft/reference only; not authorization for real onboarding |
| Passenger MVP Implementation Specification v1.0 — `docs/PASSENGER-MVP-IMPLEMENTATION-SPECIFICATION-v1.0.md` | PR #2 | `48aa9a7436358426fc3edd9c2ddc14f6b1856564` | A2 technical design baseline; D01–D07 approved; A3 not authorized |
| Android Native Bridge & Plugin Architecture A1 — `docs/architecture/ANDROID-NATIVE-BRIDGE-PLUGIN-A1.md` | `feat/maalenex-brand-identity`, PR #14 | `f84fa8f9338f3f3ca7e6490ebf41b15e057f22cf` | A1 architecture freeze for implementation planning only; runtime bridge not implemented |
| Portal Role and Page Matrix — `docs/portal/ROLE-AND-PAGE-MATRIX.md` | PR #14 | `02a2286834e505ed321d352cf06c8e37836cb37a` | Frontend prototype inventory; not a server authorization contract |
| UI Component Inventory and Gap Register — `docs/ui/MAALENEX-UI-COMPONENT-INVENTORY-AND-GAP-REGISTER.md` | PR #14 | `e7e5f8436325c37a1fe865c61f906f6e3327b186` | Design-system inventory and follow-up gap register |

### Source PR state at closure

- **PR #2** — [product scope and planning artifacts](https://github.com/akefadaka-git/maalenex/pull/2): open, unmerged; source head `3bf77bdbf6d017331a5ec2ea64e2a36577f9c8b6`.
- **PR #14** — [brand identity, Android shell and UI artifacts](https://github.com/akefadaka-git/maalenex/pull/14): open, draft, unmerged; source head `8d422a7ff14978f6e9733f0213c712e8f9d16703`.
- **PR #18** — [canonical MaaleNex identity correction](https://github.com/akefadaka-git/maalenex/pull/18): open, draft, unmerged; source head `67e6c49a5cd925b43db3356b063be53069f73df5`. Its README patch changes the public product name to MaaleNex and describes the passenger-first scope. This closure adopts that naming/scope correction as the current baseline; integration remains separate.

## 5. Genuine omissions and corrected stale findings

| ID | Finding | Closure disposition | Required downstream action |
|---|---|---|---|
| A1-R01 | The A1 plan says G1 PR #1 is still open/unmerged. | **RESOLVED / STALE.** PR #1 is merged; merge commit `ac0e05fba50e375a106ca3eaa33d66aee700fb2b`. Current `main` at closure base is `78884c0f2609edbfc94a24e42d84824bff9eed20`. Post-merge main verification run [#43627374944](https://github.com/akefadaka-git/maalenex/actions/runs/43627374944) passed according to PR #23. | A2 should reconcile later integration branches against the current main SHA, not the obsolete A1 plan snapshot. |
| A1-R02 | Product naming is inconsistent: planning and Android labels say “MaaleNex Moto”, while the newer identity correction says “MaaleNex”. | **DECIDED.** Canonical user-facing name is MaaleNex. Legacy document titles and internal package IDs are historical/technical identifiers, not alternative product brands. | A2 documentation and UI integration should normalize user-facing labels. Do not rename Android application IDs without a separate migration/compatibility review. |
| A1-R03 | The PR #14 role prototype includes motorcycle and heavy-load roles beyond the passenger-first initial release. | **SCOPE-CONSTRAINED.** Passenger is the only initial release role. Other role workspaces are future placeholders and must remain non-operational. | A2 must reconcile navigation and role visibility with the approved passenger-first baseline before A3 implementation. |
| A1-R04 | The PRD and operator onboarding draft retain open Owner decisions. | **RECORDED / NOT AN A1 BLOCKER.** The v1.0 requirements and governance baselines supersede conflicting draft assumptions. Open operational, legal and accountable-party questions remain visible. | Resolve only the relevant items before operator engagement, live services or A5. |
| A1-R05 | The A1 plan records missing runtime authentication, authorization, audit and security controls. | **RECORDED / NOT IMPLEMENTED.** A2 design decisions and contracts do not prove runtime controls exist. | A3 implementation and A4 security/authorization tests must provide exact-head evidence. |
| A1-R06 | Android native bridge A1 specification has no runtime implementation, instrumentation proof or independent security sign-off. | **RECORDED / OUT OF A1 SCOPE.** The design freeze is not runtime readiness. | Keep bridge/plugin work behind its separately approved A3 sequence and independent security review. |

## 6. Downstream open decisions and hard blockers

The following are deliberately not fabricated as resolved by A1:

- Named Jinka operator cohort, terminal authority and documented permission to operate/board.
- Verification evidence requirements and named reviewer/approver roles; no self-approval.
- Verified route, schedule, fare, vehicle, seat-layout and boarding evidence.
- Passenger support ownership, escalation coverage and pilot stop authority.
- Qualified Ethiopian legal/privacy review, lawful basis, retention/deletion, incident handling and data access policy.
- Hosting/data-location and production security architecture.
- Cancellation, refund and disruption policy; no refund promise or execution.
- Any payment provider, collection/custody, settlement, tax, commission or fee model.
- Production backup/restore, monitoring, incident response and operational support evidence.
- Android bridge runtime implementation, physical-device acceptance and independent security review, if that capability remains in scope.

The A2 specification resolves design decisions D01–D07 for the synthetic Passenger MVP design. It does not resolve the external legal, commercial, operator, terminal, support or production dependencies listed above.

## 7. Verification and evidence boundaries

- Product and planning source documents were fetched from their stated PR branches and exact blob SHAs are recorded in §4.
- G1 integration is verified through merged PR #1 and the current main ancestry; PR #23 records post-merge main workflow run #43627374944 as PASS.
- PR #14 exact-head workflow evidence previously recorded for head `8d422a7ff14978f6e9733f0213c712e8f9d16703`: Android shell run [#44](https://github.com/akefadaka-git/maalenex/actions/runs/43599553770), Cloudflare Pages workflow [#65](https://github.com/akefadaka-git/maalenex/actions/runs/43599553779), and brand/frontend run [#54](https://github.com/akefadaka-git/maalenex/actions/runs/43599553823) succeeded. The Cloudflare deployment step was skipped; these runs do not prove deployment.
- A1 documentation closure does not require passenger business-domain runtime tests. No new application tests were run by this documentation-only closure.
- No physical-device acceptance, independent security certification, independent WCAG 2.2 AA audit, legal review, operator/terminal verification, or production-topology test is claimed.

## 8. Closure checklist

- [x] Owner-approved product direction and phased roadmap identified.
- [x] Passenger-first/Jinka-first initial scope and later-freight boundary frozen.
- [x] Requirements baseline v1.0 and governance baseline v1.0 identified as controlling.
- [x] A1 architecture, dependency order, threat model, synthetic acceptance and migration/rollback artifacts reconciled.
- [x] A2 decisions D01–D07 and technical specification identified as approved design inputs, without authorizing A3.
- [x] Android bridge A1 architecture freeze identified as specification-only.
- [x] Stale G1 PR #1 finding corrected against merged history.
- [x] Canonical MaaleNex name and passenger-first release scope reconciled.
- [x] Prototype role expansion explicitly constrained to future scope.
- [x] Unresolved legal, operational, security and production dependencies retained with downstream gates.
- [x] Main branch and production state left unchanged.

## 9. Final disposition

**A1: VERIFIED-CLOSED — 100% OF A1 STAGE SCOPE, WITH RECORDED GAPS.**

The baseline is frozen. Do not reopen settled A1 decisions for unrelated implementation changes. Reopen only the affected decision if authoritative contradictory evidence, a material security issue, or a platform incompatibility is found.

**Next stage:** A2 read-only reconciliation against current `main` SHA `78884c0f2609edbfc94a24e42d84824bff9eed20`. A2 must preserve this A1 baseline, correct stale references, classify the broad feature branches, and return a bounded implementation scope. No A3 code change, PR merge, deployment or production activation is authorized by this closure.
