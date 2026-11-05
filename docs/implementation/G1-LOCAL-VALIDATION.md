# G1 local validation checklist

Run checks locally; no paid CI is required or configured by this document.

## Backend

From `backend/` with the virtual environment active:

- `pytest`
- `ruff check app tests migrations`
- `alembic upgrade head` (requires a local PostgreSQL database)

## Frontend

From `frontend/` after `npm install`:

- `npm test`
- `npm run typecheck`
- `npm run build`

Record the command, runtime version, exit status, and relevant output. A skipped check is `NOT RUN`, not PASS. Database migration execution must use a disposable local development database. Never point local checks at production or real personal data.

## Current limitation

The G1 migration framework is configured against SQLAlchemy metadata, but the metadata intentionally contains no business tables until G2 domain approval. Therefore the migration setup can be inspected and invoked, but this change does not claim a completed business schema or a verified database migration.
