#!/bin/bash

################################################################################
# Unified E2E Test Runner
# Consolidates all test running functionality into one script
#
# Modes:
#   auto       - Run all tests automatically (default)
#   interactive - Stop at each test, ask to continue
#   manual     - Full control: ask before each test, retry on failure
#   sequential - Run tests one by one, accumulate on success
#
# Usage:
#   ./run_tests.sh [mode] [options]
#
# Examples:
#   ./run_tests.sh                    # Auto mode (run all)
#   ./run_tests.sh interactive        # Interactive mode
#   ./run_tests.sh manual             # Manual control mode
#   ./run_tests.sh sequential         # Sequential accumulation mode
#   ./run_tests.sh auto --no-seed     # Skip seed data tests
#   ./run_tests.sh auto --test=02     # Run specific test
#   ./run_tests.sh manual --headed    # Show browser window
#   ./run_tests.sh manual --debug     # Browser stays open on failure
#   ./run_tests.sh auto --clear-db    # Clear DB (except users) before testing
################################################################################

set +e  # Don't exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default mode
MODE="${1:-auto}"
shift || true

# Options
SKIP_SEED=false
SPECIFIC_TEST=""
MAX_RETRIES=3
HEADED=false
DEBUG_MODE=false
CLEAR_DB=false

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-seed)
            SKIP_SEED=true
            shift
            ;;
        --test=*)
            SPECIFIC_TEST="${1#*=}"
            shift
            ;;
        --retries=*)
            MAX_RETRIES="${1#*=}"
            shift
            ;;
        --headed)
            HEADED=true
            shift
            ;;
        --debug)
            DEBUG_MODE=true
            HEADED=true  # Debug mode implies headed
            shift
            ;;
        --clear-db)
            CLEAR_DB=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            shift
            ;;
    esac
done

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0
ACCUMULATED_TESTS=()

# Log file
LOG_DIR="test-results"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/test-run-$(date +%Y%m%d-%H%M%S).log"

# Test files in order
ALL_TESTS=(
    "tests/00-seed-demo-data-simple.spec.ts"
    "tests/01-auth-flow.spec.ts"
    "tests/02-farm-registration.spec.ts"
    "tests/03-plot-management.spec.ts"
    "tests/04-ai-plot-analysis.spec.ts"
    "tests/05-ai-marketplace.spec.ts"
    "tests/06-marketplace-integration.spec.ts"
    "tests/demo-complete-workflow.spec.ts"
)

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}==========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}==========================================${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

print_test_header() {
    local test_num=$1
    local test_name=$2
    local test_file=$3
    
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}==========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}Test ${test_num}: ${test_name}${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}File: ${test_file}${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}==========================================${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

ask_user() {
    local prompt="$1"
    local default="${2:-y}"
    
    while true; do
        echo -e "${YELLOW}${prompt}${NC}"
        read -p "Choice: " choice
        choice=${choice:-$default}
        
        case "$choice" in
            y|Y|yes|Yes|YES) return 0 ;;
            n|N|no|No|NO) return 1 ;;
            s|S|skip|Skip|SKIP) return 2 ;;
            q|Q|quit|Quit|QUIT) return 3 ;;
            r|R|retry|Retry|RETRY) return 4 ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
    done
}

check_servers() {
    echo "Checking servers..." | tee -a "$LOG_FILE"
    
    # Check backend
    echo -n "Backend (port 8000)... " | tee -a "$LOG_FILE"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}✗${NC}" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo -e "${RED}Backend not running!${NC}" | tee -a "$LOG_FILE"
        echo "Start: cd cropsense-ai/python && uvicorn app.main:app --reload" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Check frontend
    echo -n "Frontend (port 3000)... " | tee -a "$LOG_FILE"
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}✗${NC}" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo -e "${RED}Frontend not running!${NC}" | tee -a "$LOG_FILE"
        echo "Start: cd cropsense-ai/solidjs && npm run dev" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo -e "${GREEN}✓ All servers ready${NC}" | tee -a "$LOG_FILE"
    return 0
}

