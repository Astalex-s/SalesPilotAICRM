# API-документация — SalesPilot AI CRM

## Интерактивная документация (Swagger)

FastAPI автоматически генерирует актуальную документацию:

| URL | Описание |
|-----|----------|
| `http://localhost:8000/api/docs` | Swagger UI — тестирование прямо в браузере |
| `http://localhost:8000/api/redoc` | ReDoc — удобное чтение |
| `http://localhost:8000/api/openapi.json` | OpenAPI JSON-схема |

При деплое через nginx замените `8000` на `80` (или ваш домен).

---

## Базовый URL

```
http://localhost:8000/api/v1
```

Все примеры в документации используют этот базовый URL. В production замените
его на адрес вашего сервера.

---

## Аутентификация

### Как получить токен

Все эндпоинты кроме `/auth/register`, `/auth/login`, `/auth/forgot-password`
и `/auth/reset-password` требуют JWT-токен в заголовке:

```
Authorization: Bearer <access_token>
```

**Шаг 1 — Получить токен:**

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ivan@example.com", "password": "pass123"}'
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Шаг 2 — Использовать токен в каждом запросе:**

```bash
curl -s http://localhost:8000/api/v1/leads \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Срок жизни токенов

| Тип | Срок | Что делать по истечении |
|-----|------|------------------------|
| `access_token` | 30 минут | Обновить через `/auth/refresh` |
| `refresh_token` | 30 дней | Выполнить повторный вход `/auth/login` |

### Обновление токена

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

Возвращает новую пару `access_token` + `refresh_token`.

### Роли пользователей

| Роль | Значение | Доступ |
|------|----------|--------|
| `admin` | Администратор | Полный доступ: пользователи, GDPR, все данные |
| `manager` | Менеджер | Лиды, сделки, воронки, AI, аналитика, Gmail, Telegram |
| `sales_rep` | Менеджер по продажам | Собственные лиды и сделки |

---

## Форматы данных

### UUID

Все идентификаторы — UUID v4. Пример: `"550e8400-e29b-41d4-a716-446655440000"`

### Дата и время

Все временные поля в формате ISO 8601 UTC:
```
"2025-06-15T14:30:00Z"
"2025-06-15T14:30:00.123456+00:00"
```

### Деньги

Сумма сделки передаётся двумя полями:
```json
{
  "deal_value_amount": "50000.00",
  "deal_value_currency": "USD"
}
```

### Ответы об ошибках

Все ошибки возвращают одинаковую структуру:
```json
{ "detail": "Лид с email test@example.com уже существует." }
```

| HTTP-код | Когда возникает |
|----------|----------------|
| `400` | Неверный статус перехода, дублирующий запрос, закрытая сделка |
| `401` | Токен отсутствует или недействителен |
| `403` | Недостаточно прав (роль не подходит) |
| `404` | Ресурс не найден |
| `409` | Конфликт: ресурс уже существует (дубль email) |
| `422` | Ошибка валидации Pydantic (неверный формат тела запроса) |
| `503` | Внешний сервис недоступен (OpenAI, Gmail, Telegram) |

---

## Сценарий: создать лида и провести по воронке

Это основной сценарий работы с CRM через API. Например, для чат-бота,
который принимает заявки от клиентов и автоматически создаёт лидов и сделки.

### Шаг 1 — Авторизоваться

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan@example.com",
    "password": "pass123"
  }'
```

Сохраните `access_token` из ответа. Все следующие запросы используют его.

### Шаг 2 — Получить ID воронки и этапов

```bash
curl -s http://localhost:8000/api/v1/pipelines \
  -H "Authorization: Bearer <access_token>"
```

```json
[
  {
    "id": "a1b2c3d4-0000-0000-0000-000000000001",
    "name": "Основная воронка",
    "owner_id": "...",
    "is_active": true,
    "stages": [
      { "id": "s1000000-0000-0000-0000-000000000001", "name": "Новый лид", "order": 1 },
      { "id": "s2000000-0000-0000-0000-000000000002", "name": "Переговоры", "order": 2 },
      { "id": "s3000000-0000-0000-0000-000000000003", "name": "Коммерческое предложение", "order": 3 },
      { "id": "s4000000-0000-0000-0000-000000000004", "name": "Закрытие", "order": 4 }
    ]
  }
]
```

Запомните `id` воронки и `id` нужного этапа.

### Шаг 3 — Узнать свой ID пользователя (для owner_id)

```bash
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

```json
{
  "id": "u0000000-0000-0000-0000-000000000042",
  "email": "ivan@example.com",
  "first_name": "Иван",
  "last_name": "Петров",
  "role": "manager",
  "is_active": true
}
```

### Шаг 4 — Создать лида

```bash
curl -s -X POST http://localhost:8000/api/v1/leads \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Анна",
    "last_name": "Иванова",
    "email": "anna@acme.com",
    "phone": "+79001234567",
    "company": "Acme Corp",
    "source": "website",
    "owner_id": "u0000000-0000-0000-0000-000000000042",
    "tags": ["горячий", "enterprise"],
    "category": "b2b",
    "target_pipeline_name": "Основная воронка"
  }'
