#!/bin/bash
# Production Setup Script for Proyecto Semilla
# Generates secure credentials and creates production-ready .env file

set -e  # Exit on error

echo "🚀 Proyecto Semilla - Production Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env.production already exists
if [ -f .env.production ]; then
    echo -e "${YELLOW}⚠️  .env.production already exists${NC}"
    read -p "Do you want to overwrite it? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    # Backup existing file
    cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Backup created${NC}"
fi

echo ""
echo "📝 Generating secure credentials..."
echo ""

# Generate JWT_SECRET (64 characters hex)
JWT_SECRET=$(openssl rand -hex 32)
echo -e "${GREEN}✅ JWT_SECRET generated (64 chars)${NC}"

# Generate DB_PASSWORD (32 characters, URL-safe)
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
echo -e "${GREEN}✅ DB_PASSWORD generated (32 chars)${NC}"

# Prompt for domain
echo ""
echo "🌐 Production Configuration"
read -p "Enter your production domain (e.g., example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Domain is required${NC}"
    exit 1
fi

# Prompt for email (optional, for Let's Encrypt)
read -p "Enter admin email (optional, for SSL certificates): " ADMIN_EMAIL

echo ""
echo "📋 Creating .env.production file..."

# Create .env.production
cat > .env.production <<EOF
# =============================================================================
# PROYECTO SEMILLA - PRODUCTION CONFIGURATION
# =============================================================================
# Generated: $(date)
# IMPORTANT: Keep this file secure and never commit it to version control
# =============================================================================

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla
DB_USER=admin
DB_PASSWORD=${DB_PASSWORD}

# -----------------------------------------------------------------------------
# Security Configuration
# -----------------------------------------------------------------------------
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# -----------------------------------------------------------------------------
# Cookie Security (HTTPS Required)
# -----------------------------------------------------------------------------
COOKIE_SECURE=true
COOKIE_DOMAIN=${DOMAIN}
COOKIE_SAME_SITE=lax

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------
BACKEND_CORS_ORIGINS='["https://${DOMAIN}","https://www.${DOMAIN}"]'

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# -----------------------------------------------------------------------------
# Redis Configuration
# -----------------------------------------------------------------------------
REDIS_URL=redis://redis:6379

# -----------------------------------------------------------------------------
# Rate Limiting
# -----------------------------------------------------------------------------
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# -----------------------------------------------------------------------------
# Frontend Configuration
# -----------------------------------------------------------------------------
NEXT_PUBLIC_API_URL=https://${DOMAIN}
NEXT_PUBLIC_ENVIRONMENT=production

# -----------------------------------------------------------------------------
# Feature Flags
# -----------------------------------------------------------------------------
HARDCODED_USERS_MIGRATION_ENABLED=true

# -----------------------------------------------------------------------------
# Email Configuration (Optional - Configure if needed)
# -----------------------------------------------------------------------------
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=noreply@${DOMAIN}
# SMTP_PASSWORD=your_smtp_password
# SMTP_TLS=true
# EMAILS_FROM_EMAIL=noreply@${DOMAIN}
# EMAILS_FROM_NAME=Proyecto Semilla

# -----------------------------------------------------------------------------
# Admin Email (For notifications and SSL certificates)
# -----------------------------------------------------------------------------
$([ -n "$ADMIN_EMAIL" ] && echo "ADMIN_EMAIL=${ADMIN_EMAIL}" || echo "# ADMIN_EMAIL=admin@${DOMAIN}")

EOF

echo -e "${GREEN}✅ .env.production created successfully${NC}"
echo ""

# Create frontend .env.production.local
echo "📋 Creating frontend/.env.production.local..."
mkdir -p frontend
cat > frontend/.env.production.local <<EOF
# Frontend Production Configuration
# Generated: $(date)

NEXT_PUBLIC_API_URL=https://${DOMAIN}
NEXT_PUBLIC_ENVIRONMENT=production

# NO CREDENTIALS IN FRONTEND ENVIRONMENT VARIABLES
# User creation is handled through the setup wizard
EOF

echo -e "${GREEN}✅ frontend/.env.production.local created${NC}"
echo ""

# Display credentials summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Production setup completed successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Generated Credentials:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Database Password:"
echo -e "${YELLOW}${DB_PASSWORD}${NC}"
echo ""
echo "JWT Secret (first 20 chars):"
echo -e "${YELLOW}${JWT_SECRET:0:20}...${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🔒 Store these credentials in a secure password manager"
echo "2. 🔒 Never commit .env.production to version control"
echo "3. 🔒 Ensure .env.production is in .gitignore"
echo "4. 🔒 Configure HTTPS/SSL before deployment"
echo "5. 🔒 Update firewall rules to allow only ports 80 and 443"
echo ""
echo "📚 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Review and customize .env.production if needed"
echo "2. Configure SSL/TLS certificates (recommended: Let's Encrypt)"
echo "3. Set up reverse proxy (Nginx or Traefik)"
echo "4. Deploy using: docker-compose -f docker-compose.prod.yml up -d"
echo "5. Run the setup wizard at: https://${DOMAIN}"
echo "6. Create your superadmin user through the wizard"
echo ""
echo "📖 For detailed deployment instructions, see:"
echo "   docs/PRODUCTION_DEPLOYMENT.md"
echo ""
echo "🔍 To verify production readiness, run:"
echo "   ./scripts/verify_production_readiness.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
