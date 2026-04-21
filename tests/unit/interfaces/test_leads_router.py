"""
Юнит-тесты роутера /api/v1/leads.
Use cases заменены AsyncMock — зависимости от БД и Redis отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.application.dtos.lead_dtos import LeadOutput
from src.application.exceptions import LeadEmailAlreadyExistsError
from src.domain.value_objects.enums import LeadSource, LeadStatus
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.v1.routers.leads import router
from src.interfaces.api.dependencies import get_create_lead_use_case, get_list_leads_use_case


# ── Вспомогательные функции ────────────────────────────────────────────────────

def make_lead_output(
    first_name: str = "Alice",
    last_name: str = "Walker",
    email: str = "alice@corp.com",
) -> LeadOutput:
    """Создаёт тестовый LeadOutput."""
    now = datetime.now(timezone.utc)
    return LeadOutput(
        id=uuid4(),
        first_name=first_name,
        last_name=last_name,
        full_name=f"{first_name} {last_name}",
        email=email,
        owner_id=uuid4(),
        status=LeadStatus.NEW,
        source=LeadSource.WEBSITE,
        phone=None,
        company="Corp Ltd",
        notes=None,
        converted_deal_id=None,
        created_at=now,
        updated_at=now,
    )


def build_app(
    create_uc: AsyncMock | None = None,
    list_uc: AsyncMock | None = None,
) -> FastAPI:
    """Строит изолированное FastAPI-приложение с подменёнными зависимостями."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    if create_uc is not None:
        app.dependency_overrides[get_create_lead_use_case] = lambda: create_uc
    if list_uc is not None:
        app.dependency_overrides[get_list_leads_use_case] = lambda: list_uc

    return app


# ── POST /api/v1/leads ─────────────────────────────────────────────────────────

class TestCreateLeadEndpoint:
    def test_returns_201_on_success(self) -> None:
        """Успешное создание лида возвращает 201 и LeadOutput."""
        uc = AsyncMock()
        uc.execute.return_value = make_lead_output()
        client = TestClient(build_app(create_uc=uc))

        resp = client.post("/api/v1/leads", json={
            "first_name": "Alice",
            "last_name": "Walker",
            "email": "alice@corp.com",
            "owner_id": str(uuid4()),
        })

        assert resp.status_code == 201
        assert resp.json()["email"] == "alice@corp.com"

    def test_use_case_called_once(self) -> None:
        """Use case вызывается ровно один раз."""
        uc = AsyncMock()
        uc.execute.return_value = make_lead_output()
        client = TestClient(build_app(create_uc=uc))

        client.post("/api/v1/leads", json={
            "first_name": "Alice",
            "last_name": "Walker",
            "email": "alice@corp.com",
            "owner_id": str(uuid4()),
        })

        uc.execute.assert_called_once()

    def test_returns_409_on_duplicate_email(self) -> None:
        """Дублирующийся e-mail возвращает 409 Conflict."""
        uc = AsyncMock()
        uc.execute.side_effect = LeadEmailAlreadyExistsError("alice@corp.com")
        client = TestClient(build_app(create_uc=uc))

        resp = client.post("/api/v1/leads", json={
            "first_name": "Alice",
            "last_name": "Walker",
            "email": "alice@corp.com",
            "owner_id": str(uuid4()),
        })

        assert resp.status_code == 409
        assert "alice@corp.com" in resp.json()["detail"]

    def test_returns_422_on_empty_first_name(self) -> None:
        """Пустое имя не проходит Pydantic-валидацию — 422."""
        uc = AsyncMock()
        client = TestClient(build_app(create_uc=uc))

        resp = client.post("/api/v1/leads", json={
            "first_name": "   ",
            "last_name": "Walker",
            "email": "alice@corp.com",
            "owner_id": str(uuid4()),
        })

        assert resp.status_code == 422

    def test_returns_422_on_missing_required_field(self) -> None:
        """Отсутствие обязательного поля email возвращает 422."""
        uc = AsyncMock()
        client = TestClient(build_app(create_uc=uc))

        resp = client.post("/api/v1/leads", json={
            "first_name": "Alice",
            "last_name": "Walker",
            "owner_id": str(uuid4()),
        })

        assert resp.status_code == 422

    def test_response_contains_full_name(self) -> None:
        """Ответ содержит поле full_name."""
        uc = AsyncMock()
        uc.execute.return_value = make_lead_output()
        client = TestClient(build_app(create_uc=uc))

        resp = client.post("/api/v1/leads", json={
            "first_name": "Alice",
            "last_name": "Walker",
            "email": "alice@corp.com",
            "owner_id": str(uuid4()),
        })

        assert "full_name" in resp.json()


# ── GET /api/v1/leads ──────────────────────────────────────────────────────────

class TestListLeadsEndpoint:
    def test_returns_200_with_list(self) -> None:
        """Успешный запрос возвращает 200 и список лидов."""
        uc = AsyncMock()
        uc.execute.return_value = [make_lead_output(), make_lead_output(email="bob@corp.com")]
        client = TestClient(build_app(list_uc=uc))

        resp = client.get("/api/v1/leads")

        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_returns_empty_list(self) -> None:
        """Пустой результат возвращается как пустой массив."""
        uc = AsyncMock()
        uc.execute.return_value = []
        client = TestClient(build_app(list_uc=uc))

        resp = client.get("/api/v1/leads")

        assert resp.status_code == 200
        assert resp.json() == []

    def test_owner_id_query_param_passed_to_use_case(self) -> None:
        """owner_id передаётся в use case через ListLeadsInput."""
        uc = AsyncMock()
        uc.execute.return_value = []
        client = TestClient(build_app(list_uc=uc))
        owner_id = uuid4()

        client.get(f"/api/v1/leads?owner_id={owner_id}")

        call_arg = uc.execute.call_args[0][0]
        assert call_arg.owner_id == owner_id

    def test_status_query_param_passed_to_use_case(self) -> None:
        """lead_status передаётся в use case через ListLeadsInput."""
        uc = AsyncMock()
        uc.execute.return_value = []
        client = TestClient(build_app(list_uc=uc))

        client.get("/api/v1/leads?lead_status=new")

        call_arg = uc.execute.call_args[0][0]
        assert call_arg.status == LeadStatus.NEW

    def test_use_case_called_once(self) -> None:
        """Use case вызывается ровно один раз при запросе."""
        uc = AsyncMock()
        uc.execute.return_value = []
        client = TestClient(build_app(list_uc=uc))

        client.get("/api/v1/leads")

        uc.execute.assert_called_once()
