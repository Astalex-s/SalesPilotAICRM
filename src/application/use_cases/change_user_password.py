"""
ChangeUserPasswordUseCase — смена пароля текущего пользователя.
Проверяет текущий пароль перед сохранением нового.
"""
from __future__ import annotations

from uuid import UUID

from src.application.dtos.auth_dtos import ChangePasswordInput
from src.application.exceptions import InvalidCurrentPasswordError, UserNotFoundError
from src.infrastructure.auth.auth_service import hash_password, verify_password
from src.infrastructure.database.repositories.user_repository import SqlUserRepository


class ChangeUserPasswordUseCase:
    def __init__(self, user_repo: SqlUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: UUID, data: ChangePasswordInput) -> None:
        result = await self._user_repo.find_by_id_with_hash(user_id)
        if result is None:
            raise UserNotFoundError(user_id)

        _, current_hash = result
        if not verify_password(data.current_password, current_hash):
            raise InvalidCurrentPasswordError()

        new_hash = hash_password(data.new_password)
        await self._user_repo.update_password_hash(user_id, new_hash)
