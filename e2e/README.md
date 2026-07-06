# E2E Test Runner - Complete Guide

## Overview

The unified test runner (`run_tests.sh`) provides 4 modes for running E2E tests with full control over execution flow.

## Quick Start

```bash
# Basic usage (auto mode)
./run_tests.sh

# Manual mode (full control)
./run_tests.sh manual
```

## All Modes

### 1. Auto Mode (Default)
Runs all tests automatically without user interaction.

```bash
./run_tests.sh auto
./run_tests.sh        # Same as auto
```

**Behavior**:
- Runs all tests sequentially
- No pauses or prompts
- Reports summary at end
- Best for: CI/CD, quick validation

### 2. Interactive Mode
Pauses after each test, asks to continue.

```bash
./run_tests.sh interactive
```

**Behavior**:
- Runs test in headless mode (no browser window)
- Shows PASS/FAIL status
- Asks: "Continue to next test? (y/n/q)"
- On failure: Asks "retry/skip/quit"
  - If you choose retry: Runs with debug mode (browser visible AND stays open on failure)
  - Browser stays open so you can inspect the error
- Best for: Step-by-step debugging

### 3. Manual Mode ⭐ (Full Control)
Complete control with yes/no prompts and retry logic.

```bash
./run_tests.sh manual
```

**Behavior**:
- **Before each test**: Asks "Run this test? (y/n/q)"
  - `y` = Run the test
  - `n` = Skip this test
  - `q` = Quit test runner
  
- **On test PASS**: Moves to next test

- **On test FAIL**: Asks "What to do? (r/s/q)"
  - `r` = Retry with DEBUG MODE (browser visible AND stays open on failure - perfect for debugging!)
  - `s` = Skip and continue to next test
  - `q` = Quit test runner
  
- **After max retries**: Asks "skip and continue or quit?"

**Key Feature**: First run is headless (fast), retries use debug mode (browser stays open even on failure so you can inspect)

**Best for**: Fixing failures, debugging issues

### 4. Sequential Mode
Accumulates tests, re-runs accumulated set on failure.

```bash
./run_tests.sh sequential
```

**Behavior**:
- Runs test 1
- Then runs tests 1+2
- Then runs tests 1+2+3
- On failure: Retries accumulated set once
- Best for: Integration testing

## Parameters & Options

### Skip Seed Tests
Skip seed data tests (00-seed-*.spec.ts)

```bash
./run_tests.sh auto --no-seed
./run_tests.sh manual --no-seed
```

### Run Specific Test
Run only tests matching pattern

```bash
# Run only farm registration test
./run_tests.sh auto --test=02

# Run only marketplace tests
./run_tests.sh manual --test=marketplace

# Run specific test file
./run_tests.sh auto --test=farm-registration
```

### Custom Retry Count
Set maximum retry attempts (manual mode only)

```bash
# Allow up to 5 retries per test
./run_tests.sh manual --retries=5

# Allow up to 10 retries per test
./run_tests.sh manual --retries=10

# No retries (1 attempt only)
./run_tests.sh manual --retries=1
```

### Run with Headed Browser
Show browser window for ALL test runs (not just retries)

```bash
# Run with visible browser from the start
./run_tests.sh manual --headed

# Run specific test with visible browser
./run_tests.sh manual --test=02 --headed

# Interactive mode with visible browser
./run_tests.sh interactive --headed
```

**Note**: Without `--headed`, tests run headless first, then retries automatically use headed mode. With `--headed`, browser is visible from the start.

### Run with Debug Mode (Browser Stays Open on Failure)
Debug mode keeps the browser open when a test fails, allowing you to inspect the error and retry

```bash
# Run with debug mode (browser stays open on failure)
./run_tests.sh interactive --debug

# Run specific test with debug mode
./run_tests.sh manual --test=02 --debug

# Debug mode with retries
./run_tests.sh manual --test=02 --debug --retries=5
```

**Debug Mode Behavior**:
- Browser window opens and stays visible
- On test failure: Browser pauses and stays open
- You can inspect the page, console, network tab
- When you retry, the browser continues from where it stopped
- Perfect for debugging failing tests interactively

