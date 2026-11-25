# MaaleNex

Amharic-first passenger mobility platform in controlled preparation, beginning with a Jinka-first pilot direction. The public application is a guest-only development preview; it does not represent live or bookable transport services.

## Product boundary

- **Current public product:** passenger mobility discovery and product-preparation preview only.
- **Guest access:** public preview is available without an account.
- **No credential collection:** the public prototype has no sign-in or registration flow and does not collect names, phone numbers, email addresses, passwords, identity documents, or payment details.
- **No operational claims:** no route, schedule, fare, vehicle, operator, seat inventory, or boarding point is presented as verified or bookable unless separately evidenced and approved.
- **Future scope:** motorcycle-driver, heavy-load/cargo, and fleet/operator capabilities remain documented for future, separately governed phases. They are not public registration roles or workspaces.
- **Administration:** no public admin navigation or privileged UI. Administrative capability remains unavailable until server-side authentication, authorization, and tenant isolation are implemented and verified.
- **Synthetic-only development:** no real passenger/operator personal data, financial data, or production secrets in development/test.
- **No launch authorization:** no live onboarding, booking, payment, ticket issuance, boarding, production deployment, or commercial activation is authorized by this preview.

## Technology

- Backend: Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Frontend: React 18, TypeScript, Vite, Vitest
- Android: native Android WebView shell with a restrictive navigation policy; it does not provide privileged administrative or account capabilities.

## Local development

Backend setup and validation are documented under `backend/` and `scripts/`. Frontend commands:

```bash
cd frontend
npm install
npm test
npm run typecheck
npm run build
npm run dev
```

Android build instructions: `android/README.md`.

## Governance

Use feature branches and pull requests. A1 product requirements remain frozen. A2 reconciliation, A3 implementation, A4 verification, and A5 deployment are separate gates. Do not merge, deploy, publish releases, or activate production without explicit Owner authorization. See `docs/governance/`.
