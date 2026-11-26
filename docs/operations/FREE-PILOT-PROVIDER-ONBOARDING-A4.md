# MaaleNex Free Pilot Provider Onboarding (A4)

**Status:** PROVIDER OPTIONS VERIFIED — SUPABASE PROJECT REFERENCE RECEIVED — DATABASE/EXTENSION STATE NOT VERIFIED — DEPLOYMENT BLOCKED BY G1 GOVERNANCE  
**Scope:** Documentation and read-only provider inspection only. This record does not authorize production deployment, a production-data migration, or a change to the G1 runtime boundary.

## 1. Owner decision and target topology

Proposed zero-cost pilot topology:

| Component | Provider | Intended use |
|---|---|---|
| React + Vite frontend | Cloudflare Pages | Static web delivery |
| FastAPI backend | Render Free Web Service | Synthetic-only API preview after the runtime boundary is separately amended |
| PostgreSQL + PostGIS | Supabase Free | Isolated synthetic pilot database after database roles and migrations are approved |

This is a **free pilot**, not a reliable commercial production service. Provider free plans have inactivity, resource, storage, backup, and availability limits.

Official plan facts checked 2026-11-26:
- Render Free web services spin down after 15 minutes without inbound traffic and take about a minute to wake. Render explicitly says Free instances are not for production. Render Free Postgres expires after 30 days and has no backups: https://render.com/docs/free
- Supabase Free includes 500 MB database storage, 5 GB egress and no automatic backups; inactive projects can pause after seven days: https://supabase.com/pricing and https://supabase.com/docs/guides/platform/free-project-pausing
- Cloudflare Pages Free permits 500 builds/month and a 20-minute build timeout: https://developers.cloudflare.com/pages/platform/limits/
- Supabase documents PostGIS support and recommends installing it in the `extensions` schema, not `public`: https://supabase.com/docs/guides/database/extensions/postgis

## 2. Read-only inspection results

### Render account

Connected workspace inspected: `My Workspace` (workspace ID `tea-dbpbd8142hec73c5pu6g`).

- One existing free web service was found. It belongs to a different repository/project and is out of scope; do not modify it.
- No Render Postgres instances were found.
- No MaaleNex backend service or MaaleNex database currently exists in this Render workspace.
- No service, database, environment variable, deploy, or billing setting was changed.

### Repository

Repository: `akefadaka-git/maalenex`  
Evidence branch at inspection: `a4/01-production-db-identity-evidence`  
Evidence branch head: `c2782177693975c95bf8f895f19756c5f773aa0d`

Relevant current configuration:
- Backend package: `backend/pyproject.toml` (FastAPI, SQLAlchemy, psycopg 3, Alembic).
- Frontend: `frontend/package.json` (React 18, TypeScript, Vite).
- `backend/app/core/config.py` rejects every environment other than development/test, requires synthetic-only mode, requires a local PostgreSQL host, and requires database `maalenex_dev`.
- `frontend/vite.config.ts` only defines development proxies to `127.0.0.1:8000` and `127.0.0.1:3000`; it is not a production API-origin configuration.
- `.github/workflows/cloudflare-pages.yml` builds the frontend and has a manual production deployment path from `main`. The current `main` is a frozen earlier baseline, while the A3 implementation is on feature branches. **Do not dispatch this workflow or connect the old main branch as the production deployment source.**
- The repository README explicitly states that production deployment, production personal-data processing and public launch are not authorized.

## 3. Mandatory blockers — do not bypass

The existing G1 boundary is intentional. It prevents a hosted API from connecting to a remote database and prevents `APP_ENV=production`. Therefore:

1. Do not set `APP_ENV=production`, weaken/remove the validator, or patch around the localhost database restriction as part of provider setup.
2. Do not put a Supabase connection string into Render or GitHub Actions yet.
3. Do not run Alembic migrations against a newly created hosted database.
4. Do not deploy the API, enable real bookings, onboard operators/passengers, or process personal/payment data.
5. Do not use Render Free Postgres as the persistent pilot database because it expires after 30 days and has no backups.
6. Do not run the current Cloudflare workflow against `main` as a substitute for an approved A3 application release.

A separate Owner-approved change must define a **non-production hosted preview boundary** (synthetic-only), the permitted remote database target, the database identity/role model, the migration execution identity, API origin/CORS rules, and a verification plan. Production remains a separate future authorization.

## 4. Provider account setup checklist

These are account-owner actions in provider dashboards. No credentials, API tokens, passwords, or billing information should be sent in chat or committed to Git.

### A. Supabase — database project (reference supplied; dashboard state not independently verified)

Owner supplied the project-specific dashboard URL `https://supabase.com/dashboard/project/awftmlipjchlysjzqunm/branches`, yielding project reference `awftmlipjchlysjzqunm`. This establishes the intended project reference for this record, but the authenticated dashboard could not be inspected in this session. Project readiness, region, database version, PostGIS installation/schema, and project health remain **UNVERIFIED**. Do not infer these from the URL.

