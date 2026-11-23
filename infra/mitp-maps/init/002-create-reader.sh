#!/bin/sh
set -eu

: "${MITP_MAP_READER_PASSWORD:?MITP_MAP_READER_PASSWORD is required}"

psql -v ON_ERROR_STOP=1 -v reader_password="$MITP_MAP_READER_PASSWORD" \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
CREATE ROLE mitp_reader LOGIN PASSWORD :'reader_password';
GRANT CONNECT ON DATABASE mitp_maps TO mitp_reader;
GRANT USAGE ON SCHEMA public TO mitp_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mitp_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE mitp_maps IN SCHEMA public
  GRANT SELECT ON TABLES TO mitp_reader;
SQL