```

```json
{
  "id": "ld000001-0000-0000-0000-000000000001",
  "first_name": "Анна",
  "last_name": "Иванова",
  "full_name": "Анна Иванова",
  "email": "anna@acme.com",
  "owner_id": "u0000000-0000-0000-0000-000000000042",
  "status": "new",
  "source": "website",
  "phone": "+79001234567",
  "company": "Acme Corp",
  "notes": null,
  "converted_deal_id": null,
  "tags": ["горячий", "enterprise"],
  "category": "b2b",
  "target_pipeline_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "created_at": "2025-06-15T10:00:00Z",
  "updated_at": "2025-06-15T10:00:00Z"
}
```

Сохраните `id` лида.

### Шаг 5 — Квалифицировать лида

Лид должен перейти в статус `qualified` перед конвертацией в сделку.

```bash
curl -s -X PATCH http://localhost:8000/api/v1/leads/ld000001-0000-0000-0000-000000000001 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "qualified"}'
```

```json
{
  "id": "ld000001-0000-0000-0000-000000000001",
  "status": "qualified",
  ...
}
```

### Шаг 6 — Конвертировать лида в сделку

```bash
curl -s -X POST http://localhost:8000/api/v1/deals \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "ld000001-0000-0000-0000-000000000001",
    "stage_id": "s1000000-0000-0000-0000-000000000001",
    "pipeline_id": "a1b2c3d4-0000-0000-0000-000000000001",
    "deal_title": "Acme Corp — Enterprise план",
    "deal_value_amount": "120000.00",
    "deal_value_currency": "RUB",
    "performed_by_id": "u0000000-0000-0000-0000-000000000042"
  }'
```

```json
{
  "id": "dl000001-0000-0000-0000-000000000001",
  "title": "Acme Corp — Enterprise план",
  "owner_id": "u0000000-0000-0000-0000-000000000042",
  "stage_id": "s1000000-0000-0000-0000-000000000001",
  "pipeline_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "value_amount": "120000.00",
  "value_currency": "RUB",
  "status": "open",
  "source_lead_id": "ld000001-0000-0000-0000-000000000001",
  "contact_name": null,
  "company": null,
  "expected_close_date": null,
  "closed_at": null,
  "created_at": "2025-06-15T10:05:00Z",
  "updated_at": "2025-06-15T10:05:00Z"
}
```

Лид автоматически переходит в статус `converted`.

### Шаг 7 — Передвинуть сделку по воронке

```bash
curl -s -X PATCH http://localhost:8000/api/v1/deals/dl000001-0000-0000-0000-000000000001/stage \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_stage_id": "s2000000-0000-0000-0000-000000000002",
    "pipeline_id": "a1b2c3d4-0000-0000-0000-000000000001",
    "performed_by_id": "u0000000-0000-0000-0000-000000000042"
  }'
```

```json
{
  "id": "dl000001-0000-0000-0000-000000000001",
  "stage_id": "s2000000-0000-0000-0000-000000000002",
  "status": "open",
  ...
}
```

### Шаг 8 — Закрыть сделку

```bash
curl -s -X PATCH http://localhost:8000/api/v1/deals/dl000001-0000-0000-0000-000000000001/close \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"outcome": "won"}'
```

```json
{
  "id": "dl000001-0000-0000-0000-000000000001",
  "status": "won",
  "closed_at": "2025-06-15T18:00:00Z",
  ...
}
```

---

## Аутентификация — `/auth`

### POST /auth/register — Регистрация

```
POST /api/v1/auth/register
Content-Type: application/json
```

**Тело запроса:**

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `first_name` | string | Да | Имя (1–100 символов) |
| `last_name` | string | Да | Фамилия (1–100 символов) |
| `email` | string | Да | Email (уникальный) |
| `password` | string | Да | Пароль (минимум 6 символов) |
| `role` | string | Нет | `admin` / `manager` / `sales_rep` (по умолчанию `sales_rep`) |

```json
{
  "first_name": "Иван",
  "last_name": "Петров",
  "email": "ivan@example.com",
  "password": "secret123"
}
```

**Ответ 201:**
```json
{
  "id": "uuid",
  "first_name": "Иван",
  "last_name": "Петров",
  "email": "ivan@example.com",
  "role": "sales_rep",
  "is_active": true
}
```

---

### POST /auth/login — Вход

```
POST /api/v1/auth/login
Content-Type: application/json
```

| Поле | Тип | Обязательно |
|------|-----|-------------|
| `email` | string | Да |
| `password` | string | Да |

```json
{ "email": "ivan@example.com", "password": "secret123" }
```

**Ответ 200:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Ошибки:** `401` — неверный email или пароль.

---

### POST /auth/refresh — Обновление токена

```
POST /api/v1/auth/refresh
Content-Type: application/json
```

```json
{ "refresh_token": "eyJhbGci..." }
```

**Ответ 200:** новая пара `access_token` + `refresh_token`.

---

### POST /auth/forgot-password — Сброс пароля (шаг 1)

Отправляет письмо со ссылкой для сброса пароля. Всегда возвращает `204`
(безопасность от перебора пользователей).

```json
{ "email": "ivan@example.com" }
```

---

### POST /auth/reset-password — Сброс пароля (шаг 2)

Токен из письма действует 15 минут и однократно.

```json
{
  "token": "токен-из-письма",
  "new_password": "newSecret456"
}
```

---

### GET /auth/me — Текущий пользователь

```
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Ответ 200:**
```json
{
  "id": "uuid",
  "first_name": "Иван",
  "last_name": "Петров",
  "email": "ivan@example.com",
  "role": "manager",
  "is_active": true
}
```

