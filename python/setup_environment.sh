#!/bin/bash

################################################################################
# CropSense AI - Python Environment Setup Script
# 
# This script automates the complete Python environment setup for the
# CropSense AI platform, handling Python 3.12, 3.13, and 3.14 compatibility.
#
# Usage:
#   ./setup_environment.sh [python_version]
#
# Examples:
#   ./setup_environment.sh           # Auto-detect Python version
#   ./setup_environment.sh 3.12      # Use Python 3.12 (recommended for production)
#   ./setup_environment.sh 3.14      # Use Python 3.14 (experimental)
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

################################################################################
# Python Version Detection
################################################################################

detect_python_version() {
    local requested_version=$1
    
    if [ -n "$requested_version" ]; then
        # User specified a version
        if command -v "python$requested_version" &> /dev/null; then
            PYTHON_CMD="python$requested_version"
            PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1 | awk '{print $2}')
            print_success "Using requested Python $PYTHON_VERSION"
            return 0
        else
            print_error "Python $requested_version not found"
            return 1
        fi
    fi
    
    # Auto-detect Python version
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    else
        print_error "Python not found. Please install Python 3.12 or later."
        exit 1
    fi
    
    # Extract major.minor version
    PYTHON_MAJOR_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f1,2)
    
    print_info "Detected Python $PYTHON_VERSION"
    
    # Check version compatibility
    case "$PYTHON_MAJOR_MINOR" in
        3.12)
            print_success "Python 3.12 detected - Recommended for production ✓"
            ;;
        3.13)
            print_warning "Python 3.13 detected - Experimental support"
            ;;
        3.14)
            print_warning "Python 3.14 detected - Pre-release, requires special handling"
            IS_PYTHON_314=true
            ;;
        *)
            print_error "Python $PYTHON_MAJOR_MINOR not supported. Please use Python 3.12 or later."
            exit 1
            ;;
    esac
}

################################################################################
# Virtual Environment Setup
################################################################################

setup_virtual_environment() {
    print_header "Setting Up Virtual Environment"
    
    # Remove old venv if exists
    if [ -d "venv" ]; then
        print_info "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create new venv
    print_info "Creating virtual environment with $PYTHON_CMD..."
    "$PYTHON_CMD" -m venv venv
    
    # Activate venv
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    print_success "Virtual environment created and activated"
}

################################################################################
# Dependency Installation
################################################################################

install_dependencies() {
    print_header "Installing Dependencies"
    
    if [ "$IS_PYTHON_314" = true ]; then
        install_dependencies_python314
    else
        install_dependencies_standard
    fi
}

install_dependencies_standard() {
    print_info "Installing dependencies for Python $PYTHON_MAJOR_MINOR..."
    
    # Install all dependencies from requirements.txt
    pip install -r requirements.txt
    
    print_success "All dependencies installed successfully"
}

install_dependencies_python314() {
    print_warning "Installing dependencies for Python 3.14 (pre-release)..."
    
    # Install core dependencies first
    print_info "Step 1/6: Installing FastAPI stack..."
    pip install fastapi uvicorn[standard] python-multipart jinja2 starlette
    
    print_info "Step 2/6: Installing database drivers..."
    pip install sqlalchemy alembic asyncpg pgvector
    # Use psycopg3 for Python 3.14
    pip install "psycopg[binary]>=3.2"
    
    print_info "Step 3/6: Installing AWS SDK..."
    pip install boto3 aioboto3 pynamodb
    
    print_info "Step 4/6: Installing security packages..."
    pip install "python-jose[cryptography]" "passlib[bcrypt]" cryptography bleach
    
    print_info "Step 5/6: Installing HTTP clients and utilities..."
    pip install httpx aiohttp requests tenacity
    pip install redis hiredis
    pip install python-dotenv structlog prometheus-client "sentry-sdk[fastapi]"
    pip install pillow pytest pytest-asyncio pytest-cov factory-boy hypothesis
    pip install black isort flake8 mypy pre-commit
    pip install celery python-magic pyowm twilio firebase-admin
    pip install geoalchemy2 shapely python-slugify email-validator phonenumbers pytz
    
    # Fix google-cloud-storage version conflict
    pip install "google-cloud-storage>=1.32.0,<3.0.0"
    
    print_info "Step 6/6: Installing ML stack..."
    # Install with forward compatibility if needed
    if ! pip install "pydantic>=2.10" "pydantic-settings>=2.7"; then
        print_warning "Pydantic installation failed, trying with forward compatibility flag..."
        PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install "pydantic>=2.10" "pydantic-settings>=2.7"
    fi
    
    pip install "numpy>=2.2"
    
    # Machine Learning handled via Cloud Bedrock (Local PyTorch/Transformers removed for size)
    print_info "Cloud-only ML mode enabled"
    
    print_success "Python 3.14 dependencies installed with workarounds"
}

################################################################################
# Code Compatibility Fixes
################################################################################

