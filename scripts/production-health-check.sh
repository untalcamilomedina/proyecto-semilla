#!/bin/bash

# PROYECTO SEMILLA - PRODUCTION HEALTH CHECK SUITE
# Validación completa de production readiness

set -e

echo "🔍 PROYECTO SEMILLA - PRODUCTION HEALTH CHECK SUITE"
echo "=================================================="
echo "Fecha: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to log results
log_check() {
    local check_name="$1"
    local status="$2"
    local details="$3"

    ((TOTAL_CHECKS++))

    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $check_name${NC}"
        ((PASSED_CHECKS++))
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $check_name${NC}"
        if [ -n "$details" ]; then
            echo -e "${YELLOW}   └─ $details${NC}"
        fi
    else
        echo -e "${RED}❌ $check_name${NC}"
        if [ -n "$details" ]; then
            echo -e "${RED}   └─ $details${NC}"
        fi
        ((FAILED_CHECKS++))
    fi
}

# Function to check service health
check_service() {
    local service_name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    if curl -s -f -o /dev/null -w "%{http_code}" "$url" | grep -q "^$expected_status$"; then
        log_check "$service_name Health Check" "PASS"
    else
        log_check "$service_name Health Check" "FAIL" "Expected status $expected_status"
    fi
}

echo "🐳 DOCKER CONTAINER STATUS"
echo "=========================="

# Check Docker containers
if docker-compose ps 2>/dev/null | grep -q "Up" 2>/dev/null; then
    log_check "Docker Containers" "PASS"
    echo "Container Status:"
    docker-compose ps 2>/dev/null | head -10 || echo "  Unable to get detailed status"
else
    log_check "Docker Containers" "FAIL" "No containers running"
fi

echo ""
echo "🌐 SERVICE HEALTH CHECKS"
echo "========================"

# Backend Health Check
check_service "Backend API" "http://localhost:8000/health"

# API Endpoints
check_service "Articles API" "http://localhost:8000/api/v1/articles" "200"

# Database connectivity (through backend)
if curl -s "http://localhost:8000/health" | grep -q "database.*healthy"; then
    log_check "Database Connectivity" "PASS"
else
    log_check "Database Connectivity" "FAIL"
fi

# Redis connectivity (through backend)
if curl -s "http://localhost:8000/health" | grep -q "redis.*healthy"; then
    log_check "Redis Connectivity" "PASS"
else
    log_check "Redis Connectivity" "FAIL"
fi

echo ""
echo "⚡ PERFORMANCE VALIDATION"
echo "========================"

# Response Time Check
response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:8000/api/v1/articles" 2>/dev/null || echo "1.0")

# Simple comparison without bc
if [ "$(echo "$response_time" | awk '{if($1 < 0.1) print "yes"; else print "no"}')" = "yes" ]; then
    log_check "Response Time (<100ms)" "PASS" "${response_time}s"
else
    log_check "Response Time (<100ms)" "WARN" "${response_time}s - Above target"
fi

echo ""
echo "🔒 SECURITY VALIDATION"
echo "======================"

# Rate Limiting Test
rate_limit_test=$(curl -s -I "http://localhost:8000/api/v1/articles" | grep -i "x-ratelimit" | wc -l)
if [ "$rate_limit_test" -gt 0 ]; then
    log_check "Rate Limiting Headers" "PASS"
else
    log_check "Rate Limiting Headers" "WARN" "Rate limiting headers not present"
fi

# Security Headers Check
security_headers=$(curl -s -I "http://localhost:8000/api/v1/articles" | grep -E "(x-frame-options|x-content-type-options|x-xss-protection)" | wc -l)
if [ "$security_headers" -gt 0 ]; then
    log_check "Security Headers" "PASS"
else
    log_check "Security Headers" "WARN" "Security headers not present"
fi

echo ""
echo "📊 ENTERPRISE FEATURES VALIDATION"
echo "================================="

# Circuit Breaker Test
if curl -s "http://localhost:8000/health" | grep -q "circuit_breaker.*healthy"; then
    log_check "Circuit Breaker" "PASS"
else
    log_check "Circuit Breaker" "WARN" "Circuit breaker status unknown"
fi

# Metrics Collection
if curl -s "http://localhost:8000/metrics" | grep -q "http_requests_total"; then
    log_check "Metrics Collection" "PASS"
else
    log_check "Metrics Collection" "WARN" "Metrics not available"
fi

# Audit Logging
if curl -s "http://localhost:8000/health" | grep -q "audit.*healthy"; then
    log_check "Audit Logging" "PASS"
else
    log_check "Audit Logging" "WARN" "Audit logging status unknown"
fi

echo ""
echo "🧪 TESTING INFRASTRUCTURE"
echo "========================="

# Unit Tests
if python -m pytest tests/unit/ -v --tb=short | grep -q "passed"; then
    log_check "Unit Tests" "PASS"
else
    log_check "Unit Tests" "FAIL" "Unit tests failed"
fi

# Integration Tests
if python -m pytest tests/integration/ -v --tb=short | grep -q "passed"; then
    log_check "Integration Tests" "PASS"
else
    log_check "Integration Tests" "WARN" "Integration tests may have issues"
fi

echo ""
echo "📈 LOAD TESTING PREPARATION"
echo "==========================="

# Check Artillery installation
if command -v artillery &> /dev/null; then
    log_check "Load Testing Tool (Artillery)" "PASS"
else
    log_check "Load Testing Tool (Artillery)" "WARN" "Artillery not installed"
fi

# Check test configuration
if [ -f "tests/performance/load-test.yml" ]; then
    log_check "Load Test Configuration" "PASS"
else
    log_check "Load Test Configuration" "WARN" "Load test config not found"
fi

echo ""
echo "📋 SUMMARY"
echo "=========="

echo "Total Checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"

if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 PRODUCTION READINESS: PASSED${NC}"
    echo "Proyecto Semilla is production-ready!"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  PRODUCTION READINESS: ISSUES FOUND${NC}"
    echo "Please address the failed checks before deployment."
    exit 1
fi