---

## Пользователи — `/users`

### GET /users — Список пользователей

> Только `admin`.

```
GET /api/v1/users
Authorization: Bearer <token>
```

**Ответ 200:** массив объектов `UserOutput`.

---

### PATCH /users/me — Обновить профиль

```
PATCH /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "first_name": "Иван",
  "last_name": "Сидоров"
}
```

---

### POST /users/me/change-password — Смена пароля

```
POST /api/v1/users/me/change-password
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "current_password": "старый_пароль",
  "new_password": "новый_пароль_минимум_6"
}
```

---

### PATCH /users/{user_id}/role — Изменить роль

> Только `admin`.

```
PATCH /api/v1/users/{user_id}/role
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "role": "manager" }
```

Допустимые значения: `admin`, `manager`, `sales_rep`.

---

## Лиды — `/leads`

### Объект LeadOutput

```json
{
  "id": "uuid",
  "first_name": "Анна",
  "last_name": "Иванова",
  "full_name": "Анна Иванова",
  "email": "anna@acme.com",
  "owner_id": "uuid",
  "status": "new",
  "source": "website",
  "phone": "+79001234567",
  "company": "Acme Corp",
  "notes": "Заинтересована в Enterprise-тарифе",
  "converted_deal_id": null,
  "tags": ["горячий", "enterprise"],
  "category": "b2b",
  "created_at": "2025-06-15T10:00:00Z",
  "updated_at": "2025-06-15T10:00:00Z"
}
```

### Статусы лида и переходы

```
new ──────────────► contacted
 │                      │
 └──► qualified ◄───────┘
 │        │
 └──► unqualified ◄──────┐
          │               │
          └───────────────┘
          (qualified ↔ unqualified допустимо)

qualified ──► converted  (только через создание сделки, нельзя установить напрямую)
```

| Статус | Описание |
|--------|----------|
| `new` | Только что создан, не обработан |
| `contacted` | Установлен первый контакт |
| `qualified` | Квалифицирован, готов к конвертации в сделку |
| `unqualified` | Не подходит |
| `converted` | Конвертирован в сделку (терминальный) |

**Недопустимые переходы** вернут `400 Bad Request`.

### Источники лида (поле `source`)

| Значение | Описание |
|----------|----------|
| `website` | С сайта |
| `referral` | Рекомендация |
| `cold_call` | Холодный звонок |
| `social_media` | Социальные сети |
| `email_campaign` | Email-рассылка |
| `other` | Другой (по умолчанию) |

---

### GET /leads — Список лидов

```
GET /api/v1/leads
Authorization: Bearer <token>
```

**Query-параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `owner_id` | UUID | Фильтр по владельцу |
| `lead_status` | string | Фильтр по статусу: `new`, `contacted`, `qualified`, `unqualified`, `converted` |
| `tag` | string | Фильтр по тегу (точное совпадение) |

```bash
# Только квалифицированные лиды текущего пользователя
curl -s "http://localhost:8000/api/v1/leads?owner_id=uuid&lead_status=qualified" \
  -H "Authorization: Bearer <token>"
```

**Ответ 200:** массив `LeadOutput`.

---

### POST /leads — Создать лида

