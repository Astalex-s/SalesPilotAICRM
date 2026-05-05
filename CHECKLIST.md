# SalesPilotAI CRM — Project Checklist

> Статус: **В разработке** | Последнее обновление: 2026-05-04
> Стек: FastAPI · React 18 · PostgreSQL · Redis · Docker · OpenAI · Gmail · Telegram

---

## БЭКЕНД

### Архитектура и ядро
- [x] Clean Architecture (Domain → Application → Infrastructure → Interfaces)
- [x] Доменные сущности: Lead, Deal, Pipeline, Stage, Activity, User
- [x] Репозитории (абстракции + SQLAlchemy реализации)
- [x] Модель воронки и этапов (Pipeline / Stage)
- [x] Append-only лог активности
- [x] Pydantic v2 DTO на всех границах
- [x] FastAPI async + SQLAlchemy 2.0 async
- [x] Alembic миграции в lifespan (заменил create_all — см. раздел Инфраструктура)

### Аутентификация и роли
- [x] JWT (bcrypt + токен доступа)
- [x] Регистрация / Логин / GET /auth/me
- [x] Роли: admin, manager, sales_rep
- [x] Зависимости: get_current_user, require_admin, require_manager
- [x] PATCH /users/{id}/role (только admin)
- [x] Refresh-токены (access + refresh, автоматический refresh в axios interceptor)
- [x] Сброс пароля по email

### Лиды (Leads)
- [x] CRUD лидов
- [x] Статусы: new → contacted → qualified → unqualified → converted
- [x] Источники лида (website, referral, cold_call и т.д.)
- [x] Конвертация лида в сделку (POST /deals)
- [x] Bulk-импорт лидов из CSV

### Сделки (Deals)
- [x] Создание сделки из квалифицированного лида
- [x] Список сделок с фильтрацией (pipeline_id, stage_id, owner_id)
- [x] Смена этапа (PATCH /deals/{id}/stage)
- [x] Telegram-уведомление при смене этапа (фоновая задача)
- [x] PATCH /users/me — обновление профиля (имя + фамилия)
- [x] POST /users/me/password — смена пароля (проверка текущего пароля)
- [x] Закрытие сделки (won / lost) — PATCH /deals/{id}/close + кнопки Won/Lost в таблице сделок
- [x] Прикрепление файлов к сделке (upload/list/delete/download + DealAttachmentsDialog)

### Воронка (Pipeline)
- [x] GET /pipelines/{id} — воронка с этапами
- [x] Создание / редактирование / удаление воронок через API (POST/PATCH/DELETE /pipelines)
- [x] Несколько воронок для одного аккаунта (GET /pipelines, switcher в PipelinePage)
- [x] CRUD этапов через API (POST/PATCH/DELETE /pipelines/{id}/stages)
- [x] Цвет этапа (color field в Stage + color picker 8 preset + null)
- [x] Редактирование названия этапа воронки

### AI-функции
- [x] Оценка лида (POST /ai/leads/{id}/score)
- [x] Прогноз сделки (POST /ai/deals/{id}/forecast)
- [x] Следующее лучшее действие (POST /ai/{type}/{id}/next-action)
- [x] Генерация email (POST /ai/leads/{id}/generate-email)
- [x] AI-анализ потерянных сделок (batch) — POST /ai/deals/lost-analysis
- [x] AI-сводка по воронке (weekly digest) — GET /ai/pipeline/{id}/weekly-digest

### Gmail
- [x] OAuth2 авторизация (GET /auth/gmail, callback)
- [x] Статус подключения (GET /auth/gmail/status)
- [x] Получение писем (GET /emails)
- [x] Отправка письма (POST /emails/send)
- [x] Привязка письма к лиду (POST /emails/{id}/link-lead)
- [x] Автоматическая синхронизация входящих через Celery
- [x] Треды (отображение цепочки писем)

### Telegram
- [x] Уведомление при создании лида
- [x] Уведомление при смене этапа сделки
- [x] Регистрация webhook (POST /telegram/set-webhook)
- [x] Статус бота (GET /telegram/status)
- [x] Приём команд от бота (/leads, /deals — ответ в чат)
- [x] Уведомление при создании новой сделки

### GDPR
- [x] Удаление всех данных пользователя (POST /gdpr/users/{id}/delete)
- [x] Анонимизация лида (POST /gdpr/leads/{id}/anonymize)
- [x] Журнал аудита (GET /gdpr/audit-log)
- [x] Экспорт данных пользователя (Art. 20 — Right to Portability)
- [x] Автоматическое удаление по расписанию (retention policy)

