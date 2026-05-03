"""
DTO для GDPR-модуля.
Read-model: результаты операций по запросам субъектов данных.
Нет зависимостей на ORM, FastAPI или конкретные провайдеры.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.value_objects.enums import GdprEventType


# ── Экспорт данных (Art. 20) ──────────────────────────────────────────────────

class LeadExportItem(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    status: str
    source: str
    company: str | None = None
    phone: str | None = None
    notes: str | None = None
    created_at: datetime


class DealExportItem(BaseModel):
    id: UUID
    title: str
    status: str
    value_amount: float
    value_currency: str
    created_at: datetime


class EmailExportItem(BaseModel):
    id: str
    subject: str
    from_address: str
    to_addresses: list[str]
    direction: str
    received_at: datetime


class UserDataExportOutput(BaseModel):
    """Полный экспорт данных пользователя — GDPR Art. 20 Right to Portability."""

    user_id: UUID
    exported_at: datetime
    leads: list[LeadExportItem]
    deals: list[DealExportItem]
    emails: list[EmailExportItem]
    audit_entry_id: UUID


# ── Retention policy ──────────────────────────────────────────────────────────

class RetentionPolicyOutput(BaseModel):
    """Результат применения политики хранения данных."""

    retention_days: int
    leads_deleted: int = Field(ge=0)
    deals_deleted: int = Field(ge=0)
    emails_deleted: int = Field(ge=0)
    activities_erased: int = Field(ge=0)
    audit_entry_id: UUID


class GdprAuditEntryOutput(BaseModel):
    """Запись журнала аудита GDPR для API-ответа."""

    id: UUID
    event_type: GdprEventType
    target_type: str
    target_id: UUID
    summary: str
    performed_at: datetime
    performed_by_id: UUID | None = None


class DeleteUserDataOutput(BaseModel):
    """Результат удаления данных пользователя (GDPR Right to Erasure)."""

    user_id: UUID
    leads_deleted: int = Field(ge=0, description="Количество удалённых лидов")
    emails_deleted: int = Field(ge=0, description="Количество удалённых email-сообщений")
    deals_deleted: int = Field(ge=0, description="Количество удалённых сделок")
    activities_erased: int = Field(ge=0, description="Количество удалённых активностей")
    audit_entry_id: UUID = Field(description="ID записи аудита GDPR")


class AnonymizeLeadOutput(BaseModel):
    """Результат анонимизации лида (GDPR Right to Erasure / псевдонимизация)."""

    lead_id: UUID
    emails_deleted: int = Field(ge=0, description="Количество удалённых email-сообщений лида")
    activities_erased: int = Field(ge=0, description="Количество удалённых активностей лида")
    audit_entry_id: UUID = Field(description="ID записи аудита GDPR")


class GdprAuditLogOutput(BaseModel):
    """Страница журнала аудита GDPR с пагинацией."""

    entries: list[GdprAuditEntryOutput]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
