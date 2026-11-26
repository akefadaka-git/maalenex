# A4-01 — Production Database Identity and Least-Privilege Evidence

**Repository:** `akefadaka-git/maalenex`  
**Branch:** `a4/01-production-db-identity-evidence`  
**Assessment date:** 2026-11-26  
**Status:** **PARTIAL — DATABASE CONTRACT ESTABLISHED; PRODUCTION PRINCIPAL AND LIVE MEMBERSHIP UNVERIFIED**  
**Execution boundary:** Read-only repository inspection and evidence preparation. No database connection, role creation, grant, migration, secret access, or production change was performed.

## 1. Executive determination

The application uses one SQLAlchemy engine created from `settings.database_url` in `backend/app/db/session.py`. That is the application database identity boundary: the PostgreSQL login embedded in the runtime connection URI (or supplied through its secret reference) is the principal that must assume the A3.5 capability roles.

**The actual production login name cannot be established from the repository.** No production deployment manifest, secret-manager reference, host configuration, or live database role catalogue is present in the inspected repository. The G1 settings explicitly reject production mode, remote database hosts, non-synthetic operation, and any database other than local `maalenex_dev`. The current branch therefore contains no production database identity to inspect.

Do not infer a production login name from a proposed convention. The owner/operator of the eventual hosting environment must identify the actual role from the deployed `DATABASE_URL` secret metadata (username only; never disclose or copy the password) and confirm the database/cluster identity.

## 2. Verified application-to-database capability contract

The application code at `backend/app/domains/geo/security.py` contains a static allowlist mapping application permission codes to database capability roles:

| Application permission | PostgreSQL capability role | Intended capability |
|---|---|---|
| `platform.geo.internal.read` | `maalenex_geo_internal_reader` | SELECT vehicle positions and invoker-security internal positions view |
| `platform.tracking.read` | `maalenex_geo_internal_reader` | SELECT vehicle positions and invoker-security internal positions view |
| `platform.tracking.manage` | `maalenex_geo_tenant_manager` | SELECT positions; SELECT/INSERT/UPDATE devices and device assignments |
| `platform.geo.manage` | `maalenex_geo_catalog_manager` | SELECT/INSERT/UPDATE tenant-owned geography, provenance and publication tables |
| `platform.geo.publish` | `maalenex_geo_catalog_manager` | SELECT/INSERT/UPDATE on the catalog/publication capability tables; application authorization still controls permission semantics |
| `platform.geo.audit.read` | `maalenex_geo_audit_reader` | SELECT tenant-scoped append-only geo audit events |

The four capability roles are NOLOGIN roles. Migration `0023_geo_tenant_rls_permissions` hardens them as NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOBYPASSRLS and NOINHERIT. The role names are selected only from the static application mapping; no client-supplied role name is interpolated.

The application calls `SET LOCAL ROLE <mapped-role>` only after validating staff identity, active organization membership and the relevant scoped permission (or explicit platform-wide grant). It then sets `app.current_organization_id` transaction-locally and records the access event. Transaction-local role/context is cleared by commit or rollback.

**Implication:** the application login needs PostgreSQL 16+ role membership with the `SET` option for the capability roles it must assume. Do not grant the capability privileges directly to the login and do not make the login a table owner, schema owner, database owner, superuser, or migration principal.

## 3. Required separation of identities

| Identity | Purpose | Required boundary |
|---|---|---|
| Application runtime login | SQLAlchemy runtime connection | LOGIN; non-owner; NOSUPERUSER; NOCREATEDB; NOCREATEROLE; NOREPLICATION; NOBYPASSRLS; NOINHERIT; SET membership only in the four A3.5 capability roles required by deployed application features |
| Capability roles | Temporary transaction-local privileges | Existing NOLOGIN roles listed in section 2; no direct login |
| Migration/deployment principal | Alembic schema changes | Separate controlled identity; never used by application runtime; not a member of runtime capability roles unless a separately justified and reviewed need exists |
| Martin public-reader login | Public map tile service | Separate LOGIN identity; SET membership only in `maalenex_geo_public_reader`; never use the application runtime or migration identity |

This register does not prescribe a production login name because none is evidenced. Record the exact existing principal from the production secret reference when the deployment target is identified. Store only the username/role name and secret-manager reference identifier here; never store a connection URI, password, token, or private key.