### Аналитика
- [x] Обзор (GET /analytics) — win rate, avg deal, closed revenue, forecast
- [x] Прогноз выручки (GET /analytics/forecast)
- [x] Детальный отчёт по менеджерам
- [x] Экспорт отчётов в CSV / PDF

### Celery / фоновые задачи
- [x] Telegram-уведомления как фоновые задачи
- [x] Периодическая синхронизация Gmail (Celery Beat, каждые 10 мин)
- [x] GDPR retention policy (Celery Beat, раз в сутки)
- [x] Напоминания по сделкам (overdue deals)
- [x] Еженедельный AI-дайджест (on-demand через GET /ai/pipeline/{id}/weekly-digest)

### Тестирование бэкенда
- [x] 692 теста, 90% покрытие
- [x] Интеграционные тесты API (TestClient + тестовая БД)
- [x] Покрытие до 90%+

---

## ФРОНТЕНД

### Архитектура
- [x] Vite + TypeScript + React 18
- [x] MUI v6, Zustand v5, Axios
- [x] Дизайн-система Stitch (navy #0D2144, cyan #00A8E8, bg #F7F9FC)
- [x] i18n: react-i18next, EN + RU, все строки переведены
- [x] Axios interceptor (Bearer token, 401 → logout)
- [x] ProtectedRoute, роль-зависимый доступ
- [x] Sidebar (64px / 220px), TopBar, AppLayout
- [x] Drag-and-drop совместим с React 18 (@hello-pangea/dnd вместо react-beautiful-dnd)

### Страницы
- [x] Login / Register (двухколоночный макет, OAuth-заглушки)
- [x] ForgotPassword / ResetPassword (форма → письмо → новый пароль)
- [x] Dashboard (4 KPI-карты, графики сделок/лидов, AI Insights, Pipeline Health)
- [x] Leads (таблица, поиск, фильтр по статусу, пагинация, диалог добавления)
- [x] Lead Detail (3 колонки: инфо, таймлайн активности, AI-блок)
- [x] Pipeline / Kanban (drag-drop, оптимистичный UI, скелетон, итоги)
- [x] Deals (таблица с реальным API, статус-бейджи, привязка к воронке)
- [x] Analytics (воронка конверсии, прогноз выручки, разбивка по воронкам)
- [x] Gmail (OAuth-флоу, таблица писем, Compose, привязка к лиду)
- [x] Telegram (статус бота, настройка webhook, список возможностей)
- [x] GDPR (удаление данных, анонимизация, журнал аудита)
- [x] Users & Roles (таблица, смена роли, карточки ролей)
- [x] AI Assistant (табы: оценка лида, прогноз сделки, генератор писем, анализ проигрышей, дайджест воронки)
- [x] Settings (язык, внешний вид, уведомления, приватность)

### Функциональность
- [x] Add Deal диалог (конвертация лида → сделка)
  - [x] Форма: лид, название, сумма, валюта, этап, дата закрытия
  - [x] Предупреждение если лид не квалифицирован + кнопка «Qualify Lead»
  - [x] После создания: AI-оценка, отправка email, Telegram-инфо
  - [x] Открывается из кнопки «+» в колонках воронки с предвыбором этапа
- [x] Kanban drag-drop с rollback при ошибке (карточки не меняют размер при drag)
- [x] Переключатель воронок в Sidebar — flyout-меню со списком всех воронок
- [x] Квалификация лида прямо из LeadInfoCard (кликабельный бейдж статуса → меню переходов)
- [x] Compose email с AI-генерацией
- [x] Уведомления в реальном времени (WebSocket / SSE)
- [x] Уведомления: колокольчик с панелью (email, deal, lead, system + badge + dismiss + mark all read)
- [x] Поиск по всему приложению (TopBar search pill)
- [x] Профиль пользователя: смена имени, цвет аватара, смена пароля (UI)
- [x] Страница настроек приложения (/settings — язык, внешний вид, уведомления, приватность)
- [x] Dark mode

### Kanban UI (добавлено 2026-05-02)
- [x] Убран серо-голубой фон колонок — карточки лежат на фоне страницы
- [x] Пустой этап: пунктирная рамка по размеру карточки вместо текста
- [x] Кнопка «+» внизу каждой колонки — открывает AddDealDialog с нужным этапом

### Лиды в воронке (добавлено 2026-05-03)
- [x] LeadCard — draggable карточка лида (имя, компания/email, статус-бейдж, кнопка перехода)
- [x] LeadPoolColumn — нулевая колонка «Нераспределённые» (droppableId="leads-pool")
- [x] useKanbanStore: leadsPool, loadLeadsPool, addLeadToPool, reorderLeadsPool, promoteLeadToDeal
- [x] Drag лида в этап → auto-qualify + create deal (optimistic + rollback)
- [x] Кнопка «+» в колонках показывает меню «Добавить лида / Добавить сделку»
- [x] AddLeadDialog — создание лида прямо из воронки (components/leads/)

### Тестирование фронтенда
- [x] 48 тестов (Vitest)
- [x] Покрыть Add Deal диалог тестами (25 unit-тестов AddDealDialog)
- [x] E2E тесты (Playwright) — auth, dashboard, leads, settings

---

## ИНФРАСТРУКТУРА

### Docker
- [x] Multi-stage build (frontend, backend)
- [x] nginx как gateway (:80)
- [x] docker-compose.prod.yml
- [x] Сервисы: nginx, frontend, backend, celery_worker, celery_beat, postgres, redis
- [x] Health checks в docker-compose
- [x] docker-compose.dev.yml с hot reload
- [x] Alembic миграции вместо create_all (alembic.ini + async env.py + 0001_initial)

### CI/CD
- [x] GitHub Actions: lint + тесты при push
- [x] Автодеплой на сервер при merge в main
- [x] Docker Hub или GHCR для образов

### Мониторинг
- [x] Sentry (frontend + backend)
- [ ] Structured logging (JSON) в бэкенде
- [ ] Prometheus + Grafana (опционально)

---

## ПРОДУКТ / POLISH

### Качество UI
- [x] Пустые состояния (empty state) на всех страницах с иллюстрацией
- [x] Анимации переходов между страницами
- [x] Мобильная адаптация (responsive) — мобильный Drawer, hamburger, responsive padding, overflowX таблиц
- [x] Skeleton loading на всех загружаемых секциях (некоторые есть)

### Бизнес-функции
- [ ] Комментарии к сделке / лиду
- [ ] Теги и категории лидов
- [ ] Задачи (Tasks) — назначение на менеджера, дедлайн
- [ ] Календарь встреч
- [ ] Дашборд менеджера (обзор команды)
- [x] Управление несколькими воронками через UI (PipelineManagerDialog + Sidebar switcher)

### Документация
- [x] README.md — запуск проекта, стек, скриншоты
- [ ] API документация (Swagger уже есть через FastAPI)
- [ ] Гайд по локальной разработке (dev setup)
- [ ] ARCHITECTURE.md — описание Clean Architecture

---

## ТЕКУЩЕЕ ПОЛОЖЕНИЕ

**Где мы сейчас (2026-05-04):**
Проект в высокой степени готовности для портфолио. Всё ядро реализовано и задеплоено.

Бэкенд (полностью):
- Clean Architecture, все домены, JWT Auth + Refresh, роли, сброс пароля
- AI: оценка лидов, прогноз сделки, NBA, генератор писем, анализ потерь, дайджест воронки
- Gmail: OAuth, sync через Celery, треды, отправка, привязка к лиду
- Telegram: webhook, уведомления (лид/сделка/смена этапа), команды /leads /deals
- GDPR: удаление, анонимизация, экспорт (Art. 20), retention policy, журнал аудита
- Celery Beat: Gmail sync (10 мин) + GDPR retention (24ч)
- 692 теста, 90% покрытие, интеграционные тесты

Фронтенд (полностью):
- 14 страниц, дизайн-система, i18n EN+RU, dark mode, мобильная адаптация
- Kanban drag-drop, лиды в воронке, drag-в-этап → auto-qualify + create deal
- Gmail: flat/threads view, sync, compose, привязка
- AI Assistant: 5 табов
- 48 Vitest тестов + Playwright E2E (auth, dashboard, leads, settings)

Инфраструктура:
- Docker: 7 сервисов (nginx, frontend, backend, celery_worker, celery_beat, postgres, redis)
- Alembic миграции (2 ревизии), health checks, docker-compose.dev.yml
- GitHub Actions CI/CD

**Остаток (незакрытые пункты):**
- CI/CD: ✓ GHCR + SSH autodeploy — готово (.github/workflows/cd.yml)
- Мониторинг: Sentry, Structured logging, Prometheus+Grafana
- UI polish: ✓ skeleton на всех секциях — готово
- Бизнес: комментарии к сделкам, теги лидов, задачи, календарь
- Документация: ARCHITECTURE.md, dev setup guide

**Следующий логичный шаг (для портфолио):**
1. ARCHITECTURE.md — описание Clean Architecture для рекрутёров
2. Structured logging (JSON) в бэкенде
3. Skeleton loading на оставшихся секциях

---

*Файл поддерживается вручную. Отмечай [x] по мере выполнения.*
