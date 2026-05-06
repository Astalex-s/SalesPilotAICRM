# Architecture — SalesPilot AI CRM

SalesPilot follows **Clean Architecture** (Robert C. Martin). The goal is to
keep business rules independent of frameworks, databases, and external services.
The result is code that is testable without infrastructure and adaptable without
touching domain logic.

---

## Core Principle: Dependency Rule

Dependencies point **inward only**:

```
Interfaces (FastAPI)
    |
    v
Application (Use Cases)
    |
    v
Domain (Entities, Rules)
    ^
    |
Infrastructure (DB, AI, Gmail...)
```

- **Domain** knows nothing about FastAPI, SQLAlchemy, Redis, or OpenAI.
- **Application** knows about Domain but not about HTTP or SQL.
- **Infrastructure** implements Domain interfaces defined as abstract classes.
- **Interfaces** (controllers) know about Application DTOs but never touch
  Domain directly or Infrastructure directly.

Violating this rule — for example, importing an SQLAlchemy model into a use
case — is treated as a hard rejection in code review.

---

## Layer Map

```
src/
├── domain/
│   ├── entities/            # Core business objects
│   ├── repositories/        # Abstract interfaces (ABCs)
│   ├── services/            # Domain services (multi-entity logic)
│   ├── value_objects/       # Immutable typed primitives
│   └── exceptions.py        # Domain-specific exceptions
│
├── application/
│   ├── use_cases/           # One file = one use case class
│   ├── dtos/                # Pydantic v2 input/output models
│   ├── ports/               # Abstract interfaces for external services
│   └── exceptions.py        # Application-level exceptions
│
├── infrastructure/
│   ├── database/
│   │   ├── models/          # SQLAlchemy ORM models (≠ domain entities)
│   │   ├── repositories/    # Concrete repository implementations
│   │   └── session.py       # Async engine + session factory
│   ├── ai/                  # OpenAI service + prompt templates
│   ├── auth/                # bcrypt + JWT implementation
│   ├── cache/               # Redis client
│   ├── celery/              # Background task workers + beat schedule
│   ├── config/              # Settings (pydantic-settings)
│   ├── email/               # SMTP client
│   ├── gmail/               # Gmail OAuth2 service
│   ├── notifications/       # In-app notification bus
│   └── telegram/            # Telegram Bot service
│
└── interfaces/
    └── api/
        ├── v1/routers/      # FastAPI route handlers (one file per domain)
        ├── schemas/         # Request body schemas (separate from DTOs)
        ├── dependencies.py  # Dependency injection wiring
        ├── auth_dependencies.py  # get_current_user, role guards
        └── exception_handlers.py  # Map domain exceptions → HTTP codes
```

---

## Layer Details

### Domain

The innermost layer. Contains pure Python — no third-party imports except
`dataclasses` and the standard library.

**Entities** are plain dataclasses with business methods:

```python
# src/domain/entities/lead.py
@dataclass
class Lead:
    id: UUID
    status: LeadStatus

    def qualify(self) -> None:
        """Validates and performs the status transition."""
        self._transition_to(LeadStatus.QUALIFIED)

    def mark_converted(self, deal_id: UUID) -> None:
        if self.is_converted:
            raise LeadAlreadyConvertedError(...)
        if not self.is_qualified:
            raise LeadNotQualifiedError(...)
        self.status = LeadStatus.CONVERTED
        self.converted_deal_id = deal_id
```

State transitions are encoded in `_VALID_TRANSITIONS` — a dict that acts as a
state machine. Entities enforce their own invariants; no service or controller
can bypass them.

**Value Objects** wrap primitives with validation:

```python
# src/domain/value_objects/email.py
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise InvalidEmailError(self.value)
```

`frozen=True` makes them immutable. Two `Email("a@b.com")` instances are equal
by value, not identity.

**Repository interfaces** are abstract base classes:

```python
# src/domain/repositories/lead_repository.py
class ILeadRepository(BaseRepository[Lead]):
    @abstractmethod
    async def find_by_email(self, email: str) -> Lead | None: ...

    @abstractmethod
    async def find_by_tag(self, tag: str) -> list[Lead]: ...
```