**Note**: Debug mode automatically enables headed mode (--headed is implied)

### Combine Options
You can combine multiple options

```bash
# Manual mode, skip seed tests, only farm tests, 5 retries
./run_tests.sh manual --no-seed --test=farm --retries=5

# Interactive mode, specific test, with browser visible
./run_tests.sh interactive --test=02 --headed

# Manual mode with debug (browser stays open on failure)
./run_tests.sh manual --test=farm --debug --retries=5

# Debug mode with specific test
./run_tests.sh interactive --test=02 --debug
```

## Manual Mode - Detailed Flow

### Example Session

```bash
$ ./run_tests.sh manual

==========================================
Unified E2E Test Runner
==========================================

Mode: manual
Log:  test-results/test-run-20260305-210000.log

Checking servers...
Backend (port 8000)... ✓
Frontend (port 3000)... ✓
✓ All servers ready

Tests to run: 8

==========================================
MANUAL MODE - Full Control
==========================================

==========================================
Test 1: 00-seed-demo-data-simple
File: tests/00-seed-demo-data-simple.spec.ts
==========================================

Options: (y)es run, (n)o skip, (q)uit [y]: 
Run this test?
Choice: y

Running test...

[Playwright output...]

✓ PASSED

==========================================
Test 2: 01-auth-flow
File: tests/01-auth-flow.spec.ts
==========================================

Options: (y)es run, (n)o skip, (q)uit [y]: 
Run this test?
Choice: y

Running test...

[Playwright output...]

✗ FAILED

Options: (r)etry, (s)kip, (q)uit [r]: 
What to do?
Choice: r

Retry 1/3

Running test...

[Playwright output...]

✓ PASSED

[... continues for all tests ...]
```

## User Input Options

### Before Running Test
- `y` / `yes` / `Y` / `YES` → Run the test
- `n` / `no` / `N` / `NO` → Skip the test
- `q` / `quit` / `Q` / `QUIT` → Exit test runner

### After Test Failure
- `r` / `retry` / `R` / `RETRY` → Retry the test
- `s` / `skip` / `S` / `SKIP` → Skip and continue
- `q` / `quit` / `Q` / `QUIT` → Exit test runner

### After Test Pass (Interactive Mode)
- `y` / `yes` → Continue to next test
- `n` / `no` → Stop test runner
- `q` / `quit` → Exit test runner

## Test Files

The runner executes tests in this order:

1. `00-seed-demo-data-simple.spec.ts` - Seed test data
2. `01-auth-flow.spec.ts` - Authentication flow
3. `02-farm-registration.spec.ts` - Farm registration ⭐ CORE
4. `03-plot-management.spec.ts` - Plot management
5. `04-ai-plot-analysis.spec.ts` - AI plot analysis
6. `05-ai-marketplace.spec.ts` - AI marketplace
7. `06-marketplace-integration.spec.ts` - Marketplace integration
8. `demo-complete-workflow.spec.ts` - Complete workflow

## Log Files

All test runs create timestamped log files:

```
test-results/test-run-YYYYMMDD-HHMMSS.log
```

### View Logs

```bash
# List all logs
ls -lt test-results/

# View latest log
tail -f test-results/test-run-*.log

# View specific log
cat test-results/test-run-20260305-210000.log

# Search logs for errors
grep -i "error" test-results/test-run-*.log
```

## Prerequisites

### 1. Start Backend Server

```bash
# Terminal 1
cd rural-farming-platform/python
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Start Frontend Server

```bash
# Terminal 2
cd rural-farming-platform/solidjs
npm run dev
```

### 3. Run Tests

```bash
# Terminal 3
cd rural-farming-platform/e2e
./run_tests.sh manual
```

## Troubleshooting

### Backend Not Running

```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend
cd rural-farming-platform/python
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Not Running

```bash
# Check if frontend is running
curl http://localhost:3000

# Start frontend
cd rural-farming-platform/solidjs
npm run dev
```

### View Detailed Test Results

