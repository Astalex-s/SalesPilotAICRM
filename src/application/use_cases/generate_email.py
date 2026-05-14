"""
GenerateEmailUseCase — AI-генерация персонализированного email для лида.

Единственная ответственность: загрузить лида, передать контекст в AI-сервис,
вернуть готовый черновик письма.
"""
from __future__ import annotations

from src.application.dtos.ai_dtos import GenerateEmailInput, GenerateEmailOutput
from src.application.exceptions import LeadNotFoundError
from src.application.ports.ai_service import IAIService
from src.domain.repositories.lead_repository import ILeadRepository


class GenerateEmailUseCase:
    """Генерирует персонализированное email-письмо для лида через AI-сервис."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        ai_service: IAIService,
    ) -> None:
        self._lead_repo = lead_repo
        self._ai_service = ai_service

    async def execute(self, data: GenerateEmailInput) -> GenerateEmailOutput:
        """Генерирует email-черновик для лида.

        Последовательность:
        1. Загружает лида — LeadNotFoundError если не найден.
        2. Сериализует контекст лида.
        3. Вызывает IAIService.generate_email().
        4. Возвращает GenerateEmailOutput.
        """
        # Шаг 1: загрузка доменной сущности
        lead = await self._lead_repo.get_by_id(data.lead_id)
        if lead is None:
            raise LeadNotFoundError(data.lead_id)

        # Шаг 2: сериализация контекста
        lead_context = {
            "name": lead.full_name,
            "first_name": lead.first_name,
            "email": str(lead.email),
            "company": lead.company or "Не указана",
            "source": lead.source.value,
            "status": lead.status.value,
            "notes": lead.notes or "Нет заметок",
        }

        # Шаг 2b: контекст отправителя
        sender_context = {
            "name": data.sender_name,
            "email": data.sender_email,
        } if data.sender_name else None

        # Шаг 3: вызов AI через абстракцию
        draft = await self._ai_service.generate_email(
            lead_context=lead_context,
            tone=data.tone,
            extra_context=data.extra_context,
            sender_context=sender_context,
        )

        # Шаг 4: формирование DTO
        return GenerateEmailOutput(
            lead_id=lead.id,
            subject=draft.subject,
            body=draft.body,
            tone=data.tone,
        )
