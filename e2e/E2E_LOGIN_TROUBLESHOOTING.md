# E2E Login Troubleshooting Guide

## Current Error

```
❌ Login failed - still on signin page
Current URL: http://localhost:3000/auth/signin
Error: Login failed - check credentials or backend connection
```

## Root Cause

The test user `testfarmer` doesn't exist in the database yet. The E2E tests require an existing user to log in with.

## Solution: Create Test User

You have 3 options to create the test user:

### Option 1: Create via UI (Recommended - Most Reliable)

1. **Start both servers**:
   ```bash
   # Terminal 1: Backend
   cd rural-farming-platform/python
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Frontend (in new terminal)
   cd rural-farming-platform/solidjs
   npm run dev
   ```

2. **Open browser and create user**:
   - Go to: http://localhost:3000/auth/signup
   - Fill in the form:
     - Username: `testfarmer`
     - Full Name: `Test Farmer`
     - Email: `test.farmer@example.com`
     - Phone: `+919876543210`
     - Password: `TestPass123!`
     - Confirm Password: `TestPass123!`
   - Click "Sign Up"

3. **Verify login works**:
   - Go to: http://localhost:3000/auth/signin
   - Login with:
     - Username: `testfarmer`
     - Password: `TestPass123!`
   - Should redirect to dashboard

4. **Run E2E tests**:
   ```bash
   cd rural-farming-platform/e2e
   npm test
   ```

### Option 2: Create via API (Quick)

```bash
# Make sure backend is running first
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "password": "TestPass123!",
    "email": "test.farmer@example.com",
    "phone_number": "+919876543210",
    "full_name": "Test Farmer",
    "user_type": "farmer"
  }'
```

Expected response:
```json
{
  "message": "User registered successfully",
  "username": "testfarmer",
  "requires_confirmation": false
}
```

### Option 3: Create via Database Script

Create a script to insert the user directly:

```bash
cd rural-farming-platform/python
python3 << 'EOF'
from app.core.database import SessionLocal
from app.orm.user import User
from app.core.security import get_password_hash
import uuid

db = SessionLocal()
try:
    # Check if user exists
    existing = db.query(User).filter(User.username == "testfarmer").first()
    if existing:
        print("User already exists")
    else:
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            username="testfarmer",
            email="test.farmer@example.com",
            full_name="Test Farmer",
            phone_number="+919876543210",
            hashed_password=get_password_hash("TestPass123!"),
            user_type="farmer",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        print("User created successfully")
finally:
    db.close()
EOF
```

## Pre-Flight Checklist

Before running E2E tests, verify:

### 1. Backend is Running

```bash
# Check if backend is responding
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"..."}
```

If this fails:
```bash
cd rural-farming-platform/python
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend is Running

```bash
# Check if frontend is responding
curl http://localhost:3000

# Should return HTML
```

If this fails:
```bash
cd rural-farming-platform/solidjs
npm run dev
```

### 3. Database is Running

```bash
# Check PostgreSQL
psql -U postgres -d cropsense_dev -c "SELECT 1;"

