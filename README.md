# MaaleNex Moto

Amharic-first motorcycle mobility and service platform for Ethiopia, designed for offline-capable workflows and controlled, secure dispatch.

## Status
Greenfield development. This public repository is synthetic-data-only. Never commit secrets, personal data, real driver/passenger records, identity documents, addresses, payment credentials, or production data.

## Stack
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic
- Frontend: React, TypeScript, Vite
- Database: PostgreSQL
- Offline foundation: IndexedDB queue planned in G1/G4

## Local development
See `backend/` and `frontend/` for application setup. Copy `.env.example` to `.env` and use local development credentials only.

## Governance and safety
Use feature branches and pull requests. No license has been selected; public visibility does not grant an open-source license. Live dispatch, real payments, production personal-data processing, production deployment, and public service launch are not authorized. See `SECURITY.md`, `CONTRIBUTING.md`, and `docs/`.