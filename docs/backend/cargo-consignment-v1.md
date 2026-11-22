# MaaleNex Cargo Consignment Backend v1

## Scope

This increment adds the first organization-scoped cargo consignment lifecycle to the MaaleNex API. It is backend-only and does not add passenger-facing screens, frontend routes, payment collection, pricing, dispatch optimization, live tracking, or external carrier integrations.

## Lifecycle

`draft -> accepted -> assigned -> in_transit -> delivered`

An active consignment may enter `exception` where explicitly allowed; exception recovery must return through assignment or transit. Draft, accepted and assigned consignments may be cancelled. Delivered and cancelled are terminal. Invalid or skipped transitions return HTTP 409.

## Data and controls

- Each consignment belongs to an approved MaaleNex organization.
- Reference and idempotency key are unique within the owning organization.
- Reusing an idempotency key with a different payload returns HTTP 409.
- Carrier assignment requires an approved operator organization.
- Staff endpoints require the explicit `platform.cargo.manage` permission and CSRF protection for mutations.
- Every create and transition appends a redacted audit event.
- Weight is stored as integer grams; no currency, fare or payment fields are introduced.
- No passenger contact details, payment credentials, or identity documents are collected in this increment.

## API

- `POST /api/v1/cargo/consignments`
- `GET /api/v1/cargo/consignments?organization_id=<uuid>&limit=50`
- `POST /api/v1/cargo/consignments/{id}/transition`

The API prefix is controlled by the existing MaaleNex backend configuration. The exact prefix must be read from the deployed environment; no deployment is included here.

## Release boundaries

The migration is additive and follows revision `0018_koybe_boarding_point`. No migration has been applied to a hosted database. No route geometry, passenger trip, wallet, payment, or IROKA execution is affected. IROKA remains advisory and disabled by default.
