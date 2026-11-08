# A3 — Shared Platform Foundation v1.0

**Status:** IN IMPLEMENTATION  
**Parent baseline:** Passenger foundation `0a01631a21a823b720337d1d80aa690e5df347bc`  
**Branch:** `feat/a3-maalenex-shared-platform-foundation`  
**Scope:** A3.1/A3.2 first bounded increment — platform service registry and geographic availability policy  
**Data boundary:** synthetic-only; no live service activation

## Objective

Create a common, explicit registry for the eight frozen MaaleNex service lines and their area-specific rollout state. The registry must distinguish planned, synthetic-test, pilot, active and suspended states. A synthetic-test record must never be represented as live service availability.

## Implemented in this increment

- PostgreSQL/Alembic migration `0008_platform_service_registry`, appended after existing revision `0007_operator_invites_support`.
- `platform_services`: canonical service code, display name, description, rollout status, enabled flag and display order.
- `service_areas`: stable area code, display name, country code and administrative-area metadata.
- `service_area_availability`: service/area policy, rollout state, enablement and validity window, with uniqueness, foreign keys and database checks.
- Read-only API `GET /api/v1/platform/services`, optionally filtered by `area_code`.
- Test-only deterministic seed for eight service lines across Koybe, Jinka, Wolaita Sodo and Addis Ababa.
- Synthetic Transit catalog status only; all other service lines remain planned and disabled.
- PostgreSQL integration tests for idempotent seeding, all-eight-service enumeration, unknown-area behavior and the prohibition on treating synthetic-test state as live availability.
- Dedicated GitHub Actions workflow for migration, seed, backend/PostgreSQL tests, Alembic parity, downgrade/re-upgrade and frontend regression gates.

## Explicit non-claims

- No service is activated for real customers or operators.
- No live dispatch, GPS, maps provider, payment collection, ticket issuance, boarding or commercial operation is enabled.
- This increment does not implement complete Move, Delivery, Cargo, Market, Fleet, Business or Pay workflows.
- Synthetic catalog availability is not proof of real operator supply, published schedules or regulatory readiness.
- No production hosting or persistent HTTPS API is created.

## Next A3 increments

1. Complete cross-service identity, account, organization and role/tenant authorization contracts.
2. Complete trust/verification and document metadata lifecycle.
3. Add transactional outbox/inbox, idempotent worker and failure observability foundations.
4. Add consent-bound location-session contracts with synthetic-only location samples.
5. Build service-specific Move, Delivery and Cargo state machines, followed by Market, Business, Fleet expansion and synthetic Pay ledger invariants.

Every increment remains on a feature branch, adds focused tests, extends the single Alembic chain and must pass exact-commit remote verification. Merge and A5 deployment are separately gated.