1. Open the supplied project URL and confirm that the dashboard loads and the project is healthy.
2. Record the actual project name, plan, region and PostgreSQL major version; confirm whether the name is `maalenex-pilot` and correct the record if it differs.
3. Use a unique database password and store it only in the provider's password manager/secret store; never send it in chat.
4. In the project dashboard, open **Database → Extensions**, search for `postgis`, and verify that it is enabled in schema `extensions`. If it is not enabled, enable it and keep the schema as `extensions`. Supabase's current official guide explicitly says not to install PostGIS into `public`: https://supabase.com/docs/guides/database/extensions/postgis
5. After verifying, use the SQL Editor for this **read-only verification query**:
   ```sql
   select
       e.extname,
       n.nspname as installed_schema,
       e.extversion
   from pg_extension e
   join pg_namespace n on n.oid = e.extnamespace
   where e.extname = 'postgis';
   ```
   Expected result: one row with `extname = postgis` and `installed_schema = extensions`. If it reports `public`, stop; do not proceed or try to move the extension casually.
6. Do not run application migrations yet. Do not expose the database to the public Data API or create application roles yet.
7. Record only the project reference, region, PostgreSQL major version, PostGIS version/schema, and a redacted connection-host identifier. Never record the password, API secret, or full connection URI in Git or chat.

### B. Cloudflare Pages — frontend (not yet created)

1. Open https://dash.cloudflare.com/ and connect the GitHub account.
2. Do not bind production to `main` while it remains the frozen baseline.
3. Do not run the existing production workflow.
4. After an approved frontend release branch and API-origin configuration exist, create the Pages project `maalenex` with:
   - Framework preset: Vite
   - Root directory: `frontend`
   - Build command: `npm install --no-package-lock --no-audit --no-fund && npm run build`
   - Build output directory: `dist`
5. Keep preview deployments separate from production and do not publish a non-functional frontend as a public service.

### C. Render — API (not yet created)

1. Open https://dashboard.render.com/ and confirm the existing workspace.
2. Do not modify the unrelated existing service.
3. Do not create a MaaleNex API service until the Owner-approved hosted-preview runtime boundary exists.
4. Once that boundary is approved, the intended service definition is:
   - Type: Web Service
   - Repository: `https://github.com/akefadaka-git/maalenex`
   - Root directory: `backend`
   - Runtime: Python
   - Build command: `pip install .`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health path: `/api/v1/health`
5. Do not supply `DATABASE_URL` or deploy until the runtime guard, DB least-privilege contract, migrations and synthetic-only hosted-preview policy have been separately approved and verified.

## 5. Secret and identity contract (future, not provisioned)

The API service will eventually need provider-managed environment variables, set only in Render's dashboard:
- `APP_ENV`: only the separately approved preview value; never override the current G1 validator.
- `DATABASE_URL`: dedicated application login URI; never a superuser, owner, or migration credential.
- `CORS_ORIGINS`: exact approved Cloudflare Pages preview/production origin(s), not wildcard.
- `SYNTHETIC_DATA_ONLY`: `true` for the pilot.
- `SECURE_COOKIES`: enable only with the approved HTTPS/proxy configuration.

The migration principal must be separate from the runtime principal. The application login must have only the minimum direct privileges and explicit capability-role memberships; it must not inherit owner, superuser, database-creation, role-creation, or RLS-bypass powers. The A4-01 identity record remains the governing least-privilege contract until live identity evidence is available.

## 6. Closure evidence required

- [x] Supabase project reference received from Owner: `awftmlipjchlysjzqunm`.
- [ ] Supabase dashboard health, project name/plan/region, database version and PostGIS-in-`extensions` evidence.
- [ ] Supabase free-plan limits and backup/restore limitations acknowledged.
- [ ] Runtime login name and live PostgreSQL role memberships verified read-only.
- [ ] Dedicated migration identity and controlled migration procedure approved.
- [ ] Hosted preview boundary approved without weakening G1 safeguards.
- [ ] Backend API origin and exact CORS allowlist established.
- [ ] Cloudflare Pages project configured on an approved release branch.
- [ ] Frontend API calls use a configured HTTPS API origin (not Vite's localhost-only development proxy).
- [ ] Render API service configured only after the code/runtime gate passes.
- [ ] TLS, health checks, negative authorization tests, synthetic-only checks and provider limits verified.
- [ ] Separate Owner authorization for any A5 production deployment.

## 7. Current disposition

**PARTIAL — provider selection and onboarding procedure documented; Supabase project reference received but dashboard/database state remains unverified.**  
**MISSING/UNVERIFIED — Supabase project configuration and PostGIS evidence, live database identity, Cloudflare project, Render runtime service, production API origin, TLS evidence and deployment verification.**  
**NOT RUN — provider provisioning, database migrations, deployment and production tests.**  
**NOT AUTHORIZED — production deployment and live-data use.**

The Supabase project reference was supplied by the Owner; no project settings were inspected or modified. No secrets were read or written. No database connection or migration was attempted. No CI workflow was dispatched. No merge, deployment or `main` modification occurred.
