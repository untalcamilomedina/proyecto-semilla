#!/bin/bash
# Automated Database Backup Script
# Creates compressed backups with timestamp and retains last N backups

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=7
MAX_BACKUPS=10
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="proyecto_semilla_backup_${TIMESTAMP}.sql.gz"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🗄️  Proyecto Semilla - Database Backup"
echo "======================================"
echo ""

# Load environment variables
if [ -f .env.production ]; then
    source .env.production
elif [ -f .env ]; then
    source .env
else
    echo -e "${RED}❌ No environment file found (.env or .env.production)${NC}"
    exit 1
fi

# Verify required variables
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}❌ Missing database configuration${NC}"
    echo "Required: DB_NAME, DB_USER, DB_PASSWORD"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "📋 Backup Configuration:"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Backup Dir: $BACKUP_DIR"
echo "   Retention: $RETENTION_DAYS days / $MAX_BACKUPS backups"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Check if database container is running
if ! docker ps | grep -q proyecto_semilla_db; then
    echo -e "${RED}❌ Database container is not running${NC}"
    exit 1
fi

echo -e "${YELLOW}🔄 Starting backup...${NC}"

# Create backup using pg_dump
docker exec proyecto_semilla_db pg_dump \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ] && [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup created successfully${NC}"
    echo "   File: $BACKUP_FILE"
    echo "   Size: $BACKUP_SIZE"
    echo ""
else
    echo -e "${RED}❌ Backup failed${NC}"
    exit 1
fi

# Clean up old backups (by date)
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "proyecto_semilla_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
DELETED_BY_DATE=$?

# Keep only last N backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "proyecto_semilla_backup_*.sql.gz" -type f | wc -l)
if [ $BACKUP_COUNT -gt $MAX_BACKUPS ]; then
    BACKUPS_TO_DELETE=$((BACKUP_COUNT - MAX_BACKUPS))
    find "$BACKUP_DIR" -name "proyecto_semilla_backup_*.sql.gz" -type f -printf '%T+ %p\n' | \
        sort | \
        head -n $BACKUPS_TO_DELETE | \
        cut -d' ' -f2 | \
        xargs rm -f
    echo -e "${GREEN}✅ Deleted $BACKUPS_TO_DELETE old backup(s)${NC}"
fi

# List current backups
echo ""
echo "📦 Current Backups:"
find "$BACKUP_DIR" -name "proyecto_semilla_backup_*.sql.gz" -type f -printf '%T+ %p %s\n' | \
    sort -r | \
    while read line; do
        BACKUP_DATE=$(echo $line | awk '{print $1}')
        BACKUP_PATH=$(echo $line | awk '{print $2}')
        BACKUP_SIZE=$(echo $line | awk '{print $3}')
        BACKUP_SIZE_MB=$(echo "scale=2; $BACKUP_SIZE / 1024 / 1024" | bc)
        BACKUP_NAME=$(basename $BACKUP_PATH)
        echo "   • $BACKUP_NAME (${BACKUP_SIZE_MB}MB)"
    done

echo ""
echo -e "${GREEN}✅ Backup completed successfully${NC}"
echo ""

# Show restore command
echo "💡 To restore this backup, run:"
echo "   gunzip -c $BACKUP_DIR/$BACKUP_FILE | docker exec -i proyecto_semilla_db psql -U $DB_USER -d $DB_NAME"
echo ""

exit 0
