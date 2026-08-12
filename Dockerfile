# ── Stage 1: Build dependencies ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Production image ─────────────────────────────────────────────────
FROM python:3.11-slim

# Runtime system dependencies (no gcc / build tools needed here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source (respects .dockerignore)
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY celery_worker.py .

# Run as non-root for security
RUN useradd --system --create-home --home-dir /app appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Two Uvicorn workers — override in celery_worker service via 'command:'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
