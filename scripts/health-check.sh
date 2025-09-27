#!/bin/bash

# Proyecto Semilla Health Check Script
# Usage: ./health-check.sh [service_name] [environment]

set -e

SERVICE=${1:-all}
ENVIRONMENT=${2:-development}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Health check functions
check_backend() {
    local url="http://localhost:8000/health"
    log_info "Checking backend health at $url"

    if curl -f -s --max-time 10 "$url" > /dev/null 2>&1; then
        log_success "Backend is healthy"
        return 0
    else
        log_error "Backend health check failed"
        return 1
    fi
}

check_frontend() {
    local url="http://localhost:3000"
    log_info "Checking frontend health at $url"

    if curl -f -s --max-time 10 "$url" > /dev/null 2>&1; then
        log_success "Frontend is healthy"
        return 0
    else
        log_error "Frontend health check failed"
        return 1
    fi
}

check_database() {
    log_info "Checking database connectivity"

    if [ "$ENVIRONMENT" = "production" ]; then
        # In production, check via docker exec
        if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T db pg_isready -U "${DB_USER:-postgres}" -d proyecto_semilla > /dev/null 2>&1; then
            log_success "Database is healthy"
            return 0
        fi
    else
        # In development, check via docker exec
        if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T db pg_isready -U admin -d proyecto_semilla > /dev/null 2>&1; then
            log_success "Database is healthy"
            return 0
        fi
    fi

    log_error "Database health check failed"
    return 1
}

check_redis() {
    log_info "Checking Redis connectivity"

    if [ "$ENVIRONMENT" = "production" ]; then
        # In production, check via docker exec
        if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T redis redis-cli ping | grep -q PONG; then
            log_success "Redis is healthy"
            return 0
        fi
    else
        # In development, check via docker exec
        if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T redis redis-cli ping | grep -q PONG; then
            log_success "Redis is healthy"
            return 0
        fi
    fi

    log_error "Redis health check failed"
    return 1
}

check_mcp_server() {
    local url="http://localhost:8001/docs"
    log_info "Checking MCP server health at $url"

    if curl -f -s --max-time 10 "$url" > /dev/null 2>&1; then
        log_success "MCP server is healthy"
        return 0
    else
        log_error "MCP server health check failed"
        return 1
    fi
}

check_api_endpoints() {
    log_info "Checking API endpoints"

    local base_url="http://localhost:8000"
    local endpoints=(
        "/api/v1/health"
        "/api/v1/docs"
        "/api/v1/tenants"
    )

    local failed=0
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time 10 "$base_url$endpoint" > /dev/null 2>&1; then
            log_success "Endpoint $endpoint is accessible"
        else
            log_error "Endpoint $endpoint is not accessible"
            ((failed++))
        fi
    done

    if [ $failed -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

check_system_resources() {
    log_info "Checking system resources"

    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log_error "Disk usage is high: ${disk_usage}%"
        return 1
    else
        log_success "Disk usage is acceptable: ${disk_usage}%"
    fi

    # Check memory usage
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$mem_usage" -gt 90 ]; then
        log_error "Memory usage is high: ${mem_usage}%"
        return 1
    else
        log_success "Memory usage is acceptable: ${mem_usage}%"
    fi

    return 0
}

# Main health check logic
main() {
    log_info "🚀 Starting health checks for Proyecto Semilla ($ENVIRONMENT)"

    local failed_checks=0

    case $SERVICE in
        backend)
            check_backend || ((failed_checks++))
            ;;
        frontend)
            check_frontend || ((failed_checks++))
            ;;
        database|db)
            check_database || ((failed_checks++))
            ;;
        redis)
            check_redis || ((failed_checks++))
            ;;
        mcp)
            check_mcp_server || ((failed_checks++))
            ;;
        api)
            check_api_endpoints || ((failed_checks++))
            ;;
        system)
            check_system_resources || ((failed_checks++))
            ;;
        all)
            check_backend || ((failed_checks++))
            check_frontend || ((failed_checks++))
            check_database || ((failed_checks++))
            check_redis || ((failed_checks++))
            check_mcp_server || ((failed_checks++))
            check_api_endpoints || ((failed_checks++))
            check_system_resources || ((failed_checks++))
            ;;
        *)
            log_error "Unknown service: $SERVICE"
            log_info "Available services: backend, frontend, database, redis, mcp, api, system, all"
            exit 1
            ;;
    esac

    if [ $failed_checks -eq 0 ]; then
        log_success "✅ All health checks passed!"
        exit 0
    else
        log_error "❌ $failed_checks health check(s) failed"
        exit 1
    fi
}

# Error handling
trap 'log_error "Health check failed with error code $?"' ERR

# Run main function
main "$@"