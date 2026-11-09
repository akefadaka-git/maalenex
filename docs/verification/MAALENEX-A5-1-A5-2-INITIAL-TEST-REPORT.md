# MaaleNex — A5.1–A5.2 Initial Readiness Test Report

**Status:** PARTIAL — A5.1/A5.2 baseline inspection and automated verification completed; focused remediation/regression work remains  
**Stage:** A5.1 baseline/architecture reconciliation and A5.2 functional/business-logic assessment  
**Product name:** MaaleNex  
**Repository identity:** `akefadaka-git/maalenex-moto` (existing GitHub slug; not changed by this work)  
**Branch:** `a5/deployment-readiness-assessment`  
**A5 assessment baseline:** `6708c6191523f61cf75ac921829255ac8a9c4c0f`  
**A5 verification workflow commit:** `22db26fac66789a6fd742eda589739e91be1deb1`  
**A4 parent baseline:** `d54b0291a58499891baaac5d5106ea8eed85a96b`  
**Deployment/merge/activation:** NOT AUTHORIZED; none performed.

## 1. A5.1 — Baseline and architecture reconciliation

### Evidence checked
- Confirmed A5 branch points to the A4 verified HEAD, then contains the A5 assessment and A5 verification workflow commits.
- Inspected repository tree, application settings, API registration, README, SECURITY policy, backend package metadata, frontend package metadata, domain models/services, migrations and CI workflows.
- Confirmed the repository's default branch is `main`; the existing A3 PRs #9 and #10 remain open and unmerged.
- Confirmed the A5 branch is not protected in GitHub branch metadata. This is a governance/control gap to address before production branch operations, not a reason to alter branch protection during this assessment.

### Findings

| ID | Finding | Status | Consequence / next action |
|---|---|---|---|
| A51-01 | Runtime configuration permits only `development` and `test`; synthetic-only is mandatory; PostgreSQL must be local and database name must be `maalenex_dev`. | BLOCKED BY INTENTIONAL SAFETY GUARD | Preserve during A5. Production-mode design must be a separately approved change; do not bypass. |
| A51-02 | No production deployment topology, infrastructure-as-code, container deployment definition, production ingress, or provider configuration was evidenced in the inspected repository tree. | NOT EVIDENCED | Specify target infrastructure, ownership, network boundaries, data region, cost ceiling and rollback plan before production remediation. |
| A51-03 | TLS, backup/restore, disaster recovery, production monitoring and operational runbooks have no production evidence in the inspected repository. | NOT EVIDENCED | Carry into A5.3–A5.6 evidence collection and exercises. |
| A51-04 | Product naming is inconsistent in repository artifacts: README, FastAPI app metadata and package names still use the former “Moto” label, while the current product name is MaaleNex. | PARTIAL | Correct product-facing names in a controlled branding cleanup; preserve the existing repository slug unless separately directed. |
| A51-05 | GitHub reports the A5 branch as unprotected. | PARTIAL | Define required checks, review rules and restricted write/merge policy before any production-bound branch is used. |
| A51-06 | The architecture is a modular monolith with FastAPI, PostgreSQL/Alembic and React/TypeScript/Vite. The current scope includes identity, audit, organizations, platform registry, catalog, fleet, trips, fares, bookings and reservation access. | ESTABLISHED — NOT PRODUCTION-VALIDATED | Retain this architecture; do not split into microservices without measured need. |

## 2. A5.2 — Functional and business-logic assessment

### Implemented foundations observed
- Public catalog endpoints expose published locations/routes and published trip search.
- Trip search uses Ethiopia's UTC+03:00 calendar-day boundary, approved operator status, published routes/trips/terminals, effective ETB fare versions and seat availability.
- Booking hold creation validates passenger/seat cardinality, duplicate seats, hold duration, contact fields and idempotency key; it locks trip/seat rows and records fare snapshots.
- PostgreSQL partial unique indexes protect active seat holds and allocations.
- Reservation acceptance checks active, unexpired holds and allocations, converts holds and creates a reservation reference. The code explicitly records that ticket issuance and payment collection did not occur.
- Guest booking access uses verification challenges, hashed challenge/access credentials, expiry, revocation and rate-limit state.
- Service permission evaluation requires an active user, approved organization, active membership and matching service-scoped role.
- Fare workflow supports proposal, submission, separate reviewer decision and separate publisher identity.
- Existing tests include PostgreSQL seat concurrency/maintenance, service-scoped authorization, guest booking access, audit redaction, platform registry and identity lifecycle coverage.

### Findings

