# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

WORKDIR /app

# System dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install backend dependencies only
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ============================================================
# Test stage
# ============================================================
FROM base AS test

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY . .
RUN ruff check backend/ || true
RUN pytest backend/tests/ -v --tb=short

# ============================================================
# Production stage — MAHA LAKSHMI Backend + Frontend
# ============================================================
FROM base AS production

COPY backend ./backend
COPY maha-lakshmi ./maha-lakshmi
COPY maha-command-center ./maha-command-center
COPY index.html ./
COPY CNAME ./

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Render provides PORT automatically; respect it at runtime
CMD ["sh", "-c", "python3 -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"]