apply_code_fixes() {
    print_header "Applying Code Compatibility Fixes"
    
    # Check if auth.py needs JWT import fix
    if grep -q "^import jwt$" app/core/auth.py 2>/dev/null; then
        print_info "Fixing JWT import in auth.py..."
        
        # Backup original file
        cp app/core/auth.py app/core/auth.py.backup
        
        # Fix JWT import
        sed -i.tmp 's/^import jwt$/from jose import jwt/' app/core/auth.py
        rm -f app/core/auth.py.tmp
        
        # Add get_current_user alias if not present
        if ! grep -q "get_current_user = get_current_user_from_token" app/core/auth.py; then
            echo "" >> app/core/auth.py
            echo "# Alias for backward compatibility" >> app/core/auth.py
            echo "get_current_user = get_current_user_from_token" >> app/core/auth.py
        fi
        
        print_success "JWT import fixed in auth.py"
    else
        print_info "auth.py already has correct JWT import"
    fi
    
    # Check if aioredis is being used (deprecated)
    if grep -rq "import aioredis" app/ 2>/dev/null; then
        print_warning "Found deprecated aioredis imports. Please update to use redis.asyncio"
        print_info "Replace: import aioredis"
        print_info "With:    import redis.asyncio as redis"
    fi
}

################################################################################
# Environment Configuration
################################################################################

setup_environment_file() {
    print_header "Checking Environment Configuration"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_info "Creating .env from .env.example..."
            cp .env.example .env
            print_warning "Please update .env with your actual configuration values"
        else
            print_warning ".env file not found. Please create one with required configuration."
        fi
    else
        print_success ".env file exists"
    fi
}

################################################################################
# Verification
################################################################################

verify_installation() {
    print_header "Verifying Installation"
    
    print_info "Testing critical imports..."
    
    python -c "
import sys
print(f'Python: {sys.version}')
print('---')

try:
    import fastapi
    print(f'✓ FastAPI: {fastapi.__version__}')
except ImportError as e:
    print(f'✗ FastAPI: {e}')
    sys.exit(1)

try:
    import sqlalchemy
    print(f'✓ SQLAlchemy: {sqlalchemy.__version__}')
except ImportError as e:
    print(f'✗ SQLAlchemy: {e}')
    sys.exit(1)

try:
    import asyncpg
    print(f'✓ asyncpg: {asyncpg.__version__}')
except ImportError as e:
    print(f'✗ asyncpg: {e}')
    sys.exit(1)

try:
    import pydantic
    print(f'✓ Pydantic: {pydantic.__version__}')
except ImportError as e:
    print(f'✗ Pydantic: {e}')
    sys.exit(1)

try:
    import redis
    print(f'✓ Redis: {redis.__version__}')
except ImportError as e:
    print(f'✗ Redis: {e}')
    sys.exit(1)

try:
    import boto3
    print(f'✓ Boto3: {boto3.__version__}')
except ImportError as e:
    print(f'✗ Boto3: {e}')
    sys.exit(1)

try:
    import pytest
    print(f'✓ Pytest: {pytest.__version__}')
except ImportError as e:
    print(f'✗ Pytest: {e}')
    sys.exit(1)

try:
    from jose import jwt
    print(f'✓ python-jose: JWT support available')
except ImportError as e:
    print(f'✗ python-jose: {e}')
    sys.exit(1)

print('---')
print('✅ All critical imports successful!')
" || {
        print_error "Import verification failed"
        exit 1
    }
    
    print_success "All critical packages verified"
}

################################################################################
# Test Execution
################################################################################

run_tests() {
    print_header "Running AC2 Tests"
    
    print_info "Running AC2 integration tests..."
    if python -m pytest tests/test_ac2_integration.py -v; then
        print_success "AC2 integration tests passed"
    else
        print_warning "AC2 integration tests failed (may need database setup)"
    fi
    
    print_info "Running AC2 unit tests..."
    if python -m pytest tests/test_ac2_annual_strategy.py -v; then
        print_success "AC2 unit tests passed"
    else
        print_warning "AC2 unit tests failed"
    fi
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "CropSense AI - Python Environment Setup"
    
    # Parse arguments
    REQUESTED_VERSION=$1
    IS_PYTHON_314=false
    
    # Detect Python version
    detect_python_version "$REQUESTED_VERSION"
    
    # Setup virtual environment
    setup_virtual_environment
    
    # Install dependencies
    install_dependencies
    
    # Apply code fixes
    apply_code_fixes
    
    # Setup environment file
    setup_environment_file
    
    # Verify installation
    verify_installation
    
    # Run tests (optional)
    if [ "$RUN_TESTS" = "true" ]; then
        run_tests
    fi
    
    # Final instructions
    print_header "Setup Complete!"
    
    echo -e "${GREEN}✓ Python environment successfully configured${NC}"
    echo -e "\n${BLUE}Next Steps:${NC}"
    echo -e "  1. Activate the virtual environment:"
    echo -e "     ${YELLOW}source venv/bin/activate${NC}"
    echo -e "\n  2. Update .env with your configuration"
    echo -e "\n  3. Run database migrations:"
    echo -e "     ${YELLOW}alembic upgrade head${NC}"
    echo -e "\n  4. Start the development server:"
    echo -e "     ${YELLOW}uvicorn app.main:app --reload${NC}"
    echo -e "\n  5. Run tests:"
    echo -e "     ${YELLOW}pytest tests/ -v${NC}"
    
    if [ "$IS_PYTHON_314" = true ]; then
        echo -e "\n${YELLOW}⚠ Python 3.14 Notes:${NC}"
        echo -e "  - You're using a pre-release Python version"
        echo -e "  - For production, use Python 3.12"
        echo -e "  - Some packages may have compatibility issues"
    fi
    
    echo -e "\n${GREEN}Happy coding! 🚀${NC}\n"
}

# Run main function
main "$@"
