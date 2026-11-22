# MaaleNex Moto backend runtime

## Runtime model

The backend is a single FastAPI service shared by passenger, driver, agent and administrator clients. Deploy the same API image for all roles; enforce access through the existing server-side identity and RBAC policies. Do not create separate role databases or role-specific API deployments.

The container runs one Uvicorn process manager with a configurable worker count. Run the booking-hold scheduler as a separate worker process using the same image and database. Do not start the scheduler inside every web worker.

## Production configuration

Use `backend/.env.production.example` as the configuration checklist. Supply real values through the hosting provider's secret manager; never commit secrets.

Production startup validation requires:
- `APP_ENV=production`
- `SYNTHETIC_DATA_ONLY=false`
- `SECURE_COOKIES=true`
- Remote PostgreSQL using the psycopg driver, a non-development database name, credentials and `sslmode=require` or stronger
- Exact HTTPS CORS origins, including `https://appassets.androidplatform.net` for the packaged Android WebView and the actual passenger/admin web origins

Development and test remain local-PostgreSQL, synthetic-only environments. Production cannot silently fall back to local development settings.

## Build and release

Build the API image from the `backend/` directory:

```sh
docker build -t maalenex-moto-api:release .
```

Use a one-off release task with the same image and production environment to apply migrations:

```sh
alembic upgrade head
```

Only after the migration task succeeds should the hosting platform start or roll out the API service. Do not run migrations concurrently from every API replica.

Run the web service with the Dockerfile's default command. Configure the platform health/readiness probe to call:

```
GET /api/v1/ready
```

The liveness endpoint `GET /api/v1/health` does not require the database. Readiness executes `SELECT 1` against the configured database and returns HTTP 503 when it cannot connect.

The API container disables interactive OpenAPI/Swagger routes in production. Keep the API behind the hosting provider's HTTPS termination proxy. Set `FORWARDED_ALLOW_IPS` to the provider's documented proxy source IPs; do not blindly trust forwarded headers from arbitrary clients.

For the separate scheduler service, use the same image and command:

```sh
python -m app.jobs.scheduler_worker
```

Set `SCHEDULER_ENABLED=true` only on that worker service. Keep it false on the web service. The scheduler uses the existing PostgreSQL lease so only one worker owns a cycle at a time.

## Actual passenger app connection

Build the frontend and Android package with the actual API origin:

```sh
VITE_API_BASE_URL=https://api.YOUR-REAL-DOMAIN npm run build
```

The value must be the HTTPS origin only, without a path, credentials, query or fragment. The Vite build injects that exact origin into the restrictive WebView Content Security Policy. The Android passenger client then sends credentialed requests to `/api/v1` and uses secure cross-origin session cookies.

Do not use the example domain above as a live endpoint. The repository currently has no verified API hostname, DNS record, hosting service, production database credentials or deployed service. Therefore the container/runtime and client connection path can be prepared and verified in CI, but a live end-to-end connection requires an explicitly authorized A5 deployment, a real HTTPS API origin, database provisioning and provider-issued secrets.

## Operational gates still required

Before production traffic: provision and test database backups/restore, object storage and its CORS policy if fleet evidence uploads are enabled, monitoring/alerting, rate limits and trusted proxy configuration; complete end-to-end passenger tests against the deployed API; run independent security review; and separately authorize deployment. Real-money payment providers remain disabled until merchant onboarding, official integration credentials, callback verification and reconciliation are completed.
