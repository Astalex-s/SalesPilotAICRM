# Local Development Setup

This guide walks through running SalesPilot AI CRM locally — both with Docker
(recommended) and without it.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | Use `pyenv` or official installer |
| Node.js | 18+ | For the React frontend |
| Docker + Docker Compose | v2+ | Optional but recommended |
| PostgreSQL | 16 | Only needed for no-Docker setup |
| Redis | 7 | Only needed for no-Docker setup |

---

## Option A — Docker Compose (recommended)

This is the fastest path. All infrastructure (Postgres, Redis, backend, frontend)
starts with one command.

### 1. Clone and configure

```bash
git clone https://github.com/your-username/SalesPilotAICRM.git
cd SalesPilotAICRM
cp .env.example .env   # create .env.example if missing — see "Environment Variables" below
```

Edit `.env` and fill in at minimum:

```env
SECRET_KEY=any-random-32-char-string
OPENAI_API_KEY=sk-...
```

### 2. Start in development mode

```bash
docker compose up --build
```

Services started:

| Service | URL |
|---------|-----|
| Backend (FastAPI + hot-reload) | http://localhost:8000 |
| Frontend (Vite + HMR) | http://localhost:5173 |
| Swagger UI | http://localhost:8000/api/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

The backend container mounts the project root as a volume, so code changes
trigger automatic reload via `uvicorn --reload`.

### 3. Stop

```bash
docker compose down
# To also delete database volume:
docker compose down -v
```

---

## Option B — Without Docker

Use this if you prefer to run services directly on your machine.

### 1. Start infrastructure

```bash
# PostgreSQL
pg_ctl start   # or use your OS service manager
createdb salespilot

# Redis
redis-server
```

### 2. Python environment

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment variables

Create `.env` in the project root:

```env
# App
APP_NAME=SalesPilot AI CRM
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/salespilot

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (required for AI features)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Email / SMTP (for password reset — optional in dev)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@salespilot.local
FRONTEND_URL=http://localhost:5173

# Telegram (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_NOTIFICATION_CHAT_ID=
TELEGRAM_WEBHOOK_SECRET=

# Gmail OAuth2 (optional)
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/auth/gmail/callback

# Sentry (optional)
SENTRY_DSN=

# Logging
LOG_LEVEL=DEBUG
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173. It proxies `/api` requests to
`http://localhost:8000` via Vite's `server.proxy` config.

### 7. Start Celery workers (optional)

Celery handles background tasks: Gmail sync, overdue deal notifications,
GDPR retention policy.

```bash
# In a separate terminal
celery -A src.infrastructure.celery.app worker --loglevel=info

# Celery Beat scheduler (for periodic tasks)
celery -A src.infrastructure.celery.app beat --loglevel=info
```

---

## Test Accounts

The first run creates no seed data. Use the register endpoint or run:

```bash
# Create admin account
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123","first_name":"Admin","last_name":"User"}'
```

Then promote to admin via psql:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

Or use the pre-seeded accounts if you restore a dev dump:

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | admin123 | admin |
| ivan@example.com | pass123 | manager |

---

## Running Tests

### Backend

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Specific module
pytest tests/unit/domain/
pytest tests/unit/use_cases/
pytest tests/integration/

# Fast (skip slow integration tests)
pytest -m "not slow"
```

Tests use an in-memory SQLite database — no Postgres needed.
A `.env.test` is not required; test fixtures override settings.

### Frontend

```bash
cd frontend
npm test              # run Vitest once
npm run test:watch    # watch mode
npm run test:coverage # with coverage report
```

---

## Code Style and Linting

### Backend

```bash
# Format
ruff format .

# Lint
ruff check .

# Type checking
mypy src/
```

### Frontend

```bash
cd frontend
npm run lint         # ESLint
npm run type-check   # tsc --noEmit
```

---

## Database Migrations

Migrations are managed with Alembic.

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration (after changing SQLAlchemy models)
alembic revision --autogenerate -m "add column foo to leads"

# Roll back last migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

Migration files live in `alembic/versions/`.

The app applies migrations automatically on startup in both development
(via `asyncio.run_in_executor`) and production (via `scripts/entrypoint.sh`).

---

## Environment Variable Reference

All variables with defaults can be omitted from `.env`. Variables without
defaults are required in production.

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `SECRET_KEY` | `change-me-in-production` | **Prod** | JWT signing key (min 32 chars) |
| `DATABASE_URL` | postgres@localhost/salespilot | **Prod** | asyncpg connection string |
| `REDIS_URL` | redis://localhost:6379/0 | **Prod** | Redis connection string |
| `OPENAI_API_KEY` | `` | AI features | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | No | Model to use for AI features |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | No | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | No | JWT refresh token lifetime |
| `SMTP_HOST` | `` | Password reset | SMTP server hostname |
| `SMTP_USER` | `` | Password reset | SMTP login |
| `SMTP_PASSWORD` | `` | Password reset | SMTP password |
| `TELEGRAM_BOT_TOKEN` | `` | Telegram | Bot token from @BotFather |
| `TELEGRAM_NOTIFICATION_CHAT_ID` | `` | Telegram | Chat ID to send notifications |
| `GMAIL_CLIENT_ID` | `` | Gmail | OAuth2 client ID |
| `GMAIL_CLIENT_SECRET` | `` | Gmail | OAuth2 client secret |
| `SENTRY_DSN` | `` | No | Sentry error tracking DSN |
| `GDPR_RETENTION_DAYS` | `730` | No | Days before auto-deletion of inactive data |
| `LOG_LEVEL` | `INFO` | No | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `DEBUG` | `false` | No | Enables FastAPI debug mode |

---

## Useful Commands

```bash
# Check which migrations are pending
alembic current

# Open psql inside Docker Compose postgres container
docker compose exec db psql -U postgres salespilot

# Open Redis CLI
docker compose exec redis redis-cli

# View backend logs
docker compose logs -f backend

# Rebuild backend image after requirements change
docker compose up --build backend

# Run a single use case test
pytest tests/unit/use_cases/test_create_lead.py -v
```

---

## Project Structure

```
SalesPilotAICRM/
├── main.py                  # FastAPI app factory + lifespan
├── alembic/                 # Migration scripts
├── src/
│   ├── domain/              # Business rules (no framework deps)
│   ├── application/         # Use cases + DTOs
│   ├── infrastructure/      # DB, Redis, AI, Gmail, Telegram, Celery
│   └── interfaces/api/v1/   # FastAPI routers (thin controllers)
├── tests/
│   ├── unit/                # Domain and use case tests (no I/O)
│   └── integration/         # DB-backed repository tests
├── frontend/                # React + TypeScript + Vite
├── docs/                    # Documentation
├── scripts/                 # entrypoint.sh (production startup)
├── monitoring/              # Prometheus + Grafana configs
├── nginx/                   # nginx reverse proxy config
├── docker-compose.yml       # Development compose
├── docker-compose.prod.yml  # Production compose
└── Dockerfile               # Multi-stage: builder / production / development
```

See [ARCHITECTURE.md](../ARCHITECTURE.md) for a detailed description of the
Clean Architecture layers.
