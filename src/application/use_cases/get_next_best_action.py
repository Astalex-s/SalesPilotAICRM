"""
GetNextBestActionUseCase — AI-рекомендация следующего действия для лида или сделки.

Единственная ответственность: загрузить сущность нужного типа,
сериализовать контекст, вызвать IAIService.next_best_action() и вернуть DTO.
"""
from __future__ import annotations

from src.application.dtos.ai_dtos import NextBestActionInput, NextBestActionOutput
from src.application.exceptions import DealNotFoundError, LeadNotFoundError
from src.application.ports.ai_service import IAIService
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.lead_repository import ILeadRepository


class GetNextBestActionUseCase:
    """Запрашивает у AI-сервиса следующее наилучшее действие для лида или сделки."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
        ai_service: IAIService,
    ) -> None:
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo
        self._ai_service = ai_service

    async def execute(self, data: NextBestActionInput) -> NextBestActionOutput:
        """Определяет следующее наилучшее действие.

        Последовательность:
        1. Загружает лида или сделку в зависимости от entity_type.
        2. Сериализует контекст с дискриминатором entity_type.
        3. Вызывает IAIService.next_best_action().
        4. Возвращает NextBestActionOutput.

        Вызывает:
            LeadNotFoundError: лид с entity_id не найден.
            DealNotFoundError: сделка с entity_id не найдена.
        """
        if data.entity_type == "lead":
            entity_context = await self._build_lead_context(data)
        else:
            entity_context = await self._build_deal_context(data)

        # Вызов AI через абстракцию
        result = await self._ai_service.next_best_action(entity_context)

        return NextBestActionOutput(
            entity_id=data.entity_id,
            entity_type=data.entity_type,
            action=result.action,
            priority=result.priority,
            reasoning=result.reasoning,
        )

    async def _build_lead_context(self, data: NextBestActionInput) -> dict:
        """Строит контекст для лида."""
        lead = await self._lead_repo.get_by_id(data.entity_id)
        if lead is None:
            raise LeadNotFoundError(data.entity_id)
        return {
            "entity_type": "lead",
            "name": lead.full_name,
            "email": str(lead.email),
            "company": lead.company or "Не указана",
            "status": lead.status.value,
            "source": lead.source.value,
            "notes": lead.notes or "Нет заметок",
        }

    async def _build_deal_context(self, data: NextBestActionInput) -> dict:
        """Строит контекст для сделки."""
        deal = await self._deal_repo.get_by_id(data.entity_id)
        if deal is None:
            raise DealNotFoundError(data.entity_id)
        return {
            "entity_type": "deal",
            "title": deal.title,
            "status": deal.status.value,
            "value_amount": str(deal.value.amount),
            "value_currency": deal.value.currency,
            "company": deal.company or "Не указана",
            "contact_name": deal.contact_name or "Не указан",
            "expected_close_date": (
                deal.expected_close_date.isoformat()
                if deal.expected_close_date else "Не задана"
            ),
        }
