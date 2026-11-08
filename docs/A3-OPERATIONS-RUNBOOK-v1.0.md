# A3 Passenger MVP Operations Runbook v1.0

Status: A3 implementation reference; development/test synthetic-only.

## Security and activation boundary

The current repository configuration intentionally permits only local PostgreSQL development/test databases and synthetic data. `SECURE_COOKIES=true` is the explicit setting for TLS-terminating reverse-proxy environments; verify it in the deployment configuration before exposing any HTTPS endpoint. Do not use real passenger information, real operator identity documents, live payment credentials, production passenger accounts, or production trip publication. Payment collection, travel-ticket issuance and boarding validation remain disabled.

A reservation reference is not a travel ticket and does not authorize boarding.

## Operator membership invitations

1. Provision a synthetic platform administrator using `python scripts/seed_synthetic_admin.py`.
2. Create and approve a synthetic operator through the protected administration API.
3. Create a membership invitation through `POST /api/v1/operators/{organization_id}/invitations`.
4. The API returns a one-time synthetic invitation token only in the synthetic development/test environment. No email/SMS is sent.
5. Accept the invitation through `POST /api/v1/auth/operator-invitations/accept` with the token and a password of at least 14 characters.
6. The token expires after 48 hours and can be used once. A later invitation revokes an earlier unaccepted invitation for the same operator/login.
7. Revoke unused invitations or memberships through the protected administration endpoints. Membership revocation also revokes the user's role assignments for that operator.

Do not distribute synthetic invitation tokens as real operator onboarding links.

## Passenger booking access and recovery

- Challenge creation and verification use separate durable per-IP rate-limit buckets. Verification attempts are counted across challenge IDs; requesting another challenge does not reset the verification budget. The verification endpoint returns HTTP 429 when the IP-level window is exhausted.
- When running behind a TLS-terminating reverse proxy, set `SECURE_COOKIES=true` in the application environment. This forces the `Secure` attribute on staff-session, staff-CSRF, booking-access and booking-CSRF cookies even when the ASGI request scheme is HTTP. Do not rely on untrusted forwarded headers to infer the external scheme. Local HTTP development may leave this setting false; HTTPS requests always receive Secure cookies.

- Booking access is granted only after the booking contact challenge succeeds.
- Access grants are opaque, stored as hashes, scoped to one booking, expire after two hours and are CSRF-bound.
- The passenger app stores only the active booking ID in sessionStorage. The access cookie remains HttpOnly and booking-path scoped.
- On refresh, the app retrieves booking state, the existing reservation reference and the reservation QR through protected booking APIs.
- The QR encodes only a versioned opaque reservation reference. It is an identification reference, not a travel ticket and cannot authorize boarding.
- A passenger can revoke all active grants for the booking. Revocation clears the browser cookies and the sessionStorage booking pointer.
- Challenge codes are returned to the UI only when running in development/test with synthetic-only mode. A real delivery provider is not configured.

## Support queue

Passengers with a verified booking grant can submit a bounded support case for booking access, reservation status, accessibility or other issues. Staff with `platform.support.manage` can list cases, claim a case and resolve it with a resolution code and note.

Audit metadata records the case category and lifecycle action; it does not copy the passenger's free-text message into the audit log. Support messages may still contain personal information and must be handled as restricted passenger data.

## Passenger manifest access

The trip manifest endpoint requires `operator.trip.manifest.read` scoped to the trip's operator. It returns only reserved passenger names, seat codes and booking references. Booking contact phone numbers are excluded. Every manifest read is audited.

This is an operational roster view only; it does not enable boarding validation.

## Booking maintenance

Run from `backend/` in a configured local synthetic environment:

```powershell
python scripts/booking_maintenance.py --batch-size 500
```

The command is restricted by application settings to development/test synthetic-only mode. It:
- Expires active seat holds whose database expiry time has passed.
- Releases their active seat allocations and transitions expired held bookings to `expired`.
- Purges expired idempotency records.
- Purges expired/consumed access challenges after one day.
- Purges expired/revoked guest access grants after 30 days.
- Purges guest rate-limit records older than 30 days.
- Purges expired, accepted or revoked operator invitations after 30 days.

The command is bounded and safe to rerun. For recurring synthetic maintenance, run the supervised worker from `backend/`:

```powershell
python scripts/booking_maintenance_worker.py --interval-seconds 60 --batch-size 500
```

The worker handles SIGINT/SIGTERM, logs each cycle, retries on the next interval after a failed cycle and uses PostgreSQL `SKIP LOCKED` batches so concurrent worker instances do not process the same hold rows. Use a local process supervisor if automatic restart is needed. No production scheduler or production worker has been installed or enabled.

## Passenger UI accessibility baseline

The passenger UI uses semantic headings and forms, associated visible labels, a localized keyboard skip link, visible keyboard focus indicators, an `aria-live` trip-results region, pressed-state seat controls, disabled unavailable seats and alternative text for the reservation QR. This is an implementation-level accessibility baseline; an independent WCAG 2.2 AA audit and assistive-technology usability review have not been performed.

## Verification

The A3 GitHub Actions workflow runs:
- Python compilation and focused Ruff correctness checks.
- Backend tests, including PostgreSQL seat contention, hold expiry, access revocation, invitation acceptance and support-case access.
- PostgreSQL migration upgrade, Alembic metadata parity, downgrade and clean re-upgrade.
- Frontend Vitest, TypeScript typecheck and Vite production build.

A successful CI run verifies the exact commit SHA checked out by that run. It does not constitute production readiness, legal review, penetration testing, or approval to activate a pilot.
