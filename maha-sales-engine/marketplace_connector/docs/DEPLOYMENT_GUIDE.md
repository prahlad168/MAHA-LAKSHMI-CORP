# MAHA SALES ENGINE V1 - Deployment Guide

Deploy marketplace connector to production.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+ or SQLite
- 2GB RAM minimum
- 10GB storage

## Environment Variables

```bash
# Required
MARKETPLACE_DB_URL=postgresql://user:pass@host/db
GUMROAD_API_KEY=your-api-key
WEBHOOK_SECRET=your-webhook-secret

# Optional
LOG_LEVEL=INFO
WORKER_CONCURRENCY=4
RETRY_MAX_ATTEMPTS=3
CACHE_TTL=300
```

## Installation

```bash
# Clone repository
git clone https://github.com/your-org/maha-sales-engine.git
cd maha-sales-engine

# Install dependencies
pip install -r requirements.txt

# Run migrations
python3 -m marketplace_connector.db.migrate

# Start API server
uvicorn marketplace_connector.api.routes:app --host 0.0.0.0 --port 8000
```

## Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "marketplace_connector.api.routes:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] API key secured
- [ ] Webhook secret configured
- [ ] Health endpoint responding
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Backup strategy in place

## Scaling

- Use multiple API workers
- Separate queue workers for retries
- Database connection pooling
- Redis for caching
- CDN for static assets

## Monitoring

- Health endpoint: `/marketplace/health`
- Metrics endpoint: `/marketplace/metrics`
- Log aggregation: Structured JSON logs
- Alerts: Failed publications, queue depth, provider latency
