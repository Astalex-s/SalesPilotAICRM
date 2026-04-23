#!/bin/bash
# Production entrypoint for the SalesPilotAI CRM backend.
# Runs database migrations (if alembic is configured), then starts Gunicorn.

set -euo pipefail

echo "==> SalesPilotAI CRM starting up..."

# ── Database migrations ────────────────────────────────────────────────────────
if [ -f "alembic.ini" ]; then
    echo "==> Running Alembic migrations..."
    alembic upgrade head
    echo "==> Migrations complete."
else
    echo "==> No alembic.ini found — skipping migrations."
fi

# ── Start Gunicorn ────────────────────────────────────────────────────────────
echo "==> Starting Gunicorn (workers=${GUNICORN_WORKERS:-4})..."

exec gunicorn main:app \
    --worker-class   uvicorn.workers.UvicornWorker \
    --workers        "${GUNICORN_WORKERS:-4}" \
    --bind           "0.0.0.0:8000" \
    --timeout        "${GUNICORN_TIMEOUT:-120}" \
    --keep-alive     5 \
    --access-logfile "-" \
    --error-logfile  "-" \
    --log-level      "${LOG_LEVEL:-info}"
