# SalesPilotAI CRM

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-380%20passed-22C55E)
![Coverage](https://img.shields.io/badge/Coverage-81%25-22C55E)

Portfolio CRM project demonstrating **Clean Architecture** in a full-stack AI-powered application.
Manages leads, deals, sales pipelines with AI scoring, Gmail integration, and Telegram notifications.

---

## Features

- **Leads & Deals** — full lifecycle from lead capture to deal close; status state machine with valid transitions
- **Kanban Pipeline** — drag-and-drop board with multi-pipeline support and optimistic UI
- **AI Assistant** — lead scoring, deal forecast, next best action, email generation (OpenAI GPT-4o)
- **Gmail integration** — OAuth2 flow, inbox, compose, link emails to leads
- **Telegram Bot** — notifications on lead creation and deal stage changes
- **GDPR tools** — user data deletion, lead anonymization, append-only audit log
- **Analytics** — conversion funnel, revenue forecast, pipeline breakdown
- **Auth** — JWT access + refresh tokens, role-based access (admin / manager / sales_rep), forgot/reset password
- **i18n** — English and Russian, switchable at runtime

---

## Screenshots

> _Screenshots coming soon. Run the project locally to explore the UI._

| Dashboard | Kanban Pipeline | Lead Detail |
|-----------|----------------|-------------|
| 4 KPI cards, AI insights, charts | Drag-drop stages, pipeline switcher | Activity timeline, AI block |

| AI Assistant | Analytics | Settings |
|--------------|-----------|---------|
| Score, forecast, email gen | Funnel, forecast, breakdown | Language, notifications, privacy |

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | FastAPI · SQLAlchemy 2.0 async · Pydantic v2 · Celery · Redis |
| **AI** | OpenAI (lead scoring · deal forecast · next best action · email generation) |
| **Integrations** | Gmail OAuth2 · Telegram Bot API |
| **Frontend** | Vite · TypeScript · React 18 · MUI v6 · Zustand v5 · Axios · recharts |
| **Drag & Drop** | @hello-pangea/dnd (React 18 compatible) |
| **Database** | PostgreSQL 16 |
| **Auth** | bcrypt · JWT access + refresh tokens · Redis for token invalidation |
| **Infra** | Docker multi-stage build · nginx gateway · docker-compose |
| **Tests** | pytest 380 tests · 81% coverage · Vitest 23 frontend tests |

---

## Architecture

The backend follows **Clean Architecture** with strict layer separation:

```
src/
├── domain/              # Entities, value objects, repository interfaces
│   ├── entities/        # Lead, Deal, Pipeline, Stage, Activity, User
│   ├── repositories/    # Abstract repository interfaces
│   ├── services/        # Domain services (lead conversion)
│   └── value_objects/   # Email, Money, Phone
├── application/
│   ├── use_cases/       # One class per use case, single execute() method
│   └── dtos/            # Pydantic v2 input/output models
├── infrastructure/
│   ├── database/        # SQLAlchemy models + repository implementations
│   ├── ai/              # OpenAI service + prompt templates
│   ├── auth/            # bcrypt + JWT
│   ├── gmail/           # Gmail OAuth2 service
│   ├── telegram/        # Telegram Bot service
│   └── celery/          # Background task workers
└── interfaces/api/v1/
    └── routers/         # FastAPI controllers — only call use_case.execute()
```

**Key rules enforced:**
- Controllers never contain business logic — only `use_case.execute()` calls
- Domain entities own state transitions (e.g. `lead.qualify()` validates the transition)
- Activity log is append-only (`delete()` raises `NotImplementedError`)
- All layer boundaries use Pydantic v2 DTOs

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- An OpenAI API key (for AI features)
- Optional: Gmail OAuth credentials, Telegram Bot token

### 1. Clone and configure

```bash
git clone https://github.com/your-username/SalesPilotAICRM.git
cd SalesPilotAICRM
cp .env.example .env
```

Edit `.env` and set required values:

```env
# Required
SECRET_KEY=your-secret-key-min-32-chars
POSTGRES_PASSWORD=your-db-password
OPENAI_API_KEY=sk-...

# Optional — AI features will be mocked without these
TELEGRAM_BOT_TOKEN=...
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Start

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Open **http://localhost** in your browser.

### 3. Database migration (first run only)

The tables are created automatically on startup via `Base.metadata.create_all`.

If you recreate the DB container, run this SQL manually:

```sql
ALTER TABLE stages ADD COLUMN IF NOT EXISTS color VARCHAR(7) NULL;
```

---

## Test Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | admin123 | admin |
| ivan@example.com | pass123 | manager |

**Admin** has access to Users and GDPR pages.
**Manager** has full access to leads, deals, pipeline, AI, Gmail, Telegram, Analytics.

---

## API Documentation

FastAPI auto-generates interactive docs:

- **Swagger UI** — http://localhost/api/docs
- **ReDoc** — http://localhost/api/redoc

### Key endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/login | Login → JWT tokens |
| POST | /auth/register | Register new user |
| GET | /auth/me | Current user info |
| GET/POST | /leads | List / Create lead |
| GET/PATCH | /leads/{id} | Get / Update lead status |
| GET/POST | /deals | List / Create deal |
| PATCH | /deals/{id}/stage | Move deal to stage |
| GET | /pipelines/{id} | Pipeline with stages |
| POST | /ai/leads/{id}/score | AI lead score |
| POST | /ai/deals/{id}/forecast | AI deal forecast |
| POST | /ai/leads/{id}/generate-email | AI email generation |
| GET | /analytics | Analytics overview |
| GET | /analytics/forecast | Revenue forecast |
| GET | /auth/gmail | Start Gmail OAuth |
| POST | /telegram/set-webhook | Register Telegram webhook |
| POST | /gdpr/leads/{id}/anonymize | Anonymize lead data |
| GET | /gdpr/audit-log | GDPR audit log |

---

## Running Tests

```bash
# Backend tests
pip install -r requirements.txt
pytest --cov=src --cov-report=term-missing

# Frontend tests
cd frontend
npm install
npm test
```

---

## Project Structure (Frontend)

```
frontend/src/
├── api/          # Axios API clients per domain
├── store/        # Zustand stores (auth, kanban, leads, notifications, settings)
├── types/        # TypeScript interfaces for all domain models
├── i18n/         # EN + RU translation files
├── components/   # Reusable UI components (kanban, lead, notifications, profile)
└── pages/        # 14 route pages
```

---

## Roadmap

- [ ] Leads in pipeline — drag unqualified leads into stages to auto-promote to deals
- [ ] Real-time notifications via WebSocket / SSE
- [ ] PATCH /users/me — save profile changes to backend
- [ ] Dark mode
- [ ] Mobile responsive layout
- [ ] Bulk lead import from CSV
- [ ] GitHub Actions CI/CD
- [ ] Alembic migrations (replace create_all)
- [ ] E2E tests (Playwright)

---

## License

MIT