```
POST /api/v1/leads
Authorization: Bearer <token>
Content-Type: application/json
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `first_name` | string | Да | Имя |
| `last_name` | string | Да | Фамилия |
| `email` | string | Да | Email (уникальный) |
| `owner_id` | UUID | Да | ID ответственного менеджера |
| `phone` | string | Нет | Телефон |
| `company` | string | Нет | Компания |
| `source` | string | Нет | Источник (по умолчанию `other`) |
| `tags` | string[] | Нет | Список тегов |
| `category` | string | Нет | Категория лида |
| `target_pipeline_name` | string | Нет | Название воронки, в которую лид будет направлен при конвертации |

> **Воронка при создании лида:** если у вас несколько воронок продаж, передайте `target_pipeline_name` с точным названием воронки. Система найдёт воронку по имени (регистронезависимо) и сохранит её ID внутри лида. В ответе вернётся поле `target_pipeline_id` с UUID воронки. Если воронка не найдена — ошибка `422`.

```bash
curl -s -X POST http://localhost:8000/api/v1/leads \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Анна",
    "last_name": "Иванова",
    "email": "anna@acme.com",
    "phone": "+79001234567",
    "company": "Acme Corp",
    "source": "website",
    "owner_id": "u0000000-0000-0000-0000-000000000042",
    "target_pipeline_name": "Новые клиенты"
  }'
```

**Ответ 201:** `LeadOutput`.

**Ошибки:**
- `409` — лид с таким email уже существует
- `422` — некорректный формат email или пустое имя
- `422` — воронка с указанным `target_pipeline_name` не найдена

---

### GET /leads/tags — Все теги лидов

```
GET /api/v1/leads/tags
Authorization: Bearer <token>
```

**Ответ 200:**
```json
["b2b", "enterprise", "горячий", "холодный"]
```

---

### GET /leads/{lead_id} — Получить лида

```
GET /api/v1/leads/{lead_id}
Authorization: Bearer <token>
```

**Ответ 200:** `LeadOutput`. **Ошибки:** `404`.

---

### PATCH /leads/{lead_id} — Обновить лида

```
PATCH /api/v1/leads/{lead_id}
Authorization: Bearer <token>
Content-Type: application/json
```

Все поля опциональны:

| Поле | Тип | Описание |
|------|-----|----------|
| `status` | string | Новый статус (см. таблицу переходов) |
| `notes` | string | Заметки |
| `tags` | string[] | Теги (полная замена) |
| `category` | string | Категория |

```bash
# Изменить статус на "qualified"
curl -s -X PATCH http://localhost:8000/api/v1/leads/ld000001-... \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "qualified", "notes": "Подтвердил интерес, готов к демо"}'
```

**Ответ 200:** обновлённый `LeadOutput`.

**Ошибки:**
- `400` — недопустимый переход статуса (например, `new` → `converted`)
- `404` — лид не найден

---

### GET /leads/{lead_id}/activities — Журнал активностей

```
GET /api/v1/leads/{lead_id}/activities
Authorization: Bearer <token>
```

**Ответ 200:**
```json
[
  {
    "id": "uuid",
    "entity_type": "lead",
    "entity_id": "uuid",
    "type": "status_change",
    "performed_by_id": "uuid",
    "body": "Статус изменён: new → qualified",
    "created_at": "2025-06-15T10:10:00Z"
  }
]
```

Типы активности: `call`, `email`, `meeting`, `note`, `status_change`,
`stage_change`, `lead_converted`.

---

### POST /leads/{lead_id}/comments — Добавить комментарий

```
POST /api/v1/leads/{lead_id}/comments
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "body": "Перезвонил, готов к встрече в пятницу" }
```

**Ответ 201:** объект активности с типом `note`.

---

### POST /leads/bulk-import — Массовый импорт из CSV

```
POST /api/v1/leads/bulk-import
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

Поле `file` — CSV-файл.

**Обязательные колонки:** `first_name`, `last_name`, `email`
**Опциональные колонки:** `phone`, `company`, `source`

Пример CSV:
```csv
first_name,last_name,email,phone,company,source
Анна,Иванова,anna@acme.com,+79001234567,Acme Corp,website
Иван,Сидоров,ivan@corp.ru,,Corp Ltd,referral
```

```bash
curl -s -X POST http://localhost:8000/api/v1/leads/bulk-import \
  -H "Authorization: Bearer <token>" \
  -F "file=@leads.csv"
```

**Ответ 200:**
```json
{
  "created": 42,
  "skipped": 3,
  "error_count": 0,
  "errors": [],
  "leads": [ ... ]
}
```

Дубли по email пропускаются (попадают в `skipped`), не являются ошибкой.

---

## Сделки — `/deals`

### Объект DealOutput

```json
{
  "id": "uuid",
  "title": "Acme Corp — Enterprise план",
  "owner_id": "uuid",
  "stage_id": "uuid",
  "pipeline_id": "uuid",
  "value_amount": "120000.00",
  "value_currency": "RUB",
  "status": "open",
  "contact_name": null,
  "company": null,
  "source_lead_id": "uuid",
  "expected_close_date": null,
  "closed_at": null,
  "created_at": "2025-06-15T10:05:00Z",
  "updated_at": "2025-06-15T10:05:00Z"
}
```

### Статусы сделки

| Статус | Описание |
|--------|----------|
| `open` | Активная сделка |
| `won` | Выиграна (терминальный — нельзя изменить) |
| `lost` | Проиграна (можно передвинуть в этап для повторной работы) |

