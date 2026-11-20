# MaaleNex

Amharic-first mobility and digital-services platform being developed for Ethiopia, with an initial regional focus on Koybe, Jinka, and South Omo.

## Product experience

The current feature branch introduces the full application shell:
- Smart header, dashboard, reusable widgets, and responsive navigation.
- Map discovery interface with verified-data-only route presentation.
- Wallet, profile, login, and registration screens.
- Help center, issue reporting, and About MaaleNex.
- Dedicated MaaleNex emblem, local SVG icon family, PWA assets, Android launcher resources, and branded splash experience.
- Amharic-first interface with English support.

## Current implementation state

This is an active development build, not a live commercial service.
- Authentication and registration screens are UI foundations; the passenger identity API and verification delivery are not yet connected.
- The map view is a local preview; a production map provider, permission flow, and verified operating route data are not yet connected.
- The wallet ledger foundation uses double-entry postings, idempotency, and audit events. It is not yet a customer wallet or payment-provider integration.
- The wallet UI does not initiate deposits, withdrawals, transfers, or any real-money operation.
- Help and report screens currently demonstrate local interaction; persistent support workflows are not yet connected.
- No route, schedule, fare, operator, account balance, or transaction is represented as live unless backed by approved operational data.

## Technology

- Backend: Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Frontend: React 18, TypeScript, Vite, Vitest
- Android: native Android WebView shell with local asset loading and a restricted navigation policy

## Local development

Frontend:
```bash
cd frontend
npm ci
npm test
npm run typecheck
npm run build
npm run dev
```

Backend:
```bash
cd backend
python -m pip install -e ".[dev]"
python -m pytest -q
python -m alembic upgrade head
```

Android build instructions: `android/README.md`.

## Financial and security controls

The ledger is an internal accounting foundation. Real-money operations require applicable Ethiopian regulatory assessment, an authorized bank/payment partner, KYC/AML controls, verified provider callbacks, reconciliation, fraud safeguards, privacy controls, and independent security review. Provider credentials remain server-side. No production financial activation is implied by UI or ledger implementation.

## Governance

Use feature branches and pull requests. A1 requirements and A2 reconciliation remain separately governed. A3 implementation, A4 verification, and A5 deployment are separate gates. Do not merge, deploy, publish releases, or activate production without explicit Owner authorization. Development and tests use synthetic data only.
