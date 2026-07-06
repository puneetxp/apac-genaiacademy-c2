# Backend Setup - Python 3.14 Compatible

## Quick Start

### One-Command Setup
```bash
./setup_python314.sh
```

### Start Server
```bash
./start_backend.sh
```

That's it! 🎉

## What These Scripts Do

### setup_python314.sh
- Detects your Python version (3.11-3.14)
- Cleans up old virtual environment
- Creates new virtual environment
- Installs all dependencies with compatibility fixes
- Verifies installation
- Handles Python 3.14 specific issues automatically

### start_backend.sh
- Activates virtual environment
- Checks prerequisites
- Starts backend server on http://localhost:8000

## Manual Setup (If Needed)

```bash
# Clean up
rm -rf venv
find . -type d -name __pycache__ -exec rm -rf {} +

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install
pip install --upgrade pip setuptools wheel
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt

# Start
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test Installation

```bash
# Activate venv
source venv/bin/activate

# Test imports
python -c "import fastapi, uvicorn, pydantic; print('✓ OK')"

# Test endpoint
curl http://localhost:8000/api/v1/ai-quota/status/1
```

## Documentation

- `QUICK_START_314.md` - Quick reference
- `PYTHON_314_SETUP_GUIDE.md` - Complete guide
- `PYTHON_314_COMPATIBILITY_COMPLETE.md` - Compatibility details
- `SETUP_COMPLETE_PYTHON_314.md` - Summary

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Permission denied | `chmod +x *.sh` |
| Import errors | `pip install --force-reinstall -r requirements.txt` |
| Port in use | `lsof -i :8000` then `kill -9 <PID>` |
| Database error | `psql -U puneetsharma -d cropsense_dev -c "SELECT 1"` |

## Python Version Support

✅ Python 3.14 (development)
✅ Python 3.13 (production)
✅ Python 3.12 (recommended)
✅ Python 3.11 (production)

## Success Indicators

✅ Script completes without errors
✅ Server starts on port 8000
✅ Endpoints return JSON responses
✅ No import errors in logs

## Need Help?

See `PYTHON_314_SETUP_GUIDE.md` for detailed troubleshooting.
