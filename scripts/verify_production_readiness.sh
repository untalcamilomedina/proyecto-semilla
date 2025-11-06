#!/bin/bash
# Production Readiness Verification Script
# Checks if the system is properly configured for production deployment

set -e

echo "🔍 Proyecto Semilla - Production Readiness Check"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ISSUES=0
WARNINGS=0

# Check 1: .env.production exists
echo "📋 Checking configuration files..."
if [ -f .env.production ]; then
    echo -e "${GREEN}✅ .env.production exists${NC}"
else
    echo -e "${RED}❌ .env.production not found${NC}"
    echo "   Run: ./scripts/setup_production.sh"
    ISSUES=$((ISSUES + 1))
fi

# Check 2: Load .env.production and verify settings
if [ -f .env.production ]; then
    source .env.production

    # Check COOKIE_SECURE
    if [ "$COOKIE_SECURE" = "true" ]; then
        echo -e "${GREEN}✅ COOKIE_SECURE is true${NC}"
    else
        echo -e "${RED}❌ COOKIE_SECURE must be true in production${NC}"
        ISSUES=$((ISSUES + 1))
    fi

    # Check DEBUG
    if [ "$DEBUG" = "false" ]; then
        echo -e "${GREEN}✅ DEBUG is false${NC}"
    else
        echo -e "${YELLOW}⚠️  DEBUG should be false in production${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check JWT_SECRET length
    JWT_LEN=${#JWT_SECRET}
    if [ $JWT_LEN -ge 32 ]; then
        echo -e "${GREEN}✅ JWT_SECRET has sufficient length (${JWT_LEN} chars)${NC}"
    else
        echo -e "${RED}❌ JWT_SECRET too short (${JWT_LEN} chars, need 32+)${NC}"
        ISSUES=$((ISSUES + 1))
    fi

    # Check DB_PASSWORD
    if [ -n "$DB_PASSWORD" ] && [ "$DB_PASSWORD" != "changeme123" ]; then
        DB_LEN=${#DB_PASSWORD}
        if [ $DB_LEN -ge 16 ]; then
            echo -e "${GREEN}✅ DB_PASSWORD is configured securely (${DB_LEN} chars)${NC}"
        else
            echo -e "${YELLOW}⚠️  DB_PASSWORD is short (${DB_LEN} chars, recommend 16+)${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo -e "${RED}❌ DB_PASSWORD is insecure or not set${NC}"
        ISSUES=$((ISSUES + 1))
    fi

    # Check HARDCODED_USERS_MIGRATION_ENABLED
    if [ "$HARDCODED_USERS_MIGRATION_ENABLED" = "true" ]; then
        echo -e "${GREEN}✅ HARDCODED_USERS_MIGRATION_ENABLED is true${NC}"
    else
        echo -e "${YELLOW}⚠️  HARDCODED_USERS_MIGRATION_ENABLED should be true${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check CORS origins don't include localhost
    if echo "$BACKEND_CORS_ORIGINS" | grep -q "localhost"; then
        echo -e "${YELLOW}⚠️  CORS origins include localhost (development only)${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✅ CORS origins properly configured${NC}"
    fi
fi

echo ""
echo "🐳 Checking Docker configuration..."

# Check if Docker is running
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "   Start Docker and try again"
    ISSUES=$((ISSUES + 1))
fi

# Check if docker-compose.prod.yml exists
if [ -f docker-compose.prod.yml ]; then
    echo -e "${GREEN}✅ docker-compose.prod.yml exists${NC}"
else
    echo -e "${YELLOW}⚠️  docker-compose.prod.yml not found${NC}"
    echo "   Using docker-compose.yml for production"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "🌐 Checking backend API (if running)..."

# Try to connect to backend health endpoint
BACKEND_URL="http://localhost:7777"
if curl -sf ${BACKEND_URL}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is accessible${NC}"

    # Check production readiness endpoint
    if curl -sf ${BACKEND_URL}/api/v1/setup/production-readiness > /dev/null 2>&1; then
        RESPONSE=$(curl -s ${BACKEND_URL}/api/v1/setup/production-readiness)

        # Parse response (requires jq)
        if command -v jq &> /dev/null; then
            READY=$(echo $RESPONSE | jq -r '.ready_for_production')
            API_ISSUES=$(echo $RESPONSE | jq -r '.issues | length')
            API_WARNINGS=$(echo $RESPONSE | jq -r '.warnings | length')

            if [ "$READY" = "true" ]; then
                echo -e "${GREEN}✅ Backend reports ready for production${NC}"
            else
                echo -e "${RED}❌ Backend reports NOT ready for production${NC}"
                echo "   API Issues: $API_ISSUES"
                echo "   API Warnings: $API_WARNINGS"
                ISSUES=$((ISSUES + API_ISSUES))
                WARNINGS=$((WARNINGS + API_WARNINGS))

                # Show issues
                echo ""
                echo "   Backend issues:"
                echo "$RESPONSE" | jq -r '.issues[]' | while read issue; do
                    echo -e "   ${RED}• $issue${NC}"
                done

                echo ""
                echo "   Backend warnings:"
                echo "$RESPONSE" | jq -r '.warnings[]' | while read warning; do
                    echo -e "   ${YELLOW}• $warning${NC}"
                done
            fi
        else
            echo -e "${YELLOW}⚠️  jq not installed, cannot parse API response${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Backend is not running (start it to verify fully)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "📁 Checking .gitignore..."

if grep -q ".env.production" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ .env.production is in .gitignore${NC}"
else
    echo -e "${RED}❌ .env.production should be in .gitignore${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Issues: ${RED}${ISSUES}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"
echo ""

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ System is READY for production deployment${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure HTTPS/SSL certificates"
    echo "2. Set up reverse proxy (Nginx/Traefik)"
    echo "3. Deploy: docker-compose -f docker-compose.prod.yml up -d"
    echo "4. Access setup wizard at your domain"
    echo ""
    exit 0
else
    echo -e "${RED}❌ System is NOT ready for production${NC}"
    echo ""
    echo "Please fix the issues above before deploying to production."
    echo ""
    echo "Common fixes:"
    echo "• Run: ./scripts/setup_production.sh"
    echo "• Ensure Docker is running"
    echo "• Add .env.production to .gitignore"
    echo "• Review configuration in .env.production"
    echo ""
    exit 1
fi
