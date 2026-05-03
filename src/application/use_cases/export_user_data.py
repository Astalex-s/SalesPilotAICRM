"""
ExportUserDataUseCase — экспорт всех данных пользователя (GDPR Art. 20 Right to Portability).

Собирает лиды, сделки и email-сообщения пользователя и возвращает
их в виде структурированного DTO для выгрузки в JSON-файл.
Фиксирует событие в журнале аудита GDPR.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from src.application.dtos.gdpr_dtos import (
    DealExportItem,
    EmailExportItem,
    LeadExportItem,
    UserDataExportOutput,
)
from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.domain.repositories.gdpr_audit_repository import IGdprAuditRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.value_objects.enums import GdprEventType


class ExportUserDataUseCase:
    """Реализует GDPR Art. 20 — Right to Data Portability."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
        email_repo: IEmailMessageRepository,
        gdpr_audit_repo: IGdprAuditRepository,
    ) -> None:
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo
        self._email_repo = email_repo
        self._gdpr_audit_repo = gdpr_audit_repo

    async def execute(
        self,
        user_id: UUID,
        performed_by_id: UUID | None = None,
    ) -> UserDataExportOutput:
        """Собирает все данные пользователя и записывает событие аудита.

        Возвращает UserDataExportOutput даже если данных нет (пустые списки),
        поскольку отсутствие данных само по себе является валидным ответом на Art. 20.
        """
        leads = await self._lead_repo.find_by_owner(user_id)
        deals = await self._deal_repo.find_by_owner(user_id)

        # Собрать email-сообщения по всем лидам пользователя
        emails = []
        for lead in leads:
            lead_emails = await self._email_repo.find_by_lead_id(lead.id)
            emails.extend(lead_emails)

        # Маппинг в export items
        lead_items = [
            LeadExportItem(
                id=lead.id,
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email.value,
                status=lead.status.value,
                source=lead.source.value,
                company=lead.company,
                phone=lead.phone.value if lead.phone else None,
                notes=lead.notes,
                created_at=lead.created_at,
            )
            for lead in leads
        ]
        deal_items = [
            DealExportItem(
                id=deal.id,
                title=deal.title,
                status=deal.status.value,
                value_amount=float(deal.value.amount),
                value_currency=deal.value.currency,
                created_at=deal.created_at,
            )
            for deal in deals
        ]
        email_items = [
            EmailExportItem(
                id=email.id,
                subject=email.subject,
                from_address=email.from_address,
                to_addresses=email.to_addresses,
                direction=email.direction.value,
                received_at=email.received_at,
            )
            for email in emails
        ]

        # Запись аудита
        exported_at = datetime.now(timezone.utc)
        summary = (
            f"User {user_id}: exported {len(leads)} leads, "
            f"{len(deals)} deals, {len(emails)} emails."
        )
        audit_entry = GdprAuditEntry.create(
            event_type=GdprEventType.USER_DATA_EXPORTED,
            target_type="user",
            target_id=user_id,
            summary=summary,
            performed_by_id=performed_by_id,
        )
        await self._gdpr_audit_repo.save(audit_entry)

        return UserDataExportOutput(
            user_id=user_id,
            exported_at=exported_at,
            leads=lead_items,
            deals=deal_items,
            emails=email_items,
            audit_entry_id=audit_entry.id,
        )
