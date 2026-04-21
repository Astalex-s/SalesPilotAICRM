"""
Юнит-тесты use case MoveDealStageUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.deal_dtos import DealOutput, MoveDealStageInput
from src.application.exceptions import (
    DealNotFoundError,
    PipelineNotFoundError,
    StageNotInPipelineError,
)
from src.application.use_cases.move_deal_stage import MoveDealStageUseCase
from src.domain.entities.deal import Deal
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage
from src.domain.exceptions import DealAlreadyClosedError
from src.domain.value_objects.enums import ActivityType
from src.domain.value_objects.money import Money
from decimal import Decimal


# ── Вспомогательные функции ────────────────────────────────────────────────────

def make_pipeline_with_two_stages() -> tuple[Pipeline, Stage, Stage]:
    """Создаёт воронку с двумя этапами; возвращает (Pipeline, Stage1, Stage2)."""
    pipeline_id = uuid4()
    stage1 = Stage(
        id=uuid4(),
        pipeline_id=pipeline_id,
        name="Prospecting",
        order=0,
        probability=0.1,
    )
    stage2 = Stage(
        id=uuid4(),
        pipeline_id=pipeline_id,
        name="Negotiation",
        order=1,
        probability=0.7,
    )
    pipeline = Pipeline(
        id=pipeline_id,
        name="Sales Pipeline",
        owner_id=uuid4(),
        stages=[stage1, stage2],
    )
    return pipeline, stage1, stage2


def make_open_deal(pipeline_id, stage_id) -> Deal:
    """Создаёт открытую сделку на указанном этапе."""
    return Deal.create(
        title="Test Deal",
        owner_id=uuid4(),
        stage_id=stage_id,
        pipeline_id=pipeline_id,
        value=Money(Decimal("5000"), "USD"),
    )


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def deal_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def pipeline_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def activity_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(
    deal_repo: AsyncMock,
    pipeline_repo: AsyncMock,
    activity_repo: AsyncMock,
) -> MoveDealStageUseCase:
    return MoveDealStageUseCase(
        deal_repo=deal_repo,
        pipeline_repo=pipeline_repo,
        activity_repo=activity_repo,
    )


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestMoveDealStageHappyPath:
    async def test_returns_deal_output(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """execute возвращает DealOutput при корректных данных."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(MoveDealStageInput(
            deal_id=deal.id,
            new_stage_id=stage2.id,
            pipeline_id=pipeline.id,
            performed_by_id=uuid4(),
        ))
        assert isinstance(result, DealOutput)

    async def test_deal_stage_updated(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """stage_id в DTO отражает новый этап."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(MoveDealStageInput(
            deal_id=deal.id,
            new_stage_id=stage2.id,
            pipeline_id=pipeline.id,
            performed_by_id=uuid4(),
        ))
        assert result.stage_id == stage2.id

    async def test_deal_saved(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Обновлённая сделка сохраняется в репозиторий."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(MoveDealStageInput(
            deal_id=deal.id,
            new_stage_id=stage2.id,
            pipeline_id=pipeline.id,
            performed_by_id=uuid4(),
        ))
        deal_repo.save.assert_called_once()

    async def test_activity_saved(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
        activity_repo: AsyncMock,
    ) -> None:
        """Запись аудита о смене этапа сохраняется."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(MoveDealStageInput(
            deal_id=deal.id,
            new_stage_id=stage2.id,
            pipeline_id=pipeline.id,
            performed_by_id=uuid4(),
        ))
        activity_repo.save.assert_called_once()

    async def test_activity_has_stage_change_type(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
        activity_repo: AsyncMock,
    ) -> None:
        """Тип активности в сохранённой записи — STAGE_CHANGE."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(MoveDealStageInput(
            deal_id=deal.id,
            new_stage_id=stage2.id,
            pipeline_id=pipeline.id,
            performed_by_id=uuid4(),
        ))
        saved_activity = activity_repo.save.call_args[0][0]
        assert saved_activity.activity_type == ActivityType.STAGE_CHANGE

    async def test_activity_body_contains_stage_names(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
        activity_repo: AsyncMock,
    ) -> None:
        """Тело активности содержит имена обоих этапов."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(MoveDealStageInput(
            deal_id=deal.id,
            new_stage_id=stage2.id,
            pipeline_id=pipeline.id,
            performed_by_id=uuid4(),
        ))
        saved_activity = activity_repo.save.call_args[0][0]
        assert "Prospecting" in saved_activity.body
        assert "Negotiation" in saved_activity.body

    async def test_performer_id_on_activity(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
        activity_repo: AsyncMock,
    ) -> None:
        """performed_by_id передаётся в активность."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        performer = uuid4()
        await use_case.execute(MoveDealStageInput(
            deal_id=deal.id,
            new_stage_id=stage2.id,
            pipeline_id=pipeline.id,
            performed_by_id=performer,
        ))
        saved_activity = activity_repo.save.call_args[0][0]
        assert saved_activity.performed_by_id == performer


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestMoveDealStageGuards:
    async def test_deal_not_found_raises(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Отсутствующая сделка вызывает DealNotFoundError."""
        deal_repo.get_by_id.return_value = None

        with pytest.raises(DealNotFoundError):
            await use_case.execute(MoveDealStageInput(
                deal_id=uuid4(),
                new_stage_id=uuid4(),
                pipeline_id=uuid4(),
                performed_by_id=uuid4(),
            ))

    async def test_pipeline_not_found_raises(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Отсутствующая воронка вызывает PipelineNotFoundError."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = None

        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(MoveDealStageInput(
                deal_id=deal.id,
                new_stage_id=stage2.id,
                pipeline_id=pipeline.id,
                performed_by_id=uuid4(),
            ))

    async def test_stage_not_in_pipeline_raises(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Чужой этап вызывает StageNotInPipelineError."""
        pipeline, stage1, _ = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        with pytest.raises(StageNotInPipelineError):
            await use_case.execute(MoveDealStageInput(
                deal_id=deal.id,
                new_stage_id=uuid4(),  # нет в воронке
                pipeline_id=pipeline.id,
                performed_by_id=uuid4(),
            ))

    async def test_closed_deal_raises(
        self,
        use_case: MoveDealStageUseCase,
        deal_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Перемещение закрытой сделки вызывает доменное DealAlreadyClosedError."""
        pipeline, stage1, stage2 = make_pipeline_with_two_stages()
        deal = make_open_deal(pipeline.id, stage1.id)
        deal.win()  # закрываем сделку
        deal_repo.get_by_id.return_value = deal
        pipeline_repo.get_by_id.return_value = pipeline

        with pytest.raises(DealAlreadyClosedError):
            await use_case.execute(MoveDealStageInput(
                deal_id=deal.id,
                new_stage_id=stage2.id,
                pipeline_id=pipeline.id,
                performed_by_id=uuid4(),
            ))
