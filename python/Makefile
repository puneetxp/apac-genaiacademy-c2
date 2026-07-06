# CropSense AI - Python Backend Makefile
# 
# Quick commands for common development tasks

.PHONY: help setup install test clean run dev lint format check migrate db-upgrade db-downgrade

# Default target
.DEFAULT_GOAL := help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)CropSense AI - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## Full environment setup (auto-detect Python version)
	@echo "$(BLUE)Setting up environment...$(NC)"
	@./setup_environment.sh

setup-312: ## Setup with Python 3.12 (recommended for production)
	@echo "$(BLUE)Setting up with Python 3.12...$(NC)"
	@./setup_environment.sh 3.12

setup-314: ## Setup with Python 3.14 (experimental)
	@echo "$(BLUE)Setting up with Python 3.14...$(NC)"
	@./setup_environment.sh 3.14

install: ## Install/update dependencies only
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing dev dependencies...$(NC)"
	@. venv/bin/activate && pip install -r requirements-test.txt
	@echo "$(GREEN)✓ Dev dependencies installed$(NC)"

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	@. venv/bin/activate && python -m pytest tests/ -v

test-ac2: ## Run AC2 tests only
	@echo "$(BLUE)Running AC2 tests...$(NC)"
	@. venv/bin/activate && python -m pytest tests/test_ac2_integration.py tests/test_ac2_annual_strategy.py -v

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@. venv/bin/activate && python -m pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	@. venv/bin/activate && python -m pytest tests/ -v --looponfail

clean: ## Clean up generated files and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -rf htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned up$(NC)"

clean-all: clean ## Clean everything including venv
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	@rm -rf venv/
	@echo "$(GREEN)✓ Everything cleaned$(NC)"

run: ## Run development server
	@echo "$(BLUE)Starting development server...$(NC)"
	@. venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev: run ## Alias for 'run'

run-prod: ## Run production server with gunicorn
	@echo "$(BLUE)Starting production server...$(NC)"
	@. venv/bin/activate && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

lint: ## Run linters (flake8, mypy)
	@echo "$(BLUE)Running linters...$(NC)"
	@. venv/bin/activate && flake8 app/ tests/ --max-line-length=120 --exclude=venv,alembic
	@. venv/bin/activate && mypy app/ --ignore-missing-imports
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	@. venv/bin/activate && black app/ tests/ --line-length=120
	@. venv/bin/activate && isort app/ tests/ --profile black
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code format...$(NC)"
	@. venv/bin/activate && black app/ tests/ --check --line-length=120
	@. venv/bin/activate && isort app/ tests/ --check --profile black

check: lint format-check test ## Run all checks (lint, format, test)

migrate: ## Create a new database migration
	@echo "$(BLUE)Creating migration...$(NC)"
	@read -p "Migration message: " msg; \
	. venv/bin/activate && alembic revision --autogenerate -m "$$msg"
	@echo "$(GREEN)✓ Migration created$(NC)"

db-upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying migrations...$(NC)"
	@. venv/bin/activate && alembic upgrade head
	@echo "$(GREEN)✓ Database upgraded$(NC)"

db-downgrade: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	@. venv/bin/activate && alembic downgrade -1
	@echo "$(GREEN)✓ Migration rolled back$(NC)"

db-reset: ## Reset database (downgrade all, then upgrade)
	@echo "$(YELLOW)Resetting database...$(NC)"
	@. venv/bin/activate && alembic downgrade base
	@. venv/bin/activate && alembic upgrade head
	@echo "$(GREEN)✓ Database reset$(NC)"

shell: ## Open Python shell with app context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@. venv/bin/activate && python -i -c "from app.main import app; from app.core.database import SessionLocal; db = SessionLocal(); print('App context loaded. Use: app, db')"

verify: ## Verify installation
	@echo "$(BLUE)Verifying installation...$(NC)"
	@. venv/bin/activate && python -c "import fastapi, sqlalchemy, asyncpg, pydantic, redis, boto3, pytest; print('✓ All critical imports successful')"
	@echo "$(GREEN)✓ Installation verified$(NC)"

fix-314: ## Fix Python 3.14 compatibility issues
	@echo "$(BLUE)Fixing Python 3.14 compatibility...$(NC)"
	@if grep -q "^import jwt$$" app/core/auth.py 2>/dev/null; then \
		sed -i.bak 's/^import jwt$$/from jose import jwt/' app/core/auth.py; \
		echo "$(GREEN)✓ Fixed JWT import$(NC)"; \
	fi
	@if ! grep -q "get_current_user = get_current_user_from_token" app/core/auth.py; then \
		echo "" >> app/core/auth.py; \
		echo "# Alias for backward compatibility" >> app/core/auth.py; \
		echo "get_current_user = get_current_user_from_token" >> app/core/auth.py; \
		echo "$(GREEN)✓ Added get_current_user alias$(NC)"; \
	fi
	@. venv/bin/activate && pip install "psycopg[binary]>=3.2" "python-jose[cryptography]" requests aiohttp
	@echo "$(GREEN)✓ Python 3.14 fixes applied$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t cropsense-api:latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	@docker run -p 8000:8000 --env-file .env cropsense-api:latest

requirements-update: ## Update requirements.txt from current environment
	@echo "$(BLUE)Updating requirements.txt...$(NC)"
	@. venv/bin/activate && pip freeze > requirements.txt
	@echo "$(GREEN)✓ requirements.txt updated$(NC)"

info: ## Show environment information
	@echo "$(BLUE)Environment Information:$(NC)"
	@echo ""
	@if [ -d "venv" ]; then \
		echo "$(GREEN)✓ Virtual environment exists$(NC)"; \
		. venv/bin/activate && python --version; \
		. venv/bin/activate && pip --version; \
	else \
		echo "$(YELLOW)✗ Virtual environment not found$(NC)"; \
		echo "  Run: make setup"; \
	fi
	@echo ""
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✓ .env file exists$(NC)"; \
	else \
		echo "$(YELLOW)✗ .env file not found$(NC)"; \
		echo "  Run: cp .env.example .env"; \
	fi