## 4. Read-only production evidence collection

Run the following checks only from an authorized administrative session against the confirmed production cluster. Use a secure terminal and a non-secret psql variable for the actual runtime login name. These statements are read-only; they do not create, alter, or grant roles.

### 4.1 Confirm cluster and connected identity

```sql
SELECT
    current_database() AS connected_database,
    current_user AS inspecting_principal,
    inet_server_addr() AS server_address,
    inet_server_port() AS server_port,
    version() AS postgres_version;
```

Record the cluster identifier from the hosting control plane separately. Do not publish private network addresses if the evidence repository is public.

### 4.2 Inspect the runtime login attributes and direct memberships

Set the psql variable to the actual username from the production `DATABASE_URL` secret metadata (username only):

```psql
\set runtime_login 'REPLACE_WITH_VERIFIED_RUNTIME_LOGIN'
```

```sql
SELECT
    r.rolname AS runtime_login,
    r.rolcanlogin,
    r.rolsuper,
    r.rolcreatedb,
    r.rolcreaterole,
    r.rolreplication,
    r.rolbypassrls,
    r.rolinherit,
    granted.rolname AS directly_granted_role,
    m.admin_option,
    m.set_option
FROM pg_catalog.pg_roles AS r
LEFT JOIN pg_catalog.pg_auth_members AS m
    ON m.member = r.oid
LEFT JOIN pg_catalog.pg_roles AS granted
    ON granted.oid = m.roleid
WHERE r.rolname = :'runtime_login'
ORDER BY granted.rolname;
```

Expected login attributes: `rolcanlogin=true`; `rolsuper=false`; `rolcreatedb=false`; `rolcreaterole=false`; `rolreplication=false`; `rolbypassrls=false`; `rolinherit=false`. Confirm the principal is not owner of the database, schemas, protected tables, or sequences using the database catalogue/hosting control plane.

### 4.3 Verify SET capability for each mapped role

```sql
WITH required(role_name) AS (
    VALUES
        ('maalenex_geo_internal_reader'),
        ('maalenex_geo_tenant_manager'),
        ('maalenex_geo_catalog_manager'),
        ('maalenex_geo_audit_reader')
)
SELECT
    required.role_name,
    pg_catalog.pg_has_role(
        :'runtime_login',
        required.role_name,
        'SET'
    ) AS can_set_role,
    pg_catalog.pg_has_role(
        :'runtime_login',
        required.role_name,
        'MEMBER'
    ) AS is_member
FROM required
ORDER BY required.role_name;
```

Expected: `can_set_role=true` and `is_member=true` for each capability the production application is actually expected to use. If a capability is not part of the deployed feature set, document that explicit exclusion and prove the corresponding API feature is disabled. No blanket `ADMIN OPTION` is permitted.

### 4.4 Enumerate unexpected direct memberships

```sql
SELECT granted.rolname AS unexpected_direct_membership
FROM pg_catalog.pg_auth_members AS m
JOIN pg_catalog.pg_roles AS member
    ON member.oid = m.member
JOIN pg_catalog.pg_roles AS granted
    ON granted.oid = m.roleid
WHERE member.rolname = :'runtime_login'
  AND granted.rolname NOT IN (
      'maalenex_geo_internal_reader',
      'maalenex_geo_tenant_manager',
      'maalenex_geo_catalog_manager',
      'maalenex_geo_audit_reader'
  )
ORDER BY granted.rolname;
```

Expected: zero rows, unless each additional membership has a documented, separately approved runtime requirement. Specifically reject membership in owner, migration, superuser, public-reader, or unrelated administrative roles.

### 4.5 Validate effective permissions while connected as the runtime login

After the administrative catalogue checks, open a separate session using the actual runtime login through the normal secret mechanism (do not put the password in shell history). The following checks are read-only:

```sql
SELECT
    current_user,
    session_user,
    rolsuper,
    rolcreatedb,
    rolcreaterole,
    rolreplication,
    rolbypassrls
FROM pg_catalog.pg_roles
WHERE rolname = current_user;
```

For each required capability role, test the application-authorized transaction path in a disposable tenant fixture or approved production-safe read-only test tenant. Verify:
- `SET LOCAL ROLE` succeeds only for explicitly granted capabilities.
- Missing tenant context returns zero tenant rows.
- Tenant A cannot read tenant B records.
- The runtime login cannot read `geo.legacy_tracking_quarantine`, credentials, unrelated internal tables, or migration metadata.
- The runtime login cannot CREATE objects, alter schema, create roles/databases, bypass RLS, or change role membership.
- Commit and rollback both clear the local role and `app.current_organization_id` context.

