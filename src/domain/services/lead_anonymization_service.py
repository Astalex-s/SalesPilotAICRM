"""
LeadAnonymizationService — доменный сервис анонимизации PII лида.
Мутирует лид in-place: заменяет персональные данные на псевдонимы GDPR.
"""
from __future__ import annotations

from src.domain.entities.lead import Lead
from src.domain.value_objects.email import Email


class LeadAnonymizationService:
    """Заменяет все PII-поля лида на GDPR-безопасные заглушки.

    Формат анонимной почты: anon-{uuid8}@gdpr.deleted
    — проходит валидацию Email VO (regex допускает домен gdpr.deleted).
    Статус и pipeline-данные сохраняются для аналитики.
    """

    def anonymize(self, lead: Lead) -> None:
        """Мутирует лид in-place, удаляя все персональные данные.

        Оставляет нетронутыми: id, owner_id, status, source,
        created_at, converted_deal_id — они не являются PII.
        """
        anon_id = str(lead.id)[:8]
        lead.first_name = "[ANONYMIZED]"
        lead.last_name = "[ANONYMIZED]"
        lead.email = Email(f"anon-{anon_id}@gdpr.deleted")
        lead.phone = None
        lead.company = None
        lead.notes = None
        lead._touch()
