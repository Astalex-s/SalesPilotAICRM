"""
Юнит-тесты use case ConvertLeadToDealUseCase.
"""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.deal_dtos import ConvertLeadToDealInput, DealOutput
from src.application.exceptions import (
    LeadNotFoundError,
    PipelineNotFoundError,
    StageNotInPipelineError,
)
from src.application.use_cases.convert_lead_to_deal import ConvertLeadToDealUseCase
from src.domain.entities.lead import Lead
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.stage import Stage
from src.domain.exceptions import LeadAlreadyConvertedError, LeadNotQualifiedError
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadStatus


# ── Вспомогательные функции ────────────────────────────────────────────────────

def make_qualified_lead() -> Lead:
    """Создаёт квалифицированного лида для тестов."""
    lead = Lead.create(
        first_name="Alice",
        last_name="Walker",
        email=Email("alice@corp.com"),
        owner_id=uuid4(),
        company="Corp Ltd",
    )
    lead.qualify()
    return lead


def make_pipeline_with_stage() -> tuple[Pipeline, Stage]:
    """Создаёт воронку с одним этапом; возвращает (Pipeline, Stage)."""
    pipeline_id = uuid4()
    stage = Stage(
        id=uuid4(),
        pipeline_id=pipeline_id,
        name="Qualification",
        order=0,
        probability=0.3,
    )
    pipeline = Pipeline(
        id=pipeline_id,
        name="Sales Pipeline",
        owner_id=uuid4(),
        stages=[stage],
    )
    return pipeline, stage


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def lead_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.return_value = None
    return repo


@pytest.fixture
def deal_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.return_value = None
    return repo


@pytest.fixture
def activity_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.return_value = None
    return repo


@pytest.fixture
def pipeline_repo() -> AsyncMock:
    repo = AsyncMock()
    return repo


@pytest.fixture
def use_case(
    lead_repo: AsyncMock,
    deal_repo: AsyncMock,
    activity_repo: AsyncMock,
    pipeline_repo: AsyncMock,
) -> ConvertLeadToDealUseCase:
    return ConvertLeadToDealUseCase(
        lead_repo=lead_repo,
        deal_repo=deal_repo,
        activity_repo=activity_repo,
        pipeline_repo=pipeline_repo,
    )


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestConvertLeadToDealHappyPath:
    async def test_returns_deal_output(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """execute возвращает DealOutput для квалифицированного лида."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
        ))
        assert isinstance(result, DealOutput)

    async def test_deal_has_correct_pipeline(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Созданная сделка привязана к правильной воронке."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
        ))
        assert result.pipeline_id == pipeline.id

    async def test_deal_has_correct_stage(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Созданная сделка начинается на правильном этапе."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
        ))
        assert result.stage_id == stage.id

    async def test_deal_custom_title(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Пользовательский заголовок сделки сохраняется."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
            deal_title="Enterprise Deal",
        ))
        assert result.title == "Enterprise Deal"

    async def test_deal_value_set(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Сумма сделки отражается в DTO."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
            deal_value_amount=Decimal("100000"),
            deal_value_currency="USD",
        ))
        assert result.value_amount == Decimal("100000")
        assert result.value_currency == "USD"

    async def test_all_three_repos_saved(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        deal_repo: AsyncMock,
        activity_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Сохраняются сделка, лид и активность."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
        ))
        deal_repo.save.assert_called_once()
        lead_repo.save.assert_called_once()
        activity_repo.save.assert_called_once()

    async def test_source_lead_id_on_deal(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Сделка содержит ссылку на исходный лид."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        result = await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
        ))
        assert result.source_lead_id == lead.id


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestConvertLeadToDealGuards:
    async def test_lead_not_found_raises(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Отсутствующий лид вызывает LeadNotFoundError."""
        lead_repo.get_by_id.return_value = None
        pipeline_repo.get_by_id.return_value = None

        with pytest.raises(LeadNotFoundError):
            await use_case.execute(ConvertLeadToDealInput(
                lead_id=uuid4(),
                stage_id=uuid4(),
                pipeline_id=uuid4(),
            ))

    async def test_pipeline_not_found_raises(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Отсутствующая воронка вызывает PipelineNotFoundError."""
        lead = make_qualified_lead()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = None

        with pytest.raises(PipelineNotFoundError):
            await use_case.execute(ConvertLeadToDealInput(
                lead_id=lead.id,
                stage_id=uuid4(),
                pipeline_id=uuid4(),
            ))

    async def test_stage_not_in_pipeline_raises(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Этап из другой воронки вызывает StageNotInPipelineError."""
        lead = make_qualified_lead()
        pipeline, _ = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        # Передаём случайный stage_id, которого нет в воронке
        with pytest.raises(StageNotInPipelineError):
            await use_case.execute(ConvertLeadToDealInput(
                lead_id=lead.id,
                stage_id=uuid4(),  # чужой этап
                pipeline_id=pipeline.id,
            ))

    async def test_unqualified_lead_raises(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Неквалифицированный лид вызывает доменное LeadNotQualifiedError."""
        lead = Lead.create(
            first_name="Bob",
            last_name="Smith",
            email=Email("bob@example.com"),
            owner_id=uuid4(),
        )
        # Статус NEW — не квалифицирован
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        with pytest.raises(LeadNotQualifiedError):
            await use_case.execute(ConvertLeadToDealInput(
                lead_id=lead.id,
                stage_id=stage.id,
                pipeline_id=pipeline.id,
            ))

    async def test_already_converted_lead_raises(
        self,
        use_case: ConvertLeadToDealUseCase,
        lead_repo: AsyncMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Повторная конвертация вызывает доменное LeadAlreadyConvertedError."""
        lead = make_qualified_lead()
        pipeline, stage = make_pipeline_with_stage()
        lead_repo.get_by_id.return_value = lead
        pipeline_repo.get_by_id.return_value = pipeline

        # Первая конвертация — успешная
        await use_case.execute(ConvertLeadToDealInput(
            lead_id=lead.id,
            stage_id=stage.id,
            pipeline_id=pipeline.id,
        ))

        # Вторая конвертация того же лида
        with pytest.raises(LeadAlreadyConvertedError):
            await use_case.execute(ConvertLeadToDealInput(
                lead_id=lead.id,
                stage_id=stage.id,
                pipeline_id=pipeline.id,
            ))
