# MN-011 — Synthetic Hosted-Preview Boundary and Runtime/Database Identity Specification

**Artifact:** MN-011-SYNTHETIC-HOSTED-PREVIEW-BOUNDARY-001  
**Version:** 1.0.0  
**Assessment date:** 2026-11-26  
**Status:** DELIVERED — TARGET BOUNDARY SPECIFIED; HOSTED RUNTIME NOT PROVISIONED/VERIFIED  
**Repository:** `akefadaka-git/maalenex`  
**Main baseline:** `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78`  
**Method:** Read-only reconciliation of PR #43, PR #54 and PR #56 documentation and recorded provider inspection. No provider resources, database, secrets or deployment workflows were changed.

## 1. Executive disposition

The repository has a defined local development/test boundary and an Android UI-preview build. A free hosted synthetic preview is a possible future A4 activity, but it is **not currently evidenced as provisioned or operational**.

The existing G1 backend configuration intentionally rejects production mode and remote database hosts. PR #43 proposes a production-capable runtime candidate, but it is open/draft and its exact-head PR-event verification remains unresolved. PR #54's APK has no configured external test API origin; it is a UI preview. PR #56 documents a proposed free-provider topology and explicitly records that no MaaleNex Render service or database was created and that the Supabase project state was not independently verified.

This record specifies the safe preview boundary. It does not authorize weakening the G1 guard, connecting a remote database, creating provider resources, setting secrets, running migrations or deploying.

## 2. Evidence baseline

| Evidence | Exact reference | Finding |
|---|---|---|
| Main | `c988b9d2a3b09c831daa4f1d17fa3b75f69e7e78` | Current canonical baseline |
| PR #43 | `20c855b881e30aacf97dbb0d8fbb85755eb7bdf5` | Production-capable runtime candidate; not merged |
| PR #54 | `34e4aab8d84561828fb0a1bc8bdce9f914bc32ca` | Android UI/API-origin readiness candidate; exact-head build PASS |
| PR #56 | `9656ae29c210cfd132eb3a7f1a2b821ad98acc39` | Documentation-only provider onboarding record; PARTIAL |
| PR #56 base | `c2782177693975c95bf8f895f19756c5f773aa0d` | Prior A4 provider-inspection record |

## 3. Current provider inspection — recorded facts and limits

PR #56 records the following read-only inspection:

### Render

- The inspected workspace contained one unrelated free web service.
- No MaaleNex backend service was found.
- No Render Postgres instance was found.
- No MaaleNex provider resource, environment variable, deployment or billing setting was changed.

### Supabase

- The Owner supplied project reference `awftmlipjchlysjzqunm`.
- The authenticated dashboard was not inspected in the recorded session.
- Project health, region, PostgreSQL version, PostGIS installation/schema, roles and database readiness remain UNVERIFIED.
- A project reference is not proof that the database is ready or that a connection is authorized.

### Cloudflare Pages

- The intended frontend candidate is Cloudflare Pages.
- No MaaleNex Pages project was recorded as created.
- The existing production workflow targets the frozen `main` branch; PR #56 explicitly says not to dispatch it as a substitute for an approved release.

These findings must be refreshed before any future provider setup. They are not a current assertion that the provider account state cannot have changed since the inspection.

## 4. Preview versus production — strict separation

A hosted preview, if separately authorized, must satisfy all of the following:

- Explicitly labelled **SYNTHETIC PREVIEW — NOT PRODUCTION** in the UI and operational documentation.
- Synthetic-only records and synthetic identities; no real passenger, operator, driver, recipient or staff personal data.
- No commercial bookings, payment collection, wallet money movement, ticket entitlement, boarding authority or live transport dispatch.
- No real GPS devices, live tracking or public vehicle positions.
- No Cargo evidence uploads containing real personal data.
- No external email/SMS/WhatsApp delivery.
- No production API credentials, provider keys or secrets in frontend assets, APKs, source control or workflow logs.
- No public indexing or representation as a live operating service.
- A documented shutdown/rollback path and owner for the preview.

A synthetic preview is not a production deployment and must not be used to bypass the A5 gate.

## 5. Runtime and identity contract

A separately authorized preview design must define distinct identities and permissions:

