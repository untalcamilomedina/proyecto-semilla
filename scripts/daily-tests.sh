#!/bin/bash

# Daily Testing Pipeline for Proyecto Semilla
# Executed at the end of each development day
# Ensures code quality and catches issues early

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_RESULTS_DIR="$PROJECT_ROOT/test-results/daily/$(date +%Y%m%d)"
PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test Results
UNIT_TESTS_PASSED=true
INTEGRATION_TESTS_PASSED=true
PERFORMANCE_TESTS_PASSED=true
HEALTH_CHECKS_PASSED=true
SECURITY_TESTS_PASSED=true

# Create results directory
mkdir -p "$TEST_RESULTS_DIR"

# Header
echo -e "${BLUE}🧪 DAILY TESTING PIPELINE - PROYECTO SEMILLA${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${CYAN}📅 Date: $(date)${NC}"
echo -e "${CYAN}📁 Results: $TEST_RESULTS_DIR${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to log results
log_test_result() {
    local test_name="$1"
    local result="$2"
    local duration="$3"

    echo -e "${CYAN}[$test_name]${NC} Duration: ${YELLOW}${duration}s${NC}"

    if [ "$result" = "PASS" ]; then
        echo -e "${CYAN}[$test_name]${NC} ${GREEN}✅ PASSED${NC}"
    else
        echo -e "${CYAN}[$test_name]${NC} ${RED}❌ FAILED${NC}"
    fi
}

# 1. UNIT TESTS
echo -e "${YELLOW}📝 Running Unit Tests...${NC}"
UNIT_START_TIME=$(date +%s)

if PYTHONPATH="$PWD/backend:$PYTHONPATH" python3 -m pytest tests/unit/ -v --tb=short --junitxml="$TEST_RESULTS_DIR/unit-tests.xml" > "$TEST_RESULTS_DIR/unit-tests.log" 2>&1; then
    log_test_result "UNIT_TESTS" "PASS" $(($(date +%s) - UNIT_START_TIME))
else
    log_test_result "UNIT_TESTS" "FAIL" $(($(date +%s) - UNIT_START_TIME))
    UNIT_TESTS_PASSED=false
fi

# 2. INTEGRATION TESTS
echo -e "${YELLOW}🔗 Running Integration Tests...${NC}"
INTEGRATION_START_TIME=$(date +%s)

if PYTHONPATH="$PWD/backend:$PYTHONPATH" python3 -m pytest tests/integration/ -v --tb=short --junitxml="$TEST_RESULTS_DIR/integration-tests.xml" > "$TEST_RESULTS_DIR/integration-tests.log" 2>&1; then
    log_test_result "INTEGRATION_TESTS" "PASS" $(($(date +%s) - INTEGRATION_START_TIME))
else
    log_test_result "INTEGRATION_TESTS" "FAIL" $(($(date +%s) - INTEGRATION_START_TIME))
    INTEGRATION_TESTS_PASSED=false
fi

# 3. PERFORMANCE TESTS (Quick version)
echo -e "${YELLOW}⚡ Running Performance Tests...${NC}"
PERFORMANCE_START_TIME=$(date +%s)

if [ -f "scripts/run-performance-tests.sh" ]; then
    if bash scripts/run-performance-tests.sh --quick > "$TEST_RESULTS_DIR/performance-tests.log" 2>&1; then
        log_test_result "PERFORMANCE_TESTS" "PASS" $(($(date +%s) - PERFORMANCE_START_TIME))
    else
        log_test_result "PERFORMANCE_TESTS" "FAIL" $(($(date +%s) - PERFORMANCE_START_TIME))
        PERFORMANCE_TESTS_PASSED=false
    fi
else
    echo -e "${YELLOW}⚠️  Performance test script not found, skipping...${NC}"
    PERFORMANCE_TESTS_PASSED=false
fi

# 4. HEALTH CHECKS
echo -e "${YELLOW}❤️ Running Health Checks...${NC}"
HEALTH_START_TIME=$(date +%s)

if PYTHONPATH="$PWD/backend:$PYTHONPATH" python3 -m pytest tests/health/ -v --tb=short --junitxml="$TEST_RESULTS_DIR/health-checks.xml" > "$TEST_RESULTS_DIR/health-checks.log" 2>&1; then
    log_test_result "HEALTH_CHECKS" "PASS" $(($(date +%s) - HEALTH_START_TIME))
