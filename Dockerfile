# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# Installs Python dependencies into /deps to keep the final image lean.
FROM python:3.11-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/deps -r requirements.txt


# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM python:3.11-slim AS production

# Runtime system dependencies only (no gcc/build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /deps /usr/local

# Non-root user for security
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser

# Copy application source
COPY --chown=appuser:appgroup . .

# Make entrypoint executable
RUN chmod +x scripts/entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]


# ── Stage 3: Development ──────────────────────────────────────────────────────
FROM production AS development

USER root

# Dev extras: reload support
RUN pip install --no-cache-dir watchfiles

USER appuser

# Reset entrypoint so uvicorn runs directly without the prod entrypoint script
ENTRYPOINT []
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