```bash
# Open Playwright HTML report
npx playwright show-report

# View test results JSON
cat test-results/results.json
```

### Clean Test Results

```bash
# Remove all test results
rm -rf test-results/

# Remove Playwright reports
rm -rf playwright-report/

# Remove both
rm -rf test-results/ playwright-report/
```

## Advanced Usage

### Run Single Test File Directly

```bash
# Run specific test with Playwright
npx playwright test tests/02-farm-registration.spec.ts

# Run with UI mode
npx playwright test tests/02-farm-registration.spec.ts --ui

# Run in debug mode
npx playwright test tests/02-farm-registration.spec.ts --debug
```

### Generate Test Report

```bash
# Run tests and generate report
./run_tests.sh auto

# View report
npx playwright show-report
```

### Update Playwright Browsers

```bash
# Update browsers
npx playwright install

# Update specific browser
npx playwright install chromium
```

## Examples

### Example 1: Fix Failing Test with Debug Mode

```bash
# Run in manual mode with debug (browser stays open on failure)
./run_tests.sh manual --test=02 --debug

# When test fails:
# 1. Browser stays open - inspect the error
# 2. Check console, network tab, page state
# 3. Choose 'r' to retry - browser continues
# 4. If still fails, choose 'q' to quit
# 5. Fix the issue in code
# 6. Run again: ./run_tests.sh manual --test=02 --debug
```

### Example 2: Interactive Debug Session

```bash
# Run in interactive mode with debug
./run_tests.sh interactive --debug

# Behavior:
# - Browser opens and stays visible
# - On failure: Browser pauses, you can inspect
# - Choose retry to continue with same browser
# - Perfect for step-by-step debugging
```

### Example 3: Quick Validation

```bash
# Run all tests automatically
./run_tests.sh auto

# Or skip seed tests for faster run
./run_tests.sh auto --no-seed
```

### Example 3: Quick Validation

```bash
# Run all tests automatically
./run_tests.sh auto

# Or skip seed tests for faster run
./run_tests.sh auto --no-seed
```

### Example 4: Debug Specific Test

```bash
# Run only the failing test with debug mode
./run_tests.sh manual --test=02 --debug --retries=5

# This gives you:
# - Browser stays open on failure
# - Can inspect error in real-time
# - Up to 5 retry attempts
# - Time to fix issues between retries
```

### Example 5: Step Through Tests

```bash
# Use interactive mode to pause after each test
./run_tests.sh interactive

# Review results after each test
# Continue when ready
```

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

## Summary Output

At the end of each run, you'll see:

```
==========================================
TEST SUMMARY
==========================================

Total Tests:  8
Passed:       7
Failed:       1
Skipped:      0

Pass Rate:    87%

Log file: test-results/test-run-20260305-210000.log
```

## Tips

1. **Use debug mode** when fixing failures - browser stays open so you can see exactly what's wrong
2. **Use manual mode** for full control with yes/no prompts
3. **Use auto mode** for CI/CD or quick validation
4. **Use interactive mode** for step-by-step debugging
5. **Use sequential mode** to ensure tests work together
6. **Always check logs** when tests fail
7. **Use --test option** to focus on specific tests
8. **Increase --retries** for flaky tests
9. **Use --debug with --retries** for interactive debugging with multiple attempts

## Getting Help

- View this README: `cat README.md`
- View quick start: `cat QUICK_START.md`
- View consolidation guide: `cat TEST_RUNNER_CONSOLIDATION.md`
- View test runner: `cat run_tests.sh`

## Support

For issues or questions:
1. Check the log files in `test-results/`
2. Review Playwright report: `npx playwright show-report`
3. Check server logs (backend/frontend)
4. Review test file source code in `tests/`

---

**Quick Reference**: 
- `./run_tests.sh interactive` - Run headless, retry with debug mode (browser stays open on failure)
- `./run_tests.sh manual` - Full control, retries use debug mode (browser stays open for inspection)
- `./run_tests.sh manual --headed` - Browser visible from the start
- `./run_tests.sh manual --debug` - Debug mode from the start (browser stays open on all failures)
