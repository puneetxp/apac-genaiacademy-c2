#!/bin/bash

################################################################################
# CropSense AI - Quick Setup Script
# 
# One-command setup for common scenarios
################################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
   ____                 ____                        _    ___ 
  / ___|_ __ ___  _ __ / ___|  ___ _ __  ___  ___  / \  |_ _|
 | |   | '__/ _ \| '_ \\___ \ / _ \ '_ \/ __|/ _ \/ _ \  | | 
 | |___| | | (_) | |_) |__) |  __/ | | \__ \  __/ ___ \ | | 
  \____|_|  \___/| .__/____/ \___|_| |_|___/\___/_/   \_\___|
                 |_|                                          
EOF
echo -e "${NC}"

echo -e "${GREEN}Quick Setup - Choose your scenario:${NC}\n"
echo "1) Fresh install (recommended)"
echo "2) Update dependencies only"
echo "3) Fix Python 3.14 compatibility issues"
echo "4) Run tests only"
echo "5) Full setup + run tests"
echo "6) Production setup (Python 3.12)"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo -e "\n${BLUE}Running fresh install...${NC}"
        ./setup_environment.sh
        ;;
    2)
        echo -e "\n${BLUE}Updating dependencies...${NC}"
        source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Dependencies updated${NC}"
        ;;
    3)
        echo -e "\n${BLUE}Fixing Python 3.14 compatibility...${NC}"
        source venv/bin/activate
        
        # Fix JWT import
        if grep -q "^import jwt$" app/core/auth.py 2>/dev/null; then
            sed -i.bak 's/^import jwt$/from jose import jwt/' app/core/auth.py
            echo -e "${GREEN}✓ Fixed JWT import${NC}"
        fi
        
        # Add get_current_user alias
        if ! grep -q "get_current_user = get_current_user_from_token" app/core/auth.py; then
            echo "" >> app/core/auth.py
            echo "# Alias for backward compatibility" >> app/core/auth.py
            echo "get_current_user = get_current_user_from_token" >> app/core/auth.py
            echo -e "${GREEN}✓ Added get_current_user alias${NC}"
        fi
        
        # Install missing packages
        pip install "psycopg[binary]>=3.2" "python-jose[cryptography]" requests aiohttp
        
        echo -e "${GREEN}✓ Python 3.14 compatibility fixes applied${NC}"
        ;;
    4)
        echo -e "\n${BLUE}Running tests...${NC}"
        source venv/bin/activate
        python -m pytest tests/test_ac2_integration.py tests/test_ac2_annual_strategy.py -v
        ;;
    5)
        echo -e "\n${BLUE}Running full setup with tests...${NC}"
        RUN_TESTS=true ./setup_environment.sh
        ;;
    6)
        echo -e "\n${BLUE}Setting up for production (Python 3.12)...${NC}"
        if command -v python3.12 &> /dev/null; then
            ./setup_environment.sh 3.12
        else
            echo -e "${YELLOW}Python 3.12 not found. Please install it first:${NC}"
            echo "  macOS: brew install python@3.12"
            echo "  Ubuntu: sudo apt install python3.12"
            exit 1
        fi
        ;;
    *)
        echo -e "${YELLOW}Invalid choice. Please run again and select 1-6.${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✓ Setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
