# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Base stage — shared foundation for both dev and prod
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS base

WORKDIR /app

# System deps needed to build some Python packages (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install deps first so this layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Dev stage — used by docker-compose for local development
# ---------------------------------------------------------------------------
FROM base AS dev

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Code is bind-mounted at runtime via docker-compose, so this COPY is mostly
# a fallback (e.g. if someone runs this stage without a volume mount)
COPY app .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------------------------------------------------------------------------
# Prod stage — used for the deployable image
# ---------------------------------------------------------------------------
FROM base AS prod

# Create a non-root user — don't run production containers as root
RUN useradd --create-home --shell /bin/bash appuser

COPY app .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Basic healthcheck so orchestrators (ECS, Cloud Run, k8s) know the app is alive
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]