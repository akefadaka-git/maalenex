# MaaleNex A5 — Organization and Service Route Authorization Matrix

**Scope:** A5.2 authorization review of the current passenger foundation API. This matrix describes route guards present in the A5 assessment branch; it is not a statement that every planned service is implemented or enabled.

## Authorization invariants

1. A staff request must resolve to an active user and valid, unrevoked, unexpired staff session.
2. Mutating staff routes additionally require CSRF validation.
3. A tenant-scoped grant must match the exact target `organization_id`; a grant for one organization must not authorize another.
4. Tenant-scoped legacy role grants require an active membership in an approved organization. Revoked membership, revoked assignment, or inactive user denies access.
5. A service-scoped grant must match the exact `organization_id`, `service_code`, active user, active membership, approved organization, and unrevoked service-role assignment.
6. Platform-wide privileges are explicit: a null-organization role assignment is accepted only for `platform.*` permission codes. These are control-plane privileges and intentionally span tenants.
7. Guest booking access is capability-based and bound to a booking, scope, expiry, revocation state and (for mutations) CSRF proof. It is not a staff tenant role.

## Route matrix

| Route family | HTTP routes | Required guard | Tenant/service boundary |
|---|---|---|---|
| Public catalog and discovery | `GET /catalog/locations`, `GET /catalog/routes`, `GET /trips/search`, `GET /trips/{trip_id}/seats` | No staff session; query filters only published records, approved operator and effective ETB fare | Public read-only data; no tenant write authority |
| Public service registry | `GET /platform/services` | No staff session; service and area rollout flags are evaluated | Public rollout metadata; synthetic-test availability is not live availability |
| Platform operator control | `POST /operators`, `POST /operators/{organization_id}/review` | `platform.operator.create`, `platform.operator.review` | Explicit platform-wide control-plane authority |
| Platform access administration | `POST /operators/{organization_id}/role-assignments`, `POST /operators/{organization_id}/invitations`, invitation revoke, membership revoke | `platform.access.manage` | Explicit platform-wide administrator may manage the target tenant; target IDs are still checked against the requested organization |
| Platform catalog management | Location, terminal and route create/publish endpoints | `platform.catalog.manage`, `platform.catalog.publish` | Shared platform catalog; platform-wide |
| Operator fleet | `POST /operators/{organization_id}/vehicles`, `POST /vehicles/{vehicle_id}/seat-layouts` | `operator.fleet.manage` | Tenant ID comes from route organization or persisted vehicle; exact organization grant required |
| Platform fleet review | `POST /vehicles/{vehicle_id}/review`, `POST /seat-layouts/{layout_id}/approve` | `platform.fleet.review` | Platform-wide review privilege |
| Operator trips | `POST /operators/{organization_id}/trips`, `POST /trips/{trip_id}/submit` | `operator.trip.manage` | Tenant ID comes from route organization or persisted trip |
| Trip manifest | `GET /trips/{trip_id}/manifest` | `operator.trip.manifest.read` | Tenant ID is derived from the persisted trip; sensitive passenger manifest |
| Platform trip control | `POST /trips/{trip_id}/approve`, `POST /trips/{trip_id}/publish` | `platform.trip.approve`, `platform.trip.publish` | Platform-wide approval/publication privilege |
| Operator fares | `POST /operators/{organization_id}/fares`, fare-version submit | `operator.fare.propose` | Tenant ID comes from route organization or persisted fare |
| Platform fare control | Fare-version review and publish | `platform.fare.approve`, `platform.fare.publish` | Platform-wide reviewer/publisher privilege; proposer and reviewer remain separate identities in fare workflow |
| Support and audit | Support list/claim/resolve; audit event list | `platform.support.manage`, `platform.audit.read` | Platform-wide support/audit administration |
| Guest booking capability | Booking read, reservation QR, support cases, reservation acceptance and access revoke | Booking-specific guest grant; mutation requires `manage` scope and CSRF | Grant is bound to the booking; no staff role is implied |
| Disabled capabilities | Cancellation, ticket issuance, boarding validation | Explicit disabled response | Not authorized or implemented for live operation |

## Service-scoped authorization status

The shared authorization function `has_service_permission()` enforces the complete service tuple (user, organization, service code, permission) and verifies active membership, approved organization and active user. Its PostgreSQL integration tests cover wrong-service, wrong-organization, revoked assignment and revoked membership.

**Important implementation boundary:** current operator route guards call the organization-scoped `has_permission()` helper with `operator.*` permissions. They do not yet call `has_service_permission()` or derive a service code from each route. The service-scoped model/helper is therefore verified as a policy primitive, but service-role enforcement is not yet wired end-to-end across operator routes. Do not interpret this matrix as proof that the eight product service lines have independent route-level role enforcement.

## A5 regression coverage added

- Nested audit metadata arrays are recursively redacted without flattening or stringifying safe lists.
- Organization-scoped route guard denies a grant when the requested tenant differs, even when the same user is a member of both organizations.
- Organization-scoped route guard denies a revoked membership and an inactive user even if a role assignment row remains.
- Service-scoped guard denies a grant for another tenant or another service and denies revoked assignments/memberships.

## Remaining work / limits

- Build a route-to-service mapping and wire service-scoped checks into routes only after the Owner-approved service/permission mapping is explicit.
- Add end-to-end HTTP tests for each sensitive route family using authenticated synthetic staff sessions.
- Keep platform-wide control-plane permissions distinct from operator tenant privileges; do not silently narrow or broaden these existing platform roles.
- Cross-tenant tests use synthetic PostgreSQL fixtures only. They do not authorize live data, production access or deployment.
