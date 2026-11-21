# MaaleNex scheduler operations and role-based administration

## Scope and safety boundary

This design is production-compatible in its process and database coordination model, but this repository baseline remains synthetic development/test only. It does not enable production mode, remote database access, payment, refunds, ticketing, boarding, SMS, or email. Scheduler execution is opt-in and disabled by default.

## Scheduler topology

Run the API and maintenance worker as separate processes. The API never starts a scheduler task in its lifespan. Apply the database migrations first, then start the worker explicitly from `backend/`:

```bash
SCHEDULER_ENABLED=true python -m app.jobs.scheduler_worker
```

The worker refuses to start unless the application is in development/test mode, synthetic-only mode is true, and the explicit enable flag is set. The existing configuration still rejects production mode, non-local databases, and non-synthetic operation.

The scheduler uses PostgreSQL-backed durable state:
- `scheduler_leases`: one lease row per job, owner identity, lease expiry and heartbeat.
- `scheduler_runs`: execution history with status, count, duration and sanitized error class.
- Lease acquisition uses atomic PostgreSQL upsert with a conditional takeover only after expiry or for the same worker.
- The hold-expiry batch uses ordered row locks and `SKIP LOCKED`; concurrent workers cannot claim the same booking row.
- Each cycle is bounded by batch size and commits the booking batch independently.
- Crashed workers stop heartbeating; another worker may take over after lease expiry.
- Failures are recorded and retried after the configured interval. No raw exception message, passenger data, or secrets are stored in telemetry.

Defaults: 30-second poll interval, 90-second lease, 100 bookings per batch. The lease must be at least twice the polling interval.

## Monitoring and alert semantics

`GET /api/v1/admin/operations/scheduler` requires `platform.scheduler.read`. `POST /api/v1/admin/operations/scheduler/run-once` requires `platform.scheduler.manage`, CSRF, and the explicit development/test opt-in flag. It exposes:
- health: `not_configured`, `healthy`, `degraded`, or `stale`;
- number of due-but-not-expired seat holds and age of the oldest overdue hold;
- heartbeat age and lease expiry;
- last success/failure and sanitized error class;
- consecutive failures, total batches/records and last duration;
- recent execution history.

Suggested alert thresholds for a future external monitor:
- stale heartbeat for more than 2 lease periods;
- two or more consecutive failed cycles;
- no successful cycle within 3 polling intervals while worker is expected to run;
- repeated non-zero expiry backlog after multiple cycles.

No paid monitoring service is required. The database-backed status endpoint and structured process logs can be polled by existing free infrastructure. This PR does not configure a hosted monitoring provider or alert delivery.

## Staff identity, roles and dashboards

Staff authentication remains separate from passenger identity and uses the existing HttpOnly session cookie, CSRF protection, rate-limited login and revocable sessions. Staff access is additive RBAC: permissions are derived from active role assignments and checked server-side for every protected API request.

Seeded roles:
- Synthetic platform administrator (manual local provisioning only)
- Platform access manager (staff role and invitation administration)
- Platform operations manager
- Platform support agent
- Platform safety moderator
- Platform auditor (read-only audit and scheduler visibility)
- Platform scheduler operator
- Platform catalog manager
- Platform dispatch manager
- Platform fleet reviewer
- Platform fare manager
- Organization-scoped operator manager, dispatcher, fleet manager and fare manager

Platform roles require a null organization scope. Operator roles require an active organization membership and explicit organization ID. Platform roles cannot be assigned by operator invitation. Role assignment and revocation require platform access-management permission, CSRF, an audit event, and a second administrator (self-assignment/revocation is rejected).

### Role and dashboard matrix

| Role | Scope | Dashboard / permissions |
|---|---|---|
| `synthetic_platform_admin` | Platform | Full platform permission set; manual synthetic bootstrap only |
| `platform_access_manager` | Platform | Staff accounts, role catalogue, role assignments, invitations, audit read |
| `platform_operations_manager` | Platform | Operator review, catalog, trip, fleet, fare, support and scheduler read |
| `platform_support_agent` | Platform | Passenger/operator support and complaint queues |
| `platform_safety_moderator` | Platform | Support/safety moderation and audit read |
| `platform_auditor` | Platform | Read-only audit and scheduler monitoring |
| `platform_scheduler_operator` | Platform | Scheduler monitoring and guarded one-cycle action |
| `platform_catalog_manager` | Platform | Locations, terminals and routes |
| `platform_dispatch_manager` | Platform | Trip approval and publication |
| `platform_fleet_reviewer` | Platform | Vehicle and seat-layout review |
| `platform_fare_manager` | Platform | Fare approval and publication |
| `operator_manager` | Operator organization | Organization-scoped fleet, trips, fare proposals and manifests |
| `operator_dispatcher` | Operator organization | Organization-scoped trip and manifest operations |
| `operator_fleet_manager` | Operator organization | Organization-scoped fleet |
| `operator_fare_manager` | Operator organization | Organization-scoped fare proposals |

The staff dashboard returns only modules and aggregate statistics allowed by the current permission set. Platform metrics are not returned to organization-scoped staff; operator metrics are filtered to the assigned organizations. The access-management endpoints expose the role catalogue, staff accounts, approved operator organizations, pending invitations and active assignments to authorized access administrators. The staff console supports role assignment/revocation, invitation creation/revocation, scheduler monitoring, audit review, and permission-driven dashboards. Invitation tokens are displayed only to the authorized operator admin for controlled synthetic testing; no delivery provider is called.

## Operational rollout gates (not authorized by this change)

Before any production operation, separately approve:
1. Production infrastructure and managed PostgreSQL topology, backup/restore and disaster recovery.
2. Worker process supervisor, restart policy, resource limits, and deployment health checks.
3. Independent security review of RBAC, staff invitation, lease ownership, and scheduler failure modes.
4. Monitoring/alert receiver and incident response ownership.
5. Retention policy for scheduler runs and audit data.
6. Separate production approval and change record.

Until those gates are complete, keep `SCHEDULER_ENABLED=false`, `APP_ENV` in development/test, and synthetic-only mode true.
