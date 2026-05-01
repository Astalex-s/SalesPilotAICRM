"""
LoginUserUseCase — аутентификация пользователя, выдача JWT.
"""
from __future__ import annotations

from src.application.dtos.auth_dtos import LoginInput, TokenOutput
from src.application.exceptions import InvalidCredentialsError
from src.infrastructure.auth.auth_service import create_access_token, create_refresh_token, verify_password
from src.infrastructure.database.repositories.user_repository import SqlUserRepository


class LoginUserUseCase:
    def __init__(self, user_repo: SqlUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, data: LoginInput) -> TokenOutput:
        result = await self._user_repo.find_by_email_with_hash(data.email)
        if result is None:
            raise InvalidCredentialsError()

        user, password_hash = result
        if not user.is_active or not verify_password(data.password, password_hash):
            raise InvalidCredentialsError()

        access_token = create_access_token(user_id=user.id, role=user.role.value)
        refresh_token = create_refresh_token(user_id=user.id, role=user.role.value)
        return TokenOutput(access_token=access_token, refresh_token=refresh_token)
