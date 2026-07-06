#!/usr/bin/env bash
set -euo pipefail

# Simple helper to apply backend DB migrations from anywhere in the repo.
# Usage: ./scripts/run_migrations.sh [alembic_target]
# Example: ./scripts/run_migrations.sh head

TARGET_REVISION="${1:-head}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BACKEND_DIR="${ROOT_DIR}/python"
VENV_DIR="${PY_BACKEND_DIR}/venv"

if [[ ! -d "${PY_BACKEND_DIR}" ]]; then
  echo "❌ Cannot find python backend directory at ${PY_BACKEND_DIR}" >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "❌ Missing virtual environment at ${VENV_DIR}. Run 'make setup' inside python/ first." >&2
  exit 1
fi

cd "${PY_BACKEND_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "🔄 Applying migrations (alembic upgrade ${TARGET_REVISION})..."
alembic upgrade "${TARGET_REVISION}"

echo "✅ Migrations complete"
