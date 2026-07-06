#!/bin/bash

# Script to copy backend code from crop-intelligence-platform to farming-platform
# Run this from the farming-platform directory

SOURCE="../crop-intelligence-platform/backend"
DEST="./python"

echo "Copying backend code from crop-intelligence-platform to farming-platform..."

# Copy core directory (config, database, auth)
echo "Copying core directory..."
cp -r "$SOURCE/app/core" "$DEST/app/"

# Copy schemas directory
echo "Copying schemas directory..."
cp -r "$SOURCE/app/schemas" "$DEST/app/"

# Copy custom services (not the generated ones)
echo "Copying custom services..."
cp "$SOURCE/app/services/bedrock_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/cognito_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/crop_recommendation_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/market_data_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/profit_margin_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/seasonal_trend_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/vector_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/yield_profit_service.py" "$DEST/app/services/"
cp "$SOURCE/app/services/README_MARKET_DATA.md" "$DEST/app/services/" 2>/dev/null || true

# Copy API v1 routes
echo "Copying API v1 routes..."
mkdir -p "$DEST/app/api/v1"
cp -r "$SOURCE/app/api/v1" "$DEST/app/api/"
cp "$SOURCE/app/api/__init__.py" "$DEST/app/api/" 2>/dev/null || true
cp "$SOURCE/app/api/README.md" "$DEST/app/api/" 2>/dev/null || true

# Copy supporting files
echo "Copying supporting files..."
cp "$SOURCE/requirements.txt" "$DEST/"
cp "$SOURCE/.env.example" "$DEST/"
cp "$SOURCE/.python-version" "$DEST/" 2>/dev/null || true
cp "$SOURCE/pyproject.toml" "$DEST/" 2>/dev/null || true
cp "$SOURCE/alembic.ini" "$DEST/" 2>/dev/null || true

# Copy alembic directory
echo "Copying alembic directory..."
cp -r "$SOURCE/alembic" "$DEST/" 2>/dev/null || true

# Copy tests directory
echo "Copying tests directory..."
cp -r "$SOURCE/tests" "$DEST/" 2>/dev/null || true

# Copy scripts directory
echo "Copying scripts directory..."
cp -r "$SOURCE/scripts" "$DEST/" 2>/dev/null || true

# Copy docs directory
echo "Copying docs directory..."
cp -r "$SOURCE/docs" "$DEST/" 2>/dev/null || true

# Copy examples directory
echo "Copying examples directory..."
cp -r "$SOURCE/examples" "$DEST/" 2>/dev/null || true

echo "✅ Backend code copied successfully!"
echo ""
echo "Next steps:"
echo "1. Review the copied files in python/app/"
echo "2. Update python/app/main.py to include v1 routes"
echo "3. Install dependencies: cd python && pip install -r requirements.txt"
echo "4. Set up .env file: cp .env.example .env"
echo "5. Run the server: uvicorn app.main:app --reload"
