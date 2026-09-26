#!/usr/bin/env bash
# Run CropSense locally: local Postgres + FastAPI on :8000 + Vite on :3000.
# Uses the real Firebase project for login (Google / phone / email) but keeps all data in the
# local database, so nothing touches production. Safe to re-run.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${GCP_PROJECT:-cropsense-ai-a4d5cf}"
DB="${LOCAL_DB:-cropsense_local}"

step() { printf '\n\033[1;34m▶ %s\033[0m\n' "$1"; }
die()  { printf '\033[1;31m✗ %s\033[0m\n' "$1" >&2; exit 1; }

command -v psql >/dev/null || die "psql not found — brew install postgresql"
pg_isready -q || die "Local Postgres is not running — brew services start postgresql"
[ -f "$ROOT/solidjs/.env.local" ] || die "solidjs/.env.local missing (holds the Firebase web config)"

# ── 1. Database ──────────────────────────────────────────────────────────────
step "1/4  Local database ($DB)"
if ! psql -d postgres -Atc "select 1 from pg_database where datname='$DB'" | grep -q 1; then
  createdb "$DB"
fi
if ! psql -d "$DB" -Atc "select to_regclass('public.users')" | grep -q users; then
  echo "Loading schema..."
  psql -d "$DB" -qc "CREATE EXTENSION IF NOT EXISTS vector" 2>/dev/null \
    || echo "  (pgvector not installed locally — vector columns will fail; brew install pgvector to fix)"
  for f in structure relation insert; do
    psql -d "$DB" -q -v ON_ERROR_STOP=0 -f "$ROOT/database/$f.sql" 2>&1 | grep -i error | head -5 || true
  done
else
  echo "Schema already loaded."
fi

# ── 2. Backend env + venv ────────────────────────────────────────────────────
step "2/4  Backend setup"
ENV_FILE="$ROOT/python/.env"
if [ ! -f "$ENV_FILE" ]; then
  FIREBASE_API_KEY=$(grep '^VITE_FIREBASE_API_KEY=' "$ROOT/solidjs/.env.local" | cut -d= -f2-)
  cat > "$ENV_FILE" <<EOF
# Local dev. ENVIRONMENT=local (not "development") so real Firebase tokens are verified;
# "development" switches on mock logins, which break Google / phone sign-in.
ENVIRONMENT=local
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=$(whoami)
POSTGRES_PASSWORD=
POSTGRES_DB=$DB
GOOGLE_CLOUD_PROJECT=$PROJECT
FIREBASE_PROJECT_ID=$PROJECT
FIREBASE_API_KEY=$FIREBASE_API_KEY
SECRET_KEY=local-$(openssl rand -hex 16)
OPENWEATHER_API_KEY=local-placeholder
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
EOF
  echo "Wrote python/.env"
fi
if [ ! -d "$ROOT/python/.venv" ]; then
  echo "Creating venv and installing requirements (first run takes a few minutes)..."
  python3 -m venv "$ROOT/python/.venv"
  "$ROOT/python/.venv/bin/pip" install -q --upgrade pip
  "$ROOT/python/.venv/bin/pip" install -q -r "$ROOT/python/requirements.txt"
fi
[ -f "$HOME/.config/gcloud/application_default_credentials.json" ] \
  || echo "  Note: no Google application-default credentials. Google / phone login works without them;" \
          "email sign-UP needs them (gcloud auth application-default login)."

# ── 3. Frontend deps ─────────────────────────────────────────────────────────
step "3/4  Frontend setup"
[ -d "$ROOT/solidjs/node_modules" ] || (cd "$ROOT/solidjs" && npm install)

# ── 4. Run both ──────────────────────────────────────────────────────────────
step "4/4  Starting backend :8000 and frontend :3000  (Ctrl+C stops both)"
trap 'kill 0' EXIT
(cd "$ROOT/python" && GOOGLE_CLOUD_QUOTA_PROJECT="$PROJECT" .venv/bin/uvicorn app.main:app --reload --port 8000) &
(cd "$ROOT/solidjs" && npx vite --port 3000) &
wait
