#!/bin/bash
# MAHA Sales Engine V1 - Rollback Script
# Usage: ./rollback.sh [environment]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "MAHA Sales Engine V1 - Rollback"
echo "Environment: $ENVIRONMENT"
echo "=========================================="

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Stop current deployment
echo "Stopping current deployment..."
docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" down

# Restore previous version (if using tags)
echo "Restoring previous version..."
# Add your rollback logic here (e.g., git checkout previous tag)

# Redeploy
echo "Redeploying..."
bash "$SCRIPT_DIR/deploy.sh" "$ENVIRONMENT"

echo "=========================================="
echo "Rollback completed"
echo "=========================================="
