# MaaleNex Cargo Dispatch and Tracking v1

## Scope
Backend-only dispatch offers and append-only tracking. No frontend, GPS polling, live map, public tracking links, external carrier webhooks, payment or dispatch optimization are included.

## Dispatch lifecycle

`offered -> accepted -> picked_up -> in_transit -> delivered`

Offers may be rejected or cancelled; accepted dispatches may be cancelled before pickup; accepted, picked-up or in-transit dispatches may fail into an exception. Terminal states cannot be reopened. The consignment projection is synchronized under row locks: accepted -> assigned -> in_transit -> delivered, with failed/rejected mapped to exception and cancellation limited to unstarted consignments.

Only platform dispatch managers can create offers. Only the assigned operator organization or platform dispatch manager can advance the dispatch. A carrier vehicle, if supplied, must belong to that operator and be active and approved.

## Tracking

Tracking records are append-only and ordered per dispatch by a monotonically increasing sequence number. A dispatch-scoped idempotency key prevents duplicate writes. Each record separates operator-reported `occurred_at` from server `recorded_at`; timestamps outside the preceding 30 days or more than five minutes in the future are rejected. Optional coordinates are range-checked and must be supplied as a pair. No continuous location collection is performed.

## API

- `POST /api/v1/cargo/dispatches`
- `POST /api/v1/cargo/dispatches/{id}/transition`
- `POST /api/v1/cargo/dispatches/{id}/tracking-events`
- `GET /api/v1/cargo/dispatches/{id}/tracking-events`

## Boundaries

Migration `0020_cargo_dispatch_tracking` is additive after `0019_cargo_consignments`. It is not applied to hosted databases. No commercial operation, external provider, public location feed, or IROKA autonomous action is enabled.
