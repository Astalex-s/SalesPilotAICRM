"""
ListUsersUseCase — возвращает всех пользователей (только для ADMIN).
"""
from __future__ import annotations

from src.application.dtos.auth_dtos import UserOutput
from src.infrastructure.database.repositories.user_repository import SqlUserRepository


class ListUsersUseCase:
    def __init__(self, user_repo: SqlUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self) -> list[UserOutput]:
        users = await self._user_repo.find_all()
        return [
            UserOutput(
                id=u.id,
                first_name=u.first_name,
                last_name=u.last_name,
                email=str(u.email),
                role=u.role,
                is_active=u.is_active,
            )
            for u in users
        ]