else
    log_test_result "HEALTH_CHECKS" "FAIL" $(($(date +%s) - HEALTH_START_TIME))
    HEALTH_CHECKS_PASSED=false
fi

# 5. SECURITY TESTS (Basic)
echo -e "${YELLOW}🔒 Running Security Tests...${NC}"
SECURITY_START_TIME=$(date +%s)

if PYTHONPATH="$PWD/backend:$PYTHONPATH" python3 -m pytest tests/security/ -v --tb=short --junitxml="$TEST_RESULTS_DIR/security-tests.xml" > "$TEST_RESULTS_DIR/security-tests.log" 2>&1; then
    log_test_result "SECURITY_TESTS" "PASS" $(($(date +%s) - SECURITY_START_TIME))
else
    log_test_result "SECURITY_TESTS" "FAIL" $(($(date +%s) - SECURITY_START_TIME))
    SECURITY_TESTS_PASSED=false
fi

# Generate Summary Report
echo -e "${BLUE}📊 GENERATING SUMMARY REPORT${NC}"
echo -e "${BLUE}==============================${NC}"

SUMMARY_FILE="$TEST_RESULTS_DIR/daily-summary.json"
cat > "$SUMMARY_FILE" << EOF
{
  "date": "$(date +%Y-%m-%d)",
  "timestamp": "$(date +%s)",
  "tests": {
    "unit": {
      "passed": $UNIT_TESTS_PASSED,
      "duration": $(($(date +%s) - UNIT_START_TIME))
    },
    "integration": {
      "passed": $INTEGRATION_TESTS_PASSED,
      "duration": $(($(date +%s) - INTEGRATION_START_TIME))
    },
    "performance": {
      "passed": $PERFORMANCE_TESTS_PASSED,
      "duration": $(($(date +%s) - PERFORMANCE_START_TIME))
    },
    "health": {
      "passed": $HEALTH_CHECKS_PASSED,
      "duration": $(($(date +%s) - HEALTH_START_TIME))
    },
    "security": {
      "passed": $SECURITY_TESTS_PASSED,
      "duration": $(($(date +%s) - SECURITY_START_TIME))
    }
  },
  "overall_result": "$OVERALL_RESULT"
}
EOF

# Display Results Summary
echo -e "${PURPLE}📈 DAILY TEST RESULTS SUMMARY${NC}"
echo -e "${PURPLE}==============================${NC}"

echo -e "Unit Tests:        $(if $UNIT_TESTS_PASSED; then echo -e "${GREEN}✅ PASSED${NC}"; else echo -e "${RED}❌ FAILED${NC}"; fi)"
echo -e "Integration Tests: $(if $INTEGRATION_TESTS_PASSED; then echo -e "${GREEN}✅ PASSED${NC}"; else echo -e "${RED}❌ FAILED${NC}"; fi)"
echo -e "Performance Tests: $(if $PERFORMANCE_TESTS_PASSED; then echo -e "${GREEN}✅ PASSED${NC}"; else echo -e "${RED}❌ FAILED${NC}"; fi)"
echo -e "Health Checks:     $(if $HEALTH_CHECKS_PASSED; then echo -e "${GREEN}✅ PASSED${NC}"; else echo -e "${RED}❌ FAILED${NC}"; fi)"
echo -e "Security Tests:    $(if $SECURITY_TESTS_PASSED; then echo -e "${GREEN}✅ PASSED${NC}"; else echo -e "${RED}❌ FAILED${NC}"; fi)"

echo -e "${BLUE}📁 Test Results Location:${NC}"
echo -e "  ${CYAN}$TEST_RESULTS_DIR${NC}"

# Overall Assessment
if $UNIT_TESTS_PASSED && $INTEGRATION_TESTS_PASSED && $PERFORMANCE_TESTS_PASSED && $HEALTH_CHECKS_PASSED && $SECURITY_TESTS_PASSED; then
    OVERALL_RESULT="ALL_PASSED"
    echo -e "${GREEN}🎉 ALL DAILY TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Code is ready for commit and deployment${NC}"
    echo -e "${GREEN}🚀 Quality gate passed - proceeding with confidence${NC}"
    exit 0
else
    OVERALL_RESULT="SOME_FAILED"
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo -e "${YELLOW}⚠️  Please review failed tests before committing${NC}"
    echo -e "${YELLOW}📋 Check logs in: $TEST_RESULTS_DIR${NC}"
    echo -e "${YELLOW}🔧 Fix issues and re-run tests${NC}"
    exit 1
fi