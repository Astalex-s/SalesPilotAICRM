"""
Юнит-тесты роутера /api/v1/pipelines.
Use case заменён AsyncMock — зависимости от БД отсутствуют.
"""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from src.application.dtos.auth_dtos import UserOutput
from src.application.dtos.pipeline_dtos import PipelineOutput, StageOutput
from src.application.exceptions import PipelineNotFoundError
from src.interfaces.api.auth_dependencies import get_current_user
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.v1.routers.pipelines import router
from src.interfaces.api.dependencies import get_pipeline_use_case


def _fake_current_user() -> UserOutput:
    return UserOutput(id=uuid4(), email="test@test.com", first_name="T", last_name="U", role="admin", is_active=True)


# ── Вспомогательные функции ────────────────────────────────────────────────────

def make_pipeline_output(stage_count: int = 2) -> PipelineOutput:
    """Создаёт тестовый PipelineOutput с заданным количеством этапов."""
    pipeline_id = uuid4()
    stages = [
        StageOutput(
            id=uuid4(),
            pipeline_id=pipeline_id,
            name=f"Stage {i}",
            order=i,
            probability=0.1 * (i + 1),
        )
        for i in range(stage_count)
    ]
    return PipelineOutput(
        id=pipeline_id,
        name="Sales Pipeline",
        owner_id=uuid4(),
        stages=stages,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


def build_app(pipeline_uc: AsyncMock | None = None) -> FastAPI:
    """Строит изолированное FastAPI-приложение с подменёнными зависимостями."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    app.dependency_overrides[get_current_user] = _fake_current_user
    if pipeline_uc is not None:
        app.dependency_overrides[get_pipeline_use_case] = lambda: pipeline_uc

    return app


# ── GET /api/v1/pipelines/{pipeline_id} ───────────────────────────────────────

class TestGetPipelineEndpoint:
    def test_returns_200_on_success(self) -> None:
        """Успешный запрос возвращает 200 и PipelineOutput."""
        uc = AsyncMock()
        uc.execute.return_value = make_pipeline_output()
        client = TestClient(build_app(pipeline_uc=uc))

        resp = client.get(f"/api/v1/pipelines/{uuid4()}")

        assert resp.status_code == 200

    def test_response_contains_stages(self) -> None:
        """Ответ содержит список этапов воронки."""
        uc = AsyncMock()
        uc.execute.return_value = make_pipeline_output(stage_count=3)
        client = TestClient(build_app(pipeline_uc=uc))

        resp = client.get(f"/api/v1/pipelines/{uuid4()}")

        assert len(resp.json()["stages"]) == 3

    def test_pipeline_id_from_path_passed_to_use_case(self) -> None:
        """pipeline_id берётся из пути и передаётся в GetPipelineInput."""
        uc = AsyncMock()
        uc.execute.return_value = make_pipeline_output()
        client = TestClient(build_app(pipeline_uc=uc))
        pipeline_id = uuid4()

        client.get(f"/api/v1/pipelines/{pipeline_id}")

        call_arg = uc.execute.call_args[0][0]
        assert call_arg.pipeline_id == pipeline_id

    def test_returns_404_when_not_found(self) -> None:
        """Воронка не найдена → 404."""
        uc = AsyncMock()
        uc.execute.side_effect = PipelineNotFoundError(uuid4())
        client = TestClient(build_app(pipeline_uc=uc))

        resp = client.get(f"/api/v1/pipelines/{uuid4()}")

        assert resp.status_code == 404
        assert "Pipeline" in resp.json()["detail"]

    def test_use_case_called_once(self) -> None:
        """Use case вызывается ровно один раз."""
        uc = AsyncMock()
        uc.execute.return_value = make_pipeline_output()
        client = TestClient(build_app(pipeline_uc=uc))

        client.get(f"/api/v1/pipelines/{uuid4()}")

        uc.execute.assert_called_once()

    def test_returns_422_on_invalid_uuid(self) -> None:
        """Невалидный UUID в пути → 422."""
        uc = AsyncMock()
        client = TestClient(build_app(pipeline_uc=uc))

        resp = client.get("/api/v1/pipelines/not-a-uuid")

        assert resp.status_code == 422
