# MAALENEX-IA-A3.5 — Tenant RLS and Geographic Permissions

**Status:** Implemented on integration branch; PostgreSQL execution and verification pending  
**Migration:** `0023_geo_tenant_rls_permissions`  
**Parent:** `0022_geo_publication_views`

## 1. Tenant context and application authorization

The database reads the transaction-local setting `app.current_organization_id` through `geo.current_organization_id()`. Missing, empty or malformed values return NULL. Tenant policies compare each row's tenant to this value, so absent context returns no tenant rows and rejects tenant writes.

The application helper `authorize_geo_tenant_context` requires either (a) active organization membership plus a non-revoked organization-scoped role grant, or (b) an explicit platform-wide grant for a `platform.*` permission. Only after authorization does it assume a static, least-privilege database capability role and call `set_config(..., true)`. The role switch and tenant context last only for the current transaction. Commit/rollback clears the context and role switch.

The application database login must be granted membership (with SET capability) in the relevant NOLOGIN capability roles out-of-band. If role assumption is unavailable, protected access fails closed. The app must not connect as a table owner, database owner, superuser or migration principal.

## 2. RLS coverage

RLS is enabled on:
- `geo.data_sources`, `locations`, `terminals`, `routes`, `route_stops`, `boundaries`
- `geo.route_versions` (tenant inherited through parent route)
- `geo.roads` (tenant inherited from provenance source)
- `geo.devices`, `device_vehicle_assignments`, `vehicle_positions`
- `geo.publications`
- `geo.legacy_tracking_quarantine` (no policy: default deny)

Nullable/global catalog rows do not become tenant-visible. Road and route-version access is derived from tenant-owned parent/provenance records. Quarantine remains inaccessible until its records have separately trusted tenant attribution.

RLS is enabled but not forced on table owners. This preserves the A3.4 owner-permission public views. Runtime requests must explicitly assume a non-owner capability role before querying protected data.

## 3. Database capability roles

All roles are NOLOGIN, NOSUPERUSER, NOCREATEDB and NOCREATEROLE:
- `maalenex_geo_internal_reader`: SELECT only on vehicle positions and its invoker-security view.
- `maalenex_geo_tenant_manager`: SELECT positions; SELECT/INSERT/UPDATE devices and assignments.
- `maalenex_geo_catalog_manager`: SELECT/INSERT/UPDATE tenant-owned geography, provenance and publication tables.

No role receives access to the legacy quarantine table. Roles do not receive DELETE or TRUNCATE privileges. Deployment-specific login membership is not created by migrations and must be provisioned only for trusted backend principals.

## 4. Permission catalogue and grants

New permission codes:
- `platform.geo.internal.read`
- `platform.tracking.read`
- `platform.tracking.manage`
- `platform.geo.manage`
- `platform.geo.publish`
- `platform.geo.audit.read`

Least-privilege mappings:
- Platform operations manager: internal geography and tracking read
- Platform dispatch manager: internal geography and tracking read/manage
- Platform catalog manager: geography manage/publish
- Platform auditor: geography audit read
- Operator manager: tracking read/manage within assigned organization
- Operator dispatcher: tracking read within assigned organization
- Operator fleet manager: tracking read/manage within assigned organization

Platform grants are explicit null-organization assignments. Operator grants require active membership and an organization-scoped role assignment. The permission `platform.geo.audit.read` is catalogued and assigned; a dedicated geo audit event sink remains a later integration item and is not claimed as implemented here.

## 5. Verification requirements

- [ ] Run PostgreSQL integration tests with two tenants.
- [ ] Verify no-context reads return zero rows.
- [ ] Verify tenant A cannot read tenant B's positions through the invoker view or base table.
- [ ] Verify internal reader cannot access credentials, assignments or quarantine.
- [ ] Verify application authorization rejects missing/revoked membership and ungranted users.
- [ ] Verify capability-role switching is denied to principals without explicit role membership.
- [ ] Run Alembic graph, metadata parity, downgrade and clean re-upgrade.

**Security caveat:** RLS context is a trusted application-set session variable, not an authentication credential. It must only be set after server-side identity, membership and permission validation. No endpoint or service may accept a tenant setting directly from an untrusted client.
