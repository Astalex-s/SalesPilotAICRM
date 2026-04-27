"""
UpdateUserRoleUseCase — изменение роли пользователя (только ADMIN).
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.auth_dtos import UpdateUserRoleInput, UserOutput
from src.application.exceptions import UserNotFoundError
from src.infrastructure.database.repositories.user_repository import SqlUserRepository


class UpdateUserRoleUseCase:
    def __init__(self, user_repo: SqlUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: UUID, data: UpdateUserRoleInput) -> UserOutput:
        updated = await self._user_repo.update_role(user_id, data.role.value)
        if updated is None:
            raise UserNotFoundError(user_id)

        return UserOutput(
            id=updated.id,
            first_name=updated.first_name,
            last_name=updated.last_name,
            email=str(updated.email),
            role=updated.role,
            is_active=updated.is_active,
        )
