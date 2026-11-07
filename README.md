# MaaleNex Moto

Amharic-first passenger mobility platform for Ethiopia, beginning with passenger trip discovery in Jinka. Freight logistics remains a separately phased future domain. The initial passenger product is online-first; offline boarding is not included.

## Development status

A3 Passenger MVP implementation is in progress on `feat/a3-passenger-mvp`, based on the G1 foundation branch. The public repository remains synthetic-data-only. Never commit secrets, personal data, real operator/passenger records, identity documents, addresses, payment credentials, or production data. The application deliberately rejects non-development runtime environments.

## Technology

- Backend: Python 3.11+, FastAPI, Pydantic Settings, SQLAlchemy 2, Alembic
- Database: PostgreSQL with psycopg 3
- Frontend: React 18, TypeScript, Vite, Vitest, Testing Library
- API: versioned under `/api/v1`; interactive development docs at `/api/v1/docs`
- Domain boundary: modular monolith with Identity, Audit, Organization, Catalog, Fleet, Trips, Fares, Bookings and Reservation Access domains

## Local development

### Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer and npm
- PostgreSQL 15 or newer, running locally
- Git

### Backend

From the repository root:

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Copy the root `.env.example` to `backend/.env` and adjust only local development values. The committed example contains no database username or password. Configure local PostgreSQL authentication on your machine, or supply a local-only `DATABASE_URL` through the environment; never commit authentication material. Create a local database named `maalenex_dev`, then start the API:

```bash
uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000`; health check: `GET /api/v1/health`; OpenAPI UI: `/api/v1/docs`.

Run backend checks from `backend/`:

```bash
pytest
ruff check app tests migrations
alembic upgrade head
```

Alembic is wired to application metadata and the configured PostgreSQL URL. The A3 branch contains explicit migrations for identity/audit/operator foundations and the synthetic passenger catalog, fleet, trip, fare, booking and reservation schema. Apply migrations only to the local synthetic `maalenex_dev` database. Review migration parity and run PostgreSQL integration tests before treating the schema as verified.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Run the complete local validation sequence from the repository root in Windows PowerShell after installing backend and frontend dependencies:

```powershell
.\\scripts\\validate-g1.ps1
```

The runner executes backend pytest/Ruff, the Alembic baseline migration, frontend Vitest, TypeScript typecheck, and Vite production build, recording each exit code. If the local PostgreSQL `maalenex_dev` database is not running, use `-SkipDatabaseMigration`; that check will be explicitly reported as NOT RUN. The backend guard rejects remote database hosts and any database name other than `maalenex_dev`.

Run local frontend checks individually if preferred:

```bash
npm test
npm run typecheck
npm run build
```

Vite serves the app at `http://localhost:5173`. The Amharic passenger trip-search interface is the default; use the language control to switch to English. Published trip search is read-only. Booking-access verification, reservation creation, payment collection, travel-ticket issuance and boarding APIs are not enabled yet.

## Data and operational boundary

- Synthetic fixtures only; no real people, identifiers, addresses, trips, transactions, or payment credentials.
- No live operator onboarding, real passenger bookings, payment collection, ticket issuance, boarding, production personal-data processing, production deployment, or public service launch is authorized.
- Reservation references are not travel tickets and cannot authorize boarding.
- The passenger search API returns only published trip information and availability snapshots; booking rechecks inventory transactionally.
- Do not add credentials to source control. Use local environment variables and keep `.env` untracked.
- No paid CI or external service is required for the documented local checks.
- No software license has been selected. Public visibility does not itself grant permission to use, modify, or redistribute this code.

## Governance

Use feature branches and pull requests. Do not merge, deploy, publish releases, change repository security settings, or broaden G1 into G2/G3 without explicit Owner authorization. See `CONTRIBUTING.md`, `SECURITY.md`, and `docs/`.
