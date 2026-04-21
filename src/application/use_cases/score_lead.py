"""
ScoreLeadUseCase — AI-оценка лида.

Единственная ответственность: загрузить лида, сериализовать контекст,
вызвать IAIService.score_lead() и вернуть DTO.
AI-провайдер не упоминается — только через абстракцию.
"""
from __future__ import annotations

from src.application.dtos.ai_dtos import LeadScoreInput, LeadScoreOutput
from src.application.exceptions import LeadNotFoundError
from src.application.ports.ai_service import IAIService
from src.domain.repositories.lead_repository import ILeadRepository


class ScoreLeadUseCase:
    """Запрашивает у AI-сервиса оценку вероятности конвертации лида."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        ai_service: IAIService,
    ) -> None:
        self._lead_repo = lead_repo
        self._ai_service = ai_service

    async def execute(self, data: LeadScoreInput) -> LeadScoreOutput:
        """Выполняет AI-оценку лида.

        Последовательность:
        1. Загружает лида — LeadNotFoundError если не найден.
        2. Сериализует доменные данные в словарь (граница AI).
        3. Вызывает IAIService.score_lead().
        4. Возвращает LeadScoreOutput.
        """
        # Шаг 1: загрузка доменной сущности
        lead = await self._lead_repo.get_by_id(data.lead_id)
        if lead is None:
            raise LeadNotFoundError(data.lead_id)

        # Шаг 2: сериализация контекста — доменные объекты не пересекают границу AI
        lead_context = {
            "name": lead.full_name,
            "email": str(lead.email),
            "company": lead.company or "Не указана",
            "source": lead.source.value,
            "status": lead.status.value,
            "phone": str(lead.phone) if lead.phone else None,
            "notes": lead.notes or "Нет заметок",
        }

        # Шаг 3: вызов AI через абстракцию
        result = await self._ai_service.score_lead(lead_context)

        # Шаг 4: формирование DTO
        return LeadScoreOutput(
            lead_id=lead.id,
            score=result.score,
            reasoning=result.reasoning,
            recommended_actions=result.recommended_actions,
        )
