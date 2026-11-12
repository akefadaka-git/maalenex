# MaaleNex

Amharic-first mobility and services platform for Ethiopia. The initial delivery scope is passenger mobility, beginning with a controlled Jinka pilot. Freight and other service domains remain separately phased and are not part of the initial passenger release.

## Project status

Engineering is in progress. The passenger MVP, shared platform, Android client, verification work, and deployment specifications are maintained on separate feature branches and pull requests. The default `main` branch is not yet the complete passenger MVP and must not be represented as production-ready.

This public repository is synthetic-data-only. Never commit secrets, personal data, real passenger/operator records, identity documents, addresses, payment credentials, or production data. Production personal-data processing, live dispatch, payment collection, ticket issuance, boarding, production deployment, and public service launch require separate verification and Owner approval.

## Technology

- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic
- Database: PostgreSQL
- Frontend: React, TypeScript, Vite
- Mobile: Android application shell and Capacitor integration on feature branches
- API: versioned under `/api/v1`

## Development

See `backend/`, `frontend/`, `docs/`, and `scripts/` for implementation and local validation instructions. Use synthetic development/test data only. Never place credentials in tracked files.

## Governance and safety

Use feature branches and pull requests. Integrate changes in dependency order and require exact-head verification before merge. Do not merge, deploy, publish releases, or activate live services without the applicable explicit Owner approval.

No software license has been selected. Public repository visibility does not grant an open-source license. See `SECURITY.md` and `CONTRIBUTING.md`.
