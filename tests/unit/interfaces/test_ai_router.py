"""
Юнит-тесты роутера /api/v1/ai.
Use cases заменены AsyncMock — зависимости от БД, Redis и OpenAI отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.dtos.ai_dtos import (
    DealForecastOutput,
    GenerateEmailOutput,
    LeadScoreOutput,
    NextBestActionOutput,
)
from src.application.exceptions import DealNotFoundError, LeadNotFoundError
from src.interfaces.api.dependencies import (
    get_forecast_deal_use_case,
    get_generate_email_use_case,
    get_next_best_action_use_case,
    get_score_lead_use_case,
)
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.v1.routers.ai import router


# ── Вспомогательные функции ────────────────────────────────────────────────────

def build_app(
    score_uc: AsyncMock | None = None,
    forecast_uc: AsyncMock | None = None,
    nba_uc: AsyncMock | None = None,
    email_uc: AsyncMock | None = None,
) -> FastAPI:
    """Строит изолированное FastAPI-приложение с подменёнными зависимостями."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    if score_uc is not None:
        app.dependency_overrides[get_score_lead_use_case] = lambda: score_uc
    if forecast_uc is not None:
        app.dependency_overrides[get_forecast_deal_use_case] = lambda: forecast_uc
    if nba_uc is not None:
        app.dependency_overrides[get_next_best_action_use_case] = lambda: nba_uc
    if email_uc is not None:
        app.dependency_overrides[get_generate_email_use_case] = lambda: email_uc

    return app


# ── POST /ai/leads/{lead_id}/score ─────────────────────────────────────────────