| ID | Finding | Status | Consequence / next action |
|---|---|---|---|
| A52-01 | Passenger booking is a hold → contact verification/access → reservation-reference flow; it is not a ticketing/boarding flow. | PARTIAL | Keep ticket issuance and boarding outside this baseline; implement and verify as a separately scoped passenger-service increment. |
| A52-02 | Payment collection, payment reconciliation, cancellation and refund workflows are not implemented as end-to-end capabilities. | MISSING | Do not enable Pay or represent a reservation reference as a ticket or proof of payment. |
| A52-03 | The audit metadata redactor recursively handles dictionaries but not list/array contents. A list containing objects with sensitive keys may be stringified without recursive key-level redaction. | CANDIDATE DEFECT — REGRESSION TEST REQUIRED | Add tests for nested lists, lists of dictionaries, mixed scalar/object arrays and deeply nested structures; remediate before any real personal-data processing. |
| A52-04 | Existing service-scoped authorization has targeted tests, but a repository-wide route-to-permission coverage review is still required to establish that every organization/service mutation uses the intended scope. | PARTIAL / NOT FULLY VERIFIED | Build a route authorization matrix and negative cross-tenant/cross-service tests. |
| A52-05 | Fare proposal/review/publication logic exists, including proposer/reviewer/publisher separation and ETB effective-dated versions. | PARTIAL | Extend tests for overlapping effective windows, concurrent fare creation/publication, stale versions and boundary timestamps. |
| A52-06 | Reservation and booking state transitions have targeted PostgreSQL tests, but complete lifecycle coverage (expiry, retries, repeated requests, cancellation, operator changes and trip cancellation) is not yet evidenced. | PARTIAL | Extend scenario and invariant tests before passenger production use. |
| A52-07 | Frontend is a passenger-facing React/Vite application with test, typecheck and build scripts. | PARTIAL | Automated checks will verify build correctness; usability, Amharic content quality, accessibility and low-bandwidth behavior require dedicated testing. |

## 3. Automated verification

A dedicated A5-only GitHub Actions workflow was added at:
`.github/workflows/a5-foundation-verification.yml`

It is scoped to pushes on this A5 branch and runs:
1. Backend compile, Ruff, PostgreSQL 16, full pytest suite, registry seed idempotency, Alembic parity and full downgrade/re-upgrade.
2. Frontend lockfile install, tests, TypeScript, production build and npm audit.
3. Python dependency audit and Bandit high-severity scan.

**First workflow run:** [#42559070282](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42559070282) — PASS on `22db26fac66789a6fd742eda589739e91be1deb1`.  
**Report-updated exact-HEAD workflow run:** [#42559193051 — A5.1-A5.2 Readiness Verification](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42559193051) — PASS on `f151f2f58020f2dfc23368b0548eed35f0541f17`.  
**Backend/PostgreSQL result:** PASS — compile, Ruff, migrations, service registry idempotency, full backend/PostgreSQL integration suite, Alembic parity and full downgrade/re-upgrade all succeeded.  
**Frontend result:** PASS — clean `npm ci`, frontend tests, TypeScript, Vite build and npm audit all succeeded.  
**Dependency/static security result:** PASS — pip-audit and Bandit high-severity scan succeeded.  
All three jobs passed on the report-updated exact HEAD. This is automated verification of application code in an isolated synthetic test environment and does not establish production readiness.

The workflow does not send email, use SMTP secrets, contact external providers, process real personal data, perform payment actions, or deploy.

## 4. A5.1–A5.2 disposition

- A5.1 architecture/baseline reconciliation: **PARTIAL** — repository and runtime constraints inspected; production topology and operational evidence absent; naming consistency and branch controls need remediation.
- A5.2 functional/business-logic assessment: **PARTIAL** — foundational workflows are present; important passenger lifecycle capabilities remain missing; audit-redaction regression and route authorization coverage need focused tests.
- A5.1–A5.2 automated verification: **PASS** on exact HEAD `f151f2f58020f2dfc23368b0548eed35f0541f17` (run #42559193051).
- Production readiness: **NOT READY**.
- Merge, deployment, production secrets, production data processing, live payments, live GPS, real operator onboarding and commercial operation: **NOT AUTHORIZED**.

## 5. Next actions after exact-HEAD CI

1. Record all A5 workflow results against the exact tested commit.
2. Add a focused audit-redaction regression test and remediate the confirmed behavior on the A5 branch only.
3. Build a route-to-permission matrix and add negative organization/service isolation tests.
4. Expand fare and reservation lifecycle boundary/concurrency tests.
5. Re-run exact-HEAD verification after every remediation.
6. Keep A5.3–A5.7 separate for infrastructure, secrets, TLS, recovery, monitoring, privacy, operations and regulatory evidence.

No original PR or default-branch ref is modified by this report.
