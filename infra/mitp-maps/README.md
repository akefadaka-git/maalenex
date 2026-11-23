# MITP self-hosted road-map proof of concept

This development-only stack serves OpenStreetMap-derived vector tiles from a local PostGIS database through Martin. It uses no Google Maps SDK, external tile API, API key, satellite imagery or paid map provider.

## Prerequisites

- Docker Engine and Docker Compose.
- A local OpenStreetMap .osm.pbf extract that you are permitted to use.
- osm2pgsql installed locally.
- A local-only database password; do not commit it.

## Start the local services

Set two local-only alphanumeric passwords in the current shell, then start the services:

    export MITP_MAP_DB_PASSWORD='local-owner-password-change-me'
    export MITP_MAP_READER_PASSWORD='local-reader-password-change-me'
    docker compose -f infra/mitp-maps/docker-compose.yml up -d

The PostGIS database is bound to loopback port 55432 and Martin is bound to loopback port 3000. These ports are not published on a public interface. The OSM import owner uses the database-owner account; Martin connects with a separate read-only role. Use alphanumeric-only passwords for the sample connection string, and replace the example values.

## Import road data

Use a dated, geographically appropriate OpenStreetMap PBF extract. Keep the source file outside Git and record its download date, source URL, geographic coverage and checksum in local operational notes. OSM data is subject to the Open Database License (ODbL); preserve attribution and assess any database/public-distribution obligations before external use.

Example import from the repository root (Linux/macOS shell):

    PGPASSWORD="$MITP_MAP_DB_PASSWORD" osm2pgsql \
      --create --slim --hstore \
      --host 127.0.0.1 --port 55432 \
      --username mitp_maps --database mitp_maps \
      /absolute/path/to/your-extract.osm.pbf

After import, Martin discovers the planet_osm_line and planet_osm_polygon tables. Check its local catalog at http://127.0.0.1:3000/catalog and verify the tilejson endpoints before starting the frontend.

## Frontend

Install the frontend dependencies, start Vite and open:

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173/tracking-demo. The Vite development proxy forwards /mitp-tiles to the loopback Martin service. The map style uses only the locally served vector tiles.

To overlay a vehicle, sign in with a synthetic staff account that has platform.tracking.read, then open /tracking-demo?vehicleId=YOUR-VEHICLE-UUID. A marker appears only after an installed-device record has an active vehicle assignment and the telemetry gateway has accepted a position. A position older than 90 seconds is explicitly labelled stale.

## Data and deployment boundary

- The map database is separate from the application database.
- No OSM extract, generated tile database, secrets or credentials are committed.
- This proof of concept uses road features only; it does not provide satellite imagery.
- Public/commercial use requires separate ODbL, hosting, capacity, backup, security and legal review.
- This local compose file is not a production deployment configuration.
