"""
HTTP-схемы для операций со сделками на уровне Interfaces.
Используются только там, где HTTP-форма отличается от application DTO
(например, PATCH /deals/{id}/stage — deal_id берётся из пути, не из тела).
"""
from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class MoveDealStageRequest(BaseModel):
    """Тело запроса PATCH /deals/{deal_id}/stage.

    deal_id передаётся в path-параметре и добавляется контроллером
    при формировании MoveDealStageInput для use case.
    """

    new_stage_id: UUID
    pipeline_id: UUID
    performed_by_id: UUID


class CloseDealRequest(BaseModel):
    """Тело запроса PATCH /deals/{deal_id}/close.

    deal_id и performed_by_id берутся из path и токена.
    """

    outcome: Literal["won", "lost"]
