"""
Доменные перечисления — используются во всех сущностях домена.
Нет зависимостей на инфраструктуру или фреймворки.
"""
from enum import Enum


class LeadStatus(str, Enum):
    """Статус лида в процессе квалификации."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"


class DealStatus(str, Enum):
    """Статус сделки в воронке продаж."""
    OPEN = "open"
    WON = "won"
    LOST = "lost"


class ActivityType(str, Enum):
    """Тип активности в журнале аудита."""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    STATUS_CHANGE = "status_change"
    STAGE_CHANGE = "stage_change"
    LEAD_CONVERTED = "lead_converted"


class LeadSource(str, Enum):
    """Источник привлечения лида."""
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    OTHER = "other"


class UserRole(str, Enum):
    """Роль пользователя в системе CRM."""
    ADMIN = "admin"
    MANAGER = "manager"
    SALES_REP = "sales_rep"


class EmailDirection(str, Enum):
    """Направление email-письма относительно CRM-системы."""
    INBOUND = "inbound"    # входящее (от контакта к менеджеру)
    OUTBOUND = "outbound"  # исходящее (от менеджера к контакту)
