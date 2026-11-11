# MaaleNex A3 — Location Consent Foundation

**Branch:** `feat/a3-location-consent-foundation`  
**Base:** A4 reconciled candidate `3e91081885d4d54ede01b3e281e03ad30efbd256`  
**Scope:** versioned location consent, exact active-resource scoping, revocation, expiry, freshness classification and synthetic-only sample persistence.

## Safety boundary

- No HTTP endpoint, device permission request, background collector, GPS SDK, WebSocket, map provider or live-location adapter is introduced.
- Location samples are accepted only through an internal synthetic-fixture function and the database enforces `is_synthetic = true` and `source = synthetic_fixture`.
- Every consent is bound to one account, service, resource type, resource identifier, purpose and consent-text version.
- Sessions require an authoritative resource lookup by the calling domain. The caller must pass the verified resource owner and current status; only matched/accepted/arrived/in-progress resources are eligible.
- Revocation terminates active sessions in the same transaction. Expiry is enforced by database time at session/sample boundaries and by an idempotent expiry function.
- Freshness is computed from the captured timestamp and caller-supplied freshness window; coordinates are never returned by the freshness API.
- Synthetic fixtures only. No production location data or service activation.

## State model

Consent: granted → (revoked | expired by time). Consent rows are retained as evidence; revocation is timestamped.

Session: active → completed | expired | revoked. A partial unique index permits at most one active session per consent.

Sample: immutable-by-convention synthetic fixture tied to one session; latitude/longitude range and source/synthetic checks are enforced in PostgreSQL.

## Verification

The branch workflow runs PostgreSQL 16, the full backend test suite, migration upgrade, Alembic metadata parity and full downgrade/clean re-upgrade. The implementation does not change the default branch or any existing PR. The workflow result must be checked against the exact final branch SHA before this increment can be marked verified.

## Next dependency

After this foundation is verified, implement the Move lifecycle so its authoritative ride-state and account-ownership checks are the only callers allowed to open location sessions. Live location collection remains separately gated.
