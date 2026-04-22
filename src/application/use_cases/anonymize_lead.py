"""
AnonymizeLeadUseCase — псевдонимизация PII лида (GDPR Right to Erasure / Art. 17).

Сохраняет лид в системе (аналитика, связи), но заменяет все PII-поля на заглушки.
Email-сообщения лида удаляются физически — они содержат персональные данные контакта.
Активности лида стираются (они могут содержать PII в поле body).
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.gdpr_dtos import AnonymizeLeadOutput
from src.application.exceptions import GdprTargetNotFoundError
from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.domain.repositories.gdpr_audit_repository import IGdprAuditRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.services.lead_anonymization_service import LeadAnonymizationService
from src.domain.value_objects.enums import GdprEventType


class AnonymizeLeadUseCase:
    """Анонимизирует PII лида и удаляет связанные персональные данные."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        email_repo: IEmailMessageRepository,
        activity_repo: IActivityRepository,
        gdpr_audit_repo: IGdprAuditRepository,
        anonymization_service: LeadAnonymizationService,
    ) -> None:
        self._lead_repo = lead_repo
        self._email_repo = email_repo
        self._activity_repo = activity_repo
        self._gdpr_audit_repo = gdpr_audit_repo
        self._anon_service = anonymization_service

    async def execute(
        self,
        lead_id: UUID,
        performed_by_id: UUID | None = None,
    ) -> AnonymizeLeadOutput:
        """Анонимизирует лид и возвращает сводку выполненных операций."""
        lead = await self._lead_repo.get_by_id(lead_id)
        if lead is None:
            raise GdprTargetNotFoundError("Lead", lead_id)

        # ── Шаг 1: Удалить email-сообщения лида ───────────────────────────────
        lead_emails = await self._email_repo.find_by_lead_id(lead_id)
        for email in lead_emails:
            await self._email_repo.delete(email.id)
        emails_deleted = len(lead_emails)

        # ── Шаг 2: Стереть активности лида (могут содержать PII в body) ───────
        activities_erased = await self._activity_repo.gdpr_erase_by_entity(lead_id)

        # ── Шаг 3: Анонимизировать PII лида ───────────────────────────────────
        self._anon_service.anonymize(lead)
        await self._lead_repo.save(lead)

        # ── Шаг 4: Запись аудита ───────────────────────────────────────────────
        summary = (
            f"Lead {lead_id} anonymized: "
            f"{emails_deleted} emails deleted, "
            f"{activities_erased} activities erased."
        )
        audit_entry = GdprAuditEntry.create(
            event_type=GdprEventType.LEAD_ANONYMIZED,
            target_type="lead",
            target_id=lead_id,
            summary=summary,
            performed_by_id=performed_by_id,
        )
        await self._gdpr_audit_repo.save(audit_entry)

        return AnonymizeLeadOutput(
            lead_id=lead_id,
            emails_deleted=emails_deleted,
            activities_erased=activities_erased,
            audit_entry_id=audit_entry.id,
        )
