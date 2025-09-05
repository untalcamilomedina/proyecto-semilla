#!/bin/bash

# Proyecto Semilla Deployment Script
# Usage: ./deploy.sh [staging|production]

set -e

ENVIRONMENT=$1
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

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Usage: $0 [staging|production]"
    exit 1
fi

log_info "Starting deployment to $ENVIRONMENT environment"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
    log_info "Loading environment variables from .env.$ENVIRONMENT"
    export $(cat "$PROJECT_ROOT/.env.$ENVIRONMENT" | xargs)
else
    log_warning "No environment file found for $ENVIRONMENT"
fi

# Pre-deployment checks
check_dependencies() {
    log_info "Checking dependencies..."

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi

    # Check if docker-compose is available
    if ! command -v docker-compose > /dev/null 2>&1; then
        log_error "docker-compose is not installed"
        exit 1
    fi

    log_success "Dependencies check passed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."

    cd "$PROJECT_ROOT"

    # Build backend image
    log_info "Building backend image..."
    docker build -t proyecto-semilla-backend:$ENVIRONMENT ./backend

    # Build frontend image
    log_info "Building frontend image..."
    docker build -t proyecto-semilla-frontend:$ENVIRONMENT ./frontend

    log_success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."

    cd "$PROJECT_ROOT"

    # Create environment-specific docker-compose file
    COMPOSE_FILE="docker-compose.$ENVIRONMENT.yml"

    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file $COMPOSE_FILE not found"
        exit 1
    fi

    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down || true

    # Start services
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d

    log_success "Services deployed successfully"
}

# Health checks
health_check() {
    log_info "Performing health checks..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Check backend health
        if curl -f -s "http://localhost:8000/health" > /dev/null 2>&1; then
            log_success "Backend health check passed"
            backend_healthy=true
        else
            log_warning "Backend health check failed"
            backend_healthy=false
        fi

        # Check frontend health
        if curl -f -s "http://localhost:3000" > /dev/null 2>&1; then
            log_success "Frontend health check passed"
            frontend_healthy=true
        else
            log_warning "Frontend health check failed"
            frontend_healthy=false
        fi

        # Check database connectivity
        if docker-compose -f "docker-compose.$ENVIRONMENT.yml" exec -T db pg_isready -U postgres > /dev/null 2>&1; then
            log_success "Database health check passed"
            db_healthy=true
        else
            log_warning "Database health check failed"
            db_healthy=false
        fi

        if [ "$backend_healthy" = true ] && [ "$frontend_healthy" = true ] && [ "$db_healthy" = true ]; then
            log_success "All health checks passed!"
            return 0
        fi

        sleep 10
        ((attempt++))
    done

    log_error "Health checks failed after $max_attempts attempts"
    return 1
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    cd "$PROJECT_ROOT"

    # Run basic validation script
    if python3 scripts/validate-system.py; then
        log_success "Smoke tests passed"
    else
        log_error "Smoke tests failed"
        return 1
    fi
}

# Rollback function
rollback() {
    log_error "Deployment failed, initiating rollback..."

    cd "$PROJECT_ROOT"

    # Stop current deployment
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" down

    # Start previous version (if available)
    if [ -f "docker-compose.$ENVIRONMENT.backup.yml" ]; then
        log_info "Starting previous version..."
        docker-compose -f "docker-compose.$ENVIRONMENT.backup.yml" up -d
    else
        log_warning "No backup compose file found"
    fi

    log_info "Rollback completed"
}

# Main deployment process
main() {
    log_info "🚀 Starting Proyecto Semilla deployment to $ENVIRONMENT"

    # Pre-deployment checks
    check_dependencies

    # Build images
    build_images

    # Backup current deployment
    if [ -f "docker-compose.$ENVIRONMENT.yml" ]; then
        cp "docker-compose.$ENVIRONMENT.yml" "docker-compose.$ENVIRONMENT.backup.yml"
    fi

    # Deploy services
    if deploy_services; then
        log_success "Services deployed successfully"
    else
        log_error "Service deployment failed"
        rollback
        exit 1
    fi

    # Health checks
    if health_check; then
        log_success "Health checks passed"
    else
        log_error "Health checks failed"
        rollback
        exit 1
    fi

    # Smoke tests
    if run_smoke_tests; then
        log_success "Smoke tests passed"
    else
        log_error "Smoke tests failed"
        rollback
        exit 1
    fi

    log_success "🎉 Deployment to $ENVIRONMENT completed successfully!"
    log_info "Application is available at:"
    log_info "  Frontend: http://localhost:3000"
    log_info "  Backend API: http://localhost:8000"
    log_info "  API Docs: http://localhost:8000/docs"
}

# Error handling
trap 'log_error "Deployment failed with error code $?"' ERR

# Run main function
main "$@"