---

### GET /deals — Список сделок

```
GET /api/v1/deals
Authorization: Bearer <token>
```

**Query-параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `pipeline_id` | UUID | Фильтр по воронке |
| `stage_id` | UUID | Фильтр по этапу |
| `owner_id` | UUID | Фильтр по владельцу |

**Ответ 200:** массив `DealOutput`.

---

### POST /deals — Конвертировать лида в сделку

```
POST /api/v1/deals
Authorization: Bearer <token>
Content-Type: application/json
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `lead_id` | UUID | Да | ID лида (должен быть `qualified`) |
| `stage_id` | UUID | Да | ID начального этапа |
| `pipeline_id` | UUID | Да | ID воронки |
| `deal_title` | string | Нет | Название сделки (по умолчанию — имя лида + компания) |
| `deal_value_amount` | decimal | Нет | Сумма сделки (по умолчанию 0) |
| `deal_value_currency` | string | Нет | Валюта: `RUB`, `USD`, `EUR` (по умолчанию `USD`) |
| `performed_by_id` | UUID | Нет | ID пользователя, выполняющего действие |

```bash
curl -s -X POST http://localhost:8000/api/v1/deals \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "ld000001-0000-0000-0000-000000000001",
    "stage_id": "s1000000-0000-0000-0000-000000000001",
    "pipeline_id": "a1b2c3d4-0000-0000-0000-000000000001",
    "deal_title": "Acme Corp — Enterprise план",
    "deal_value_amount": "120000.00",
    "deal_value_currency": "RUB",
    "performed_by_id": "u0000000-0000-0000-0000-000000000042"
  }'
```

**Ответ 201:** `DealOutput`.

**Ошибки:**
- `400` — лид не в статусе `qualified`
- `404` — лид, этап или воронка не найдены
- `422` — этап не принадлежит указанной воронке

---

### PATCH /deals/{deal_id}/stage — Переместить сделку по воронке

```
PATCH /api/v1/deals/{deal_id}/stage
Authorization: Bearer <token>
Content-Type: application/json
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `new_stage_id` | UUID | Да | ID нового этапа |
| `pipeline_id` | UUID | Да | ID воронки |
| `performed_by_id` | UUID | Да | ID пользователя, выполняющего действие |

```bash
curl -s -X PATCH http://localhost:8000/api/v1/deals/dl000001-.../stage \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_stage_id": "s2000000-0000-0000-0000-000000000002",
    "pipeline_id": "a1b2c3d4-0000-0000-0000-000000000001",
    "performed_by_id": "u0000000-0000-0000-0000-000000000042"
  }'
```

**Ответ 200:** обновлённый `DealOutput`.

**Ошибки:**
- `400` — сделка закрыта (WON/LOST), переместить нельзя
- `404` — сделка или этап не найдены

После смены этапа автоматически отправляется Telegram-уведомление (в фоне).

---

### PATCH /deals/{deal_id}/close — Закрыть сделку

```
PATCH /api/v1/deals/{deal_id}/close
Authorization: Bearer <token>
Content-Type: application/json
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `outcome` | string | Да | `won` — выиграна, `lost` — проиграна |

```bash
curl -s -X PATCH http://localhost:8000/api/v1/deals/dl000001-.../close \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"outcome": "won"}'
```

**Ответ 200:** `DealOutput` со статусом `won` или `lost` и заполненным `closed_at`.

**Ошибки:**
- `400` — сделка уже закрыта
- `404` — сделка не найдена

> **Важно:** сделка со статусом `won` является терминальной — её нельзя
> переоткрыть или переместить. Сделку `lost` можно переместить в этап
> (`PATCH /stage`) для повторной работы.

---

### GET /deals/{deal_id}/activities — Журнал активностей

```
GET /api/v1/deals/{deal_id}/activities
Authorization: Bearer <token>
```

**Ответ 200:** массив объектов активности (аналогично лидам).

---

### POST /deals/{deal_id}/comments — Добавить комментарий

```
POST /api/v1/deals/{deal_id}/comments
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "body": "Клиент запросил финальный расчёт, отправляем до пятницы" }
```

**Ответ 201:** объект активности типа `note`.

---

### POST /deals/notify-overdue — Уведомить о просроченных сделках

Ручной запуск Telegram-уведомлений о сделках с истёкшим `expected_close_date`.
Автоматически запускается Celery Beat раз в сутки.

```
POST /api/v1/deals/notify-overdue
Authorization: Bearer <token>
```

**Ответ 200:**
```json
{ "overdue_count": 5 }
```

---

## Вложения к сделкам — `/deals/{deal_id}/attachments`

### POST — Загрузить файл

```
POST /api/v1/deals/{deal_id}/attachments
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

```bash
curl -s -X POST http://localhost:8000/api/v1/deals/dl000001-.../attachments \
  -H "Authorization: Bearer <token>" \
  -F "file=@contract.pdf"
```

