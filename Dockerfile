# SentinelX Dockerfile
# Multi-stage build for production deployment

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libatlas-base-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p evidence/screenshots evidence/videos logs models backups

# Expose ports
EXPOSE 5000

# Health check -- /health is the unauthenticated liveness endpoint.
# /api/v1/health requires a session, so using it here would always fail.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run with Gunicorn for production.
# One worker on purpose: each worker process would start its own camera
# pipelines and detection engine, duplicating inference and fighting over the
# same SQLite file. Scale up with threads, not workers.
# --graceful-timeout must exceed pipeline teardown, which releases every camera
# handle and measured at ~28s with the bundled evidence videos.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", \
     "--timeout", "300", "--graceful-timeout", "60", "--access-logfile", "-", \
     "dashboard.app:app"]
