"""
ListLeadTagsUseCase — возвращает все уникальные теги лидов.
"""
from __future__ import annotations

from src.domain.repositories.lead_repository import ILeadRepository


class ListLeadTagsUseCase:
    def __init__(self, lead_repo: ILeadRepository) -> None:
        self._lead_repo = lead_repo

    async def execute(self) -> list[str]:
        return await self._lead_repo.get_all_tags()