class TestScoreLeadEndpoint:
    def test_returns_200_on_success(self) -> None:
        """POST /ai/leads/{id}/score возвращает 200 при успехе."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = LeadScoreOutput(
            lead_id=lead_id,
            score=0.75,
            reasoning="Хороший потенциал",
            recommended_actions=["Позвонить"],
        )
        client = TestClient(build_app(score_uc=uc))
        response = client.post(f"/api/v1/ai/leads/{lead_id}/score")
        assert response.status_code == 200

    def test_response_contains_score(self) -> None:
        """Ответ содержит поле score с корректным значением."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = LeadScoreOutput(
            lead_id=lead_id,
            score=0.65,
            reasoning="Средний потенциал",
            recommended_actions=[],
        )
        client = TestClient(build_app(score_uc=uc))
        response = client.post(f"/api/v1/ai/leads/{lead_id}/score")
        assert response.json()["score"] == 0.65

    def test_response_contains_lead_id(self) -> None:
        """Ответ содержит корректный lead_id."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = LeadScoreOutput(
            lead_id=lead_id,
            score=0.5,
            reasoning="Нейтральный",
            recommended_actions=[],
        )
        client = TestClient(build_app(score_uc=uc))
        response = client.post(f"/api/v1/ai/leads/{lead_id}/score")
        assert response.json()["lead_id"] == str(lead_id)

    def test_returns_404_when_lead_not_found(self) -> None:
        """404 если лид не найден."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.side_effect = LeadNotFoundError(lead_id)
        client = TestClient(build_app(score_uc=uc))
        response = client.post(f"/api/v1/ai/leads/{lead_id}/score")
        assert response.status_code == 404

    def test_use_case_called_with_lead_id(self) -> None:
        """Use case вызывается с lead_id из URL."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = LeadScoreOutput(
            lead_id=lead_id, score=0.5, reasoning="OK", recommended_actions=[]
        )
        client = TestClient(build_app(score_uc=uc))
        client.post(f"/api/v1/ai/leads/{lead_id}/score")
        uc.execute.assert_called_once()
        assert uc.execute.call_args[0][0].lead_id == lead_id


# ── POST /ai/deals/{deal_id}/forecast ─────────────────────────────────────────

class TestForecastDealEndpoint:
    def test_returns_200_on_success(self) -> None:
        """POST /ai/deals/{id}/forecast возвращает 200 при успехе."""
        deal_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = DealForecastOutput(
            deal_id=deal_id,
            win_probability=0.8,
            risk_factors=["Конкуренты"],
            opportunities=["Расширение"],
        )
        client = TestClient(build_app(forecast_uc=uc))
        response = client.post(f"/api/v1/ai/deals/{deal_id}/forecast")
        assert response.status_code == 200

    def test_response_contains_win_probability(self) -> None:
        """Ответ содержит поле win_probability."""
        deal_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = DealForecastOutput(
            deal_id=deal_id,
            win_probability=0.9,
            risk_factors=[],
            opportunities=[],
        )
        client = TestClient(build_app(forecast_uc=uc))
        response = client.post(f"/api/v1/ai/deals/{deal_id}/forecast")
        assert response.json()["win_probability"] == 0.9

    def test_returns_404_when_deal_not_found(self) -> None:
        """404 если сделка не найдена."""
        deal_id = uuid4()
        uc = AsyncMock()
        uc.execute.side_effect = DealNotFoundError(deal_id)
        client = TestClient(build_app(forecast_uc=uc))
        response = client.post(f"/api/v1/ai/deals/{deal_id}/forecast")
        assert response.status_code == 404

    def test_use_case_called_with_deal_id(self) -> None:
        """Use case вызывается с deal_id из URL."""
        deal_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = DealForecastOutput(
            deal_id=deal_id, win_probability=0.5, risk_factors=[], opportunities=[]
        )
        client = TestClient(build_app(forecast_uc=uc))
        client.post(f"/api/v1/ai/deals/{deal_id}/forecast")
        assert uc.execute.call_args[0][0].deal_id == deal_id


# ── POST /ai/{entity_type}/{entity_id}/next-action ────────────────────────────

class TestNextBestActionEndpoint:
    def test_returns_200_for_lead(self) -> None:
        """POST /ai/lead/{id}/next-action возвращает 200."""
        entity_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = NextBestActionOutput(
            entity_id=entity_id,
            entity_type="lead",
            action="Позвонить",
            priority="high",
            reasoning="Высокий интерес",
        )
        client = TestClient(build_app(nba_uc=uc))
        response = client.post(f"/api/v1/ai/lead/{entity_id}/next-action")
        assert response.status_code == 200

    def test_returns_200_for_deal(self) -> None:
        """POST /ai/deal/{id}/next-action возвращает 200."""
        entity_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = NextBestActionOutput(
            entity_id=entity_id,
            entity_type="deal",
            action="Выслать КП",
            priority="medium",
            reasoning="Сделка застряла",
        )
        client = TestClient(build_app(nba_uc=uc))
        response = client.post(f"/api/v1/ai/deal/{entity_id}/next-action")
        assert response.status_code == 200

    def test_returns_422_for_invalid_entity_type(self) -> None:
        """422 если entity_type не 'lead' и не 'deal'."""
        entity_id = uuid4()
        uc = AsyncMock()
        client = TestClient(build_app(nba_uc=uc))
        response = client.post(f"/api/v1/ai/contact/{entity_id}/next-action")
        assert response.status_code == 422

    def test_response_contains_action(self) -> None:
        """Ответ содержит поле action."""
        entity_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = NextBestActionOutput(
            entity_id=entity_id,
            entity_type="lead",
            action="Отправить email",
            priority="low",
            reasoning="Лид остыл",
        )
        client = TestClient(build_app(nba_uc=uc))
        response = client.post(f"/api/v1/ai/lead/{entity_id}/next-action")
        assert response.json()["action"] == "Отправить email"

    def test_returns_404_when_lead_not_found(self) -> None:
        """404 если лид не найден."""
        entity_id = uuid4()
        uc = AsyncMock()
        uc.execute.side_effect = LeadNotFoundError(entity_id)
        client = TestClient(build_app(nba_uc=uc))
        response = client.post(f"/api/v1/ai/lead/{entity_id}/next-action")
        assert response.status_code == 404


# ── POST /ai/leads/{lead_id}/generate-email ───────────────────────────────────

class TestGenerateEmailEndpoint:
    def test_returns_200_on_success(self) -> None:
        """POST /ai/leads/{id}/generate-email возвращает 200."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = GenerateEmailOutput(
            lead_id=lead_id,
            subject="Спецпредложение",
            body="Добрый день...",
            tone="friendly",
        )
        client = TestClient(build_app(email_uc=uc))
        response = client.post(f"/api/v1/ai/leads/{lead_id}/generate-email")
        assert response.status_code == 200

    def test_response_contains_subject(self) -> None:
        """Ответ содержит поле subject."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = GenerateEmailOutput(
            lead_id=lead_id,
            subject="Тема письма",
            body="Тело...",
            tone="formal",
        )
        client = TestClient(build_app(email_uc=uc))
        response = client.post(f"/api/v1/ai/leads/{lead_id}/generate-email")
        assert response.json()["subject"] == "Тема письма"

    def test_tone_param_passed_to_use_case(self) -> None:
        """Параметр tone из query string передаётся в use case."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = GenerateEmailOutput(
            lead_id=lead_id, subject="S", body="B", tone="assertive"
        )
        client = TestClient(build_app(email_uc=uc))
        client.post(f"/api/v1/ai/leads/{lead_id}/generate-email?tone=assertive")
        input_dto = uc.execute.call_args[0][0]
        assert input_dto.tone == "assertive"

    def test_extra_context_param_passed(self) -> None:
        """extra_context передаётся в use case."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.return_value = GenerateEmailOutput(
            lead_id=lead_id, subject="S", body="B", tone="friendly"
        )
        client = TestClient(build_app(email_uc=uc))
        client.post(
            f"/api/v1/ai/leads/{lead_id}/generate-email"
            "?extra_context=Встреча+на+выставке"
        )
        input_dto = uc.execute.call_args[0][0]
        assert input_dto.extra_context == "Встреча на выставке"

    def test_returns_404_when_lead_not_found(self) -> None:
        """404 если лид не найден."""
        lead_id = uuid4()
        uc = AsyncMock()
        uc.execute.side_effect = LeadNotFoundError(lead_id)
        client = TestClient(build_app(email_uc=uc))
        response = client.post(f"/api/v1/ai/leads/{lead_id}/generate-email")
        assert response.status_code == 404

    def test_invalid_tone_returns_422(self) -> None:
        """422 если передан недопустимый tone."""
        lead_id = uuid4()
        uc = AsyncMock()
        client = TestClient(build_app(email_uc=uc))
        response = client.post(
            f"/api/v1/ai/leads/{lead_id}/generate-email?tone=angry"
        )
        assert response.status_code == 422
