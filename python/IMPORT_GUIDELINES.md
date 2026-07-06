# Import Guidelines for Rural Farming Platform

## Overview

This document provides guidelines for correctly importing models in the Rural Farming Platform codebase to prevent import errors and maintain code consistency.

## Two Model Systems

The codebase has **two separate model systems** that serve different purposes:

### 1. ORM Models (`app.orm.*`)
- **Purpose**: Database operations with SQLAlchemy
- **Location**: `app/orm/`
- **Usage**: For database queries, relationships, and persistence
- **Examples**: 
  - `from app.orm.user import User`
  - `from app.orm.farm import Farm`
  - `from app.orm.farm_plot import FarmPlot`
  - `from app.orm.marketplace_listing import MarketplaceListing`
  - `from app.orm.buyer_interest import BuyerInterest`
  - `from app.orm.crop import Crop`
  - `from app.orm.crop_market_data import CropMarketData`

### 2. Pydantic Models (`app.models.*` and `app.schemas.*`)
- **Purpose**: API request/response validation and serialization
- **Location**: `app/models/` and `app/schemas/`
- **Usage**: For FastAPI endpoint type hints and data validation
- **Examples**:
  - `from app.schemas.farm import FarmCreate, FarmResponse`
  - `from app.schemas.user import UserCreate, UserResponse`
  - `from app.schemas.crop import CropRecommendationRequest`

## Import Rules

### ✅ CORRECT: Use `app.orm.*` for Database Operations

When working with database queries, relationships, or any SQLAlchemy operations:

```python
# API endpoints
from app.orm.user import User
from app.orm.farm import Farm
from app.orm.farm_plot import FarmPlot

# Services
from app.orm.marketplace_listing import MarketplaceListing
from app.orm.buyer_interest import BuyerInterest
from app.orm.crop import Crop
```

### ✅ CORRECT: Use `app.schemas.*` for API Validation

When defining FastAPI endpoint parameters and responses:

```python
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse
from app.schemas.user import UserCreate, UserResponse
from app.schemas.crop import CropRecommendationRequest, CropRecommendationResponse
```

### ❌ INCORRECT: Don't Import ORM Models from `app.models.*`

```python
# ❌ WRONG - This will cause ImportError
from app.models.user import User
from app.models.farm import Farm, FarmPlot

# ✅ CORRECT - Use app.orm instead
from app.orm.user import User
from app.orm.farm import Farm
from app.orm.farm_plot import FarmPlot
```

## Common Import Patterns

### API Endpoints (`app/*.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_farmer

# ORM models for database operations
from app.orm.user import User
from app.orm.farm import Farm
from app.orm.farm_plot import FarmPlot