### GET — Список вложений

```
GET /api/v1/deals/{deal_id}/attachments
Authorization: Bearer <token>
```

### DELETE — Удалить вложение

```
DELETE /api/v1/deals/{deal_id}/attachments/{attachment_id}
Authorization: Bearer <token>
```

---

## Воронки продаж — `/pipelines`

### Объект PipelineOutput

```json
{
  "id": "uuid",
  "name": "Основная воронка",
  "owner_id": "uuid",
  "is_active": true,
  "created_at": "2025-06-01T00:00:00Z",
  "stages": [
    {
      "id": "uuid",
      "pipeline_id": "uuid",
      "name": "Новый лид",
      "order": 1,
      "probability": 0.1,
      "color": "#94A3B8"
    },
    {
      "id": "uuid",
      "pipeline_id": "uuid",
      "name": "Переговоры",
      "order": 2,
      "probability": 0.5,
      "color": "#3B82F6"
    }
  ]
}
```

### GET /pipelines — Список воронок

```
GET /api/v1/pipelines
Authorization: Bearer <token>
```

**Ответ 200:** массив `PipelineOutput`.

---

### POST /pipelines — Создать воронку

```
POST /api/v1/pipelines
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "name": "Основная воронка" }
```

**Ответ 201:** `PipelineOutput` (без этапов, их нужно добавить отдельно).

---

### GET /pipelines/{pipeline_id} — Получить воронку

```
GET /api/v1/pipelines/{pipeline_id}
Authorization: Bearer <token>
```

**Ответ 200:** `PipelineOutput` со всеми этапами, отсортированными по `order`.

---

### PATCH /pipelines/{pipeline_id} — Переименовать воронку

```
PATCH /api/v1/pipelines/{pipeline_id}
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "name": "Новое название воронки" }
```

---

### DELETE /pipelines/{pipeline_id} — Удалить воронку

```
DELETE /api/v1/pipelines/{pipeline_id}
Authorization: Bearer <token>
```

**Ответ 204 No Content.**

---

### POST /pipelines/{pipeline_id}/stages — Добавить этап

```
POST /api/v1/pipelines/{pipeline_id}/stages
Authorization: Bearer <token>
Content-Type: application/json
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `name` | string | Да | Название этапа |
| `probability` | float | Нет | Вероятность закрытия 0.0–1.0 (по умолчанию 0.5) |
| `color` | string | Нет | Цвет в HEX: `#3B82F6` |

```json
{
  "name": "Коммерческое предложение",
  "probability": 0.6,
  "color": "#F59E0B"
}
```

**Ответ 201:** обновлённый `PipelineOutput` с новым этапом.

---

### PATCH /pipelines/{pipeline_id}/stages/{stage_id} — Обновить этап

```
PATCH /api/v1/pipelines/{pipeline_id}/stages/{stage_id}
Authorization: Bearer <token>
Content-Type: application/json
```

Все поля опциональны:

```json
{
  "name": "Финальные переговоры",
  "probability": 0.8,
  "color": "#10B981"
}
```

---

### DELETE /pipelines/{pipeline_id}/stages/{stage_id} — Удалить этап

```
DELETE /api/v1/pipelines/{pipeline_id}/stages/{stage_id}
Authorization: Bearer <token>
```

**Ответ 200:** обновлённый `PipelineOutput`.

---

## AI-аналитика — `/ai`

Все AI-эндпоинты обращаются к OpenAI GPT-4o. При отсутствии `OPENAI_API_KEY`
возвращают `503 Service Unavailable`.

### POST /ai/leads/{lead_id}/score — Оценить лида

```
POST /api/v1/ai/leads/{lead_id}/score
Authorization: Bearer <token>
```

**Ответ 200:**
```json
{
  "score": 78,
  "reasoning": "Лид имеет корпоративный email, дважды проявил интерес, соответствует портрету клиента.",
  "recommendation": "Назначьте демо-встречу в течение 48 часов."
}
```

---

### POST /ai/deals/{deal_id}/forecast — Прогноз закрытия сделки

```
POST /api/v1/ai/deals/{deal_id}/forecast
Authorization: Bearer <token>
```

**Ответ 200:**
```json
{
  "close_probability": 0.72,
  "expected_value": 86400,
  "risk_factors": ["Лицо, принимающее решения, не определено", "Конец квартала — заморозка бюджетов"],
  "recommendation": "Запросите встречу с руководством для презентации ROI."
}
```

---

### POST /ai/leads/{lead_id}/next-best-action — Следующее действие

```
POST /api/v1/ai/leads/{lead_id}/next-best-action
Authorization: Bearer <token>
```

**Ответ 200:**
```json
{
  "action": "Позвоните лиду сегодня между 14:00 и 16:00 — наиболее вероятное время ответа.",
  "priority": "high",
  "deadline": "2025-06-15T16:00:00Z"
}
```

