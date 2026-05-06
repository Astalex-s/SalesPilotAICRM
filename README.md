# SalesPilot AI CRM

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai&logoColor=white)

Полнофункциональная CRM-система с AI-аналитикой, написанная в качестве
портфолийного проекта. Демонстрирует применение **Clean Architecture**
в реальном full-stack приложении.

---

## Проблема

Команды продаж теряют лидов и сделки из-за отсутствия единого инструмента:

- Лиды теряются в мессенджерах и таблицах — менеджер не видит картину целиком
- Нет понимания, какой лид стоит обработать первым и почему
- Переписка с клиентами не связана с историей сделок
- Руководитель не видит воронку в реальном времени и не знает, кто из менеджеров эффективен
- Уведомления о новых лидах приходят вручную или не приходят вовсе
- Соответствие требованиям GDPR требует ручной обработки каждого запроса

---

## Решение

SalesPilot AI CRM объединяет лидогенерацию, управление сделками и AI-аналитику
в одном приложении:

- **Единая воронка**: все лиды и сделки в одном месте с историей каждого взаимодействия
- **AI-скоринг**: GPT-4o автоматически оценивает каждого лида (0–100), даёт рекомендацию и прогнозирует вероятность закрытия сделки
- **Telegram-уведомления**: мгновенный сигнал о новом лиде или смене этапа сделки прямо в мессенджер менеджера
- **Gmail-интеграция**: входящие и исходящие письма привязаны к лидам и видны в их карточке
- **GDPR из коробки**: анонимизация, экспорт и удаление данных через API одним запросом
- **Открытый API**: любой внешний сервис (чат-бот, форма на сайте, колл-центр) может создавать лидов и передвигать сделки через REST API

---

## Как это работает

### Жизненный цикл лида

```
Создан → Контактирован → Квалифицирован → Конвертирован в сделку
   └──────────────────→ Неквалифицирован ↔ Квалифицирован
```

1. Лид создаётся вручную, через форму на сайте или API (например, из чат-бота)
2. Менеджер меняет статус по мере продвижения: `new → contacted → qualified`
3. AI оценивает лида и рекомендует следующее действие
4. Квалифицированный лид конвертируется в сделку — автоматически создаётся запись
   в воронке, лид переходит в статус `converted`

### Жизненный цикл сделки

```
Создана (open) → перемещается по этапам воронки → Выиграна (won) / Проиграна (lost)
```

1. Сделка создаётся на первом этапе воронки
2. Менеджер или бот перемещает её между этапами drag-and-drop или через API
3. При каждом перемещении — уведомление в Telegram и запись в журнал активностей
4. AI прогнозирует вероятность закрытия и указывает на риски
5. Закрытая как `won` сделка учитывается в выручке на дашборде и в аналитике

### Путь запроса через архитектуру

```
Чат-бот / Браузер / Внешний сервис
         │
         ▼ HTTP
     nginx (80/443)
         │
         ▼
   FastAPI (8000)        ← Interfaces Layer (тонкий контроллер)
         │ DTO
         ▼
  Use Case                ← Application Layer (одна операция)
         │ Entity
         ▼
  Domain                  ← Domain Layer (бизнес-правила, машина состояний)
         │ Repository Interface
         ▼
  Infrastructure          ← PostgreSQL, Redis, OpenAI, Gmail, Telegram, Celery
```

Бизнес-логика полностью изолирована от фреймворков. FastAPI можно заменить
на любой другой транспорт, не трогая use cases и domain.

### AI-функции

| Функция | Что делает |
|---------|-----------|
| Скоринг лида | Оценивает по 100-балльной шкале, объясняет оценку |
| Прогноз сделки | Вычисляет вероятность закрытия, указывает риски |
| Следующее действие | Рекомендует конкретное действие с дедлайном |
| Генерация письма | Пишет персональное outreach-письмо |
| Анализ потерь | Находит паттерны среди проигранных сделок |
| Сводка воронки | Еженедельный AI-дайджест состояния пайплайна |

### Фоновые задачи (Celery)

| Задача | Расписание |
|--------|-----------|
| Синхронизация Gmail | Каждые 10 минут |
| Уведомления о просроченных сделках | Раз в сутки |
| Политика хранения данных (GDPR) | Раз в сутки |

---

## Результат

| Метрика | Значение |
|---------|----------|
| Слоёв архитектуры | 4 (Domain / Application / Infrastructure / Interfaces) |
| Use Cases | 60+ (один файл — одна операция) |
| API-эндпоинтов | 70+ |
| Страниц интерфейса | 14 |
| Языков интерфейса | 2 (RU / EN, переключение без перезагрузки) |

### Что умеет приложение

- **Лиды**: создание, квалификация, машина состояний переходов, теги, категории, комментарии, bulk-import из CSV
- **Сделки**: конвертация из лида, Kanban-доска с drag-and-drop, журнал активностей, вложения файлов
- **Воронки**: неограниченное количество, настройка этапов с цветом и вероятностью закрытия
- **AI-ассистент**: скоринг лида, прогноз сделки, следующее действие, генерация email, анализ потерь
- **Gmail**: OAuth2-авторизация, просмотр входящих, отправка, привязка писем к лидам
- **Telegram-бот**: уведомления о новых лидах и сменах этапов, команды бота
- **Аналитика**: конверсионная воронка, прогноз выручки, разбивка по источникам, отчёт по менеджерам, экспорт CSV
- **Задачи и встречи**: встроенный таск-менеджер и календарь встреч с привязкой к лидам
- **GDPR**: удаление данных, анонимизация, экспорт (Art. 20), append-only audit log, retention policy
- **Авторизация**: JWT access + refresh tokens, роли (admin / manager / sales_rep), сброс пароля по email
- **Мониторинг**: Prometheus + Grafana, Sentry, X-Request-ID в каждом ответе

