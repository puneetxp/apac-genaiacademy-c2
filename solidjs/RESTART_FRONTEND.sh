#!/bin/bash

# Script to restart frontend with clean install
# This ensures the-solid-router package is completely removed

echo "🛑 Stopping any running dev servers..."
pkill -f "vite"

echo "🧹 Cleaning node_modules and package-lock..."
rm -rf node_modules package-lock.json

echo "📦 Installing dependencies (this will remove the-solid-router)..."
npm install

echo "🚀 Starting dev server..."
npm run dev
