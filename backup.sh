#!/bin/bash
# MAHA LAKSHMI CORP - Database Backup Script
# Usage: ./backup.sh [backup_dir]
# Default backup_dir: ./backups

set -e

BACKUP_DIR=${1:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "MAHA LAKSHMI CORP - Database Backup"
echo "============================================================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup SQLite database
if [ -f "$PROJECT_ROOT/data/maha_lakshmi.db" ]; then
    echo "Backing up SQLite database..."
    cp "$PROJECT_ROOT/data/maha_lakshmi.db" "$BACKUP_DIR/maha_lakshmi_$TIMESTAMP.db"
    echo "Backup saved: $BACKUP_DIR/maha_lakshmi_$TIMESTAMP.db"
fi

# Backup PostgreSQL (if using)
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql://* ]]; then
    echo "Backing up PostgreSQL database..."
    pg_dump "$DATABASE_URL" > "$BACKUP_DIR/maha_lakshmi_$TIMESTAMP.sql"
    echo "Backup saved: $BACKUP_DIR/maha_lakshmi_$TIMESTAMP.sql"
fi

# Compress backups
echo "Compressing backups..."
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C "$BACKUP_DIR" "maha_lakshmi_$TIMESTAMP.db" "maha_lakshmi_$TIMESTAMP.sql" 2>/dev/null || true

# Remove old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.db" -o -name "*.sql" | head -n -7 | xargs rm -f 2>/dev/null || true
find "$BACKUP_DIR" -name "backup_*.tar.gz" | head -n -7 | xargs rm -f 2>/dev/null || true

echo ""
echo "Backup completed successfully!"
echo "Backup location: $BACKUP_DIR"
echo "============================================================"
