# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run the unified backend
CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
