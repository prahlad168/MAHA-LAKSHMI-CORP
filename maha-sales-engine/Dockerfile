FROM python:3.11-slim

LABEL maintainer="MAHA LAKSHMI HOLDINGS"
LABEL description="MAHA Sales Engine V1 - Production Container"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 maha && \
    chown -R maha:maha /app
USER maha

# Create directories
RUN mkdir -p logs data cache

# Expose ports
EXPOSE 8000 8001 8002 8003 8004 8005 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); from shared.core_engine import get_engine; engine = get_engine(); print('OK')" || exit 1

# Run application
CMD ["python", "main.py"]
