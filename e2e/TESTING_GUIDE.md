# E2E Testing Guide

## Quick Start

### Test Execution Order (Core Features First)

**Recommended test order:**
1. Auth Flow (01-auth-flow.spec.ts) - ✅ Already passing
2. Farm Registration (02-farm-registration.spec.ts) - Fix first (CORE FEATURE)
3. AI Crop Planning (03-ai-crop-planning.spec.ts) - Route redirect
4. AI Plot Analysis (04-ai-plot-analysis.spec.ts) - Stub pages
5. AI Marketplace (05-ai-marketplace.spec.ts) - Empty state handling
6. Marketplace Integration (06-marketplace-integration.spec.ts) - ✅ Already passing
7. Complete Workflow (demo-complete-workflow.spec.ts) - Integration test

**Note:** Demo data seeding tests (00-seed-*) are excluded from main test runs as they are utility tests for creating test data, not feature validation tests. Run them manually if needed.

### 1. Start Servers

**Terminal 1 - Backend:**
```bash
cd rural-farming-platform/python
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd rural-farming-platform/solidjs
npm run dev
```

### 2. Run Health Check

```bash
cd rural-farming-platform
./check_system_health.sh
```

This will verify:
- Backend is running (port 8000)
- Frontend is running (port 3000)
- Database is accessible
- Test user exists
- API endpoints are responding

### 3. Run Interactive Tests

```bash
cd rural-farming-platform/e2e
./run_tests.sh interactive
```

**Features:**
- Runs tests one at a time in recommended order (Core Features First)
- Stops at each failure
- Excludes demo data seeding tests (00-seed-*) - utility tests only
- Gives you options:
  1. View detailed error
  2. Retry the test
  3. Skip and continue
  4. Exit

**Workflow:**
1. Test runs
2. If it fails, script stops
3. You fix the issue
4. Choose "Retry" to run again
5. Continue to next test

## Test Files

### Core Feature Tests (Run in Order)
- `01-auth-flow.spec.ts` - User authentication ✅
- `02-farm-registration.spec.ts` - Farm registration (FIX FIRST)
- `03-ai-crop-planning.spec.ts` - AI crop planning (route redirect)
- `04-ai-plot-analysis.spec.ts` - AI plot analysis (stub pages)
- `05-ai-marketplace.spec.ts` - Marketplace features
- `06-marketplace-integration.spec.ts` - Marketplace integration ✅
- `demo-complete-workflow.spec.ts` - Complete user workflow

### Utility Tests (Excluded from Main Runs)
- `00-seed-demo-data-simple.spec.ts` - Simple demo data (utility)
- `00-seed-demo-data-adaptive.spec.ts` - Adaptive demo data (utility)
- `00-seed-demo-data.spec.ts` - Full demo data (utility)

**Note:** Demo data seeding tests are utility tests for creating test data, not feature validation tests. They are excluded from the main test runs but can be run manually if needed.

## Common Issues

### Backend Not Running
```bash
cd rural-farming-platform/python
uvicorn app.main:app --reload
```

### Frontend Not Running
```bash
cd rural-farming-platform/solidjs
npm run dev
```

### Database Issues
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@14

# Connect to database
psql -U puneetsharma -d cropsense_dev
```

### Test User Missing
The test user will be created automatically during tests:
- Username: `puneetxp`
- Email: `puneetsharma9@hotmail.com`
- Password: `Pa$$w0rd!`

### Frontend Cache Issues
```bash
cd rural-farming-platform/solidjs
./HARD_RESTART.sh
```

## Manual Testing

### Test Routes
- Home: http://localhost:3000
- Sign In: http://localhost:3000/signin
- Dashboard: http://localhost:3000/dashboard
- Farm Register: http://localhost:3000/farm/register
- Crop Planning: http://localhost:3000/crops/plan (redirects to /strategy/request)
- Plot Analysis: http://localhost:3000/plots/analyze
- Plot Compare: http://localhost:3000/plots/compare
- Marketplace: http://localhost:3000/marketplace

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Sign in
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username":"puneetxp","password":"Pa$$w0rd!"}'

# Get farms (requires auth token)
curl http://localhost:8000/api/v1/farms/my-farms \
  -H "Authorization: Bearer <token>"
```

## Viewing Test Reports

### HTML Report
```bash
cd rural-farming-platform/e2e
npx playwright show-report
```

### Screenshots
Failed tests automatically capture screenshots in:
```
rural-farming-platform/e2e/test-results/
```

### Videos
Test videos are saved in:
```
rural-farming-platform/e2e/test-results/
```

## Running Specific Tests

### Single Test File
```bash
npx playwright test tests/01-auth-flow.spec.ts
```

### Single Test Case
```bash
npx playwright test tests/01-auth-flow.spec.ts -g "should sign in"
```

### Debug Mode
```bash
npx playwright test tests/01-auth-flow.spec.ts --debug
```

### Headed Mode (See Browser)
```bash
npx playwright test tests/01-auth-flow.spec.ts --headed
```

## Test Credentials

### Test User
- Username: `puneetxp`
- Email: `puneetsharma9@hotmail.com`
- Password: `Pa$$w0rd!`
- Phone: `+919876543210`

Located in: `rural-farming-platform/e2e/.auth/test-user.json`

## Success Criteria

From `.kiro/specs/e2e-test-failures-fix/tasks.md`:

- ✅ All core feature tests pass (auth, farm registration, AI features, marketplace)
- ✅ Farm registration success message is visible and reliable
- ✅ Tests handle empty marketplace state gracefully
- ✅ AI feature routes are accessible (redirected or stubbed)
- ✅ No new console errors or warnings
- ✅ Test execution follows recommended order: Auth → Farm → AI Features → Marketplace → Integration
- ✅ Demo data seeding tests (00-seed-*) excluded from main runs (utility tests only)

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Playwright Not Installed
```bash
cd rural-farming-platform/e2e
npm install
npx playwright install
```

### Database Connection Failed
```bash
# Check connection
psql -U puneetsharma -d cropsense_dev -c "SELECT 1"

# Recreate database if needed
dropdb cropsense_dev
createdb cropsense_dev
```

## Next Steps

After all tests pass:
1. Review test output for warnings
2. Check browser console for errors
3. Verify manual testing works
4. Update documentation
5. Create summary report

## Support

For issues or questions:
1. Check the test output and screenshots
2. Review the spec: `.kiro/specs/e2e-test-failures-fix/`
3. Check the tasks: `.kiro/specs/e2e-test-failures-fix/tasks.md`
