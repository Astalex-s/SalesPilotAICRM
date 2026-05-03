"""
ApplyRetentionPolicyUseCase — автоматическое удаление устаревших данных (GDPR retention policy).

Удаляет лиды и сделки, созданные более чем `retention_days` дней назад.
Фиксирует событие в журнале аудита GDPR.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.application.dtos.gdpr_dtos import RetentionPolicyOutput
from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.email_message_repository import IEmailMessageRepository
from src.domain.repositories.gdpr_audit_repository import IGdprAuditRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.value_objects.enums import GdprEventType

logger = logging.getLogger(__name__)

# Системный UUID как исполнитель для автоматических retention-операций
_SYSTEM_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000001")


def _before_cutoff(dt: datetime, cutoff: datetime) -> bool:
    """Сравнивает datetime с cutoff, нормализуя timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt < cutoff


class ApplyRetentionPolicyUseCase:
    """Удаляет данные старше retention_days и фиксирует результат в аудите."""

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

    async def execute(self, retention_days: int) -> RetentionPolicyOutput:
        """Применяет политику хранения: удаляет записи старше retention_days.

        Порядок операций:
        1. Найти лиды и сделки с created_at < cutoff
        2. Для каждого лида: удалить email + активности, затем сам лид
        3. Для каждой сделки: удалить активности, затем сделку
        4. Записать событие в журнал аудита
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        logger.info("Retention policy: cutoff=%s, retention_days=%d", cutoff.date(), retention_days)

        all_leads = await self._lead_repo.find_all()
        old_leads = [l for l in all_leads if _before_cutoff(l.created_at, cutoff)]

        all_deals = await self._deal_repo.find_all()
        old_deals = [d for d in all_deals if _before_cutoff(d.created_at, cutoff)]

        emails_deleted = 0
        activities_erased = 0

        # ── Удаление лидов ────────────────────────────────────────────────────
        for lead in old_leads:
            lead_emails = await self._email_repo.find_by_lead_id(lead.id)
            for email in lead_emails:
                await self._email_repo.delete(email.id)
            emails_deleted += len(lead_emails)

            erased = await self._activity_repo.gdpr_erase_by_entity(lead.id)
            activities_erased += erased
            await self._lead_repo.delete(lead.id)
            logger.debug("Retention: удалён лид %s (created=%s)", lead.id, lead.created_at.date())

        # ── Удаление сделок ───────────────────────────────────────────────────
        for deal in old_deals:
            erased = await self._activity_repo.gdpr_erase_by_entity(deal.id)
            activities_erased += erased
            await self._deal_repo.delete(deal.id)
            logger.debug("Retention: удалена сделка %s (created=%s)", deal.id, deal.created_at.date())

        # ── Аудит ─────────────────────────────────────────────────────────────
        summary = (
            f"Retention policy ({retention_days}d): "
            f"deleted {len(old_leads)} leads, {len(old_deals)} deals, "
            f"{emails_deleted} emails, {activities_erased} activities. "
            f"Cutoff: {cutoff.date()}."
        )
        audit_entry = GdprAuditEntry.create(
            event_type=GdprEventType.RETENTION_POLICY_APPLIED,
            target_type="system",
            target_id=_SYSTEM_ACTOR_ID,
            summary=summary,
            performed_by_id=_SYSTEM_ACTOR_ID,
        )
        await self._gdpr_audit_repo.save(audit_entry)

        logger.info("Retention policy applied: %s", summary)

        return RetentionPolicyOutput(
            retention_days=retention_days,
            leads_deleted=len(old_leads),
            deals_deleted=len(old_deals),
            emails_deleted=emails_deleted,
            activities_erased=activities_erased,
            audit_entry_id=audit_entry.id,
        )
