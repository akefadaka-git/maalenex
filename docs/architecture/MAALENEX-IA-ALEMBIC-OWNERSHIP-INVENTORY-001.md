# Alembic ownership and ORM coverage inventory

**Record:** MAALENEX-IA-ALEMBIC-OWNERSHIP-001  
**Version:** 1.0.0  
**Status:** VERIFIED-CLOSED — fresh PostgreSQL CI parity and regression acceptance  
**Scope:** Reflected database objects and application model registration on the A3 integration branch.

## 1. Purpose and rules

Run #787 reported 52 reflected tables absent from Base.metadata, plus column differences in four application tables. This record separates extension-owned relations from application-owned schema and documents migration/model coverage.

1. Exclude an extension relation only when PostgreSQL records it as a member of an installed extension (pg_depend.deptype = 'e').
2. Do not use a broad name allowlist to classify extension objects.
3. Keep application tables in public represented in SQLAlchemy metadata.
4. Treat canonical schema geo as SQL-first and migration-managed. Its tables, views, grants, RLS, triggers and publication contracts are checked by dedicated A3.2–A3.8 integration tests rather than ORM metadata.
5. Keep the three legacy MITP source tables as a separate migration-owned carry-forward exception. They are preserved as source evidence and consumed by migration 0021; they are not extension objects.

## 2. Extension-owned reflected relations

Run #787's metadata error listed 36 missing reflected support relations. The fresh PostgreSQL run #822 confirmed those 36 relations are extension-owned, plus the existing `public.spatial_ref_sys` core PostGIS relation: 37 extension-owned relations in total. Exact membership is determined at runtime from PostgreSQL's extension dependency catalogue, not by trusting this static list.

### TIGER geocoder support relations (34)

addr, addrfeat, bg, county, county_lookup, countysub_lookup, cousub, direction_lookup, edges, faces, featnames, geocode_settings, geocode_settings_default, loader_lookuptables, loader_platform, loader_variables, pagc_gaz, pagc_lex, pagc_rules, place, place_lookup, secondary_unit_lookup, state, state_lookup, street_type_lookup, tabblock, tabblock20, tract, zcta5, zip_lookup, zip_lookup_all, zip_lookup_base, zip_state, zip_state_loc.

### PostGIS topology support relations (2)

- topology
- layer

### Existing core PostGIS exception

- public.spatial_ref_sys is confirmed as a PostGIS-owned core reference relation by the runtime extension dependency query.

**Verification method:** workflow run #822 printed extension name / schema / relation from `pg_extension`, `pg_depend`, `pg_class`, and `pg_namespace` before running `alembic check`. Exact output: `postgis|public|spatial_ref_sys`; 34 `postgis_tiger_geocoder|tiger|...` relations; and `postgis_topology|topology|layer` plus `postgis_topology|topology|topology`. The Alembic environment uses the same dependency relationship and `pg_table_is_visible` to match extension-owned relations reflected without schema names through `search_path`, including their indexes.

The catalog query runs before Alembic configuration. Because SQLAlchemy 2.x autobegins a transaction for the catalog read, the environment explicitly commits that read-only transaction before Alembic opens its migration transaction. This prevents migration DDL from being rolled back when the connection closes.

## 3. Application-owned tables restored to ORM metadata

All 16 missing application tables are mapped from their creating migrations. No table is dropped, renamed, or waived.

| Migration | Application tables | Model module |
|---|---|---|
| 0008 wallet ledger | ledger_accounts, ledger_transactions, ledger_postings | app.domains.ledger.models |
| 0009 passenger identity | passenger_accounts, passenger_credentials, passenger_sessions, passenger_login_attempts | app.domains.passengers.models |
| 0010 passenger support | passenger_support_cases | app.domains.passengers.models |
| 0011 passenger reports | passenger_reports, passenger_report_attachments | app.domains.passengers.models |
| 0013 notifications | passenger_notifications, passenger_notification_preferences | app.domains.passengers.models |
| 0015 scheduler | scheduler_leases, scheduler_runs | app.domains.scheduler.models |
| 0016 fleet compliance | vehicle_compliance_documents, trip_operational_exceptions | app.domains.fleet.models |

The ORM metadata also restores two migration-created indexes that were reported as drift: `ix_bookings_status_expires_at` on `(bookings.status, bookings.expires_at)` and the partial unique `uq_passenger_wallet_owner_currency` index on passenger wallet ownership/currency.

The modules are imported by app.db.model_registry before Alembic reads Base.metadata.

## 4. Application column parity repaired

| Migration | Table | Model fields restored |
|---|---|---|
| 0014 verified booking ownership | bookings | nullable passenger_account_id, FK to passenger_accounts.id with ON DELETE SET NULL, and index |
| 0016 fleet compliance | seat_layout_versions | non-null geometry_metadata JSON with the migration's empty-object server default |
| 0017 map geometry | locations | nullable latitude, longitude, coordinate_source |
| 0017 map geometry | routes | nullable geometry JSON and geometry_source |

These are real application columns and are intentionally not excluded from comparison.

## 5. Explicit migration-managed exceptions

### Canonical geo schema

The geo schema is application-owned and intentionally SQL-first. Migration 0020 creates canonical geography and tracking tables; migrations 0021–0024 add backfill, views/privileges, tenant RLS/permissions, provenance and licensing. The schema is excluded from ORM autogeneration, not classified as an extension. Its contract remains covered by the geo schema, public-view, RLS, leakage, provenance and rollback integration suites.

### Legacy MITP source tables

public.tracking_devices, public.vehicle_device_assignments, and public.vehicle_telemetry are legacy application-owned tables. Migration 0021 reads them into canonical geo structures while preserving original source records. They remain a separately documented migration-managed exception, not an extension exclusion.

## 6. Acceptance criteria

- [x] Identify all 52 relations reported by Run #787.
- [x] Separate 36 extension-owned candidates from 16 application-owned tables.
- [x] Trace all 16 application tables to their creating migrations.
- [x] Map the 16 tables and restore the four-table column parity differences in ORM metadata.
- [x] Replace static extension table-name exclusion with PostgreSQL extension-membership discovery.
- [x] Confirm exact extension ownership in fresh PostgreSQL CI: 37 extension-owned relations (1 PostGIS core, 34 TIGER geocoder, 2 topology).
- [x] Confirm `alembic check` passes against the fully registered application metadata.
- [x] Confirm backend suite: 38 passed, 31 skipped; Ruff passed.
- [x] Confirm A3.2–A3.8 gates: A3.2 (1), A3.3 (3), A3.4 (6), A3.5 (6), A3.6 authorization/API tests plus Martin integration, A3.7 (2), A3.8 (3) passed.
- [x] Confirm Martin catalog/TileJSON, actual approved-feature MVT payload, and denial of internal tracking-table access.
- [x] Confirm A3.3 downgrade preserves legacy MITP source records and full migration downgrade/re-upgrade succeeds.

**Verification evidence:** [GitHub Actions G1 backend foundation verification #822](https://github.com/akefadaka-git/maalenex/actions/runs/45720048934), commit `9750d2cba123a7c2567ef5c9bce3511f9ce0382e`, branch `feat/a3-canonical-postgis-integration`. Both backend/PostGIS and frontend jobs completed successfully.

**Disposition:** extension ownership, Alembic metadata parity, and the requested backend, migration rollback and A3.2–A3.8 CI gates are VERIFIED-CLOSED on the integration branch. This is not a merge, deployment, production database authorization, or runtime role provisioning approval.