clear_database() {
    if [ "$CLEAR_DB" = true ]; then
        echo "" | tee -a "$LOG_FILE"
        echo "🧹 Clearing database (preserving users)..." | tee -a "$LOG_FILE"
        
        # Execute the python script from the python directory to ensure correct imports
        (cd ../python && PYTHONPATH=. venv/bin/python scripts/clear_db.py) 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            echo -e "${GREEN}✓ Database cleared successfully${NC}" | tee -a "$LOG_FILE"
        else
            echo -e "${RED}✗ Failed to clear database${NC}" | tee -a "$LOG_FILE"
            return 1
        fi
        echo "" | tee -a "$LOG_FILE"
    fi
    return 0
}

run_playwright_test() {
    local test_files=("$@")
    local playwright_args=("${test_files[@]}" --reporter=list)
    
    # Add debug mode if requested (keeps browser open on failure)
    if [ "$DEBUG_MODE" = true ]; then
        playwright_args+=(--headed)
        playwright_args+=(--debug)
    # Add headed mode if requested (just shows browser)
    elif [ "$HEADED" = true ]; then
        playwright_args+=(--headed)
    fi
    
    npx playwright test "${playwright_args[@]}" 2>&1 | tee -a "$LOG_FILE"
    return ${PIPESTATUS[0]}
}

print_summary() {
    echo "" | tee -a "$LOG_FILE"
    print_header "TEST SUMMARY"
    echo "Total Tests:  $TOTAL_TESTS" | tee -a "$LOG_FILE"
    echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}" | tee -a "$LOG_FILE"
    echo -e "${RED}Failed:       $FAILED_TESTS${NC}" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}Skipped:      $SKIPPED_TESTS${NC}" | tee -a "$LOG_FILE"
    
    if [ $TOTAL_TESTS -gt 0 ]; then
        local pass_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
        echo "Pass Rate:    ${pass_rate}%" | tee -a "$LOG_FILE"
    fi
    
    echo "" | tee -a "$LOG_FILE"
    echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

################################################################################
# Mode: Auto (Run all tests automatically)
################################################################################

mode_auto() {
    print_header "AUTO MODE - Running All Tests"
    
    local test_num=0
    for test_file in "${TESTS_TO_RUN[@]}"; do
        local test_name=$(basename "$test_file" .spec.ts)
        test_num=$((test_num + 1))
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        
        print_test_header "$test_num" "$test_name" "$test_file"
        
        if run_playwright_test "$test_file"; then
            echo -e "${GREEN}✓ PASSED${NC}" | tee -a "$LOG_FILE"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}✗ FAILED${NC}" | tee -a "$LOG_FILE"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    done
}

################################################################################
# Mode: Interactive (Stop at each test)
################################################################################

