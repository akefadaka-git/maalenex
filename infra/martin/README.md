# MaaleNex Martin — public geography tiles

Martin serves vector tiles directly from the canonical MaaleNex PostgreSQL/PostGIS database. It does not create a second map database and does not import or duplicate spatial records.

## Security contract

- Martin is configured with `auto_publish: false` and exactly six named sources from `geo_public`.
- Each source is an A3.4 sanitized view; no `geo`, `geo_internal`, `geo_audit`, tracking or tenant tables are configured.
- The table properties are explicitly allowlisted. `on_invalid: abort` prevents startup with missing or incompatible views.
- Martin must connect as a dedicated login principal that is a member of `maalenex_geo_public_reader`, never as the application login, migration role, table owner or database owner.
- The service is published on loopback only by the included development Compose file. Production exposure requires a separately approved reverse-proxy/TLS, rate-limit, monitoring and capacity design.
- No internal vehicle-position tiles are exposed. Internal tracking remains an authenticated API concern and must use the A3.5 tenant authorization/context helper.

## Provision a dedicated reader login

After the A3.4/A3.5 migrations have been applied to a disposable or approved target database, provision a separate credential out-of-band. Run as a database administrator and replace the password through a secret manager or secure prompt; never commit it:

```sql
CREATE ROLE maalenex_martin_login LOGIN INHERIT;
GRANT CONNECT ON DATABASE maalenex TO maalenex_martin_login;
GRANT maalenex_geo_public_reader TO maalenex_martin_login;
```

The capability role remains NOLOGIN and receives only USAGE on `geo_public` plus SELECT on its six sanitized views. Do not grant this login membership in any other capability role. Store its connection string in the runtime secret `MAALENEX_GEO_PUBLIC_DATABASE_URL`. Use TLS and `sslmode=verify-full` when connecting across hosts.

The database name above is the canonical application database. Confirm the actual database name and host before provisioning; no credentials or live DB operations are performed by this repository change.

## Local development

1. Ensure the canonical PostGIS database has migrations through `0023_geo_tenant_rls_permissions` applied.
2. Provision the dedicated reader login as above.
3. Set `MAALENEX_GEO_PUBLIC_DATABASE_URL` in your local shell or untracked `.env` file. The host must be reachable from the container; for a host-local database on Linux the Compose file provides `host.docker.internal`.
4. Start Martin from the repository root:

   `docker compose -f infra/martin/docker-compose.yml up -d`

5. Confirm `http://127.0.0.1:3000/martin/catalog` lists only the configured public sources.
6. Start the frontend with `cd frontend && npm install && npm run dev`, then open `http://localhost:5173/map`.

The Vite development proxy forwards `/martin` to loopback Martin. The browser requests only public vector tiles. If no verified, publication-eligible geography has been approved and published, the map will be an empty base canvas; it must not be populated from unverified or synthetic operational records.

## Operational boundary

This is a local development service definition, not a Plesk deployment recipe. It does not start or migrate PostgreSQL, seed data, import OSM, create production credentials, or expose the Martin port publicly. The old `infra/mitp-maps` separate-database proof of concept is intentionally not reused.