---

### POST /ai/leads/{lead_id}/generate-email — Сгенерировать письмо

```
POST /api/v1/ai/leads/{lead_id}/generate-email
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "context": "Повторное письмо после вебинара" }
```

**Ответ 200:**
```json
{
  "subject": "Итоги вебинара и ваш следующий шаг",
  "body": "Здравствуйте, Анна!\n\nСпасибо за участие в нашем вебинаре..."
}
```

---

### POST /ai/deals/analyze-lost — Анализ потерянных сделок

```
POST /api/v1/ai/deals/analyze-lost
Authorization: Bearer <token>
```

**Ответ 200:** сводный AI-анализ всех сделок со статусом `lost` с выводами
о причинах потерь и рекомендациями.

---

### GET /ai/pipelines/{pipeline_id}/digest — Еженедельная сводка

```
GET /api/v1/ai/pipelines/{pipeline_id}/digest
Authorization: Bearer <token>
```

**Ответ 200:** текстовая сводка состояния воронки, трендов и рисков.

---

## Аналитика — `/analytics`

### GET /analytics — Расширенная аналитика

```
GET /api/v1/analytics
Authorization: Bearer <token>
```

Возвращает конверсионную воронку, разбивку по этапам, топ источников лидов.

---

### GET /analytics/dashboard — Метрики дашборда

```
GET /api/v1/analytics/dashboard
Authorization: Bearer <token>
```

**Ответ 200:**
```json
{
  "total_leads": 142,
  "qualified_leads": 38,
  "open_deals": 24,
  "total_revenue": 4800000,
  "conversion_rate": 0.27,
  "avg_deal_value": 200000
}
```

---

### GET /analytics/forecast — Прогноз выручки

```
GET /api/v1/analytics/forecast
Authorization: Bearer <token>
```

---

### GET /analytics/managers-report — Отчёт по менеджерам

```
GET /api/v1/analytics/managers-report
Authorization: Bearer <token>
```

> Только `admin` и `manager`.

---

### GET /analytics/export — Экспорт в CSV

```
GET /api/v1/analytics/export
Authorization: Bearer <token>
```

**Ответ:** файл `text/csv`.

---

## Gmail — `/gmail`, `/emails`

Требует настройки OAuth2 (`GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`).

### GET /gmail/auth — Начать OAuth2-авторизацию

```
GET /api/v1/gmail/auth
Authorization: Bearer <token>
```

**Ответ:** URL для перехода в браузере. После авторизации Google вызывает callback.

---

### POST /emails/send — Отправить письмо

```
POST /api/v1/emails/send
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "to": "anna@acme.com",
  "subject": "Коммерческое предложение",
  "body": "Здравствуйте, Анна! Высылаем наше предложение..."
}
```

---

### GET /emails — Список писем из базы

```
GET /api/v1/emails
Authorization: Bearer <token>
```

---

### POST /emails/sync — Запустить синхронизацию Gmail

```
POST /api/v1/emails/sync
Authorization: Bearer <token>
```

Запускает фоновую синхронизацию. Автоматически выполняется Celery каждые 10 минут.

---

### GET /emails/threads — Список тредов

```
GET /api/v1/emails/threads
Authorization: Bearer <token>
```

---

### GET /emails/threads/{thread_id} — Письма треда

```
GET /api/v1/emails/threads/{thread_id}
Authorization: Bearer <token>
```

---

### POST /emails/link — Привязать письмо к лиду

```
POST /api/v1/emails/link
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "email_id": "uuid",
  "lead_id": "uuid"
}
```

---

## Telegram — `/telegram`

### POST /telegram/set-webhook — Зарегистрировать вебхук

```
POST /api/v1/telegram/set-webhook
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "webhook_url": "https://your-domain.com/api/v1/telegram/webhook" }
```

---

### POST /telegram/webhook — Получить обновление от Telegram

Этот эндпоинт вызывается Telegram автоматически. Не требует авторизации.

```
POST /api/v1/telegram/webhook
```

---

## Уведомления — `/notifications`

### GET /notifications — Список уведомлений

```
GET /api/v1/notifications
Authorization: Bearer <token>
```

**Ответ 200:**
```json
[
  {
    "id": "uuid",
    "type": "lead",
    "title": "Новый лид",
    "message": "Создан лид Анна Иванова (Acme Corp)",
    "link": "/leads/uuid",
    "is_read": false,
    "timestamp": "2025-06-15T10:00:00Z"
  }
]
```

---

### POST /notifications/mark-read — Отметить как прочитанные

```
POST /api/v1/notifications/mark-read
Authorization: Bearer <token>
```

---

## CRM-задачи — `/tasks`

### POST /tasks — Создать задачу

```
POST /api/v1/tasks
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "title": "Отправить коммерческое предложение",
  "description": "Подготовить КП для Acme Corp",
  "due_date": "2025-06-20T12:00:00Z",
  "assigned_to_id": "uuid",
  "lead_id": "uuid"
}
```