# Expected: Returns 1
```

If this fails, start PostgreSQL:
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

### 4. Test User Exists

```bash
# Try to login via API
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username": "testfarmer", "password": "TestPass123!"}'
```

Expected response (success):
```json
{
  "access_token": "eyJ...",
  "id_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

Error response (user doesn't exist):
```json
{
  "detail": "Invalid credentials"
}
```

### 5. Frontend .env is Correct

```bash
cat rural-farming-platform/solidjs/.env
```

Should show:
```
VITE_API_URL=http://localhost:8000/api/v1
```

If wrong, fix it:
```bash
echo "VITE_API_URL=http://localhost:8000/api/v1" > rural-farming-platform/solidjs/.env
```

Then restart frontend:
```bash
cd rural-farming-platform/solidjs
pkill -f vite
npm run dev
```

## Common Issues

### Issue 1: "Connection refused" on port 8000

**Cause**: Backend not running

**Fix**:
```bash
cd rural-farming-platform/python
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 2: "Connection refused" on port 3000

**Cause**: Frontend not running

**Fix**:
```bash
cd rural-farming-platform/solidjs
npm run dev
```

### Issue 3: "Invalid credentials"

**Cause**: Test user doesn't exist or wrong password

**Fix**: Create test user using Option 1, 2, or 3 above

### Issue 4: "Database connection failed"

**Cause**: PostgreSQL not running or wrong credentials

**Fix**:
```bash
# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Check connection
psql -U postgres -d cropsense_dev -c "SELECT 1;"
```

### Issue 5: Login form not submitting

**Cause**: Frontend can't reach backend API

**Fix**:
1. Check `.env` file has correct API URL
2. Restart frontend after changing `.env`
3. Check browser console for errors
4. Verify CORS is configured correctly in backend

### Issue 6: "HTML reporter output folder clashes"

**Cause**: Playwright config issue (minor, doesn't affect tests)

**Fix**: Update `playwright.config.ts`:
```typescript
reporter: [
  ['html', { outputFolder: 'playwright-report' }],  // Changed from test-results/html-report
  ['list']
],
```

## Step-by-Step Test Run

Follow these steps in order:

```bash
# Step 1: Start backend
cd rural-farming-platform/python
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Step 2: Wait for backend to start
sleep 5

# Step 3: Verify backend health
curl http://localhost:8000/health

# Step 4: Start frontend (in new terminal)
cd rural-farming-platform/solidjs
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Step 5: Wait for frontend to start
sleep 5

# Step 6: Create test user (if doesn't exist)
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "password": "TestPass123!",
    "email": "test.farmer@example.com",
    "phone_number": "+919876543210",
    "full_name": "Test Farmer",
    "user_type": "farmer"
  }'

# Step 7: Verify login works
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username": "testfarmer", "password": "TestPass123!"}'

# Step 8: Run E2E tests
cd rural-farming-platform/e2e
npm test

# Cleanup (when done)
kill $BACKEND_PID $FRONTEND_PID
```

## Quick Start Script

Save this as `rural-farming-platform/e2e/setup-and-test.sh`:

```bash
#!/bin/bash

set -e

echo "🚀 Starting E2E Test Setup..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running on port 8000"
    echo "Start it with: cd rural-farming-platform/python && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✅ Backend is running"

# Check if frontend is running
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend not running on port 3000"
    echo "Start it with: cd rural-farming-platform/solidjs && npm run dev"
    exit 1
fi

echo "✅ Frontend is running"

# Create test user (ignore if already exists)
echo "👤 Creating test user..."
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "password": "TestPass123!",
    "email": "test.farmer@example.com",
    "phone_number": "+919876543210",
    "full_name": "Test Farmer",
    "user_type": "farmer"
  }' 2>/dev/null || echo "User may already exist"

# Verify login
echo "🔐 Verifying login..."
if curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username": "testfarmer", "password": "TestPass123!"}' \
  -s | grep -q "access_token"; then
    echo "✅ Login successful"
else
    echo "❌ Login failed"
    exit 1
fi

# Run tests
echo "🧪 Running E2E tests..."
npm test
```

Make it executable:
```bash
chmod +x rural-farming-platform/e2e/setup-and-test.sh
```

Run it:
```bash
cd rural-farming-platform/e2e
./setup-and-test.sh
```

## Next Steps

Once the test user is created and login works:

1. Run all E2E tests:
   ```bash
   cd rural-farming-platform/e2e
   npm test
   ```

2. Run specific test:
   ```bash
   npm test tests/01-auth-flow.spec.ts
   ```

3. Run in headed mode (see browser):
   ```bash
   npm run test:headed
   ```

4. View test report:
   ```bash
   npm run report
   ```

## Status

⚠️ **ACTION REQUIRED**: Create test user before running E2E tests

Follow Option 1 (UI) or Option 2 (API) above to create the test user, then run tests.
