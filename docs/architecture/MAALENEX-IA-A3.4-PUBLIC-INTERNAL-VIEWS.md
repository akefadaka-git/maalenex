# MAALENEX-IA-A3.4 — Public and Internal Spatial Views

**Status:** Implemented on integration branch; database execution and verification pending  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Predecessor:** `0021_mitp_tracking_to_geo`  
**Migration:** `0022_geo_publication_views`

## 1. Public publication contract

The migration creates `geo_public` and exposes six explicit views: locations, terminals, routes, route stops, boundaries and roads. Catalog views require both the feature's publication flag/status and a matching, non-revoked publication record tied to the same source. The source must be verified and publication-eligible. Roads require active status and verified, publication-eligible provenance.

The public projection intentionally omits organization/tenant IDs, device identifiers, credentials, telemetry, staff/actor identifiers, internal notes and arbitrary road attributes. Route stops are visible only when the stop, route and location all qualify for public publication.

No raw `geo` table privileges are granted to the public reader role. Views use PostgreSQL owner permissions and a security-barrier option; the non-login role receives only schema usage and SELECT on the six sanitized views. It is not granted to PUBLIC and has no login, superuser, database-creation or role-creation capability.

## 2. Internal tracking boundary

The migration creates `geo_internal.vehicle_positions` as an explicit projection with tenant and vehicle identity, timestamps, geometry and operational measurements. It uses `security_invoker = true` so that subsequent row-level security applies as the invoking database principal.

**No internal schema usage or view SELECT privilege is granted in A3.4.** This is intentional: A3.5 must implement and verify tenant RLS, fail-closed tenant context, and the required service-role grants before any internal reader can use this view. No raw tracking table access is granted to either reader role.

## 3. Role lifecycle

- `maalenex_geo_public_reader`: NOLOGIN capability role, only six public views.
- `maalenex_geo_internal_reader`: NOLOGIN placeholder; no access grants until A3.5.
- Deployment-specific login principals and membership are managed separately from migrations. No credentials or passwords are created in this migration.
- Downgrade drops views/schemas and revokes public-view grants. Cluster-level NOLOGIN roles are retained to avoid breaking external memberships.

## 4. Security and verification limits

The public view predicates require `status = 'published'`, feature publication eligibility, a matching publication row with status published and no revocation timestamp, and verified/publication-eligible source provenance. A source's license metadata must still be assessed for legal suitability; this migration does not assert that an unverified source or any particular license is publishable.

The internal view is not an authorization boundary until A3.5 RLS is applied. The view owner must remain a controlled migration/ownership principal; application and tile services must not connect as the owner or a superuser.

## 5. Verification evidence required

- [ ] Apply migration on disposable PostGIS PostgreSQL.
- [ ] Verify role attributes and exact schema/table grants.
- [ ] Verify public view column allowlists and no raw tracking access.
- [ ] Insert representative published/unpublished fixtures and prove only eligible records appear.
- [ ] Verify internal reader remains denied before A3.5.
- [ ] Run `alembic check`, full downgrade and clean re-upgrade.

**Disposition:** A3.4 migration, contract tests and documentation are committed to the integration branch. Execution remains NOT RUN. No live database, merge or deployment was touched.
