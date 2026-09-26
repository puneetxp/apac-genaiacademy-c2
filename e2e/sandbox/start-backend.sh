#!/usr/bin/env bash
# Run the FastAPI backend in E2E mode against the throwaway cropsense_e2e database.
# Mock Firebase auth, no schedulers, no Redis. Other settings (AI keys etc.) still come from python/.env.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/python"

export ENVIRONMENT=test
export E2E_MODE=true
export POSTGRES_DB="${E2E_DB:-cropsense_e2e}"
export ALLOWED_ORIGINS="http://localhost:${E2E_FRONTEND_PORT:-3100},http://127.0.0.1:${E2E_FRONTEND_PORT:-3100}"
export RATE_LIMIT_ENABLED=false
export CACHE_ENABLED=false

# E2E_RELOAD=1 restarts the server when backend code changes (handy while fixing things).
RELOAD=()
[ -n "${E2E_RELOAD:-}" ] && RELOAD=(--reload --reload-dir app)
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "${E2E_BACKEND_PORT:-8100}" ${RELOAD[@]+"${RELOAD[@]}"}