# Pydantic schemas for request/response validation
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse
from app.schemas.auth import MessageResponse
```

### Services (`app/services/*.py`)

```python
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

# ORM models for database operations
from app.orm.marketplace_listing import MarketplaceListing
from app.orm.buyer_interest import BuyerInterest
from app.orm.crop import Crop
from app.orm.farm import Farm
from app.orm.user import User

# Other services
from app.services.bedrock_service import bedrock_service
```

### Authentication (`app/core/auth.py`)

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.orm.user import User  # ORM model for database queries
```

## File Organization

```
app/
├── orm/                    # SQLAlchemy ORM models (database)
│   ├── user.py
│   ├── farm.py
│   ├── farm_plot.py
│   ├── marketplace_listing.py
│   ├── buyer_interest.py
│   └── crop.py
│
├── models/                 # Legacy Pydantic models (being phased out)
│   └── soil_health.py
│
├── schemas/                # Pydantic schemas (API validation)
│   ├── user.py
│   ├── farm.py
│   ├── crop.py
│   └── auth.py
│
├──                  # API endpoints
│   ├── farms.py
│   ├── crops.py
│   └── marketplace.py
│
└── services/               # Business logic services
    ├── bedrock_service.py
    ├── marketplace_service.py
    └── yield_profit_service.py
```

## Why This Matters

### The Problem
The original error occurred because code was trying to import ORM models from `app.models.*`:

```python
from app.models.farm import Farm, FarmPlot  # ❌ ImportError!
```

But these models actually exist in `app.orm.*`:

```python
from app.orm.farm import Farm              # ✅ Correct
from app.orm.farm_plot import FarmPlot     # ✅ Correct
```

### The Solution
Always use `app.orm.*` for database models and `app.schemas.*` for API validation models.

## Quick Reference

| Use Case | Import From | Example |
|----------|-------------|---------|
| Database queries | `app.orm.*` | `from app.orm.user import User` |
| SQLAlchemy relationships | `app.orm.*` | `from app.orm.farm import Farm` |
| API request validation | `app.schemas.*` | `from app.schemas.farm import FarmCreate` |
| API response models | `app.schemas.*` | `from app.schemas.farm import FarmResponse` |
| Service business logic | `app.orm.*` | `from app.orm.marketplace_listing import MarketplaceListing` |

## Verification

To verify your imports are correct, run:

```bash
# Check for incorrect imports
grep -r "from app.models.user import" app/api/ app/services/ app/core/

# Should return no results if all imports are fixed
```

## Pre-commit Hook (Optional)

Add this to `.git/hooks/pre-commit` to catch import errors before committing:

```bash
#!/bin/bash

# Check for incorrect ORM model imports
if git diff --cached --name-only | grep -q '\.py$'; then
    if git diff --cached | grep -E "from app\.models\.(user|farm|farm_plot|marketplace_listing|buyer_interest|crop) import"; then
        echo "❌ Error: Found incorrect ORM model imports from app.models.*"
        echo "   Use app.orm.* instead for database models"
        exit 1
    fi
fi

exit 0
```

## Summary

- **ORM Models** (`app.orm.*`): Use for database operations
- **Pydantic Schemas** (`app.schemas.*`): Use for API validation
- **Never** import ORM models from `app.models.*`
- Always import each model separately (e.g., `from app.orm.farm import Farm` and `from app.orm.farm_plot import FarmPlot`)

Following these guidelines will prevent import errors and maintain code consistency across the platform.


## Additional Import Fixes Applied

### Code Generation Issues Fixed

During the import fix process, several code generation issues were discovered and fixed:

1. **ModelService Import Error**: All auto-generated service files had incorrect import `from the_python import ModelService`
   - **Fixed**: Changed to `from app.core.model_service import ModelService`
   - **Files affected**: 13 service files in `app/services/`

2. **Missing ORM Models**: Several ORM models were referenced but didn't exist
   - **Created stub models** in `app/orm/`:
     - `historical_yield.py`
     - `crop_profitability.py`
     - `seasonal_trend.py`
     - `opportunity_cost.py`
   - **Note**: These are temporary stubs and need proper implementation with full schemas

3. **Missing Pydantic Models**: Soil health models were missing
   - **Created**: `app/models/soil_health.py` with stub classes:
     - `SoilTest`
     - `FertilizerApplication`
     - `SoilAmendment`

4. **Missing Dependency**: `python-multipart` was required but not installed
   - **Fixed**: Installed via `pip install python-multipart`

### Verification

The application now starts successfully:

```bash
cd rural-farming-platform/python
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server runs on: `http://0.0.0.0:8000`

### Known Issues

1. **Database Connection**: Database connection check fails - needs proper configuration
2. **Middleware Warnings**: CloudWatch monitoring and rate limiter middleware cannot be added after startup
3. **Pydantic Warnings**: Some models use deprecated config keys (`orm_mode` → `from_attributes`, `schema_extra` → `json_schema_extra`)
4. **Stub Models**: Several ORM and Pydantic models are stubs and need full implementation

### Next Steps

1. Implement full schemas for stub ORM models
2. Configure database connection properly
3. Fix middleware initialization order
4. Update Pydantic model configs to V2 syntax
5. Implement proper CRUD operations in ModelService base class

## Summary

All critical import errors have been fixed. The application can now start successfully, though some features may not work until stub models are properly implemented and database is configured.
