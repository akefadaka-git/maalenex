# MaaleNex A5 — Service-Scoped Operator Authorization Verification

**Status:** IMPLEMENTED; exact-head automated verification PASS on the application-code commit recorded below  
**Branch:** `a5/deployment-readiness-assessment`  
**Application-code commit tested:** `be7775a18a52bc282913401572d867d31bd90d2e`  
**Workflow:** [A5 verification run #18](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42562478263)

## Scope delivered

The operator route authorization path now uses the service-scoped policy primitive rather than the legacy organization-only permission helper for tenant-scoped operator permissions.

The canonical mapping is maintained in `backend/app/routers/admin.py` as `OPERATOR_PERMISSION_SERVICE_MAP`:

| Permission | Service | Routes |
|---|---|---|
| `operator.fleet.manage` | `fleet` | `POST /operators/{organization_id}/vehicles`; `POST /vehicles/{vehicle_id}/seat-layouts` |
| `operator.trip.manage` | `transit` | `POST /operators/{organization_id}/trips`; `POST /trips/{trip_id}/submit` |
| `operator.trip.manifest.read` | `transit` | `GET /trips/{trip_id}/manifest` |
| `operator.fare.propose` | `transit` | `POST /operators/{organization_id}/fares`; `POST /fares/{fare_id}/versions/{version_id}/submit` |

For each mapped permission, the guard requires the exact user, organization, service code and permission code; an active user; an approved organization; an active, unrevoked organization membership; and an unrevoked service-role assignment. Tenant IDs for resource-based routes are derived from the persisted vehicle, trip or fare before authorization.

Platform-wide `platform.*` control-plane permissions remain on the explicit platform-role path. They are not implicitly translated into tenant service grants. No platform-wide role semantics were widened.

## Authenticated HTTP regression tests

Added `backend/tests/test_operator_service_authorization_http.py` and updated the existing authenticated manifest integration test in `backend/tests/test_postgres_booking_concurrency.py`.

The tests use synthetic PostgreSQL records, real staff-session cookies and CSRF cookies/headers:

- **Fleet tenant isolation:** a Fleet assignment allows vehicle creation in Tenant A (HTTP 201) and denies the same authenticated principal in Tenant B (HTTP 403), even though the principal is also an active member of Tenant B.
- **Transit tenant isolation:** the Transit assignment reaches trip-domain validation in Tenant A (HTTP 409 for the deliberately unpublished/missing route) and is denied in Tenant B (HTTP 403).
- **Manifest tenant isolation:** the existing authenticated manifest test now uses a Transit service-role assignment; it permits the assigned tenant and denies access to a trip belonging to another tenant (HTTP 403).
- Existing service-helper regression tests continue to cover wrong-service, wrong-organization, revoked service assignment and revoked membership denial.

These are HTTP-level authorization checks, not only direct helper tests.

## Exact-head verification

Run [#42562478263](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42562478263) tested application-code commit `be7775a18a52bc282913401572d867d31bd90d2e` and completed successfully:

| Gate | Result |
|---|---|
| Backend compile and Ruff correctness checks | PASS |
| PostgreSQL 16 migrations and service-registry seed idempotency | PASS |
| Full backend/PostgreSQL integration suite | PASS — 47 passed, 1 warning |
| Alembic model metadata parity | PASS — no new upgrade operations |
| Full downgrade to base and clean re-upgrade | PASS |
| Frontend tests, TypeScript, Vite build and npm audit | PASS |
| Python dependency audit and Bandit high-severity scan | PASS |

The single test-suite warning is a Starlette deprecation warning about the installed httpx/TestClient integration; it did not fail the suite. The workflow also reported GitHub runner action Node.js 20 deprecation notices; these are runner/tooling notices, not application test failures.

## Scope boundaries

- No database migration or schema change was needed for this authorization wiring.
- This mapping covers the currently implemented passenger-operator route families only. It does not claim that Move, Delivery, Cargo, Market, Business or Pay have implemented route families.
- Service authorization is distinct from service rollout activation. This change does not enable a planned service or authorize commercial operation.
- No production data, live payment, live GPS, customer communications, deployment, merge or production activation occurred.
- A5 deployment readiness remains **NOT READY** pending the other infrastructure, key lifecycle, TLS, backup/recovery, monitoring, privacy and regulatory gates.