Do not run destructive probes against production. Use a controlled staging clone for negative write/DDL tests.

## 5. Provisioning contract — not executed

If and only if the hosting/database owner confirms the runtime principal and authorizes provisioning, an administrator may grant SET-only membership in the required capability roles. PostgreSQL 16+ supports the explicit `SET` membership option. The following is a template only; it is not executable until the placeholder is replaced with the verified role identifier and the exact grant set is approved:

```sql
-- TEMPLATE ONLY — NOT EXECUTED.
-- Replace the identifier after verifying the actual runtime login.
-- Do not grant ADMIN OPTION.
GRANT maalenex_geo_internal_reader
TO verified_runtime_login
WITH INHERIT FALSE, SET TRUE;

GRANT maalenex_geo_tenant_manager
TO verified_runtime_login
WITH INHERIT FALSE, SET TRUE;

GRANT maalenex_geo_catalog_manager
TO verified_runtime_login
WITH INHERIT FALSE, SET TRUE;

GRANT maalenex_geo_audit_reader
TO verified_runtime_login
WITH INHERIT FALSE, SET TRUE;
```

The SQL above illustrates the required membership shape only. The actual principal identifier must be safely quoted as a PostgreSQL identifier by the administrator; never substitute an untrusted string. Grant only roles justified by the deployed API capabilities. Review PostgreSQL version compatibility and hosting-provider restrictions before execution.

## 6. Evidence record to complete

| Evidence item | Required value | Current state |
|---|---|---|
| Hosting provider / production cluster identifier | Provider control-plane ID; no secret | **MISSING** |
| Production database name | Exact database name | **MISSING** |
| Runtime login role | Exact PostgreSQL role name derived from deployed secret metadata | **MISSING — NOT IN REPOSITORY** |
| Secret reference | Secret-manager key/reference only; no secret value | **MISSING** |
| PostgreSQL version | Exact server version | **MISSING** |
| Runtime login attributes | Read-only catalogue output | **NOT RUN** |
| Database/schema/table ownership check | Read-only catalogue evidence | **NOT RUN** |
| Four capability SET memberships | Per-role `pg_has_role(..., 'SET')` results | **NOT RUN** |
| Unexpected membership check | Zero rows or approved exception | **NOT RUN** |
| Tenant isolation and denied-privilege tests | Sanitized test output and test environment | **NOT RUN** |
| Reviewer / execution authority | Named operator and approval reference | **MISSING** |
| Evidence timestamp | UTC timestamp and cluster identifier | **NOT RUN** |

## 7. Acceptance criteria

A4-01 can be marked **VERIFIED-CLOSED** only when all are true:

1. The real production cluster, database, and runtime login have been identified from the deployment configuration/secret metadata and hosting control plane.
2. The runtime login is a dedicated LOGIN principal, not a superuser, database/table owner, migration principal, or public-reader principal.
3. It has no CREATEDB, CREATEROLE, REPLICATION, BYPASSRLS, or inherited broad privileges.
4. It has explicit SET-only membership in exactly the capability roles required by the deployed application; no ADMIN OPTION and no unapproved additional memberships.
5. Effective role switching, tenant RLS isolation, no-context denial, and negative privilege tests pass on the actual target or a faithful controlled production clone.
6. Evidence is reviewed by an authorized database/hosting operator and stored without credentials or sensitive connection details.

## 8. Current disposition and next dependency

**A4-01: PARTIAL — CONTRACT AND VERIFICATION PROCEDURE ESTABLISHED; LIVE PRODUCTION IDENTITY/MEMBERSHIP NOT ESTABLISHED.**

Repository evidence confirms the application role mapping and required PostgreSQL security model. It does not identify a deployed production login or prove any production membership. The current G1 configuration intentionally blocks production database connections. No production access was attempted and no production state was changed.

**Single external dependency:** identify the actual MaaleNex production hosting/database target and the deployed `DATABASE_URL` secret reference (username/role name only). Once that target is available, an authorized operator can run the read-only checks above. Provisioning grants remain a separately approved change.
