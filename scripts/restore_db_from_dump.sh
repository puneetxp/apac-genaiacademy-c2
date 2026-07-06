#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/restore_db_from_dump.sh /path/to/dump.sql
# This script drops all tables in the target database (by recreating the public schema)
# and restores it from the provided SQL dump. Connection details are read from python/.env.

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /absolute/path/to/dump.sql" >&2
  exit 1
fi

DUMP_FILE="$1"
if [[ ! -f "$DUMP_FILE" ]]; then
  echo "❌ Dump file not found: $DUMP_FILE" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/python/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ Missing python/.env with database credentials" >&2
  exit 1
fi

# shellcheck disable=SC2046
export $(grep -v '^#' "$ENV_FILE" | xargs)

DB_HOST="${POSTGRES_SERVER:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-cropsense_dev}"

if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
  echo "❌ POSTGRES_PASSWORD is not set in python/.env" >&2
  exit 1
fi

PSQL_BASE=(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME")

export PGPASSWORD="$POSTGRES_PASSWORD"

echo "🧹 Dropping existing schema..."
"${PSQL_BASE[@]}" -c "DROP SCHEMA IF EXISTS public CASCADE;"
"${PSQL_BASE[@]}" -c "CREATE SCHEMA public;"
"${PSQL_BASE[@]}" -c "GRANT ALL ON SCHEMA public TO public;"
"${PSQL_BASE[@]}" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

echo "📦 Restoring dump from $DUMP_FILE ..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$DUMP_FILE"

echo "✅ Database restored successfully."