---

## Стек технологий

| Слой | Технологии |
|------|-----------|
| **Backend** | Python 3.11 · FastAPI 0.115 · SQLAlchemy 2.0 async · Pydantic v2 · Uvicorn · Gunicorn |
| **Архитектура** | Clean Architecture · Repository Pattern · Use Case per operation |
| **База данных** | PostgreSQL 16 · Alembic (миграции) · asyncpg |
| **Кэш / Очередь** | Redis 7 · Celery 5 (воркеры + Beat-расписание) |
| **AI** | OpenAI GPT-4o |
| **Интеграции** | Gmail OAuth2 · Telegram Bot API |
| **Авторизация** | bcrypt · python-jose (JWT) · Redis (инвалидация токенов) |
| **Frontend** | Vite · React 18 · TypeScript 5 · MUI v6 · Zustand v5 · Axios · Recharts |
| **Drag & Drop** | @hello-pangea/dnd (React 18-совместимый форк react-beautiful-dnd) |
| **i18n** | react-i18next · EN + RU |
| **Инфраструктура** | Docker multi-stage · docker-compose · nginx |
| **Тесты** | pytest · pytest-asyncio · Vitest |
| **Мониторинг** | Prometheus · Grafana · Sentry |

---

## Быстрый старт

### Требования

- Docker и Docker Compose v2+
- OpenAI API Key (для AI-функций)

### 1. Клонировать и настроить

```bash
git clone https://github.com/your-username/SalesPilotAICRM.git
cd SalesPilotAICRM
```

Создайте файл `.env`:

```env
# Обязательно
SECRET_KEY=замените-на-случайную-строку-минимум-32-символа
OPENAI_API_KEY=sk-...

# Опционально
TELEGRAM_BOT_TOKEN=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=

# Email (для сброса пароля)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Запустить

```bash
docker compose up --build
```

| Сервис | URL |
|--------|-----|
| Приложение | http://localhost:5173 |
| API Swagger | http://localhost:8000/api/docs |
| API ReDoc | http://localhost:8000/api/redoc |

### 3. Тестовые аккаунты

| Email | Пароль | Роль |
|-------|--------|------|
| admin@example.com | admin123 | admin |
| ivan@example.com | pass123 | manager |

**Admin** — управление пользователями и GDPR.
**Manager** — полный доступ к лидам, сделкам, AI, Gmail, Telegram, аналитике.

---

## Структура проекта

```
SalesPilotAICRM/
├── main.py                      # Точка входа: фабрика FastAPI + lifespan
├── src/
│   ├── domain/                  # Бизнес-сущности и правила (без фреймворков)
│   │   ├── entities/            # Lead, Deal, Pipeline, Stage, Task, Meeting...
│   │   ├── repositories/        # Абстрактные интерфейсы репозиториев
│   │   ├── services/            # Доменные сервисы (конвертация лида в сделку)
│   │   └── value_objects/       # Email, Phone, Money (immutable)
│   ├── application/
│   │   ├── use_cases/           # 60+ use cases: один файл = одна операция
│   │   └── dtos/                # Pydantic v2 входные/выходные модели
│   ├── infrastructure/
│   │   ├── database/            # SQLAlchemy модели + реализации репозиториев
│   │   ├── ai/                  # OpenAI сервис + prompt-шаблоны
│   │   ├── celery/              # Фоновые задачи + Beat-расписание
│   │   ├── gmail/               # Gmail OAuth2
│   │   └── telegram/            # Telegram Bot
│   └── interfaces/api/v1/
│       └── routers/             # FastAPI контроллеры (только вызов use case)
├── tests/
│   ├── unit/                    # Тесты домена и use cases (без I/O)
│   └── integration/             # Тесты репозиториев с БД
├── frontend/                    # React + TypeScript + Vite
│   └── src/
│       ├── api/                 # Axios-клиенты по доменам
│       ├── store/               # Zustand stores
│       ├── pages/               # 14 страниц-маршрутов
│       └── i18n/                # EN + RU переводы
├── alembic/                     # Миграции базы данных
├── monitoring/                  # Prometheus + Grafana конфиги
├── nginx/                       # Конфигурация nginx
├── docker-compose.yml           # Development
├── docker-compose.prod.yml      # Production
└── Dockerfile                   # Multi-stage: builder / production / development
```

---

## Документация

| Документ | Описание |
|----------|----------|
| [docs/API.md](docs/API.md) | Полная API-документация на русском с примерами запросов curl/Python |
| [docs/DEV_SETUP.md](docs/DEV_SETUP.md) | Гайд по локальной разработке (с Docker и без) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Clean Architecture: слои, правила, примеры кода, data flow |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Стратегия тестирования, запуск тестов |
| http://localhost:8000/api/docs | Swagger UI — интерактивное тестирование API |

---

## Лицензия

MIT
