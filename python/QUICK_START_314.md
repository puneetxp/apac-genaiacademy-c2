# Python 3.14 Quick Start

## One-Command Setup

```bash
cd rural-farming-platform/python && ./setup_python314.sh
```

## Manual Setup (If Script Fails)

```bash
# 1. Clean up
rm -rf venv
find . -type d -name __pycache__ -exec rm -rf {} +

# 2. Create venv
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade core
pip install --upgrade pip setuptools wheel

# 4. Install dependencies
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt

# 5. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Quick Fixes

### Fix distutils error
```bash
pip install --upgrade "setuptools>=75.0.0"
```

### Fix Pydantic error
```bash
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install --upgrade "pydantic>=2.10.5"
```

### Fix uvicorn error
```bash
pip install --upgrade "uvicorn[standard]>=0.32.1"
```

### Fix PyTorch (3.14 only)
```bash
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu
```

## Test Installation

```bash
# Test imports
python -c "import fastapi, uvicorn, pydantic, sqlalchemy; print('✓ All OK')"

# Test ORM
python -c "from app.orm.ai_usage_quota import AiUsageQuota; print('✓ ORM OK')"

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test endpoint (in another terminal)
curl http://localhost:8000/api/v1/ai-quota/status/1
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Permission denied | `chmod +x setup_python314.sh` |
| Import errors | `pip install --force-reinstall -r requirements.txt` |
| Port in use | `lsof -i :8000` then `kill -9 <PID>` |
| Database error | Check PostgreSQL: `psql -U puneetsharma -d cropsense_dev -c "SELECT 1"` |

## Success Indicators

✅ Script completes without errors
✅ `python -c "import fastapi"` works
✅ Server starts on port 8000
✅ Endpoint returns JSON response

## Full Documentation

See `PYTHON_314_SETUP_GUIDE.md` for complete details.
