# Architecture overview

Initial system is a modular monolith: FastAPI backend, React PWA client, PostgreSQL target. Explicit domain boundaries precede business workflows. No microservices without evidence.

Initial domains: identity/access, organization, passenger/driver, fleet/maintenance, booking/dispatch, payments, notifications. Business domains are not yet implemented.

Development is synthetic-only. No real personal data, live dispatch, payment processing, production hosting, cross-border personal-data transfer, or launch is authorized.
