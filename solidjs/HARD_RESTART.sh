#!/bin/bash

echo "=========================================="
echo "Hard Restart Frontend (Clear Cache)"
echo "=========================================="
echo ""

# Kill any running dev servers
echo "Step 1: Killing any running dev servers..."
pkill -f "vite" || true
pkill -f "npm run dev" || true
sleep 2

# Clear node_modules cache
echo ""
echo "Step 2: Clearing node_modules/.vite cache..."
rm -rf node_modules/.vite
rm -rf .vite
rm -rf dist

# Clear browser cache hint
echo ""
echo "Step 3: Clear browser cache:"
echo "  - Open DevTools (F12)"
echo "  - Right-click refresh button"
echo "  - Select 'Empty Cache and Hard Reload'"
echo ""

# Restart dev server
echo "Step 4: Starting dev server..."
echo ""
npm run dev
