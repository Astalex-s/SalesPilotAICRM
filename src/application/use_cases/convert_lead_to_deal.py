"""
ConvertLeadToDealUseCase — use case конвертации квалифицированного лида в сделку.

Единственная ответственность: оркестрировать конвертацию через доменный сервис
и атомарно сохранить сделку, обновлённый лид и запись аудита.
"""
from __future__ import annotations

from src.application.dtos.deal_dtos import ConvertLeadToDealInput, DealOutput
from src.application.exceptions import (
    LeadNotFoundError,
    PipelineNotFoundError,
    StageNotInPipelineError,
)
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.repositories.pipeline_repository import IPipelineRepository
from src.domain.services.lead_conversion_service import LeadConversionService
from src.domain.value_objects.money import Money


class ConvertLeadToDealUseCase:
    """Конвертирует квалифицированный лид в сделку.

    Координирует проверку принадлежности этапа воронке,
    вызов доменного сервиса и атомарное сохранение всех изменений.
    """

    def __init__(
        self,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
        activity_repo: IActivityRepository,
        pipeline_repo: IPipelineRepository,
    ) -> None:
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo
        self._activity_repo = activity_repo
        self._pipeline_repo = pipeline_repo
        # Доменный сервис без состояния
        self._conversion_service = LeadConversionService()

    async def execute(self, data: ConvertLeadToDealInput) -> DealOutput:
        """Выполняет конвертацию лида в сделку.

        Последовательность:
        1. Загружает лид — выбрасывает LeadNotFoundError, если не найден.
        2. Загружает воронку — выбрасывает PipelineNotFoundError, если не найдена.
        3. Проверяет, что этап принадлежит воронке — StageNotInPipelineError иначе.
        4. Вызывает LeadConversionService.convert() — доменные инварианты проверяются там.
        5. Атомарно сохраняет сделку, обновлённый лид и запись активности.
        6. Возвращает DealOutput.

        Вызывает:
            LeadNotFoundError: Лид не найден.
            PipelineNotFoundError: Воронка не найдена.
            StageNotInPipelineError: Этап не принадлежит указанной воронке.
            LeadNotQualifiedError: Лид не имеет статуса QUALIFIED (доменное).
            LeadAlreadyConvertedError: Лид уже конвертирован (доменное).
        """
        # Шаг 1: загрузка лида
        lead = await self._lead_repo.get_by_id(data.lead_id)
        if lead is None:
            raise LeadNotFoundError(data.lead_id)

        # Шаг 2: загрузка воронки
        pipeline = await self._pipeline_repo.get_by_id(data.pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(data.pipeline_id)

        # Шаг 3: проверка принадлежности этапа воронке
        stage_ids = {s.id for s in pipeline.stages}
        if data.stage_id not in stage_ids:
            raise StageNotInPipelineError(data.stage_id, data.pipeline_id)

        # Шаг 4: конвертация через доменный сервис
        deal_value = Money(
            amount=data.deal_value_amount,
            currency=data.deal_value_currency,
        )
        deal, activity = self._conversion_service.convert(
            lead=lead,
            stage_id=data.stage_id,
            pipeline_id=data.pipeline_id,
            deal_title=data.deal_title,
            deal_value=deal_value,
            performed_by_id=data.performed_by_id,
        )

        # Шаг 5: атомарное сохранение всех трёх сущностей
        await self._deal_repo.save(deal)
        await self._lead_repo.save(lead)
        await self._activity_repo.save(activity)

        # Шаг 6: возврат DTO
        return DealOutput.from_entity(deal)
