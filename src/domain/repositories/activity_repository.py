"""
IActivityRepository — интерфейс репозитория домена для сущности Activity.
"""
from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.activity import Activity, EntityType
from src.domain.repositories.base import BaseRepository
from src.domain.value_objects.enums import ActivityType


class IActivityRepository(BaseRepository[Activity]):
    """Контракт для операций с хранилищем активностей.

    Активности только добавляются (append-only). Метод delete() в конкретных
    реализациях обязан выбрасывать NotImplementedError для защиты журнала аудита.
    """

    @abstractmethod
    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Activity]:
        """Возвращает все активности указанной сущности, начиная с последней."""
        ...

    @abstractmethod
    async def find_by_type(
        self,
        activity_type: ActivityType,
    ) -> list[Activity]:
        """Возвращает все активности указанного типа."""
        ...

    @abstractmethod
    async def find_by_performer(self, user_id: UUID) -> list[Activity]:
        """Возвращает все активности, выполненные указанным пользователем."""
        ...

    # ── GDPR-исключения из append-only правила ─────────────────────────────────
    # Эти методы существуют исключительно для выполнения требований GDPR.
    # Они НЕ являются обходом append-only инварианта для иных целей.

    @abstractmethod
    async def gdpr_erase_by_entity(self, entity_id: UUID) -> int:
        """GDPR: физически удаляет все активности сущности.

        Returns:
            Количество удалённых строк.
        """
        ...

    @abstractmethod
    async def gdpr_erase_by_performer(self, user_id: UUID) -> int:
        """GDPR: физически удаляет все активности, выполненные пользователем.

        Returns:
            Количество удалённых строк.
        """
        ...
