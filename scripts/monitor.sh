#!/bin/bash

# Proyecto Semilla Monitoring Script
# Usage: ./monitor.sh [service_name] [duration_minutes]

set -e

SERVICE=${1:-all}
DURATION=${2:-5}  # Default 5 minutes
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
    echo -e "${BLUE}[MONITOR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[MONITOR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[MONITOR]${NC} $1"
}

log_error() {
    echo -e "${RED}[MONITOR]${NC} $1"
}

# Monitoring functions
monitor_system_resources() {
    log_info "Monitoring system resources..."

    local iterations=$((DURATION * 12))  # Check every 5 seconds
    local cpu_total=0
    local mem_total=0
    local count=0

    for ((i=1; i<=iterations; i++)); do
        # CPU usage
        local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
        cpu_total=$(echo "$cpu_total + $cpu_usage" | bc -l)

        # Memory usage
        local mem_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
        mem_total=$(echo "$mem_total + $mem_usage" | bc -l)

        count=$((count + 1))

        # Check thresholds
        if (( $(echo "$cpu_usage > 90" | bc -l) )); then
            log_warning "High CPU usage detected: ${cpu_usage}%"
        fi

        if (( $(echo "$mem_usage > 90" | bc -l) )); then
            log_warning "High memory usage detected: ${mem_usage}%"
        fi

        sleep 5
    done

    # Calculate averages
    local avg_cpu=$(echo "scale=2; $cpu_total / $count" | bc -l)
    local avg_mem=$(echo "scale=2; $mem_total / $count" | bc -l)

    log_info "Average CPU usage: ${avg_cpu}%"
    log_info "Average memory usage: ${avg_mem}%"
}

monitor_containers() {
    log_info "Monitoring Docker containers..."

    local iterations=$((DURATION * 12))
    local container_stats=()

    for ((i=1; i<=iterations; i++)); do
        # Get container stats
        local stats=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}")

        # Check for unhealthy containers
        local unhealthy=$(docker ps --filter "health=unhealthy" --format "{{.Names}}")
        if [ -n "$unhealthy" ]; then
            log_warning "Unhealthy containers detected: $unhealthy"
        fi

        # Store stats for analysis
        container_stats+=("$stats")

        sleep 5
    done

    log_info "Container monitoring completed"
}

monitor_application() {
    log_info "Monitoring application health..."

    local iterations=$((DURATION * 12))
    local backend_failures=0
    local frontend_failures=0
    local api_failures=0

    for ((i=1; i<=iterations; i++)); do
        # Backend health check
        if ! curl -f -s --max-time 5 "http://localhost:8000/health" > /dev/null 2>&1; then
            backend_failures=$((backend_failures + 1))
            if [ $((i % 12)) -eq 0 ]; then  # Log every minute
                log_warning "Backend health check failed (attempt $i)"
            fi
        fi

        # Frontend health check
        if ! curl -f -s --max-time 5 "http://localhost:3000" > /dev/null 2>&1; then
            frontend_failures=$((frontend_failures + 1))
            if [ $((i % 12)) -eq 0 ]; then
                log_warning "Frontend health check failed (attempt $i)"
            fi
        fi

        # API endpoints check
        if ! curl -f -s --max-time 5 "http://localhost:8000/api/v1/tenants" > /dev/null 2>&1; then
            api_failures=$((api_failures + 1))
            if [ $((i % 12)) -eq 0 ]; then
                log_warning "API endpoints check failed (attempt $i)"
            fi
        fi

        sleep 5
    done

    # Report failures
    if [ $backend_failures -gt 0 ]; then
        log_warning "Backend had $backend_failures health check failures"
    fi

    if [ $frontend_failures -gt 0 ]; then
        log_warning "Frontend had $frontend_failures health check failures"
    fi

    if [ $api_failures -gt 0 ]; then
        log_warning "API had $api_failures health check failures"
    fi

    if [ $backend_failures -eq 0 ] && [ $frontend_failures -eq 0 ] && [ $api_failures -eq 0 ]; then
        log_success "All application health checks passed"
    fi
}

monitor_database() {
    log_info "Monitoring database performance..."

    local iterations=$((DURATION * 6))  # Check every 10 seconds

    for ((i=1; i<=iterations; i++)); do
        # Database connection check
        if ! docker-compose exec -T db pg_isready -U admin -d proyecto_semilla > /dev/null 2>&1; then
            log_error "Database connection failed"
            continue
        fi

        # Get active connections
        local active_connections=$(docker-compose exec -T db psql -U admin -d proyecto_semilla -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';" -t 2>/dev/null | xargs)

        if [ "$active_connections" -gt 50 ]; then
            log_warning "High number of active database connections: $active_connections"
        fi

        # Check for long-running queries
        local long_queries=$(docker-compose exec -T db psql -U admin -d proyecto_semilla -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '30 seconds';" -t 2>/dev/null | xargs)

        if [ "$long_queries" -gt 0 ]; then
            log_warning "Long-running queries detected: $long_queries"
        fi

        sleep 10
    done
}

generate_report() {
    log_info "Generating monitoring report..."

    local timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
    local report_file="$PROJECT_ROOT/monitoring_report_$timestamp.txt"

    {
        echo "Proyecto Semilla Monitoring Report"
        echo "Generated: $(date)"
        echo "Duration: ${DURATION} minutes"
        echo "=================================="
        echo ""

        echo "System Information:"
        echo "-------------------"
        uname -a
        echo ""

        echo "Docker Containers:"
        echo "------------------"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""

        echo "Disk Usage:"
        echo "-----------"
        df -h
        echo ""

        echo "Memory Usage:"
        echo "-------------"
        free -h
        echo ""

        echo "Running Processes:"
        echo "------------------"
        ps aux --sort=-%cpu | head -10
        echo ""

    } > "$report_file"

    log_success "Monitoring report saved to: $report_file"
}

# Main monitoring logic
main() {
    log_info "🚀 Starting Proyecto Semilla monitoring for ${DURATION} minutes"

    # Start monitoring in background
    case $SERVICE in
        system)
            monitor_system_resources &
            ;;
        containers)
            monitor_containers &
            ;;
        application|app)
            monitor_application &
            ;;
        database|db)
            monitor_database &
            ;;
        all)
            monitor_system_resources &
            monitor_containers &
            monitor_application &
            monitor_database &
            ;;
        *)
            log_error "Unknown service: $SERVICE"
            log_info "Available services: system, containers, application, database, all"
            exit 1
            ;;
    esac

    # Wait for monitoring to complete
    wait

    # Generate report
    generate_report

    log_success "✅ Monitoring completed successfully"
}

# Error handling
trap 'log_error "Monitoring failed with error code $?"' ERR

# Run main function
main "$@"