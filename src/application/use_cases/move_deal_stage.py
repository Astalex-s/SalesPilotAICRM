"""
MoveDealStageUseCase — use case перемещения сделки на новый этап воронки.

Единственная ответственность: проверить принадлежность нового этапа воронке,
переместить сделку и записать событие в журнал аудита.
"""
from __future__ import annotations

from src.application.dtos.deal_dtos import DealOutput, MoveDealStageInput
from src.application.exceptions import (
    DealNotFoundError,
    PipelineNotFoundError,
    StageNotInPipelineError,
)
from src.domain.entities.activity import Activity
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.pipeline_repository import IPipelineRepository


class MoveDealStageUseCase:
    """Перемещает открытую сделку на новый этап той же воронки."""

    def __init__(
        self,
        deal_repo: IDealRepository,
        pipeline_repo: IPipelineRepository,
        activity_repo: IActivityRepository,
    ) -> None:
        self._deal_repo = deal_repo
        self._pipeline_repo = pipeline_repo
        self._activity_repo = activity_repo

    async def execute(self, data: MoveDealStageInput) -> DealOutput:
        """Выполняет перемещение сделки на новый этап.

        Последовательность:
        1. Загружает сделку — DealNotFoundError если не найдена.
        2. Загружает воронку — PipelineNotFoundError если не найдена.
        3. Проверяет, что новый этап принадлежит воронке — StageNotInPipelineError иначе.
        4. Запоминает текущий этап, вызывает deal.move_to_stage() (доменный инвариант).
        5. Создаёт запись аудита о смене этапа.
        6. Атомарно сохраняет сделку и активность.
        7. Возвращает DealOutput.

        Вызывает:
            DealNotFoundError: Сделка не найдена.
            PipelineNotFoundError: Воронка не найдена.
            StageNotInPipelineError: Новый этап не принадлежит воронке.
            DealAlreadyClosedError: Сделка закрыта (доменное).
        """
        # Шаг 1: загрузка сделки
        deal = await self._deal_repo.get_by_id(data.deal_id)
        if deal is None:
            raise DealNotFoundError(data.deal_id)

        # Шаг 2: загрузка воронки
        pipeline = await self._pipeline_repo.get_by_id(data.pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(data.pipeline_id)

        # Шаг 3: проверка принадлежности нового этапа воронке
        stage_map = {s.id: s for s in pipeline.stages}
        if data.new_stage_id not in stage_map:
            raise StageNotInPipelineError(data.new_stage_id, data.pipeline_id)

        # Шаг 4: запоминаем старый этап и перемещаем сделку
        old_stage = stage_map.get(deal.stage_id)
        new_stage = stage_map[data.new_stage_id]

        old_stage_name = old_stage.name if old_stage else str(deal.stage_id)
        new_stage_name = new_stage.name

        deal.move_to_stage(
            new_stage_id=data.new_stage_id,
            pipeline_id=data.pipeline_id,
        )

        # Шаг 5: создание записи аудита
        activity = Activity.log_stage_change(
            deal_id=deal.id,
            performed_by_id=data.performed_by_id,
            from_stage=old_stage_name,
            to_stage=new_stage_name,
        )

        # Шаг 6: атомарное сохранение
        await self._deal_repo.save(deal)
        await self._activity_repo.save(activity)

        # Шаг 7: возврат DTO
        return DealOutput.from_entity(deal)
