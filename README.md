# MaaleNex Moto

Amharic-first motorcycle mobility and service platform for Ethiopia, designed for offline-capable workflows and controlled, secure dispatch.

## Development status

Greenfield G1 foundation. This public repository is synthetic-data-only. Never commit secrets, personal data, real driver/passenger records, identity documents, addresses, payment credentials, or production data. The application deliberately rejects non-development runtime environments in this baseline.

## Technology

- Backend: Python 3.11+, FastAPI, Pydantic Settings, SQLAlchemy 2, Alembic
- Database: PostgreSQL with psycopg 3
- Frontend: React 18, TypeScript, Vite, Vitest, Testing Library
- API: versioned under `/api/v1`; interactive development docs at `/api/v1/docs`
- Domain boundary: modular monolith; domain packages are reserved for separately approved domain work

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

Alembic is wired to application metadata and the configured PostgreSQL URL. No business tables or initial business migration are included: domain schemas and their migrations require the applicable G2 Owner approval. Do not generate migrations from unapproved domain assumptions.

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

Vite serves the app at `http://localhost:5173`. The Amharic interface is the default; use the language control to switch to English.

## Data and operational boundary

- Synthetic fixtures only; no real people, identifiers, addresses, trips, transactions, or payment credentials.
- No live dispatch, real payment processing, production personal-data processing, production deployment, or public service launch is authorized.
- Do not add credentials to source control. Use local environment variables and keep `.env` untracked.
- No paid CI or external service is required for the documented local checks.
- No software license has been selected. Public visibility does not itself grant permission to use, modify, or redistribute this code.

## Governance

Use feature branches and pull requests. Do not merge, deploy, publish releases, change repository security settings, or broaden G1 into G2/G3 without explicit Owner authorization. See `CONTRIBUTING.md`, `SECURITY.md`, and `docs/`.
