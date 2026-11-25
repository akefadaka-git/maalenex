# MAALENEX-IA-A3.5 — Tenant RLS and Geographic Permissions

**Status:** Implemented on integration branch; PostgreSQL execution and verification pending  
**Migration:** `0023_geo_tenant_rls_permissions`  
**Parent:** `0022_geo_publication_views`

## 1. Tenant context

The database reads the transaction-local setting `app.current_organization_id` through `geo.current_organization_id()`. Missing, empty or malformed values return NULL. All tenant policies compare the row's tenant to this value, so absent context returns no tenant rows and rejects tenant writes.

The application helper `authorize_geo_tenant_context` requires either (a) active organization membership plus a non-revoked organization-scoped role grant, or (b) an explicit platform-wide grant for a `platform.*` permission. Only after authorization does it call `set_config(..., true)`, which limits context to the current database transaction. The caller must keep protected queries in that same transaction; commit/rollback clears the context.

## 2. RLS coverage

RLS is enabled on:
- `geo.data_sources`, `locations`, `terminals`, `routes`, `route_stops`, `boundaries`
- `geo.route_versions` (tenant inherited through parent route)
- `geo.roads` (tenant inherited through provenance source)
- `geo.devices`, `device_vehicle_assignments`, `vehicle_positions`
- `geo.publications`
- `geo.legacy_tracking_quarantine` (no policy: default deny)

Nullable/global catalog rows do not become tenant-visible. Road and route-version access is derived from tenant-owned parent/provenance records. Quarantine remains inaccessible until its records have a separately trusted tenant attribution.

RLS is enabled but not forced on table owners. This preserves the A3.4 owner-permission public views. It also means the application and tile services must never connect as table owner, database owner, superuser or migration principal. A non-owner service principal with only the grants it needs is required for RLS to be effective.

## 3. Internal tracking role

`maalenex_geo_internal_reader` remains NOLOGIN and receives:
- USAGE on `geo` and `geo_internal`
- SELECT on `geo.vehicle_positions` and `geo_internal.vehicle_positions`
- EXECUTE on the tenant-context function

The view is invoker-security. Both direct base-table reads and view reads are filtered by the same vehicle-position RLS policy. It receives no access to device credentials, device assignments or quarantine. Credentials and writes remain outside this read-only role.

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
- [ ] Run Alembic graph, metadata parity, downgrade and clean re-upgrade.

**Security caveat:** RLS context is a trusted application-set session variable, not an authentication credential. It must only be set after server-side identity, membership and permission validation. No endpoint or service may accept a tenant setting directly from an untrusted client.