Domain defines the contract. Infrastructure fulfills it.

**Domain Services** handle logic that spans multiple entities:

```python
# src/domain/services/lead_conversion_service.py
class LeadConversionService:
    async def convert(self, lead: Lead, deal_input: ...) -> Deal:
        # 1. Call lead.mark_converted() — entity validates transition
        # 2. Create Deal entity
        # 3. Return both for the use case to persist
```

---

### Application

Orchestrates domain objects to fulfill a single business operation. No HTTP,
no SQL, no framework.

**Use Cases** follow a strict pattern:

- One class per file, named `<Action>UseCase`
- One public method: `async def execute(self, data: InputDTO) -> OutputDTO`
- Constructor receives only repository / port abstractions (no concrete classes)
- No business logic — delegates to domain entities and services

```python
# src/application/use_cases/create_lead.py
class CreateLeadUseCase:
    def __init__(self, lead_repo: ILeadRepository) -> None:
        self._lead_repo = lead_repo

    async def execute(self, data: CreateLeadInput) -> LeadOutput:
        existing = await self._lead_repo.find_by_email(data.email)
        if existing is not None:
            raise LeadEmailAlreadyExistsError(data.email)

        email = Email(data.email)                      # domain validation
        lead = Lead.create(...)                        # domain factory
        lead = await self._lead_repo.save(lead)        # persist
        return LeadOutput.from_entity(lead)            # map to DTO
```

**DTOs** (Data Transfer Objects) are Pydantic v2 models that cross layer
boundaries. They are the only objects that leave the application layer:

```python
# src/application/dtos/lead_dtos.py
class CreateLeadInput(BaseModel):
    first_name: str
    last_name: str
    email: str
    owner_id: UUID
    source: LeadSource = LeadSource.OTHER

class LeadOutput(BaseModel):
    id: UUID
    full_name: str
    status: LeadStatus
    ...

    @classmethod
    def from_entity(cls, lead: Lead) -> LeadOutput:
        return cls(id=lead.id, full_name=lead.full_name, ...)
```

**Ports** define contracts for external services (AI, email, notifications):

```python
# src/application/ports/ai_port.py
class IAIService(ABC):
    @abstractmethod
    async def score_lead(self, lead: Lead) -> LeadScoreResult: ...
```

---

### Infrastructure

Adapters that connect abstract ports/repositories to real external systems.

**SQLAlchemy repositories** translate between ORM models and domain entities:

```python
# src/infrastructure/database/repositories/lead_repository.py
class SqlLeadRepository(ILeadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_email(self, email: str) -> Lead | None:
        row = await self._session.scalar(
            select(LeadModel).where(LeadModel.email == email)
        )
        return _to_entity(row) if row else None

    async def save(self, lead: Lead) -> Lead:
        row = await self._session.merge(_to_model(lead))
        await self._session.flush()
        return _to_entity(row)
```

ORM models (`LeadModel`) are never exposed outside the infrastructure layer.
The mapping functions `_to_entity` / `_to_model` live in the same file.

**AI service** wraps OpenAI calls and isolates prompts:

```python
# src/infrastructure/ai/openai_service.py
class OpenAIService(IAIService):
    async def score_lead(self, lead: Lead) -> LeadScoreResult:
        prompt = LEAD_SCORE_PROMPT.format(lead=lead)
        response = await self._client.chat.completions.create(...)
        return _parse_score(response)
```

Prompt templates are stored separately in `src/infrastructure/ai/prompts/`.
Controllers and use cases never call OpenAI directly.

---

### Interfaces

Thin HTTP adapters. Controllers have exactly one responsibility: map HTTP
request → DTO → use_case.execute() → HTTP response.

```python
# src/interfaces/api/v1/routers/leads.py
@router.post("", response_model=LeadOutput, status_code=201)
async def create_lead(
    body: CreateLeadInput,
    use_case: CreateLeadUseCase = Depends(get_create_lead_use_case),
) -> LeadOutput:
    return await use_case.execute(body)
```

No business logic. No ORM imports. No conditional branching on domain state.

**Dependency injection** is wired in `dependencies.py`:

```python
# src/interfaces/api/dependencies.py
def get_create_lead_use_case(
    session: AsyncSession = Depends(get_db),
) -> CreateLeadUseCase:
    return CreateLeadUseCase(SqlLeadRepository(session))
```

This is the only place where concrete infrastructure classes are instantiated.

**Exception handlers** map domain exceptions to HTTP status codes without
leaking internal details:

```python
# src/interfaces/api/exception_handlers.py
@app.exception_handler(LeadEmailAlreadyExistsError)
async def handle_duplicate_email(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc)})
```

---

## Data Flow Example: Create Lead

```
POST /api/v1/leads
        |
        v
[Router: create_lead()]          # Interfaces layer
  body: CreateLeadInput (DTO)
        |
        v
[CreateLeadUseCase.execute()]    # Application layer
  1. lead_repo.find_by_email()   # check uniqueness
  2. Email(data.email)           # domain validation
  3. Lead.create(...)            # domain factory
  4. lead_repo.save(lead)        # persist
  5. LeadOutput.from_entity()    # map to DTO
        |
        v
[SqlLeadRepository.save()]       # Infrastructure layer
  _to_model(lead) -> LeadModel
  session.merge(model)
  _to_entity(model) -> Lead
        |
        v
[PostgreSQL]                     # External system
```

Domain entity `Lead` never touches the database directly. The database never
touches the domain entity directly. Only the repository knows both.

---

## Background Tasks

Celery workers live in `src/infrastructure/celery/`. They call use cases
directly, not HTTP endpoints:

```python
# src/infrastructure/celery/tasks.py
@celery_app.task
def sync_gmail_task():
    asyncio.run(TriggerEmailSyncUseCase(repo).execute(...))
```

Periodic tasks (retention policy, overdue deal checks, Gmail sync) are
scheduled via Celery Beat with intervals configured in `settings.py`.

---

## Testing Strategy

The architecture enables testing at different levels without mocking frameworks:

| Test Type | What's tested | Infrastructure needed |
|-----------|---------------|----------------------|
| Unit — Domain | Entity invariants, state machines, value objects | None |
| Unit — Use Cases | Business flow with in-memory fake repositories | None |
| Integration | Repository SQL queries against real DB | PostgreSQL (test DB) |
| API | End-to-end request/response via `TestClient` | SQLite in-memory |

Fake repositories implement the same `IXxxRepository` interface:

```python
class FakeLeadRepository(ILeadRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Lead] = {}

    async def save(self, lead: Lead) -> Lead:
        self._store[lead.id] = lead
        return lead

    async def find_by_email(self, email: str) -> Lead | None:
        return next((l for l in self._store.values()
                     if l.email.value == email), None)
```

No mocking library needed. Tests are fast and deterministic.

---

## Invariants and Rules Enforced

| Rule | Where enforced |
|------|---------------|
| Lead status transitions | `Lead._transition_to()` — domain entity |
| Lead can only be converted from QUALIFIED | `Lead.mark_converted()` |
| Won deal cannot be reopened | `Deal.reopen()` raises if status is WON |
| Activity log is append-only | `IActivityRepository.delete()` raises `NotImplementedError` |
| AI calls only through `IAIService` | Enforced by import rules + code review |
| No ORM models outside infrastructure | Enforced by import rules + code review |
| No business logic in controllers | Enforced by code review (CLAUDE_REVIEW.md) |

---

## Key Design Decisions

**Why separate ORM models from domain entities?**
SQLAlchemy models carry relationship loading, session tracking, and column
metadata that would couple the domain to the database. Separating them lets
domain entities be plain dataclasses — no inheritance, no magic attributes.

**Why one use case per file?**
Each file has a single reason to change. Finding, reading, and testing a
specific operation takes seconds. A file named `create_lead.py` is unambiguous.

**Why Pydantic DTOs at layer boundaries?**
They provide automatic validation, serialization, and a clear contract between
layers. A controller cannot accidentally pass an ORM model to a use case because
the type signature rejects it.

**Why abstract repository interfaces in the domain?**
The domain defines what it needs (the interface). Infrastructure provides it.
This means use cases can be tested with fake in-memory repositories — no database
process needed, tests run in milliseconds.
