# CropSense AI - Quick Reference Card

## 🚀 Getting Started (First Time)

```bash
cd python
./setup_environment.sh
source venv/bin/activate
```

That's it! Everything is automated.

## 📋 Daily Commands

```bash
# Activate environment
source venv/bin/activate

# Start dev server
make run
# or
uvicorn app.main:app --reload

# Run tests
make test-ac2

# Format code
make format

# Check everything
make check
```

## 🔧 Common Tasks

| Task | Command |
|------|---------|
| Setup environment | `./setup_environment.sh` |
| Update dependencies | `make install` |
| Run all tests | `make test` |
| Run AC2 tests | `make test-ac2` |
| Start dev server | `make run` |
| Format code | `make format` |
| Lint code | `make lint` |
| Run all checks | `make check` |
| Clean caches | `make clean` |
| Database migration | `make migrate` |
| Apply migrations | `make db-upgrade` |
| Fix Python 3.14 | `make fix-314` |

## 🐍 Python Version Specific

```bash
# Use Python 3.12 (production)
./setup_environment.sh 3.12
make setup-312

# Use Python 3.14 (experimental)
./setup_environment.sh 3.14
make setup-314
```

## 🧪 Testing

```bash
# All tests
make test

# AC2 tests only
make test-ac2

# With coverage
make test-coverage

# Watch mode
make test-watch
```

## 🔍 Troubleshooting

### "Python not found"
```bash
# macOS
brew install python@3.12

# Ubuntu
sudo apt install python3.12
```

### "Module not found"
```bash
source venv/bin/activate
make install
```

### Python 3.14 issues
```bash
make fix-314
```

### Start fresh
```bash
make clean-all
./setup_environment.sh
```

## 📁 Important Files

```
python/
├── setup_environment.sh    # Main setup script
├── quick_setup.sh          # Interactive menu
├── Makefile                # Make commands
├── requirements.txt        # Dependencies
├── .env                    # Configuration
└── app/                    # Application code
```

## 🌐 Environment Variables

Copy and edit `.env`:
```bash
cp .env.example .env
nano .env
```

Required:
- `POSTGRES_*` - Database config
- `REDIS_*` - Cache config
- `AWS_*` - AWS credentials
- `COGNITO_*` - Auth config
- `SECRET_KEY` - App secret

## 🐳 Docker

```bash
# Build
make docker-build

# Run
make docker-run
```

## 📊 Database

```bash
# Create migration
make migrate

# Apply migrations
make db-upgrade

# Rollback
make db-downgrade

# Reset database
make db-reset
```

## 🎨 Code Quality

```bash
# Format code
make format

# Check format
make format-check

# Lint
make lint

# All checks
make check
```

## 🔐 Production

```bash
# Setup with Python 3.12
make setup-312

# Run production server
make run-prod
```

## 💡 Tips

1. **Always activate venv first:**
   ```bash
   source venv/bin/activate
   ```

2. **Use make for everything:**
   ```bash
   make help  # See all commands
   ```

3. **Format before commit:**
   ```bash
   make format
   make check
   ```

4. **Run tests frequently:**
   ```bash
   make test-ac2
   ```

5. **Keep dependencies updated:**
   ```bash
   make install
   ```

## 🆘 Get Help

```bash
# Show all make commands
make help

# Show environment info
make info

# Verify installation
make verify
```

## 📚 Documentation

- `ENVIRONMENT_SETUP_README.md` - Full setup guide
- `PYTHON_3.14_SETUP.md` - Python 3.14 guide
- `SETUP_AUTOMATION_COMPLETE.md` - Automation overview
- `AC2_IMPLEMENTATION_COMPLETE.md` - AC2 feature docs

## ✅ Quick Health Check

```bash
# 1. Check Python
python --version

# 2. Check venv
which python  # Should show venv path

# 3. Check imports
make verify

# 4. Run tests
make test-ac2

# All green? You're good to go! 🎉
```

## 🎯 Most Used Commands

```bash
# Setup (once)
./setup_environment.sh

# Daily workflow
source venv/bin/activate
make run                    # Start server
make test-ac2              # Run tests
make format                # Format code
make check                 # Check everything
```

## 🚨 Emergency Fixes

```bash
# Everything broken?
make clean-all
./setup_environment.sh

# Python 3.14 issues?
make fix-314

# Dependencies messed up?
make clean
make install

# Database issues?
make db-reset
```

---

**Remember:** When in doubt, run `make help` or check the documentation!
