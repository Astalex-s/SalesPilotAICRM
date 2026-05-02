"""
UpdateUserProfileUseCase — обновление имени и фамилии текущего пользователя.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.auth_dtos import UpdateProfileInput, UserOutput
from src.application.exceptions import UserNotFoundError
from src.infrastructure.database.repositories.user_repository import SqlUserRepository


class UpdateUserProfileUseCase:
    def __init__(self, user_repo: SqlUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: UUID, data: UpdateProfileInput) -> UserOutput:
        updated = await self._user_repo.update_profile(
            user_id, data.first_name, data.last_name
        )
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
