#!/bin/bash

# Code Regeneration Script for Rural Farming Platform
# This script regenerates all Python code from JSON schemas using setup.php

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Rural Farming Platform - Code Regeneration ===${NC}\n"

# Check if setup.php exists
if [ ! -f "setup.php" ]; then
    echo -e "${RED}Error: setup.php not found in current directory${NC}"
    echo "Please run this script from the cropsense-ai directory"
    exit 1
fi

# Backup custom files
echo -e "${YELLOW}Step 1: Backing up custom files...${NC}"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup custom API endpoints
if [ -d "python/app/api/v1" ]; then
    echo "  Backing up custom API endpoints..."
    cp -r python/app/api/v1 "$BACKUP_DIR/" 2>/dev/null || true
fi

# Backup custom services
if [ -d "python/app/services" ]; then
    echo "  Backing up custom services..."
    mkdir -p "$BACKUP_DIR/services"
    cp python/app/services/*_service.py "$BACKUP_DIR/services/" 2>/dev/null || true
fi

# Backup hand-written models that have no database/Model/*.json schema (the generator won't recreate them)
if [ -d "python/app/models" ]; then
    mkdir -p "$BACKUP_DIR/models"
    for model_file in python/app/models/*.py; do
        [ -e "$model_file" ] || continue
        model_name=$(basename "$model_file" .py)
        if [ ! -f "database/Model/${model_name}.json" ]; then
            echo "  Backing up custom model: $model_name"
            cp "$model_file" "$BACKUP_DIR/models/"
        fi
    done
fi

echo -e "${GREEN}✓ Backup completed: $BACKUP_DIR${NC}\n"

# Remove old generated files
echo -e "${YELLOW}Step 2: Removing old generated files...${NC}"
rm -rf python/app/api/isuper 2>/dev/null || true
rm -rf python/app/api/islogin 2>/dev/null || true
rm -rf python/app/api/ipublic 2>/dev/null || true
rm -rf python/app/api/roles 2>/dev/null || true
rm -f python/app/api/__init__.py 2>/dev/null || true
rm -rf python/app/models 2>/dev/null || true
echo -e "${GREEN}✓ Old files removed${NC}\n"

# Run setup.php
echo -e "${YELLOW}Step 3: Running setup.php to generate code...${NC}"
php setup.php || {
    echo -e "${RED}Error: Code generation failed${NC}"
    echo -e "${YELLOW}Restoring from backup...${NC}"
    cp -r "$BACKUP_DIR/v1" python/app/api/ 2>/dev/null || true
    cp "$BACKUP_DIR/services/"*_service.py python/app/services/ 2>/dev/null || true
    exit 1
}
echo -e "${GREEN}✓ Code generation completed${NC}\n"

# Restore custom files
echo -e "${YELLOW}Step 4: Restoring custom files...${NC}"
if [ -d "$BACKUP_DIR/v1" ]; then
    echo "  Restoring custom API endpoints..."
    cp -r "$BACKUP_DIR/v1" python/app/api/ 2>/dev/null || true
fi

if [ -d "$BACKUP_DIR/services" ]; then
    echo "  Restoring custom services..."
    cp "$BACKUP_DIR/services/"*_service.py python/app/services/ 2>/dev/null || true
fi

if [ -d "$BACKUP_DIR/models" ] && [ -n "$(ls -A "$BACKUP_DIR/models" 2>/dev/null)" ]; then
    echo "  Restoring custom models..."
    cp "$BACKUP_DIR/models/"*.py python/app/models/
fi
echo -e "${GREEN}✓ Custom files restored${NC}\n"

# Verify Python syntax
echo -e "${YELLOW}Step 5: Verifying Python syntax...${NC}"
PYTHON_BIN=$(command -v python3 || command -v python)
cd python
find app -name "*.py" -print0 | xargs -0 "$PYTHON_BIN" -m py_compile || {
    echo -e "${RED}Error: Generated code has syntax errors${NC}"
    exit 1
}
cd ..
echo -e "${GREEN}✓ Syntax verification passed${NC}\n"

echo -e "${GREEN}=== Code regeneration completed successfully! ===${NC}"
echo -e "\nGenerated files:"
echo -e "  - python/app/models/ (ORM models)"
echo -e "  - python/app/api/isuper/ (Super admin routes)"
echo -e "  - python/app/api/islogin/ (Authenticated routes)"
echo -e "  - python/app/api/ipublic/ (Public routes)"
echo -e "\nBackup location: ${YELLOW}$BACKUP_DIR${NC}\n"