mode_interactive() {
    print_header "INTERACTIVE MODE - Pause Between Tests"
    
    local test_num=0
    for test_file in "${TESTS_TO_RUN[@]}"; do
        local test_name=$(basename "$test_file" .spec.ts)
        test_num=$((test_num + 1))
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        
        print_test_header "$test_num" "$test_name" "$test_file"
        
        if run_playwright_test "$test_file"; then
            echo -e "${GREEN}✓ PASSED${NC}" | tee -a "$LOG_FILE"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            
            echo ""
            ask_user "Continue to next test? (y/n/q) [y]: " "y"
            local choice=$?
            if [ $choice -eq 3 ]; then
                echo "Stopped by user" | tee -a "$LOG_FILE"
                break
            fi
        else
            echo -e "${RED}✗ FAILED${NC}" | tee -a "$LOG_FILE"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            
            echo ""
            echo "Options: (r)etry, (s)kip, (q)uit [r]: "
            ask_user "What to do?" "r"
            local choice=$?
            
            case $choice in
                0|4) # Retry
                    echo "Retrying with debug mode (browser stays open on failure)..." | tee -a "$LOG_FILE"
                    
                    # Enable debug mode for retry (browser stays open)
                    local original_headed=$HEADED
                    local original_debug=$DEBUG_MODE
                    HEADED=true
                    DEBUG_MODE=true
                    
                    # Retry with debug mode
                    if run_playwright_test "$test_file"; then
                        echo -e "${GREEN}✓ Retry PASSED${NC}" | tee -a "$LOG_FILE"
                        PASSED_TESTS=$((PASSED_TESTS + 1))
                    else
                        echo -e "${RED}✗ Retry FAILED - Browser left open for inspection${NC}" | tee -a "$LOG_FILE"
                        FAILED_TESTS=$((FAILED_TESTS + 1))
                    fi
                    
                    # Restore original settings
                    HEADED=$original_headed
                    DEBUG_MODE=$original_debug
                    ;;
                2) # Skip
                    echo "Skipping..." | tee -a "$LOG_FILE"
                    ;;
                3) # Quit
                    echo "Stopped by user" | tee -a "$LOG_FILE"
                    break
                    ;;
            esac
        fi
    done
}

################################################################################
# Mode: Manual (Full control with retries)
################################################################################

mode_manual() {
    print_header "MANUAL MODE - Full Control"
    
    local test_num=0
    for test_file in "${TESTS_TO_RUN[@]}"; do
        local test_name=$(basename "$test_file" .spec.ts)
        test_num=$((test_num + 1))
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        
        print_test_header "$test_num" "$test_name" "$test_file"
        
        # Ask before running
        echo "Options: (y)es run, (n)o skip, (q)uit [y]: "
        ask_user "Run this test?" "y"
        local run_choice=$?
        
        if [ $run_choice -eq 3 ]; then
            echo "Stopped by user" | tee -a "$LOG_FILE"
            break
        elif [ $run_choice -eq 1 ] || [ $run_choice -eq 2 ]; then
            echo -e "${YELLOW}⊘ Skipped${NC}" | tee -a "$LOG_FILE"
            SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
            continue
        fi
        
        # Run with retry logic
        local retry_count=0
        local use_debug=false
        while [ $retry_count -lt $MAX_RETRIES ]; do
            if [ $retry_count -gt 0 ]; then
                echo -e "${YELLOW}Retry $retry_count/$MAX_RETRIES (with debug mode - browser stays open)${NC}" | tee -a "$LOG_FILE"
                use_debug=true
            fi
            
            # Enable debug mode for retries (browser stays open on failure)
            if [ "$use_debug" = true ]; then
                local original_headed=$HEADED
                local original_debug=$DEBUG_MODE
                HEADED=true
                DEBUG_MODE=true
            fi
            
            if run_playwright_test "$test_file"; then
                echo -e "${GREEN}✓ PASSED${NC}" | tee -a "$LOG_FILE"
                PASSED_TESTS=$((PASSED_TESTS + 1))
                
                # Restore original settings if changed
                if [ "$use_debug" = true ]; then
                    HEADED=$original_headed
                    DEBUG_MODE=$original_debug
                fi
                break
            else
                echo -e "${RED}✗ FAILED${NC}" | tee -a "$LOG_FILE"
                if [ "$use_debug" = true ]; then
                    echo -e "${YELLOW}Browser left open for inspection${NC}" | tee -a "$LOG_FILE"
                fi
                retry_count=$((retry_count + 1))
                
                # Restore original settings if changed
                if [ "$use_debug" = true ]; then
                    HEADED=$original_headed
                    DEBUG_MODE=$original_debug
                fi
                
                if [ $retry_count -ge $MAX_RETRIES ]; then
                    FAILED_TESTS=$((FAILED_TESTS + 1))
                    echo "Max retries reached" | tee -a "$LOG_FILE"
                    
                    echo "Options: (s)kip and continue, (q)uit [s]: "
                    ask_user "What to do?" "s"
                    if [ $? -eq 3 ]; then
                        echo "Stopped by user" | tee -a "$LOG_FILE"
                        return
                    fi
                    break
                fi
                
                echo "Options: (r)etry with debug mode (browser stays open), (s)kip, (q)uit [r]: "
                ask_user "What to do?" "r"
                local choice=$?
                
                case $choice in
                    1|2) # Skip
                        FAILED_TESTS=$((FAILED_TESTS + 1))
                        break
                        ;;
                    3) # Quit
                        FAILED_TESTS=$((FAILED_TESTS + 1))
                        echo "Stopped by user" | tee -a "$LOG_FILE"
                        return
                        ;;
                    0|4) # Retry
                        sleep 2
                        ;;
                esac
            fi
        done
    done
}

