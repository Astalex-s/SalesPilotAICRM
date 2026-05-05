"""
Pydantic-схемы запросов для роутера /leads.
Отделены от DTO приложения, чтобы не тащить HTTP-специфику в use cases.
"""
from __future__ import annotations

from pydantic import BaseModel

from src.domain.value_objects.enums import LeadStatus


class UpdateLeadRequest(BaseModel):
    """Тело запроса PATCH /leads/{lead_id}. Все поля опциональны."""

    status: LeadStatus | None = None
    notes: str | None = None
    tags: list[str] | None = None
    category: str | None = None
