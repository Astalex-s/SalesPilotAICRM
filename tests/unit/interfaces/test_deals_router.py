"""
Юнит-тесты роутера /api/v1/deals.
Use cases заменены AsyncMock — зависимости от БД отсутствуют.
"""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from src.application.dtos.deal_dtos import DealOutput
from src.application.exceptions import DealNotFoundError, PipelineNotFoundError, StageNotInPipelineError
from src.domain.exceptions import DealAlreadyClosedError
from src.domain.value_objects.enums import DealStatus
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.v1.routers.deals import router
from src.interfaces.api.dependencies import get_convert_lead_use_case, get_move_deal_stage_use_case


# ── Вспомогательные функции ────────────────────────────────────────────────────

def make_deal_output() -> DealOutput:
    """Создаёт тестовый DealOutput."""
    now = datetime.now(timezone.utc)
    return DealOutput(
        id=uuid4(),
        title="Enterprise Deal",
        owner_id=uuid4(),
        stage_id=uuid4(),
        pipeline_id=uuid4(),
        value_amount=Decimal("15000"),
        value_currency="USD",
        status=DealStatus.OPEN,
        contact_name="Jane Smith",
        company="Acme Corp",
        source_lead_id=uuid4(),
        expected_close_date=None,
        closed_at=None,
        created_at=now,
        updated_at=now,
    )


def build_app(
    convert_uc: AsyncMock | None = None,
    move_uc: AsyncMock | None = None,
) -> FastAPI:
    """Строит изолированное FastAPI-приложение с подменёнными зависимостями."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    if convert_uc is not None:
        app.dependency_overrides[get_convert_lead_use_case] = lambda: convert_uc
    if move_uc is not None:
        app.dependency_overrides[get_move_deal_stage_use_case] = lambda: move_uc

    return app


# ── POST /api/v1/deals ─────────────────────────────────────────────────────────

class TestConvertLeadToDealEndpoint:
    def test_returns_201_on_success(self) -> None:
        """Успешная конвертация возвращает 201 и DealOutput."""
        uc = AsyncMock()
        uc.execute.return_value = make_deal_output()
        client = TestClient(build_app(convert_uc=uc))

        resp = client.post("/api/v1/deals", json={
            "lead_id": str(uuid4()),
            "stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
        })

        assert resp.status_code == 201
        assert resp.json()["status"] == "open"

    def test_use_case_called_once(self) -> None:
        """Use case вызывается ровно один раз."""
        uc = AsyncMock()
        uc.execute.return_value = make_deal_output()
        client = TestClient(build_app(convert_uc=uc))

        client.post("/api/v1/deals", json={
            "lead_id": str(uuid4()),
            "stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
        })

        uc.execute.assert_called_once()

    def test_returns_404_when_lead_not_found(self) -> None:
        """Лид не найден → 404."""
        uc = AsyncMock()
        uc.execute.side_effect = DealNotFoundError(uuid4())
        client = TestClient(build_app(convert_uc=uc))

        resp = client.post("/api/v1/deals", json={
            "lead_id": str(uuid4()),
            "stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
        })

        assert resp.status_code == 404

    def test_returns_422_when_stage_not_in_pipeline(self) -> None:
        """Этап не в воронке → 422."""
        uc = AsyncMock()
        uc.execute.side_effect = StageNotInPipelineError(uuid4(), uuid4())
        client = TestClient(build_app(convert_uc=uc))

        resp = client.post("/api/v1/deals", json={
            "lead_id": str(uuid4()),
            "stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
        })

        assert resp.status_code == 422

    def test_returns_422_on_missing_required_fields(self) -> None:
        """Отсутствие обязательного поля pipeline_id → 422."""
        uc = AsyncMock()
        client = TestClient(build_app(convert_uc=uc))

        resp = client.post("/api/v1/deals", json={
            "lead_id": str(uuid4()),
            "stage_id": str(uuid4()),
        })

        assert resp.status_code == 422


# ── PATCH /api/v1/deals/{deal_id}/stage ───────────────────────────────────────

class TestMoveDealStageEndpoint:
    def test_returns_200_on_success(self) -> None:
        """Успешное перемещение этапа возвращает 200 и DealOutput."""
        uc = AsyncMock()
        deal = make_deal_output()
        uc.execute.return_value = deal
        client = TestClient(build_app(move_uc=uc))

        resp = client.patch(f"/api/v1/deals/{uuid4()}/stage", json={
            "new_stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
            "performed_by_id": str(uuid4()),
        })

        assert resp.status_code == 200

    def test_deal_id_from_path_passed_to_use_case(self) -> None:
        """deal_id берётся из пути и передаётся в MoveDealStageInput."""
        uc = AsyncMock()
        uc.execute.return_value = make_deal_output()
        client = TestClient(build_app(move_uc=uc))
        deal_id = uuid4()

        client.patch(f"/api/v1/deals/{deal_id}/stage", json={
            "new_stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
            "performed_by_id": str(uuid4()),
        })

        call_arg = uc.execute.call_args[0][0]
        assert call_arg.deal_id == deal_id

    def test_returns_404_when_deal_not_found(self) -> None:
        """Сделка не найдена → 404."""
        uc = AsyncMock()
        uc.execute.side_effect = DealNotFoundError(uuid4())
        client = TestClient(build_app(move_uc=uc))

        resp = client.patch(f"/api/v1/deals/{uuid4()}/stage", json={
            "new_stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
            "performed_by_id": str(uuid4()),
        })

        assert resp.status_code == 404

    def test_returns_422_when_deal_already_closed(self) -> None:
        """Попытка переместить закрытую сделку → 422."""
        uc = AsyncMock()
        uc.execute.side_effect = DealAlreadyClosedError("сделка закрыта")
        client = TestClient(build_app(move_uc=uc))

        resp = client.patch(f"/api/v1/deals/{uuid4()}/stage", json={
            "new_stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
            "performed_by_id": str(uuid4()),
        })

        assert resp.status_code == 422

    def test_returns_422_on_missing_performed_by_id(self) -> None:
        """Отсутствие performed_by_id → 422."""
        uc = AsyncMock()
        client = TestClient(build_app(move_uc=uc))

        resp = client.patch(f"/api/v1/deals/{uuid4()}/stage", json={
            "new_stage_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
        })

        assert resp.status_code == 422
