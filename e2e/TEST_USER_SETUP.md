# E2E Test User Setup Guide

## Overview

The E2E tests use an existing user account instead of creating new users for each test run. This approach:
- ✅ Faster test execution (no signup overhead)
- ✅ Consistent test data
- ✅ Reusable session across all tests
- ✅ No database pollution with test users

## Default Test User

The default test user credentials are configured in `global-setup.ts`:

```typescript
const testUser = {
  username: 'testfarmer',
  password: 'TestPass123!',
  email: 'test.farmer@example.com',
  full_name: 'Test Farmer',
  phone: '+919876543210',
};
```

## Setup Instructions

### Option 1: Create Test User via UI (Recommended)

1. **Start the application**:
   ```bash
   # Terminal 1: Backend
   cd rural-farming-platform/python
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Frontend
   cd rural-farming-platform/solidjs
   npm run dev
   ```

2. **Create test user**:
   - Open http://localhost:3000/auth/signup
   - Fill in the form with test user credentials:
     - Username: `testfarmer`
     - Full Name: `Test Farmer`
     - Email: `test.farmer@example.com`
     - Phone: `+919876543210`
     - Password: `TestPass123!`
   - Submit the form

3. **Verify login works**:
   - Go to http://localhost:3000/auth/signin
   - Login with:
     - Username: `testfarmer`
     - Password: `TestPass123!`
   - Should successfully login

### Option 2: Create Test User via API

```bash
# Create test user via API
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

# Verify login works
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "password": "TestPass123!"
  }'
```

### Option 3: Use Different Test User

If you want to use a different test user, update `global-setup.ts`:

```typescript
const testUser = {
  username: 'your_username',      // Change this
  password: 'YourPassword123!',   // Change this
  email: 'your.email@example.com',
  full_name: 'Your Name',
  phone: '+919876543210',
};
```

## Test User Requirements

The test user must:
- ✅ Exist in the database
- ✅ Have valid Firebase/GCP credentials
- ✅ Be able to login successfully
- ✅ Have access to all features being tested

## Running Tests

Once the test user is set up:

```bash
cd rural-farming-platform/e2e

# Run all tests (will use existing session)
npm test

# Run specific test
npm test tests/02-farm-registration.spec.ts

# Run in headed mode (see browser)
npm run test:headed
```

## Session Management

### How It Works

1. **Global Setup** (runs once):
   - Logs in with test user credentials
   - Saves authenticated session to `.auth/user.json`
   - Saves credentials to `.auth/test-user.json`

2. **All Tests** (use saved session):
   - Load session from `.auth/user.json`
   - No login required
   - All API calls use authenticated session

### Reset Session

If you need to create a new session:

```bash
# Delete auth directory
rm -rf .auth/

# Run tests (will create new session)
npm test
```

## Troubleshooting

### Test User Doesn't Exist

**Error**: `Login failed - still on signin page`

**Solution**: Create the test user using Option 1 or 2 above

### Wrong Credentials

**Error**: `Login failed - check credentials`

**Solution**: 
1. Verify credentials in `global-setup.ts` match your test user
2. Try logging in manually at http://localhost:3000/auth/signin
3. If manual login fails, reset password or create new user

### Backend Not Running

**Error**: `Failed to connect to localhost port 8000`

**Solution**:
```bash
cd rural-farming-platform/python
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Not Running

**Error**: `Failed to connect to localhost port 3000`

**Solution**:
```bash
cd rural-farming-platform/solidjs
npm run dev
```

### Session Expired

**Error**: Tests fail with 401 Unauthorized

**Solution**:
```bash
# Delete old session
rm -rf .auth/

# Run tests to create new session
npm test
```

## Test Data Management

### Farm Data

The test user should have:
- At least one farm registered
- Farm with plots for testing
- Sample crop data

### Creating Test Data

You can create test data:

1. **Via UI**: Login and create farms/plots manually
2. **Via API**: Use API endpoints to create test data
3. **Via Database**: Insert test data directly into database

### Cleaning Test Data

To reset test data:

```bash
# Option 1: Delete specific test user data
# (requires database access)

# Option 2: Reset entire database
cd rural-farming-platform/python
./scripts/reset_database.sh

# Then recreate test user
```

## Multiple Test Users

If you need multiple test users for different test scenarios:

1. **Create multiple users**:
   ```typescript
   const testUsers = {
     farmer: { username: 'testfarmer', password: 'Pass123!' },
     buyer: { username: 'testbuyer', password: 'Pass123!' },
     admin: { username: 'testadmin', password: 'Pass123!' },
   };
   ```

2. **Switch users in tests**:
   ```typescript
   // In specific test file
   test.use({ storageState: '.auth/buyer.json' });
   ```

3. **Create separate sessions**:
   - Modify `global-setup.ts` to create multiple sessions
   - Save each to different file (`.auth/farmer.json`, `.auth/buyer.json`)

## Security Notes

- ⚠️ Never commit `.auth/` directory to git (already in `.gitignore`)
- ⚠️ Use test credentials only (not production credentials)
- ⚠️ Test user should have limited permissions
- ⚠️ Regularly rotate test user passwords

## Environment-Specific Users

For different environments:

```typescript
// global-setup.ts
const env = process.env.TEST_ENV || 'local';

const testUsers = {
  local: { username: 'testfarmer', password: 'TestPass123!' },
  staging: { username: 'staging_test', password: 'StagingPass123!' },
  production: { username: 'prod_test', password: 'ProdPass123!' },
};

const testUser = testUsers[env];
```

Run with:
```bash
TEST_ENV=staging npm test
```

## Related Files

- `global-setup.ts` - Session creation logic
- `playwright.config.ts` - Test configuration
- `.auth/user.json` - Saved session (generated)
- `.auth/test-user.json` - Test credentials (generated)
- `README.md` - General E2E testing guide

## Status

✅ **READY** - E2E tests now use existing login session for faster, more reliable testing.
