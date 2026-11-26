# MAALENEX-PRODUCTION-READINESS-A2-RECONCILIATION-001

**Assessment date:** 2026-11-26  
**Status:** A2 READ-ONLY RECONCILIATION — PARTIAL / NOT PRODUCTION-READY  
**Canonical repository:** `akefadaka-git/maalenex`  
**Main snapshot:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Method:** GitHub repository/PR/commit/file/CI evidence inspection only  
**Changes made to application code, migrations, workflows or main:** None

This report is specific to the production-readiness assessment. It does not replace, reopen or amend the frozen `MAALENEX-IA-A1-SPEC-001` or the previously recorded MaaleNex–IROKA A2 disposition.

## 1. Executive disposition

**Production readiness: NOT READY (indicative 2/10).** Current main explicitly enforces synthetic-only development/test operation and rejects production configuration. There is no verified production API hostname, hosted service, production database, production credentials or live deployment evidence.

There is meaningful passenger and operational implementation in open, stacked pull requests, and several child-branch CI workflows pass. Those results do not mean the work is integrated into main or production-ready. The largest blockers are branch-stack integration, migration-head reconciliation, the canonical geographic data contract, unverified API/device connectivity, incomplete notification delivery, and production operational/security evidence.

## 2. Repository baseline

- Repository: public `akefadaka-git/maalenex`; default branch `main`.
- Exact main HEAD at assessment: `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`.
- Existing frozen platform architecture: `docs/architecture/MAALENEX-IA-A1-SPEC-001.md`.
- Main migration tree contains revisions `0001` through `0007`.
- Main backend is FastAPI/Pydantic Settings/SQLAlchemy 2/Alembic/PostgreSQL; frontend is React 18/TypeScript/Vite/Vitest.
- Main README describes an Amharic-first, online-first passenger MVP in development, synthetic-only, with payments/tickets/boarding disabled.

## 3. Main-branch implementation evidence

### 3.1 Backend/runtime

**VERIFIED:** `backend/app/core/config.py` permits only `development` and `test`, requires `synthetic_data_only=true`, PostgreSQL/psycopg, local database host and database name `maalenex_dev`. The main health endpoint returns a static process status and does not check database readiness. Main registers staff auth, admin, booking and passenger catalog routers. OpenAPI/docs are enabled on main development runtime.

**VERIFIED:** Existing staff identity code uses PBKDF2-HMAC-SHA256 with 600,000 iterations, opaque random session tokens stored as digests, eight-hour sessions, CSRF token verification and database-backed failed-login throttling. Guest booking access includes challenge verification, CSRF checks, per-IP limits and grant revocation.

**VERIFIED:** Booking hold service uses an idempotency record, transaction-scoped row locks on trip and seat rows, inventory rechecks, active-hold expiry handling, ETB fare snapshots and audit events. Main includes PostgreSQL booking-concurrency tests.

**GAP:** These controls do not establish production readiness. Main rejects production, has no database-aware readiness route, and lacks production deployment/operations evidence.

### 3.2 Passenger UI

**VERIFIED:** Main `frontend/src/App.tsx` contains the existing Amharic-first passenger journey: published trip search, seat selection, synthetic holds, contact verification, reservation confirmation/QR reference, booking recovery and support. It explicitly tells users that the current environment is synthetic and that a reservation QR is not a travel ticket.

**GAP:** Main remains a relatively compact passenger application and does not contain the later NEXUS application shell, staff workspaces, passenger map or notification inbox. Those capabilities are in unmerged branches. Preserve the current journey and extend it incrementally; do not replace it.

## 4. Open pull-request and branch reconciliation

The passenger/runtime work is a stacked chain, not a set of independent PRs directly based on current main:

| PR | Current branch/head | Base | Reconciliation |
|---|---|---|---|
| [#38](https://github.com/akefadaka-git/maalenex/pull/38) | `feat/passenger-notifications-service` / `046da5e6cb435f2c9baeb2228fc9918287bd584e` | `feat/passenger-wallet-service` / `94d15c8af349bc5b9c3fd9e9eef4a09859e93c45` | Open draft; notification inbox, booking ownership/claim and safe hold cancellation; depends on unmerged wallet branch |
| [#39](https://github.com/akefadaka-git/maalenex/pull/39) | `feat/my-bookings-hold-expiry-notifications` / `63b85d65a2c6224f17c873a9dd6afbb6025cb58e` | PR #38 head | Open draft; My Bookings/hold expiry layer |
| [#40](https://github.com/akefadaka-git/maalenex/pull/40) | `feat/scheduler-operations-rbac-dashboards` / `65fdbe86ad2054f11c2b341643957039ae48d286` | PR #39 head | Open draft; scheduler, RBAC, operations and staff workspaces |
| [#41](https://github.com/akefadaka-git/maalenex/pull/41) | `fix/passenger-password-minimum-six` / `5640e9067aef5c8a1cb9fada32bf5123aa693162` | PR #40 head | Open draft; password minimum correction |
| [#43](https://github.com/akefadaka-git/maalenex/pull/43) | `feat/passenger-backend-connectivity-foundation` / `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | PR #41 head | Open draft; production-capable runtime, Android/API transport and passenger map changes |
| [#44](https://github.com/akefadaka-git/maalenex/pull/44) | `feat/iroka-integration-contract-v1` / `e2e997e1a6d48f8aeb041cd50339bebe4d434a60` | PR #43 head | Open draft; one backend-only IROKA contract commit |

The PR metadata confirms the exact base/head relationships above. The stack must be reconciled in dependency order. Do not cherry-pick or merge PR #43 as if it were a self-contained main-based patch. PR #54 is separate and directly based on current main. PR #53 is a separate MITP tracking/map branch.

### 4.1 PR #43 production-runtime proposal

PR #43 adds:
- Production configuration validation requiring `APP_ENV=production`, `SYNTHETIC_DATA_ONLY=false`, secure cookies, remote PostgreSQL credentials, PostgreSQL TLS and exact HTTPS CORS origins.
- A non-root Docker image and production environment template.
- Separate liveness and database-aware readiness endpoints.
- Production OpenAPI/docs disabling.
- Separate scheduler worker configuration.
- Passenger map coordinates/route geometry and Android API-origin/CSP transport work.

These are useful implementation candidates, but remain in an open draft stack. The exact PR #43 head `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` had no PR-triggered workflow runs returned and no combined status checks returned in this inspection. PR #44's child head passed one backend workflow; that is not an exact-head PR #43 verification.

The PR #43 runtime document itself lists remaining operational gates: backups/restore, object-storage configuration if enabled, monitoring/alerting, rate limits, trusted proxy configuration, end-to-end passenger tests, independent security review and separately authorized deployment.

### 4.2 PR #54 About/API-origin/Android increment

[PR #54](https://github.com/akefadaka-git/maalenex/pull/54) is open/draft, based on current main at `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`, with exact head `34e4aab8d84561828fb0a1bc8bdce9f914bc32ca`.

Exact-head workflow evidence:
- Run [45765359641](https://github.com/akefadaka-git/maalenex/actions/runs/45765359641): frontend tests, TypeScript check and Vite build succeeded; deployment steps skipped.
- Run [45765359628](https://github.com/akefadaka-git/maalenex/actions/runs/45765359628): frontend tests/build, Capacitor sync and Android debug APK assembly/artifact verification succeeded.

**Not verified:** `MAALENEX_TEST_API_BASE_URL` was not configured, so the APK is a UI preview and server-backed passenger actions do not connect from that standalone WebView. Cross-origin API, CORS, cookie, CSRF and physical-device acceptance on this exact APK remain NOT VERIFIED / NOT RUN. No deployment occurred.

## 5. Notification capability reconciliation

Main has no passenger notification domain or notification router.

The unmerged PR #38/#43 stack adds an authenticated, passenger-owned in-app inbox, read/unread state, deduplication and preferences. The inspected model has only `in_app_enabled`, `email_enabled` and `sms_enabled`; email/SMS default false. The preferences endpoint explicitly forces email and SMS false and reports delivery unavailable.

**NOT FOUND in the inspected PR #43 tree:** WhatsApp or Telegram channels, provider adapters, a transactional delivery outbox, delivery worker, provider callback verification, delivery receipts, dead-letter handling or channel-specific consent records. Email/SMS delivery is described as disabled. The current scheduler worker is for booking-hold expiry, not notification delivery.

**Recommended target:** in-app as the durable source of truth; WhatsApp Business as preferred outbound transactional channel for users who explicitly opt in; SMS for OTP/fallback; email for formal/security correspondence; Telegram only as an optional user-linked channel. Implement provider-neutral adapters and an outbox before connecting providers. Do not activate a provider or incur cost under this assessment.

## 6. Geographic/map and migration reconciliation

Three distinct approaches appear in the open branches:

1. PR #43 adds nullable latitude/longitude and JSON route geometry to the operational schema and a passenger map component that loads Google Maps using `VITE_GOOGLE_MAPS_API_KEY`. This requires a separately configured external API key and is not the selected self-hosted-first direction.
2. PR #53 adds a MapLibre tracking proof of concept, Martin vector tiles and a separate local PostGIS map database. Its documentation says the map database is separate from the application database; the CI job verifies synthetic road/polygon fixtures, not a real OSM extract or a browser-rendered operational map.
3. The platform architecture and prior Owner-approved direction call for one canonical PostGIS in the primary PostgreSQL platform database, with `geo`, `geo_public`, `geo_internal`, `geo_audit` schemas, MapLibre/Martin and tenant-scoped public/internal access controls.

These are not yet reconciled. The PR #43 passenger map also relies on Google Maps, while PR #53 is an isolated tracking/map proof of concept. Neither proves the canonical shared geographic model, RLS/tenant policy or licensed authoritative route data.

### 6.1 Alembic conflict

- PR #43's passenger/runtime stack contains `0008_wallet_double_entry_ledger`, whose `down_revision` is `0007_operator_invites_support`, followed by the later wallet/passenger/scheduler/fleet/map revisions through `0018_koybe_boarding_point`.
- PR #53 contains a different `0008_mitp_tracking`, also with `down_revision = 0007_operator_invites_support`.

Combining these histories without an explicit migration-graph reconciliation creates parallel Alembic heads. This is a blocking integration issue. Do not apply production migrations until one authoritative graph, model parity and upgrade/downgrade path are verified.

PR #43's `0017_passenger_map_geometry` stores route geometry as JSON and location coordinates as floating-point columns; it is not the canonical PostGIS schema. PR #43's `0018_koybe_boarding_point` registers the supplied Koybe point as draft data and deliberately fails on ambiguous duplicate location/terminal records. Route geometry and stop sequence remain unverified; do not publish fabricated route traces.

## 7. Exact-head CI evidence inspected

| PR / SHA | Evidence found | Limits |
|---|---|---|
| #40 / `65fdbe86ad2054f11c2b341643957039ae48d286` | NEXUS UI, backend foundation and Android shell workflows succeeded (runs 44996800691, 44996800678, 44996800889) | Branch remains stacked and unmerged |
| #41 / `5640e9067aef5c8a1cb9fada32bf5123aa693162` | NEXUS UI workflow succeeded (run 45001037944) | No backend exact-head run found |
| #43 / `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | No PR-triggered workflow run or combined status returned | Exact-head CI evidence missing |
| #44 / `e2e997e1a6d48f8aeb041cd50339bebe4d434a60` | Backend workflow succeeded (run 45034367684), including container build, backend tests, PostgreSQL migration/parity/downgrade/re-upgrade and HTTPS session/CORS smoke flow | Child PR head, not PR #43 head or a live service |
| #53 / `6d6a2de592381cd751c52f40824a9da1dd17b07a` | Backend, frontend and local PostGIS/Martin proof-of-concept workflows succeeded (runs 45155547829, 45155547922, 45155547849) | Synthetic fixtures; real OSM import and browser map acceptance not run; branch is behind current main |
| #54 / `34e4aab8d84561828fb0a1bc8bdce9f914bc32ca` | Frontend build and Android debug APK workflows succeeded (runs 45765359641, 45765359628) | No configured test API origin; physical-device/API acceptance not run |

No workflow was dispatched or rerun during this assessment.

## 8. Production gaps and acceptance blockers

| Area | Status | Evidence / required closure |
|---|---|---|
| Production API runtime | MISSING on main | Main rejects production; reconcile and verify PR #43 runtime |
| PR stack integration | UNRESOLVED | Reconcile PRs #38–#44 and their base dependencies before integration |
| Alembic graph | BLOCKED | Resolve competing 0008 branches; verify one head, metadata parity, clean upgrade/downgrade |
| Passenger API end-to-end | PARTIAL | Verify real web/API and Android/API session, cookies, CORS, CSRF on exact build |
| Android physical device | NOT RUN | Install and accept exact APK on target handset |
| Passenger map | UNRESOLVED | Adopt canonical PostGIS/MapLibre architecture; source-verify route geometry and stop order |
| Notifications | PARTIAL | In-app inbox exists only in unmerged stack; add outbox and provider adapters/consent |
| WhatsApp/SMS/email/Telegram | MISSING | No provider selected or activated; sandbox, compliance and cost evaluation needed |
| NEXUS UI | PARTIAL / UNMERGED | Design-system v2.0 and workspaces are on unmerged branch; reconcile with main passenger UI |
| Backups/restore | NOT VERIFIED | Evidence of backup policy and witnessed restore required |
| Monitoring/alerting | NOT VERIFIED | Production metrics, redacted logs, alert thresholds and incident runbook required |
| Independent security review | NOT RUN | Complete after implementation/integration, before A5 |
| Legal/privacy/operational readiness | NOT VERIFIED | Data-protection, transport, provider and commercial-operation gates remain separate |
| Production deployment | NOT RUN / NOT AUTHORIZED | No verified host, production DB, credentials or deployment evidence |

## 9. A2 disposition and carry-forward

**A2 production-readiness reconciliation: PARTIAL — NOT CLOSED.** Repository and exact-head evidence is sufficient to identify the main blockers, but not to certify the complete stacked implementation or close all acceptance questions.

Priority carry-forwards:
1. Reconcile the full PR #38 → #39 → #40 → #41 → #43 → #44 stack against current main without discarding unrelated work.
2. Reconcile the PR #53 tracking branch and resolve the parallel Alembic heads.
3. Implement the Owner-approved canonical PostGIS schema and tenant-scoped access contract only after the integration design is frozen.
4. Reconcile the Google Maps passenger map with the self-hosted MapLibre/Martin direction and verified route-source evidence.
5. Complete passenger API connectivity and exact-build physical-device acceptance.
6. Specify and later implement transactional notification outbox, consent and channel adapters; WhatsApp Business is the preferred outbound candidate, not an activated provider.
7. Close production operations/security/privacy evidence before A4/A5.

**No A3 code implementation, migration execution, provider activation, merge or deployment is performed or authorized by this A2 report.** A3 requires separate explicit authorization. A5 remains a separate Owner approval gate.


## 10. Follow-up A2: full dependency chain and Alembic graph (2026-11-26)

This section supersedes any shorthand that described PRs #38–#44 as the entire passenger stack. The upstream dependency chain begins earlier:

| PR | Head branch | Base branch | Role in dependency chain |
|---|---|---|---|
| [#32](https://github.com/akefadaka-git/maalenex/pull/32) | `feat/passenger-identity-service` | `feat/acceptance-remediation` | Passenger registration and sessions |
| [#33](https://github.com/akefadaka-git/maalenex/pull/33) | `feat/passenger-journey-search` | PR #32 head | Published journey search |
| [#34](https://github.com/akefadaka-git/maalenex/pull/34) | `feat/passenger-booking-flow` | PR #33 head | Seat selection and reservation |
| [#35](https://github.com/akefadaka-git/maalenex/pull/35) | `feat/passenger-support-service` | PR #34 head | Passenger support |
| [#36](https://github.com/akefadaka-git/maalenex/pull/36) | `feat/passenger-reports-complaints` | PR #35 head | Passenger reports/complaints |
| [#37](https://github.com/akefadaka-git/maalenex/pull/37) | `feat/passenger-wallet-service` | PR #36 head | ETB ledger and passenger wallet |
| [#38](https://github.com/akefadaka-git/maalenex/pull/38) | `feat/passenger-notifications-service` | PR #37 head | In-app notification inbox and booking ownership/claim |
| [#39](https://github.com/akefadaka-git/maalenex/pull/39) | `feat/my-bookings-hold-expiry-notifications` | PR #38 head | My Bookings and hold expiry |
| [#40](https://github.com/akefadaka-git/maalenex/pull/40) | `feat/scheduler-operations-rbac-dashboards` | PR #39 head | Scheduler, RBAC and staff workspaces |
| [#41](https://github.com/akefadaka-git/maalenex/pull/41) | `fix/passenger-password-minimum-six` | PR #40 head | Password policy correction |
| [#43](https://github.com/akefadaka-git/maalenex/pull/43) | `feat/passenger-backend-connectivity-foundation` | PR #41 head | Runtime, Android/API connectivity and passenger map |
| [#44](https://github.com/akefadaka-git/maalenex/pull/44) | `feat/iroka-integration-contract-v1` | PR #43 head | Backend-only IROKA contract |

All PRs #32–#44 inspected here remain open/draft. PR #37's description reports backend/frontend exact-head CI success for its own head, but it is not merged into main. The branch chain is a set of dependent slices and must be treated as one integration program with staged review and exact-SHA verification, not as independent merge candidates. PR #43's comparison to current main is 672 commits ahead and 6 behind, with merge base `78884c0f2609edbfc94a24e42d84824bff9eed20`; this makes a direct merge/rebase decision especially sensitive to unrelated intervening history.

### 10.1 Exact Alembic graph

The current main migration head is `0007_operator_invites_support`.

The passenger/runtime chain on PR #43 is linear:

`0001_g1_foundation` → `0002_identity_audit_orgs` → `0003_passenger_domains` → `0004_staff_auth_controls` → `0005_booking_access_challenges` → `0006_guest_access_rate_limits` → `0007_operator_invites_support` → `0008_wallet_double_entry_ledger` → `0009_passenger_identity` → `0010_passenger_support_cases` → `0011_passenger_reports` → `0012_passenger_wallet` → `0013_passenger_notifications` → `0014_verified_booking_ownership` → `0015_scheduler_operations_rbac` → `0016_fleet_compliance` → `0017_passenger_map_geometry` → `0018_koybe_boarding_point`.

The PR #53 tracking branch independently adds `0008_mitp_tracking`, whose `down_revision` is also `0007_operator_invites_support`. It is not a duplicate revision identifier; it is a second child of the same parent. When both feature histories are combined without a merge revision, Alembic will discover two heads: `0018_koybe_boarding_point` and `0008_mitp_tracking`.

The migration bodies create distinct tables: the wallet branch creates `ledger_accounts`, `ledger_transactions` and `ledger_postings`; the tracking branch creates `tracking_devices`, `vehicle_device_assignments` and `vehicle_telemetry`, plus tracking permissions. No direct table-name collision was found in these two migration bodies. However, both branches modify `backend/app/db/model_registry.py`, so model imports must be combined rather than one side overwriting the other.

**Preferred migration reconciliation candidate (design only; not implemented):** preserve both existing immutable revision files and add a no-op Alembic merge revision after the passenger chain, with `down_revision = ("0018_koybe_boarding_point", "0008_mitp_tracking")`. This creates a single descendant of both heads without renumbering or rewriting either historical migration. Before accepting this approach, verify that Alembic resolves one head, that the merge revision upgrades from a clean `0007` database through both branches, that downgrade/re-upgrade is deterministic, and that model metadata parity and migration checks pass. If any database has already applied either branch, inventory its actual `alembic_version` state first; do not assume an empty database. No migration has been executed in this assessment.

### 10.2 Tracking branch freshness and scope

PR #53 is based on main SHA `1daf201bfb407280604534e28440b9fa83178efb`, not current main. Compared with current main `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`, its head `6d6a2de592381cd751c52f40824a9da1dd17b07a` is 97 commits ahead and 1 behind, with merge base equal to its recorded base SHA. The 1-commit divergence must be reconciled before accepting it.

PR #53 adds tracking device credentials, vehicle/device assignments, synthetic telemetry ingestion/simulation, a tracking API and a MapLibre/Martin proof of concept. The inspected tracking model stores coordinates as numeric latitude/longitude; it does not itself establish the canonical PostGIS route/stop model, geographic schema boundaries or tenant row-level security. Its local map proof-of-concept uses a separate PostGIS database and synthetic fixtures. It is not a production geographic platform.

### 10.3 Integration order (proposed, not authorized)

1. Keep current `main` immutable during reconciliation.
2. Reconcile the upstream passenger chain #32–#44 in dependency order, starting with its actual base `feat/acceptance-remediation`; inspect that base and every PR diff for overlap with current main before choosing a merge strategy.
3. Preserve and verify the wallet ledger, passenger ownership, booking concurrency and support invariants; keep all real-money operations disabled.
4. Reconcile PR #53 onto the selected passenger integration candidate, merge the two Alembic heads through a dedicated migration revision, combine model registry imports and test both branch upgrade paths from the shared `0007` parent.
5. Replace the isolated map PoC and Google Maps passenger map with one explicitly approved shared PostGIS/MapLibre/Martin design only after route/stop evidence and data licensing are resolved.
6. Run exact-head backend/frontend/Android and database migration verification on the resulting integration candidate. Do not infer success from child-branch CI.
7. Keep PR #54 separate until its About/API-origin work is reviewed against the chosen passenger UI integration candidate; it is not a substitute for passenger API/device acceptance.

This is a proposed reconciliation sequence only. It does not authorize branch rebasing, cherry-picking, code edits, migration execution, merge or deployment.


## 11. Upstream integration ancestry follow-up (2026-11-26)

The passenger implementation stack extends earlier than PR #32:

| PR | Head branch | Base branch | State / role |
|---|---|---|---|
| [#30](https://github.com/akefadaka-git/maalenex/pull/30) | `feat/full-platform-clean` / `ec5f8060855869c7eba8905e87216d5c8ada93b9` | `feat/a3-passenger-only-integration` / `bab7aa9f6eb202a58415e54ad0c6aae67a995a66` | Open draft; full mobility/digital-services experience |
| [#31](https://github.com/akefadaka-git/maalenex/pull/31) | `feat/acceptance-remediation` / `9ece201039df2ad2426637e0f8aa93310baa6b00` | PR #30 head | Open draft; mobile acceptance remediation |
| [#32](https://github.com/akefadaka-git/maalenex/pull/32) | `feat/passenger-identity-service` / `83bb469057a8246f0a330430573646377d5b11f1` | PR #31 head | Open draft; passenger identity/session foundation |
| [#33–#44](#10-follow-up-a2-full-dependency-chain-and-alembic-graph-2026-11-26) | As recorded above | Sequential dependent PR heads | Open drafts; passenger capability/runtime chain |

PR #29, which had a similar full-platform experience scope, is closed and described as superseded; it is not an active integration candidate.

PR #30's head compared with current main is 150 commits ahead and 6 behind, with merge base `78884c0f2609edbfc94a24e42d84824bff9eed20`. PR #31 and PR #32 also compare against current main from that same merge base and are 165 and 196 commits ahead respectively, each 6 behind. This confirms the entire #30–#44 stack shares a substantially older ancestry point than current main. The PR base metadata is internally consistent within the stack, but it does not remove the need to reconcile the six later main commits and overlapping file changes.

**Updated integration finding:** the candidate passenger platform is a long-lived stacked branch series (#30–#44), not a small feature PR. It must be treated as a controlled integration/reconciliation effort against current main, with a file-level ownership matrix and preservation of all post-merge-base main changes. No direct merge, rebase or cherry-pick is recommended until that matrix and the precise desired baseline are reviewed.


## 12. Main-branch divergence content audit (2026-11-26)

The six commits between the passenger stack's common merge base `78884c0f2609edbfc94a24e42d84824bff9eed20` and current main are:

1. `b931e4decf71a2b8f27aab9ac5770fb55bf5c31e` — correct product name to MaaleNex.
2. `0408df1c0b9b18b75664f362497fde3c21cec351` — add MITP A1 specification with Owner decisions.
3. `e32c6b37a8d0642349422285f30735c882568269` — record Owner approval and close MITP A1 baseline.
4. `0ec30fe935c16fe5dfe3c5e83c8bd533889a6952` — align MITP A1 status with approved closure.
5. `1daf201bfb407280604534e28440b9fa83178efb` — reconcile MITP stage-gate language with Owner authorization.
6. `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` — freeze MaaleNex invisible-intelligence A1 specification.

The GitHub compare response shows that these six commits modify only `README.md`, add `docs/architecture/MITP-A1-SPECIFICATION-v1.0.md`, and add `docs/architecture/MAALENEX-IA-A1-SPEC-001.md`. No backend, frontend, Android, migration, workflow or application source files changed on main in this six-commit interval.

**Impact assessment:** the #30–#44 stack is old and very large, but its six-commit lag behind current main is documentation/product-governance drift, not six intervening application-code changes. The application-level integration risk remains in the large stacked feature set itself and in shared-file overlaps between feature branches. The README does overlap: current main retains the passenger-MVP/synthetic-only/development-only description, while PR #30's README describes a broader full-platform UI and marks identity/map/support as unconnected foundations. Any integration must preserve the stricter current governance and avoid overstating branch functionality. Do not simply take either README wholesale.

PR #53 is based exactly on `1daf201bfb407280604534e28440b9fa83178efb`, the fifth of those six main commits. Its one-commit lag is therefore the final MaaleNex A1 freeze commit `c988b9d...`; the PR #53 compare shows no application-code commits missing from its base interval. Its own branch does include the MITP A1 specification and A3 implementation record. Preserve the frozen MaaleNex A1 specification and MITP A1 closure when reconciling that branch.

**Updated finding:** no evidence of post-merge-base application-code changes on main was found. A controlled rebase/merge of the feature stack may be technically feasible after review, but the branch stack's large application changes, README semantics, PR dependency order, and the Alembic two-head issue still require a file-level integration plan and exact-SHA verification. This content audit does not authorize rebase, cherry-pick, merge or implementation.

## 13. File-level integration ownership matrix and branch topology update (2026-11-26)

A fresh GitHub metadata and per-PR compare inspection was performed for PRs #30–#44, #53 and #54. All 17 PRs were open and draft at the time of inspection. No PR was merged, no workflow was dispatched or rerun, and no application branch was modified.

### 13.1 Confirmed dependency topology

- #30 → #31 → #32 → #33 → #34 → #35 → #36 → #37 → #38 → #39 → #40 → #41 is the principal stacked passenger/platform chain.
- #42 (feat/passenger-backend-functional-foundation, head d3011e288c7487ebdca824d8c4dcd998ad3cfc7b) and #43 (feat/passenger-backend-connectivity-foundation, head 20c855b881e30aacf97dbb0d8fbb85755eb7bdf5) are sibling branches: both use PR #41 head 5640e9067aef5c8a1cb9fada32bf5123aa693162 as their base. They are not sequential. Their intended overlap and selection/combination policy must be decided before A3.
- #44 (head e2e997e1a6d48f8aeb041cd50339bebe4d434a60) is based on #43.
- #53 is a separate MITP branch based on main SHA 1daf201bfb407280604534e28440b9fa83178efb.
- #54 is a separate passenger About/API-origin/Android branch based on current main SHA c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78.

### 13.2 High-priority shared-file ownership

| Path | PRs touching path | Ownership and reconciliation rule |
|---|---|---|
| frontend/src/App.tsx | #30–#41, #43, #54 | Highest-risk UI integration point. Preserve existing passenger flow; integrate dependent passenger additions in order; review #54 About page separately. |
| frontend/src/App.test.tsx | #30–#38, #43, #54 | Reconcile tests against the integrated UI and API contract; do not select one branch's file wholesale. |
| frontend/src/passenger-api.ts | #32–#39, #43 | One canonical client contract for identity, journeys, booking, support, reports, notifications and connectivity. |
| backend/app/db/model_registry.py | #30, #32, #35, #36, #38, #40, #53 | Combine all approved model imports; preserve wallet/passenger and tracking registrations. |
| backend/app/main.py | #32, #35–#40, #43, #53 | One router/lifecycle registry; reconcile startup/shutdown and scheduler registration. |
| backend/app/core/config.py | #32, #40, #43, #53 | Consolidate settings and fail-closed synthetic-only/production configuration rules. |
| backend/migrations/versions/* | #30, #32, #35–#38, #40, #43, #53 | Preserve immutable migrations; resolve parallel 0008 heads with an explicit merge revision after inventorying database revision state. |
| .github/workflows/g1-backend-verification.yml | #30–#32, #34–#40, #42, #43, #53 | Consolidate one authoritative backend verification workflow; no dispatch/rerun during A2. |
| .github/workflows/nexus-ui-verification-v2.yml | #30, #31, #35, #37–#40 | Consolidate UI verification and preserve exact-SHA evidence. |
| .github/workflows/android-shell-verification.yml | #31, #40, #42, #43 | Reconcile Android build/CSP/geolocation verification. |
| android/app/src/main/java/com/maalenex/moto/MainActivity.kt | #30, #31, #43 | Consolidate WebView navigation, API-origin and geolocation behavior; later verify on physical hardware. |
| android/app/src/main/AndroidManifest.xml | #42, #43 | Reconcile network/security permissions and exported-component policy. |
| frontend/src/styles.css | #30, #35, #38, #39, #40, #43, #54 | Integrate shared passenger shell and design system without regressions. |
| frontend/src/main.tsx | #30, #31, #53 | Reconcile app entry point and tracking registration. |
| frontend/vite.config.ts | #43, #53 | Reconcile API proxy/build configuration and map-related build settings. |
| backend/app/routers/admin.py | #35, #36, #40 | Preserve admin authorization and integrate passenger support/report and staff operations routes. |
| backend/app/routers/passenger_auth.py | #32, #38, #41 | Preserve identity/session behavior and notification/ownership integration. |
| backend/app/domains/wallet/models.py | #30, #37 | Reconcile base double-entry ledger model with passenger wallet extension. |
| backend/app/domains/bookings/models.py | #38, #40 | Preserve booking ownership/inventory invariants while integrating fleet/operations links. |
| backend/app/jobs/scheduler_worker.py | #40, #43 | Preserve scheduler task boundaries and production worker runtime. |

A shared path indicates multiple PRs change the same path; it does not prove a textual conflict. A three-way content review is required before integration. This matrix is an ownership-risk inventory, not authorization to modify any listed file.

### 13.3 PR-level changed-file inventory

| PR | Files changed | Distinct responsibility |
|---|---:|---|
| #30 | 32 | Full platform shell, Android shell, wallet ledger, UI and workflows |
| #31 | 9 | Mobile acceptance remediation |
| #32 | 13 | Passenger identity and sessions |
| #33 | 3 | Passenger journey search UI/API |
| #34 | 6 | Passenger seat selection and booking flow |
| #35 | 13 | Passenger support |
| #36 | 11 | Reports and complaints |
| #37 | 10 | ETB wallet |
| #38 | 26 | Notifications, booking ownership and client integration |
| #39 | 11 | My Bookings and hold expiry |
| #40 | 38 | Scheduler, RBAC, fleet/operations and staff workspaces |
| #41 | 3 | Passenger password policy correction |
| #42 | 4 | Android/API functional foundation |
| #43 | 33 | Backend runtime, Android/API connectivity and passenger map |
| #44 | 4 | Fail-closed IROKA integration contract |
| #53 | 32 | MITP tracking and self-hosted map proof of concept |
| #54 | 11 | About page, API URL resolver and Android debug packaging |

### 13.4 A2 file-level disposition

- CLEAN-CARRY CANDIDATES: newly added, isolated documentation and feature files may be carried forward only after dependency, licensing, security and product-scope review. A new file is not automatically approved for production.
- CONTROLLED-INTEGRATION REQUIRED: App.tsx, App.test.tsx, passenger-api.ts, model_registry.py, main.py, config.py, admin.py, authentication, booking models, scheduler worker, Android shell/manifest, Vite config and shared workflows.
- MIGRATION-BLOCKED: the wallet/passenger migration chain and MITP tracking migration must be reconciled as one Alembic graph; no revision rewrite or migration execution is authorized.
- SEPARATE REVIEW: PR #54 About/API origin and PR #53 map PoC should remain separate review units until the passenger and geographic target architectures are frozen.
- NOT ACCEPTED AS PRODUCTION EVIDENCE: synthetic tracking fixtures, local PostGIS/Martin PoC, UI-only APK behavior and child-branch CI do not prove live passenger operations.

## 14. Development and deployment schedule baseline (planning estimate, not committed dates)

The following durations are estimates from the current repository state. They are not completion promises, scheduled GitHub milestones or Owner approvals. Durations assume timely access to authoritative route/stop, legal, privacy and hosting evidence and no major rework.

| Stage | Work package | Entry condition | Estimate | Exit evidence |
|---|---|---|---:|---|
| A1 — Assessment/specification/freeze | Confirm passenger MVP scope, platform architecture, map/notification decisions, acceptance criteria and non-goals | Owner review of current A1 drafts | 3–5 working days | Explicit Owner approval and frozen version/hash |
| A2 — Read-only reconciliation | Complete PR/file ownership review, dependency graph, Alembic plan, exact-SHA CI inventory, security and operational gap register | A1 scope available for reconciliation | 5–10 working days | Reconciled A2 report with PASS/PARTIAL/MISSING/UNRESOLVED labels; Owner closure decision |
| A3 — Implementation | Integrate approved passenger chain, resolve sibling #42/#43 policy, migration graph, map architecture, notifications and runtime; retain synthetic-only restrictions until separately approved | A1 frozen and A2 closed; explicit A3 authorization | 3–6 weeks | Reviewed implementation candidate, migration plan and exact commit SHAs |
| A4 — Verification/acceptance | Backend/frontend regression, migration upgrade/downgrade, security review, API/device session tests, route/map validation, backup/restore and operational acceptance | A3 implementation complete and candidate frozen | 1–2 weeks | Exact-SHA test evidence, independent security review and signed acceptance/gap disposition |
| A5 — Deployment | Provision approved hosting, secrets, production DB, monitoring, backup/restore, migration and rollback; controlled release | A4 accepted and separate explicit A5 authorization | 3–7 working days | Deployment SHA, environment evidence, migration record, smoke checks, monitoring and rollback evidence |

Indicative planning horizon: approximately 6–10 weeks from A1 review through an A4-ready release candidate, plus the A5 deployment window. This is conditional and may expand if integration, regulatory or independent security findings require remediation. A5 is not included in any automatic authorization.

No deployment date is committed. No production host, production database, provider credentials, production secrets, or operational approval has been verified in this A2 inspection. No commercial operation, payment collection, ticket issuance or passenger boarding is authorized by this schedule.


## 15. Sibling PR #42 / #43 exact-head reconciliation (2026-11-26)

### 15.1 Repository facts

| Item | PR #42 | PR #43 |
|---|---|---|
| Title | Enable passenger Android API connectivity foundation | Connect passenger Android shell to production-capable backend runtime |
| Base branch | fix/passenger-password-minimum-six | fix/passenger-password-minimum-six |
| Exact base SHA | 5640e9067aef5c8a1cb9fada32bf5123aa693162 | 5640e9067aef5c8a1cb9fada32bf5123aa693162 |
| Current head SHA inspected | d3011e288c7487ebdca824d8c4dcd998ad3cfc7b | 20c855b881e30aacf97dbb0d8fbb85755eb7bdf5 |
| Changed files | 4 | 33 |
| Additions / deletions | 8 / 5 | 976 / 91 |
| State | Open, draft, unmerged | Open, draft, unmerged |
| Reviews / inline threads | None returned | None returned |

Both PRs are sibling branches from the same #41 parent. Neither contains the other's commits. PR #43 is a much broader integration candidate, not a child of #42.

### 15.2 PR #42 exact file ownership

1. `.github/workflows/android-shell-verification.yml`: adds `fix/passenger-password-minimum-six` to the PR base-branch filter and adds a manifest assertion for Android INTERNET permission.
2. `.github/workflows/g1-backend-verification.yml`: adds the same parent base branch to the PR trigger filter.
3. `android/app/src/main/AndroidManifest.xml`: adds INTERNET permission.
4. `backend/tests/test_passenger_identity.py`: moves Pydantic ValidationError and PassengerRegistration imports to module scope; the password-minimum test still uses try/except.

### 15.3 PR #43 exact file ownership and overlap

PR #43 changes the same four files above plus 29 other files. Its corresponding changes:
- Android manifest: INTERNET, ACCESS_NETWORK_STATE, ACCESS_COARSE_LOCATION and ACCESS_FINE_LOCATION permissions.
- Android MainActivity and WebView geolocation policy: permission prompt, trusted-origin checks and cookie handling for cross-origin API sessions.
- Android and backend workflows: push triggers for the #43 feature branch, API-origin/CSP checks, Android build/emulator/SBOM/OSV coverage, Docker image build and HTTPS API/CORS/CSRF smoke steps.
- Backend runtime: production configuration validation, database-backed readiness endpoint, Dockerfile, scheduler-worker entry point, deployment template and runtime documentation.
- Passenger map: route/stop coordinate and geometry API types, route-list request, Google Maps renderer, map marker selection and route polyline behavior.
- Passenger identity test: also changes the password test to pytest.raises; this is a cleaner form than #42's try/except version.

The #43 PR description still states a previous head SHA (409a7d03efe3e07f71523f12b64d4e0109c54c1e), while current PR metadata reports 20c855b881e30aacf97dbb0d8fbb85755eb7bdf5. The PR description is stale and should be corrected by its maintainer before review/acceptance.

### 15.4 Intended ownership decision for A3 planning

- **PR #43 is the preferred integration owner for the broader Android/API runtime and passenger-map foundation**, subject to exact-head verification, security review and Owner-approved A3 scope. It includes the INTERNET permission and extends Android behavior beyond #42.
- **PR #42 should not be merged as a separate sibling integration on top of #43.** Its narrow contribution is useful as independent baseline evidence and as a reference for the missing PR-base workflow filter. Its manifest and identity-test changes are duplicated or superseded in #43.
- Preserve the best version of the identity test from #43 (`pytest.raises`) rather than carrying both sibling edits.
- Reconcile workflow trigger filters explicitly. PR #42 added `fix/passenger-password-minimum-six` to PR branch filters. PR #43's pull_request branch filters do not include that base branch, although its workflows add push triggers for the #43 feature branch. Do not assume a PR-triggered check will run for #43 merely because its workflow file exists.
- PR #43's Android manifest adds location permissions. Retain them only with a documented permission purpose, trusted-origin boundary, user-consent UX, denial/fallback behavior and tests. Do not treat manifest declarations as proof of working or compliant location capture.
- PR #43 is not accepted for integration until its own exact head has passing backend and Android evidence. PR #42's green runs cannot be transferred to #43.

### 15.5 Exact-head verification evidence

PR #42 exact head `d3011e288c7487ebdca824d8c4dcd998ad3cfc7b` has two successful pull-request workflow runs:
- [Android shell verification — run 45002401214](https://github.com/akefadaka-git/maalenex/actions/runs/45002401214): Android build/lint, frontend tests/build, manifest and CSP checks, emulator install/launch, Android unit tests, OSV scan and artifact uploads all completed successfully. The generated Gradle metadata commit job was skipped.
- [G1 backend verification — run 45002401119](https://github.com/akefadaka-git/maalenex/actions/runs/45002401119): Ruff, backend tests, PostgreSQL migration upgrade, Alembic metadata parity and full downgrade/re-upgrade completed successfully.

PR #43 exact head `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5`: the pull-request-triggered workflow-run lookup returned no runs, and the commit status endpoint returned no status entries. This does not prove that no push-triggered workflow ever ran; the available workflow lookup is PR-triggered only. Exact-head PR verification is therefore NOT EVIDENCED. No workflow was dispatched or rerun.

## 16. Alembic graph and model registry reconciliation

### 16.1 Confirmed migration fork

Two different revision IDs both descend directly from `0007_operator_invites_support`:

- `0008_wallet_double_entry_ledger` (passenger/platform chain): creates `ledger_accounts`, `ledger_transactions`, and `ledger_postings` with double-entry and idempotency constraints.
- `0008_mitp_tracking` (PR #53): creates `tracking_devices`, `vehicle_device_assignments`, and `vehicle_telemetry`, including unique active-device/vehicle assignment indexes and tracking permissions.

The two revisions have distinct Alembic revision IDs and distinct primary table sets. They are parallel heads, not a filename collision. The passenger chain continues from the wallet revision through passenger identity, support, reports, wallet, notifications, booking ownership, scheduler/RBAC and fleet compliance, then:
`0017_passenger_map_geometry` → `0018_koybe_boarding_point`.
The map revision adds latitude/longitude/source fields to locations and JSON geometry/source fields to routes. The Koybe revision records the operator-confirmed terminal pin (5.7678630, 36.7985890) and intentionally preserves the created terminal/coordinates on downgrade.

### 16.2 Safe graph reconciliation candidate — NOT IMPLEMENTED

After confirming all deployed and non-production database revision states, preserve both existing migration files and add a no-op Alembic merge revision whose parents are:
`down_revision = ("0018_koybe_boarding_point", "0008_mitp_tracking")`.

This is a candidate graph design only. Before any migration is created or executed:
1. Inventory every database's `alembic_version` rows and backup/restore status.
2. Verify both branches upgrade cleanly from the common `0007_operator_invites_support` parent.
3. Verify the merge produces exactly one Alembic head.
4. Run metadata parity, full upgrade, downgrade and clean re-upgrade against disposable PostgreSQL.
5. Confirm downgrade semantics for the Koybe data-preserving revision and all tracking tables/permissions.
6. Verify no other PR or downstream branch adds a third head.

No database state was queried and no migration was run in this A2 inspection. Applied revision state is UNKNOWN.

### 16.3 Model registry union

The #43 passenger/runtime branch's `backend/app/db/model_registry.py` includes audit, bookings, catalog, fares, fleet, identity, passenger identity, notifications, operations, organizations, reservations, support, passenger support, passenger reports, trips and wallet models.

PR #53 directly adds the tracking domain model import to its older registry, alongside the baseline domain imports. It does not carry all the passenger-only imports present in the #43 stack. The correct integration rule is a union of the complete #43 registry and the tracking import:
- retain all #43 passenger/platform imports;
- add `app.domains.tracking.models`;
- avoid dropping passenger identity, notifications, operations, passenger support, passenger reports or wallet imports;
- run Alembic metadata parity and model-registration tests after integration.

Correction to Section 13: PR #43 does not itself list model_registry.py among its 33 changed paths; it inherits the passenger registry from its parent stack. PR #53 is the branch that directly changes the registry for tracking. The required combined result is still the union described above.

### 16.4 Config and application registration union

- **config.py:** PR #43 adds a production-capable validation path while preserving strict synthetic/local-only development and test rules. PR #53 adds a SecretStr-based MITP device encryption key and accessor but only permits development/test. Reconcile by retaining #43's runtime validation and adding the tracking secret safely; require the key when the tracking credential-encryption feature is enabled. Never place the key in source, workflow logs or client bundles.
- **main.py:** retain #43's passenger routers, readiness/liveness split, exact-origin credentialed CORS, allowed methods/headers and production-disabled interactive API docs; add the tracking router and its required MITP headers/methods. Keep tracking authorization staff-only. Do not replace the passenger router set with PR #53's older minimal router list.
- **Alembic env/model registry:** import the combined registry before metadata is inspected. No table or migration is to be dropped to simplify the graph.

## 17. Passenger UI, advanced UI and map integration

### 17.1 Passenger application ownership

- The existing passenger application remains the primary product shell and source of truth for passenger navigation and journeys.
- PR #43 extends the passenger map page in `frontend/src/App.tsx` and the API contract in `frontend/src/passenger-api.ts`: published locations, route list, ordered stops, optional coordinates, GeoJSON LineString geometry and origin/destination selection.
- Keep the map integrated as a passenger feature inside the existing shell. Do not replace the passenger application with the standalone tracking proof of concept.
- The #43 map must show explicit missing-key, offline, missing-coordinate/geometry and API error states. It must never fabricate a route between endpoints.

### 17.2 Two map implementations are not yet one architecture

**Passenger map in PR #43:** Google Maps JavaScript API, configured through `VITE_GOOGLE_MAPS_API_KEY`; it draws catalog location markers and only published route geometry. The key is not evidenced as configured. Google Maps key use may require Google Cloud billing and restricted key management; no billing activation is authorized.

**MITP map in PR #53:** MapLibre GL JS with a self-hosted Martin/PostGIS proof-of-concept tile service, a separate local style URL and synthetic tracking telemetry. It is a staff-oriented tracking demonstration, not a passenger journey map or verified production GIS platform. Its current `/tracking-demo` entry in `frontend/src/main.tsx` replaces the normal root application rather than registering a protected route within the shared application shell.

### 17.3 Recommended target boundary for Owner review

- Keep one shared map-rendering component/provider abstraction, but separate passenger journey layers from staff-only live/synthetic vehicle telemetry.
- Prefer evaluating MapLibre as the common renderer because it avoids requiring a Google Maps API key and billing account; this remains a recommendation, not an approved provider decision. Self-hosted tile infrastructure, OpenStreetMap attribution/licensing, data freshness, bandwidth and hosting costs still require review.
- Keep the passenger map data contract tied to published, verified stop coordinates and route geometry. Keep tracking telemetry behind staff authorization and never expose vehicle telemetry through the public passenger catalog.
- Establish one authoritative geographic data model and source-of-truth database before publishing geometry. PR #43 currently stores route geometry as JSON; PR #53's PostGIS/Martin stack is a separate proof-of-concept database. They are not yet reconciled into a shared canonical PostGIS model.
- Use Koybe's operator-confirmed pin only for that boarding point. Do not infer the Koybe–Jinka route trace, intermediate stops or schedule from endpoints.
- Do not put map API keys or secrets into frontend source, APK assets or public repository variables that are readable by client builds.

### 17.4 Advanced UI ownership and sequence

1. Preserve the existing passenger-first app shell and its working passenger flows.
2. Complete the passenger map/catalog contract and accessible map states inside the passenger shell.
3. Register MITP TrackingMap as a protected staff feature/route, not a replacement root application. Reuse the shared design system, localization, navigation and API client.
4. Add driver, agent, dispatch and administrator workspaces only after passenger regression and authorization boundaries are verified.
5. Keep Amharic-first responsive layouts, keyboard/screen-reader semantics, clear loading/empty/error/offline states, visible synthetic-data labels and role-aware navigation as acceptance criteria.
6. Use one shared API client/error/session layer. PR #53's TrackingMap currently calls fetch directly; it should be reconciled with the shared authenticated API client and staff permission handling.
7. Treat PR #54 About/API-origin/Android work as a separate review unit. Preserve the “Coming soon” About status until a real corporate website exists.

No visual regression suite, accessibility audit or integrated passenger-plus-staff UI verification has been evidenced for a single combined commit.

## 18. Workflow and PR #55 recheck

### 18.1 Workflow ownership and safety findings

- PR #42's two workflows passed on its exact head, as recorded in Section 15.5.
- PR #43 adds push triggers and broadens the Android/backend verification pipelines. Its pull_request branch filters do not include its actual base branch `fix/passenger-password-minimum-six`; verify trigger behavior and exact-head evidence before relying on the PR checks.
- PR #43 Android verification consumes `VITE_API_BASE_URL` and `VITE_GOOGLE_MAPS_API_KEY` repository variables. Their presence, restrictions, billing state and secret handling are not established here.
- PR #43's Android workflow contains a conditional job that can write generated Gradle verification metadata back to the PR head when a pull request targets main. This is an automated branch mutation. Review whether it should be removed or separately authorized before any future main-targeted workflow execution.
- The backend workflow's Docker build and HTTPS/CORS/CSRF smoke checks are useful verification design, but workflow definitions are not evidence that they passed.
- No workflow was dispatched, rerun or otherwise initiated for this inspection.

### 18.2 PR #55 current state

At the latest recheck:
- State: OPEN, DRAFT, UNMERGED.
- Base: main at `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`.
- Head: `docs/production-readiness-a1-a2` at `7a3d805a175fd3c178fa1a33f9aa674f4ea14d73`.
- Changed files: two documentation files; six commits ahead, zero behind main.
- Compare result: `ahead`, with the merge base equal to current main.
- GitHub PR metadata: `mergeable = true` at the final recheck after the documentation and PR-description updates. The value fluctuated during successive metadata reads (false, then true); treat it as a transient merge-conflict signal only, not an approval or readiness decision.
- Reviews: none returned. Inline review threads: none returned. PR conversation comments: none returned.
- PR-head workflow-run lookup: no runs returned. Commit status endpoint: no status entries returned.
- No merge was attempted.

The PR description still cites the prior head SHA `742f8279fb43c25f2f8db6468b19e2ff2ab0ebc3`; it must be refreshed after this report update. PR #55 remains draft and requires Owner review. Its documentation-only status does not authorize application changes.

## 19. Consolidated A2 gap register for Owner review

Statuses mean: PASS = directly evidenced for the stated scope; PARTIAL = some evidence exists but does not close the control; MISSING = required evidence is absent; UNRESOLVED = competing designs or decisions remain; UNKNOWN = state cannot be determined from available access; NOT RUN = verification was deliberately not performed.

| ID | Area / finding | Status | Severity / gate | Required closure evidence |
|---|---|---|---|---|
| A2-01 | A1 product scope and target architecture not Owner-frozen | UNRESOLVED | Critical / A1 | Explicit Owner approval of versioned A1 baseline |
| A2-02 | #42/#43 sibling ownership and integration policy | PARTIAL | High / A2 | Owner accepts #43 as integration candidate and #42 as baseline evidence, subject to exact-head verification |
| A2-03 | PR #43 exact-head CI | MISSING | Critical / A2 | Successful backend and Android checks on exact SHA 20c855b881e30aacf97dbb0d8fbb85755eb7bdf5; no dispatch/rerun performed |
| A2-04 | PR #43 workflow trigger filters and automatic metadata writeback | UNRESOLVED | High / A2 | Reviewed trigger matrix and approved non-mutating or explicitly authorized workflow behavior |
| A2-05 | Parallel Alembic heads 0008 wallet / 0008 tracking | UNRESOLVED | Critical / A2 | Database revision inventory, approved merge-revision design and disposable-PostgreSQL verification plan |
| A2-06 | Database migration state and backups | UNKNOWN | Critical / A2/A4 | Inventory all target DB alembic_version rows and backup/restore evidence |
| A2-07 | Combined model registry | PARTIAL | High / A2 | Confirm full #43 passenger imports plus tracking import and Alembic metadata parity on integrated candidate |
| A2-08 | Combined config.py/main.py | UNRESOLVED | Critical / A2 | Approved runtime policy, tracking secret handling, router/middleware registration and staff authorization review |
| A2-09 | Passenger map provider and canonical GIS architecture | UNRESOLVED | High / A1/A2 | Owner decision on renderer/hosting/licensing and one authoritative geographic data model |
| A2-10 | Authoritative route trace, stop sequence and provenance | MISSING | Critical / A2/A4 | Operator-verified route/stop dataset and approved geometry source; Koybe pin alone is insufficient |
| A2-11 | Google Maps key/billing and MapLibre/Martin hosting | MISSING | High / A2/A5 | Approved provider, restricted credentials or self-hosted tile infrastructure, cost and licensing evidence |
| A2-12 | Passenger UI + staff tracking UI integration | PARTIAL | High / A2/A4 | One shared shell, role-protected tracking route, shared API client, responsive/accessibility and regression evidence |
| A2-13 | Advanced UI accessibility and device acceptance | MISSING | High / A4 | WCAG-oriented review, physical Android device test and user acceptance record |
| A2-14 | PR #55 documentation evidence | PASS (docs-only scope) | Medium / A2 | Two docs present on branch; retain draft status pending Owner review |
| A2-15 | PR #55 independent review and CI | MISSING | Medium / A2 | Owner/reviewer disposition and applicable documentation checks; none currently recorded |
| A2-16 | Production host, domain, DB, secrets and monitoring | MISSING | Critical / A5 | Approved infrastructure inventory, secure secret delivery, observability and operations ownership |
| A2-17 | Regulatory, privacy, insurance and commercial operating approvals | MISSING | Critical / A5 | Applicable Ethiopian transport, insurance, privacy and operating approvals evidenced before live service |
| A2-18 | Notifications provider and consent/channel contracts | UNRESOLVED | Medium / A3/A4 | Provider selection, costs, consent, delivery/security contract and failure-mode tests |
| A2-19 | Independent security review | MISSING | Critical / A4/A5 | Independent review of auth/session/CSRF, staff RBAC, tracking-device credentials, secrets, dependencies and production config |
| A2-20 | Operational recovery and support | MISSING | High / A4/A5 | Backup/restore drill, rollback plan, incident/support owner, runbooks and monitoring evidence |
| A2-21 | Exact integrated release candidate | NOT RUN | Critical / A4 | Frozen integration SHA with full regression, migration and security evidence |
| A2-22 | Deployment and live operation | NOT AUTHORIZED | Critical / A5 | Separate explicit Owner A5 approval after A4 acceptance |

### 19.1 A2 exit recommendation

A2 remains **PARTIAL / NOT CLOSED**. The evidence is sufficient to identify the integration strategy and material blockers, but not to authorize integration or declare a production-ready system.

Recommended order after Owner review:
1. Freeze A1 scope and approve the #43/#42 disposition.
2. Obtain exact-head #43 verification evidence through the normal approved CI path; do not treat #42's success as transferable.
3. Approve the migration merge design and database inventory procedure.
4. Approve one geographic architecture and passenger/staff map boundary.
5. Complete the config/main/model-registry/workflow integration plan.
6. Close the remaining security, regulatory, privacy, hosting and operations evidence gaps before A4/A5.

No code, migration, workflow, deployment, branch history or main-branch changes were made by this A2 report update.
