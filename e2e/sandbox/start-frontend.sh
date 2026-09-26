#!/usr/bin/env bash
# Run the SolidJS dev server pointed at the E2E backend (port 8100 by default).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/solidjs"

export VITE_API_URL="http://localhost:${E2E_BACKEND_PORT:-8100}"
exec npx vite --port "${E2E_FRONTEND_PORT:-3100}" --strictPort
