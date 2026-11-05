# G1 module boundaries

G1 establishes infrastructure seams, not domain approval.

- `app/core`: runtime configuration and cross-cutting primitives.
- `app/db`: SQLAlchemy base, engine, and request-scoped session lifecycle.
- `app/routers`: HTTP transport adapters; routers must not own persistence logic.
- `app/schemas`: explicit API request/response contracts.
- `app/domains`: reserved for domain-owned application services, models, and policies after G2 approval.

Domain packages must not import another domain's persistence internals. Cross-domain collaboration must use explicit application interfaces. Shared infrastructure must not become a dumping ground for business rules. No passenger, driver, vehicle, booking, dispatch, payment, or service domain model is created in this G1 change.
