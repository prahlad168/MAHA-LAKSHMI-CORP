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
# Production stage — FastAPI + Sales System
# ============================================================
FROM base AS production

COPY app/ ./app/
COPY sales-system/ ./sales-system/
COPY app/payments/ ./app/payments/
COPY bot/ ./bot/
RUN mkdir -p /app/dev-agent /root/.molty-royale /app/sales-system

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
