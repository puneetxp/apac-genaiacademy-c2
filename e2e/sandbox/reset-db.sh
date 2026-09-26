#!/usr/bin/env bash
# Rebuild the throwaway E2E database from the schema files and seed test users/data.
# Only ever touches a database whose name ends in _e2e (default: cropsense_e2e).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DB="${E2E_DB:-cropsense_e2e}"
# Connects as $PGUSER / the current OS user, like psql itself.

case "$DB" in
  *_e2e) ;;
  *) echo "Refusing to reset '$DB': the E2E database name must end in _e2e" >&2; exit 1 ;;
esac

echo "Resetting $DB ..."
dropdb --if-exists --force "$DB"
createdb "$DB"

psql_e2e() { psql -d "$DB" -v ON_ERROR_STOP=1 -q "$@"; }

psql_e2e -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql_e2e -f "$ROOT/database/structure.sql"
psql_e2e -f "$ROOT/database/relation.sql"
for extra in "$ROOT"/e2e/sandbox/schema-extra/*.sql; do
  [ -e "$extra" ] && psql_e2e -f "$extra"
done
psql_e2e -f "$ROOT/e2e/sandbox/seed.sql"

echo "$DB ready: $(psql -d "$DB" -Atc "select count(*) from information_schema.tables where table_schema='public'") tables, $(psql -d "$DB" -Atc "select count(*) from users") users"
