"""
Интерфейс репозитория встреч — контракт для инфраструктурного слоя.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.meeting import Meeting
from src.domain.value_objects.enums import MeetingStatus


class IMeetingRepository(ABC):

    @abstractmethod
    async def get_by_id(self, meeting_id: UUID) -> Meeting | None: ...

    @abstractmethod
    async def save(self, meeting: Meeting) -> Meeting: ...

    @abstractmethod
    async def delete(self, meeting_id: UUID) -> None: ...

    @abstractmethod
    async def find_all(
        self,
        created_by_id: UUID | None = None,
        lead_id: UUID | None = None,
        deal_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        status: MeetingStatus | None = None,
    ) -> list[Meeting]: ...
