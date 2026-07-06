#!/bin/bash

# Python 3.14 Compatible Setup Script
# Handles all compatibility issues and sets up the virtual environment

set -e  # Exit on error

echo "=========================================="
echo "Python 3.14 Compatible Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "   Python version: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
    print_success "Python version is compatible (3.11+)"
else
    print_error "Python 3.11 or higher is required"
    exit 1
fi

# Detect if Python 3.14
IS_PYTHON_314=false
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
    IS_PYTHON_314=true
    print_warning "Python 3.14 detected - applying compatibility fixes"
fi

# Change to script directory
cd "$(dirname "$0")"

# Step 1: Clean up old virtual environment
print_info "Cleaning up old virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
    print_success "Removed old venv"
fi

# Clean Python cache
print_info "Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
print_success "Python cache cleaned"

# Step 2: Create new virtual environment
print_info "Creating new virtual environment..."
python3 -m venv venv
print_success "Virtual environment created"

# Step 3: Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Upgrade pip, setuptools, and wheel
print_info "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel
print_success "Core packages upgraded"

# Step 5: Install compatibility packages for Python 3.14
if [ "$IS_PYTHON_314" = true ]; then
    print_info "Installing Python 3.14 compatibility packages..."
    
    # Install setuptools with distutils support
    pip install --upgrade "setuptools>=75.0.0"
    
    # Install packaging (required for some packages)
    pip install --upgrade "packaging>=24.0"
    
    print_success "Compatibility packages installed"
fi

# Step 6: Install dependencies with special handling
print_info "Installing dependencies from requirements.txt..."

# For Python 3.14, we need to handle some packages specially
if [ "$IS_PYTHON_314" = true ]; then
    print_warning "Using Python 3.14 compatible installation strategy..."
    
    # Install Pydantic with forward compatibility
    print_info "Installing Pydantic..."
    PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install "pydantic>=2.10.5" "pydantic-settings>=2.7.0"
    
    # Install uvicorn with compatible version
    print_info "Installing uvicorn..."
    pip install "uvicorn[standard]>=0.32.1"
    
    # Install other dependencies
    print_info "Installing remaining dependencies..."
    pip install -r requirements.txt --no-deps || true
    pip install -r requirements.txt
else
    # Standard installation for Python 3.11-3.13
    pip install -r requirements.txt
fi

print_success "Dependencies installed"

# Step 7: Cloud AI handles Machine Learning (PyTorch removed to save space)
print_info "Using Cloud Bedrock for embeddings and AI (Local PyTorch removed to save size)"

# Step 8: Verify critical imports
print_info "Verifying critical imports..."

IMPORT_ERRORS=0

# Test FastAPI
if python -c "import fastapi" 2>/dev/null; then
    print_success "FastAPI import OK"
else
    print_error "FastAPI import failed"
    IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
fi

# Test uvicorn
if python -c "import uvicorn" 2>/dev/null; then
    print_success "uvicorn import OK"
else
    print_error "uvicorn import failed"
    IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
fi

# Test Pydantic
if python -c "import pydantic" 2>/dev/null; then
    print_success "Pydantic import OK"
else
    print_error "Pydantic import failed"
    IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
fi

# Test SQLAlchemy
if python -c "import sqlalchemy" 2>/dev/null; then
    print_success "SQLAlchemy import OK"
else
    print_error "SQLAlchemy import failed"
    IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
fi

# Test psycopg
if python -c "import psycopg" 2>/dev/null; then
    print_success "psycopg import OK"
else
    print_error "psycopg import failed"
    IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
fi

# Test custom ORM
if python -c "from app.orm.ai_usage_quota import AiUsageQuota" 2>/dev/null; then
    print_success "Custom ORM import OK"
else
    print_warning "Custom ORM import failed (may need to run migrations)"
fi

# Step 9: Check for distutils issues (Python 3.14 specific)
if [ "$IS_PYTHON_314" = true ]; then
    print_info "Checking for distutils compatibility..."
    if python -c "import setuptools._distutils" 2>/dev/null; then
        print_success "distutils compatibility OK"
    else
        print_warning "distutils may have issues - installing fix..."
        pip install --upgrade --force-reinstall "setuptools>=75.0.0"
    fi
fi

# Step 10: Summary
echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""

if [ $IMPORT_ERRORS -eq 0 ]; then
    print_success "All critical imports successful!"
    echo ""
    print_info "Virtual environment is ready to use"
    echo ""
    echo "To activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "To start the backend server:"
    echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    print_success "Setup complete!"
else
    print_error "Setup completed with $IMPORT_ERRORS import errors"
    echo ""
    print_warning "Please check the errors above and try:"
    echo "   1. Deactivate and reactivate the virtual environment"
    echo "   2. Run: pip install --upgrade --force-reinstall -r requirements.txt"
    echo "   3. Check the troubleshooting section in PYTHON_314_SETUP_GUIDE.md"
    exit 1
fi

# Step 11: Create activation helper script
cat > activate_venv.sh << 'EOF'
#!/bin/bash
# Quick activation script for the virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"
echo "Python version: $(python --version)"
echo ""
echo "To start the backend:"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
EOF

chmod +x activate_venv.sh
print_success "Created activation helper: ./activate_venv.sh"

echo ""
echo "=========================================="
