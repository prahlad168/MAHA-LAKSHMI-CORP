#!/bin/bash
# MAHA Sales Engine V1 - Production Deployment Script
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "MAHA Sales Engine V1 - Deployment"
echo "Environment: $ENVIRONMENT"
echo "=========================================="

# Pre-deployment checks
echo "Running pre-deployment checks..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "ERROR: .env file not found. Copy deploy/env.template to .env and configure."
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/Dockerfile" ]; then
    echo "ERROR: Dockerfile not found"
    exit 1
fi

# Load environment variables
set -a
source "$PROJECT_ROOT/.env"
set +a

# Run migrations
echo "Running database migrations..."
python "$PROJECT_ROOT/deploy/migrations/runner.py"

# Build images
echo "Building Docker images..."
docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" build

# Deploy
echo "Deploying services..."
docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" up -d

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Health check
echo "Running health check..."
python "$PROJECT_ROOT/deploy/health.py" --check

echo "=========================================="
echo "Deployment completed successfully"
echo "=========================================="