---

### GET /tasks — Список задач

```
GET /api/v1/tasks
Authorization: Bearer <token>
```

---

### PATCH /tasks/{task_id} — Обновить задачу

Статусы задачи: `pending`, `in_progress`, `done`, `cancelled`.

```
PATCH /api/v1/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{ "status": "done" }
```

---

### DELETE /tasks/{task_id} — Удалить задачу

```
DELETE /api/v1/tasks/{task_id}
Authorization: Bearer <token>
```

---

## Встречи — `/meetings`

### POST /meetings — Создать встречу

```
POST /api/v1/meetings
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "title": "Демо для Acme Corp",
  "scheduled_at": "2025-06-20T14:00:00Z",
  "lead_id": "uuid",
  "notes": "Показать модуль аналитики"
}
```

---

### GET /meetings — Список встреч

```
GET /api/v1/meetings
Authorization: Bearer <token>
```

---

### PATCH /meetings/{meeting_id} — Обновить встречу

```
PATCH /api/v1/meetings/{meeting_id}
Authorization: Bearer <token>
Content-Type: application/json
```

Статусы встречи: `scheduled`, `completed`, `cancelled`.

---

### DELETE /meetings/{meeting_id} — Удалить встречу

```
DELETE /api/v1/meetings/{meeting_id}
Authorization: Bearer <token>
```

---

## GDPR — `/gdpr`

> Все эндпоинты только для роли `admin`. Все действия записываются в audit log.

### POST /gdpr/users/{user_id}/delete — Удалить данные пользователя

```
POST /api/v1/gdpr/users/{user_id}/delete
Authorization: Bearer <token>
```

Удаляет все личные данные пользователя (право на удаление, GDPR Art. 17).

---

### POST /gdpr/leads/{lead_id}/anonymize — Анонимизировать лида

```
POST /api/v1/gdpr/leads/{lead_id}/anonymize
Authorization: Bearer <token>
```

Заменяет персональные данные лида на псевдонимы. CRM-история сохраняется.

---

### GET /gdpr/audit-log — Журнал аудита

```
GET /api/v1/gdpr/audit-log
Authorization: Bearer <token>
```

Журнал append-only — записи нельзя изменить или удалить.

---

### GET /gdpr/users/{user_id}/export — Экспорт данных (Art. 20)

```
GET /api/v1/gdpr/users/{user_id}/export
Authorization: Bearer <token>
```

**Ответ:** JSON с полным набором данных пользователя.

---

### POST /gdpr/apply-retention-policy — Политика хранения

```
POST /api/v1/gdpr/apply-retention-policy
Authorization: Bearer <token>
```

Удаляет данные старше `GDPR_RETENTION_DAYS` (по умолчанию 730 дней).
Автоматически запускается Celery Beat раз в сутки.

---

## Быстрый старт для внешней интеграции

Минимальный сценарий для чат-бота: принять заявку → создать лида → квалифицировать → создать сделку.

```python
import httpx

BASE_URL = "http://your-crm.domain/api/v1"
OWNER_ID = "uuid-ответственного-менеджера"
PIPELINE_ID = "uuid-основной-воронки"
STAGE_ID = "uuid-первого-этапа"

# 1. Авторизация
res = httpx.post(f"{BASE_URL}/auth/login", json={
    "email": "bot@example.com",
    "password": "botpassword"
})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Создать лида (сразу указываем целевую воронку по названию)
res = httpx.post(f"{BASE_URL}/leads", headers=headers, json={
    "first_name": "Анна",
    "last_name": "Иванова",
    "email": "anna@acme.com",
    "phone": "+79001234567",
    "company": "Acme Corp",
    "source": "website",
    "owner_id": OWNER_ID,
    "target_pipeline_name": "Основная воронка"  # опционально — маршрутизация по названию
})
lead_id = res.json()["id"]

# 3. Квалифицировать лида
httpx.patch(f"{BASE_URL}/leads/{lead_id}", headers=headers,
            json={"status": "qualified"})

# 4. Создать сделку
res = httpx.post(f"{BASE_URL}/deals", headers=headers, json={
    "lead_id": lead_id,
    "stage_id": STAGE_ID,
    "pipeline_id": PIPELINE_ID,
    "deal_title": "Acme Corp — заявка с сайта",
    "deal_value_amount": "0",
    "deal_value_currency": "RUB",
    "performed_by_id": OWNER_ID
})
deal_id = res.json()["id"]
print(f"Сделка создана: {deal_id}")
```

---

## Заголовок X-Request-ID

Каждый ответ содержит заголовок `X-Request-ID` (UUID v4) для корреляции логов:

```
X-Request-ID: 3f7a8b2c-1234-5678-9abc-def012345678
```

Используйте его при обращении в поддержку для поиска запроса в логах.
