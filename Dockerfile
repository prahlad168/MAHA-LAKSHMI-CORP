# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# Test stage — lint + pytest
# ============================================================
FROM base AS test

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY . .

RUN ruff check app/ bot/ tests/
RUN pytest tests/ -v --tb=short

# ============================================================
# Production stage — Autonomous Sales Agent 24/7
# ============================================================
FROM base AS production

COPY app/ ./app/
COPY sales-system/ ./sales-system/
COPY bot/ ./bot/
COPY autonomous-sales-agent/ ./autonomous-sales-agent/
COPY global-sales-agent/ ./global-sales-agent/
COPY global-sales/ ./global-sales/
COPY n8n-workflows/ ./n8n-workflows/

RUN mkdir -p /app/autonomous-sales-agent/logs /app/autonomous-sales-agent/data

EXPOSE 8000

# Start the webhook server which also starts the orchestrator
CMD ["python3", "autonomous-sales-agent/webhooks/server.py"]
