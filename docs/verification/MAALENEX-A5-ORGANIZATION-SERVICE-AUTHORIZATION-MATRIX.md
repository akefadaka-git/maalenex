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
| Operator vehicle fleet | `POST /operators/{organization_id}/vehicles`, `POST /vehicles/{vehicle_id}/seat-layouts` | `operator.fleet.manage` + service code `fleet` | Service assignment and exact tenant membership; seat-layout tenant is derived from persisted vehicle |
| Platform fleet review | `POST /vehicles/{vehicle_id}/review`, `POST /seat-layouts/{layout_id}/approve` | `platform.fleet.review` | Platform-wide review privilege; not an operator service grant |
| Operator trips | `POST /operators/{organization_id}/trips`, `POST /trips/{trip_id}/submit` | `operator.trip.manage` + service code `transit` | Service assignment and exact tenant membership; submit tenant is derived from persisted trip |
| Trip manifest | `GET /trips/{trip_id}/manifest` | `operator.trip.manifest.read` + service code `transit` | Service assignment and exact tenant membership; tenant derived from persisted trip |
| Platform trip control | `POST /trips/{trip_id}/approve`, `POST /trips/{trip_id}/publish` | `platform.trip.approve`, `platform.trip.publish` | Platform-wide approval/publication privilege; not an operator service grant |
| Operator fares | `POST /operators/{organization_id}/fares`, `POST /fares/{fare_id}/versions/{version_id}/submit` | `operator.fare.propose` + service code `transit` | Service assignment and exact tenant membership; submit tenant is derived from persisted fare |
| Platform fare control | Fare-version review and publish | `platform.fare.approve`, `platform.fare.publish` | Platform-wide reviewer/publisher privilege; proposer and reviewer remain separate identities in fare workflow |
| Support and audit | Support list/claim/resolve; audit event list | `platform.support.manage`, `platform.audit.read` | Platform-wide support/audit administration |
| Guest booking capability | Booking read, reservation QR, support cases, reservation acceptance and access revoke | Booking-specific guest grant; mutation requires `manage` scope and CSRF | Grant is bound to the booking; no staff role is implied |
| Disabled capabilities | Cancellation, ticket issuance, boarding validation | Explicit disabled response | Not authorized or implemented for live operation |

## Service-scoped authorization status

The shared authorization function `has_service_permission()` enforces the complete service tuple (user, organization, service code, permission) and verifies active membership, approved organization and active user. Operator route authorization now resolves service code through `OPERATOR_PERMISSION_SERVICE_MAP` in `backend/app/routers/admin.py` and invokes this service-scoped guard for every tenant-scoped `operator.*` permission listed below.

| Permission code | Service code | Operator route coverage |
|---|---|---|
| `operator.fleet.manage` | `fleet` | Vehicle creation and seat-layout creation |
| `operator.trip.manage` | `transit` | Trip creation and trip submission |
| `operator.trip.manifest.read` | `transit` | Passenger manifest read |
| `operator.fare.propose` | `transit` | Fare proposal and fare-version submission |

Platform-wide `platform.*` permissions remain on the existing explicit platform-role path and are not implicitly converted to tenant service grants. The service code is always paired with the exact organization ID, permission code, active user, approved organization, active membership and unrevoked service-role assignment.

PostgreSQL HTTP integration tests authenticate with real synthetic staff-session cookies and CSRF tokens. They prove that a Fleet service assignment permits vehicle creation in its assigned tenant but returns HTTP 403 for another tenant even when the user is also a member there; Transit trip creation reaches domain validation in the assigned tenant but returns HTTP 403 for the other tenant. Separate helper tests continue to cover wrong-service and revoked-grant denial.

This mapping covers the currently implemented passenger-operator routes only. It does not imply that Move, Delivery, Cargo, Market, Business or Pay have implemented route families or active commercial availability.

## A5 regression coverage added

- Nested audit metadata arrays are recursively redacted without flattening or stringifying safe lists.
- Organization-scoped route guard denies a grant when the requested tenant differs, even when the same user is a member of both organizations.
- Organization-scoped route guard denies a revoked membership and an inactive user even if a role assignment row remains.
- Service-scoped guard denies a grant for another tenant or another service and denies revoked assignments/memberships.

## Remaining work / limits

- Extend the mapping only when additional service route families are implemented and their permission contracts are specified.
- Continue adding authenticated HTTP tests for newly introduced sensitive route families.
- Keep platform-wide control-plane permissions distinct from operator tenant privileges; do not silently narrow or broaden these existing platform roles.
- Cross-tenant tests use synthetic PostgreSQL fixtures only. They do not authorize live data, production access or deployment.
