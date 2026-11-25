# Alembic ownership and ORM coverage inventory

**Record:** MAALENEX-IA-ALEMBIC-OWNERSHIP-001  
**Version:** 1.0.0  
**Status:** Implemented inventory; CI confirmation pending  
**Scope:** Reflected database objects and application model registration on the A3 integration branch.

## 1. Purpose and rules

Run #787 reported 52 reflected tables absent from Base.metadata, plus column differences in four application tables. This record separates extension-owned relations from application-owned schema and documents migration/model coverage.

1. Exclude an extension relation only when PostgreSQL records it as a member of an installed extension (pg_depend.deptype = 'e').
2. Do not use a broad name allowlist to classify extension objects.
3. Keep application tables in public represented in SQLAlchemy metadata.
4. Treat canonical schema geo as SQL-first and migration-managed. Its tables, views, grants, RLS, triggers and publication contracts are checked by dedicated A3.2–A3.8 integration tests rather than ORM metadata.
5. Keep the three legacy MITP source tables as a separate migration-owned carry-forward exception. They are preserved as source evidence and consumed by migration 0021; they are not extension objects.

## 2. Extension-owned reflected relations

Run #787's metadata error listed the following 36 missing reflected relations. Their names identify the PostGIS TIGER geocoder support catalogue and PostGIS topology support. Exact membership is determined at runtime from PostgreSQL's extension dependency catalogue, not by trusting this static list.

### TIGER geocoder support relations (34)

addr, addrfeat, bg, county, county_lookup, countysub_lookup, cousub, direction_lookup, edges, faces, featnames, geocode_settings, geocode_settings_default, loader_lookuptables, loader_platform, loader_variables, pagc_gaz, pagc_lex, pagc_rules, place, place_lookup, secondary_unit_lookup, state, state_lookup, street_type_lookup, tabblock, tabblock20, tract, zcta5, zip_lookup, zip_lookup_all, zip_lookup_base, zip_state, zip_state_loc.

### PostGIS topology support relations (2)

- topology
- layer

### Existing core PostGIS exception

- public.spatial_ref_sys is already explicitly excluded as the PostGIS core reference table. Runtime catalogue discovery also recognizes it when the installed extension records ownership.

**Verification method:** the workflow prints extension_name / schema_name / relation_name from pg_extension, pg_depend, pg_class, and pg_namespace before running alembic check. The Alembic environment uses the same extension-membership relationship to exclude only those relations.

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
- [ ] Confirm exact extension ownership and Alembic parity in a fresh GitHub Actions PostgreSQL run.
- [ ] Confirm backend tests, lint, migration upgrade/downgrade, and A3.2–A3.8 integration gates remain green.

**Disposition:** inventory and source/model repairs implemented on the A3 branch; CI verification pending. This is not a merge, deployment, or production database authorization.