| Identity | Intended responsibility | Restriction |
|---|---|---|
| Runtime application DB role | Execute only approved application operations | No schema ownership, superuser or unrestricted DDL |
| Migration role | Apply reviewed Alembic migrations during an approved release window | Not used by the running API; credential isolated from runtime |
| Read-only verification role | Inspect schema/version and selected health metadata | No writes or secret disclosure |
| Provider/deployment identity | Deploy only the approved preview artifact | Least privilege, scoped repository/environment permissions |
| Human Owner/admin identity | Approve provider setup, secret custody and preview activation | Credentials remain in provider secret manager; never sent in chat |

The preview API must use a dedicated non-production database and isolated credentials. The database must not be shared with an unrelated project or production environment. The runtime role must not be able to execute migrations or create arbitrary schema objects.

No database username, password, full connection URI, API token, cookie secret or encryption key belongs in this document or in Git.

## 6. Database and migration boundary

Before any remote database connection or migration:

1. The Owner must separately approve the exact non-production project and region.
2. The project owner must verify the PostgreSQL version, health, backup/retention limits and PostGIS extension/schema if GIS is included.
3. The migration graph and model registry must be reconciled under the approved A3 integration plan.
4. The exact candidate SHA and Alembic heads must be recorded.
5. A dedicated migration identity and a separate restricted runtime identity must be created.
6. Backup/restore and rollback expectations must be documented.
7. Migration execution must be separately authorized and recorded.
8. No migration may be run against production or an unknown database.

No database was accessed in this MN-011 assessment. The deployed database migration state remains UNKNOWN.

## 7. API origin, network and browser security

A preview API origin must:

- Use HTTPS with a valid certificate.
- Be explicitly configured through a non-secret build/runtime setting.
- Contain only the origin, not credentials, path, query or fragment.
- Match the exact credentialed CORS allowlist.
- Use secure cookie attributes and explicit CSRF protection.
- Reject unapproved origins and insecure production cookies.
- Disable interactive API documentation where required by the approved runtime policy.
- Expose liveness separately from database-backed readiness.
- Avoid exposing internal health, database, tracking or administrative data publicly.

The Android APK must be rebuilt against the approved test origin and tested on physical devices. A same-origin fallback in a standalone WebView is not evidence of connectivity to a separately hosted API.

## 8. Provider cost and activation controls

The documented free-provider proposal is:

- Cloudflare Pages for static frontend delivery.
- Render Free Web Service as a possible synthetic API preview after the runtime boundary is separately amended.
- Supabase Free as a possible PostgreSQL/PostGIS preview database after database identity, extension and migration controls are approved.

Free-tier availability, limits, sleep/pause behavior, storage, backups, egress, service terms and regional availability must be rechecked at activation time. A free tier is not a production reliability or backup commitment.

No paid plan, billing activation, top-up, procurement, domain purchase or provider resource creation is authorized by this record. If a provider requires payment or billing activation, stop and return to the Owner for a separate decision; do not ask the Owner to fund an unapproved service.

## 9. Preview readiness checklist

| Gate | Required evidence | Current status |
|---|---|---|
| Owner-approved preview scope | Exact non-production boundary and exclusions | PARTIAL — target documented |
| Provider project | Correct MaaleNex project, region and plan | MISSING / NOT VERIFIED |
| Database | Healthy isolated PostgreSQL project | MISSING / NOT VERIFIED |
| PostGIS | Extension installed in approved schema if GIS is included | NOT VERIFIED |
| Migration identity | Dedicated credential and permission review | MISSING |
| Runtime identity | Restricted DB role and secret custody | MISSING |
| API origin | HTTPS host, exact CORS/cookie/CSRF tests | MISSING |
| Frontend deployment source | Approved candidate SHA/branch | MISSING |
| Synthetic dataset | Reviewed fixtures only | PARTIAL — development fixtures exist |
| Android connectivity | Physical-device end-to-end test | NOT RUN |
| Monitoring/shutdown | Preview health, logs, owner and shutdown procedure | MISSING |
| Production controls | Separate production gates remain enforced | PASS — no production activation evidenced |

## 10. MN-011 disposition and governance

**MN-011: DELIVERED — SYNTHETIC HOSTED-PREVIEW AND IDENTITY BOUNDARY SPECIFIED.**  
**Hosted preview: NOT PROVISIONED / NOT VERIFIED.**  
**Remote database access/migration: NOT PERFORMED.**  
**Production deployment: NOT AUTHORIZED.**

This is documentation-only A2 work. It does not create provider resources, connect to Supabase/Render/Cloudflare, change runtime configuration, set secrets, run migrations, dispatch workflows, merge, deploy or activate commercial operations.