"""
LeadConversionService — чистый доменный сервис.

Оркестрирует безопасную конвертацию квалифицированного лида в сделку.
Без ORM, без HTTP, без внешних вызовов — только доменные сущности и правила.
"""
from __future__ import annotations

from uuid import UUID

from src.domain.entities.activity import Activity
from src.domain.entities.deal import Deal
from src.domain.entities.lead import Lead
from src.domain.value_objects.money import Money


class LeadConversionService:
    """Конвертирует квалифицированный лид в сделку с полным журналом аудита.

    Сервис не имеет состояния. Все бизнес-правила делегированы
    непосредственно сущности Lead.

    Пример использования:
        service = LeadConversionService()
        deal, activity = service.convert(lead, stage_id=..., pipeline_id=...)
    """

    def convert(
        self,
        lead: Lead,
        stage_id: UUID,
        pipeline_id: UUID,
        deal_title: str | None = None,
        deal_value: Money | None = None,
        performed_by_id: UUID | None = None,
    ) -> tuple[Deal, Activity]:
        """Конвертирует квалифицированный лид в сделку.

        Последовательность операций:
        1. Создаёт Deal на основе данных лида.
        2. Вызывает lead.mark_converted() — который проверяет инвариант QUALIFIED.
        3. Генерирует неизменяемую запись Activity в журнал аудита.

        Аргументы:
            lead: Лид в статусе QUALIFIED.
            stage_id: Начальный этап для новой сделки.
            pipeline_id: Воронка, которой принадлежит этап.
            deal_title: Необязательный заголовок; по умолчанию «Deal — {lead.full_name}».
            deal_value: Необязательная начальная сумма; по умолчанию Money.zero().
            performed_by_id: ID пользователя, выполняющего конвертацию; по умолчанию владелец лида.

        Возвращает:
            Кортеж (Deal, Activity) — оба объекта должны быть сохранены вызывающим Use Case.

        Вызывает:
            LeadNotQualifiedError: Если lead.status != QUALIFIED.
            LeadAlreadyConvertedError: Если лид уже конвертирован.
        """
        actor_id: UUID = performed_by_id or lead.owner_id
        title: str = deal_title or f"Deal — {lead.full_name}"
        value: Money = deal_value or Money.zero()

        deal = Deal.create(
            title=title,
            owner_id=lead.owner_id,
            stage_id=stage_id,
            pipeline_id=pipeline_id,
            value=value,
            contact_name=lead.full_name,
            company=lead.company,
            source_lead_id=lead.id,
        )

        # Проверяет доменный инвариант: выбрасывает, если лид не QUALIFIED или уже конвертирован
        lead.mark_converted(deal_id=deal.id)

        activity = Activity.log_lead_conversion(
            lead_id=lead.id,
            deal_id=deal.id,
            performed_by_id=actor_id,
            lead_name=lead.full_name,
            deal_title=deal.title,
        )

        return deal, activity