################################################################################
# Mode: Sequential (Accumulate tests)
################################################################################

mode_sequential() {
    print_header "SEQUENTIAL MODE - Accumulate Tests"
    
    local test_num=0
    for test_file in "${TESTS_TO_RUN[@]}"; do
        local test_name=$(basename "$test_file" .spec.ts)
        test_num=$((test_num + 1))
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        
        print_test_header "$test_num" "$test_name" "$test_file"
        
        # Add to accumulated list
        ACCUMULATED_TESTS+=("$test_file")
        
        echo "Running accumulated tests: ${ACCUMULATED_TESTS[*]}" | tee -a "$LOG_FILE"
        
        if run_playwright_test "${ACCUMULATED_TESTS[@]}"; then
            echo -e "${GREEN}✓ PASSED${NC}" | tee -a "$LOG_FILE"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}✗ FAILED${NC}" | tee -a "$LOG_FILE"
            echo "Retrying accumulated tests..." | tee -a "$LOG_FILE"
            sleep 2
            
            if run_playwright_test "${ACCUMULATED_TESTS[@]}"; then
                echo -e "${GREEN}✓ Retry PASSED${NC}" | tee -a "$LOG_FILE"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${RED}✗ Retry FAILED${NC}" | tee -a "$LOG_FILE"
                FAILED_TESTS=$((FAILED_TESTS + 1))
                
                echo "Continue anyway? (y/n) [n]: "
                ask_user "Continue?" "n"
                if [ $? -ne 0 ]; then
                    echo "Stopped" | tee -a "$LOG_FILE"
                    break
                fi
            fi
        fi
    done
}

################################################################################
# Main Execution
################################################################################

print_header "Unified E2E Test Runner"

echo "Mode: $MODE" | tee -a "$LOG_FILE"
echo "Log:  $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check servers
if ! check_servers; then
    exit 1
fi

# Clear database if requested
if ! clear_database; then
    exit 1
fi

# Filter tests
TESTS_TO_RUN=()
for test_file in "${ALL_TESTS[@]}"; do
    # Skip seed tests if requested
    if [[ "$test_file" == *"00-seed"* ]] && [ "$SKIP_SEED" = true ]; then
        continue
    fi
    
    # Filter by specific test if requested
    if [ -n "$SPECIFIC_TEST" ]; then
        if [[ "$test_file" != *"$SPECIFIC_TEST"* ]]; then
            continue
        fi
    fi
    
    # Check if file exists
    if [ -f "$test_file" ]; then
        TESTS_TO_RUN+=("$test_file")
    fi
done

echo "Tests to run: ${#TESTS_TO_RUN[@]}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run tests based on mode
case "$MODE" in
    auto)
        mode_auto
        ;;
    interactive)
        mode_interactive
        ;;
    manual)
        mode_manual
        ;;
    sequential)
        mode_sequential
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        echo "Valid modes: auto, interactive, manual, sequential"
        exit 1
        ;;
esac

# Print summary
print_summary

# Exit code
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}✗ TESTS FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    exit 0
fi
