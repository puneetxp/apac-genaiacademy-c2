# Python Environment Setup - Quick Start Guide

This guide explains how to use the automated setup script to configure your Python environment for the CropSense AI platform.

## Quick Start

### Option 1: Auto-detect Python Version (Recommended)

```bash
cd python
./setup_environment.sh
```

This will automatically detect your Python version and configure the environment accordingly.

### Option 2: Specify Python Version

```bash
# Use Python 3.12 (recommended for production)
./setup_environment.sh 3.12

# Use Python 3.13 (experimental)
./setup_environment.sh 3.13

# Use Python 3.14 (pre-release, requires workarounds)
./setup_environment.sh 3.14
```

## What the Script Does

The `setup_environment.sh` script automates the entire environment setup process:

1. **Detects Python Version**
   - Auto-detects installed Python version
   - Validates compatibility (3.12, 3.13, or 3.14)
   - Warns about experimental/pre-release versions

2. **Creates Virtual Environment**
   - Removes old venv if exists
   - Creates fresh virtual environment
   - Upgrades pip, setuptools, and wheel

3. **Installs Dependencies**
   - Standard installation for Python 3.12/3.13
   - Special handling for Python 3.14:
     - Installs psycopg3 instead of psycopg2
     - Handles Pydantic with forward compatibility
     - Installs PyTorch from nightly builds if needed
     - Fixes google-cloud-storage version conflicts

4. **Applies Code Fixes**
   - Fixes JWT import in auth.py (jose.jwt instead of jwt)
   - Adds get_current_user alias for backward compatibility
   - Checks for deprecated aioredis usage

5. **Verifies Installation**
   - Tests all critical imports
   - Validates package versions
   - Reports any issues

6. **Optional: Runs Tests**
   - AC2 integration tests
   - AC2 unit tests

## Manual Setup (Alternative)

If you prefer manual setup or the script fails:

### For Python 3.12/3.13

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlalchemy, asyncpg, pydantic; print('✓ Success')"
```

### For Python 3.14

```bash
# Create virtual environment
python3.14 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install fastapi uvicorn[standard] python-multipart jinja2 starlette
pip install sqlalchemy alembic asyncpg pgvector

# CRITICAL: Use psycopg3 for Python 3.14
pip install "psycopg[binary]>=3.2"

# Install AWS and security
pip install boto3 aioboto3 pynamodb
pip install "python-jose[cryptography]" "passlib[bcrypt]" cryptography bleach

# Install utilities
pip install httpx aiohttp requests tenacity
pip install redis hiredis
pip install python-dotenv structlog prometheus-client "sentry-sdk[fastapi]"
pip install pillow pytest pytest-asyncio pytest-cov factory-boy hypothesis
pip install black isort flake8 mypy pre-commit
pip install celery python-magic pyowm twilio firebase-admin
pip install geoalchemy2 shapely python-slugify email-validator phonenumbers pytz

# Fix google-cloud-storage conflict
pip install "google-cloud-storage>=1.32.0,<3.0.0"

# Install Pydantic (may need forward compatibility)
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install "pydantic>=2.10" "pydantic-settings>=2.7"

# Install ML stack
pip install "numpy>=2.2" "pandas>=2.2" "scikit-learn>=1.6"

# Install PyTorch (use nightly for 3.14)
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu
pip install transformers sentence-transformers

# Optional: OpenCV (may fail on 3.14)
pip install opencv-python || echo "OpenCV skipped (not critical)"
```

## Code Fixes Required for Python 3.14

### 1. Fix JWT Import in auth.py

**Before:**
```python
import jwt
from jose import JWTError, jwk
```

**After:**
```python
from jose import jwt, JWTError, jwk
```

### 2. Add get_current_user Alias

Add to the end of `app/core/auth.py`:
```python
# Alias for backward compatibility
get_current_user = get_current_user_from_token
```

### 3. Replace aioredis (if used)

**Before:**
```python
import aioredis
redis_client = await aioredis.create_redis_pool("redis://localhost")
```

**After:**
```python
import redis.asyncio as redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
```

## Troubleshooting

### Issue: "Python not found"

**Solution:** Install Python 3.12 or later:
```bash
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt install python3.12 python3.12-venv

# Windows
# Download from python.org
```

### Issue: "ModuleNotFoundError: No module named 'jwt'"

**Solution:** The script should fix this automatically. If not:
```bash
source venv/bin/activate
pip install "python-jose[cryptography]"
```

Then update `app/core/auth.py` to use `from jose import jwt`.

### Issue: "psycopg2-binary not available for Python 3.14"

**Solution:** Use psycopg3:
```bash
pip uninstall psycopg2-binary
pip install "psycopg[binary]>=3.2"
```

Update connection strings from `postgresql+psycopg2://` to `postgresql+psycopg://`.

### Issue: "torch not available for Python 3.14"

**Solution:** Use nightly build:
```bash
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu
```

### Issue: "Pydantic build fails on Python 3.14"

**Solution:** Use forward compatibility flag:
```bash
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install pydantic
```

### Issue: "google-cloud-storage version conflict"

**Solution:** Install compatible version:
```bash
pip install "google-cloud-storage>=1.32.0,<3.0.0"
```

## Running Tests

After setup, verify everything works:

```bash
# Activate virtual environment
source venv/bin/activate

# Run AC2 integration tests
python -m pytest tests/test_ac2_integration.py -v

# Run AC2 unit tests
python -m pytest tests/test_ac2_annual_strategy.py -v

# Run all tests
python -m pytest tests/ -v
```

Expected results:
- AC2 Integration Tests: 7/7 passing ✓
- AC2 Unit Tests: 8/8 passing ✓

## Environment Variables

Create a `.env` file with required configuration:

```bash
# Copy example
cp .env.example .env

# Edit with your values
nano .env
```

Required variables:
- `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_HOST`, `REDIS_PORT`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `COGNITO_USER_POOL_ID`, `COGNITO_CLIENT_ID`, `COGNITO_CLIENT_SECRET`
- `SECRET_KEY` (generate with `openssl rand -hex 32`)

## Starting the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script (if available)
./run_dev.sh
```

## Production Deployment

For production, use Python 3.12:

```bash
# Install Python 3.12
brew install python@3.12  # macOS
# or
sudo apt install python3.12  # Ubuntu

# Run setup script with Python 3.12
./setup_environment.sh 3.12

# Use production WSGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Docker Alternative

For consistent environments across all systems:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t cropsense-api .
docker run -p 8000:8000 --env-file .env cropsense-api
```

## Script Options

The setup script supports several environment variables:

```bash
# Run tests after setup
RUN_TESTS=true ./setup_environment.sh

# Skip code fixes
SKIP_CODE_FIXES=true ./setup_environment.sh

# Verbose output
VERBOSE=true ./setup_environment.sh
```

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review `PYTHON_3.14_SETUP.md` for detailed Python 3.14 instructions
3. Check `PYTHON_3.14_SUCCESS.md` for known working configuration
4. Run the script with verbose output: `VERBOSE=true ./setup_environment.sh`

## Summary

The automated setup script handles all the complexity of setting up the Python environment, including:

- ✅ Python version detection and validation
- ✅ Virtual environment creation
- ✅ Dependency installation with version-specific workarounds
- ✅ Code compatibility fixes
- ✅ Installation verification
- ✅ Optional test execution

Just run `./setup_environment.sh` and you're ready to go!
