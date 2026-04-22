"""
DeleteUserDataUseCase — полное удаление данных пользователя (GDPR Right to Erasure).

Порядок операций:
1. Найти все лиды пользователя
2. Для каждого лида: удалить email-сообщения + стереть активности сущности
3. Удалить лиды
4. Найти все сделки пользователя → удалить
5. Стереть активности, где пользователь является исполнителем
6. Записать в журнал аудита GDPR
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.gdpr_dtos import DeleteUserDataOutput
from src.application.exceptions import GdprTargetNotFoundError
from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.domain.repositories.gdpr_audit_repository import IGdprAuditRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.value_objects.enums import GdprEventType


class DeleteUserDataUseCase:
    """Реализует GDPR Right to Erasure для пользователя-владельца данных."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
        email_repo: IEmailMessageRepository,
        activity_repo: IActivityRepository,
        gdpr_audit_repo: IGdprAuditRepository,
    ) -> None:
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo
        self._email_repo = email_repo
        self._activity_repo = activity_repo
        self._gdpr_audit_repo = gdpr_audit_repo

    async def execute(
        self,
        user_id: UUID,
        performed_by_id: UUID | None = None,
    ) -> DeleteUserDataOutput:
        """Удаляет все данные пользователя из системы и фиксирует событие аудита."""
        leads = await self._lead_repo.find_by_owner(user_id)
        deals = await self._deal_repo.find_by_owner(user_id)

        if not leads and not deals:
            raise GdprTargetNotFoundError("User", user_id)

        emails_deleted = 0
        activities_erased = 0

        # ── Шаг 1-3: Лиды и связанные данные ──────────────────────────────────
        for lead in leads:
            # Удалить email-сообщения лида
            lead_emails = await self._email_repo.find_by_lead_id(lead.id)
            for email in lead_emails:
                await self._email_repo.delete(email.id)
            emails_deleted += len(lead_emails)

            # GDPR-стереть активности сущности «лид»
            erased = await self._activity_repo.gdpr_erase_by_entity(lead.id)
            activities_erased += erased

            await self._lead_repo.delete(lead.id)

        # ── Шаг 4: Сделки ──────────────────────────────────────────────────────
        for deal in deals:
            erased = await self._activity_repo.gdpr_erase_by_entity(deal.id)
            activities_erased += erased
            await self._deal_repo.delete(deal.id)

        # ── Шаг 5: Активности, выполненные пользователем ──────────────────────
        erased = await self._activity_repo.gdpr_erase_by_performer(user_id)
        activities_erased += erased

        # ── Шаг 6: Запись аудита ───────────────────────────────────────────────
        summary = (
            f"User {user_id}: deleted {len(leads)} leads, "
            f"{len(deals)} deals, {emails_deleted} emails, "
            f"{activities_erased} activities."
        )
        audit_entry = GdprAuditEntry.create(
            event_type=GdprEventType.USER_DATA_DELETED,
            target_type="user",
            target_id=user_id,
            summary=summary,
            performed_by_id=performed_by_id,
        )
        await self._gdpr_audit_repo.save(audit_entry)

        return DeleteUserDataOutput(
            user_id=user_id,
            leads_deleted=len(leads),
            emails_deleted=emails_deleted,
            deals_deleted=len(deals),
            activities_erased=activities_erased,
            audit_entry_id=audit_entry.id,
        )
