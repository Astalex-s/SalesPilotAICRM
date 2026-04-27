"""
RegisterUserUseCase — регистрация нового пользователя.
"""
from __future__ import annotations

from src.application.dtos.auth_dtos import RegisterInput, UserOutput
from src.application.exceptions import UserAlreadyExistsError
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.infrastructure.auth.auth_service import hash_password
from src.infrastructure.database.repositories.user_repository import SqlUserRepository


class RegisterUserUseCase:
    def __init__(self, user_repo: SqlUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, data: RegisterInput) -> UserOutput:
        existing = await self._user_repo.find_by_email(data.email)
        if existing:
            raise UserAlreadyExistsError(data.email)

        user = User.create(
            first_name=data.first_name,
            last_name=data.last_name,
            email=Email(data.email),
            role=data.role,
        )
        password_hash = hash_password(data.password)
        saved = await self._user_repo.save_with_hash(user, password_hash)

        return UserOutput(
            id=saved.id,
            first_name=saved.first_name,
            last_name=saved.last_name,
            email=str(saved.email),
            role=saved.role,
            is_active=saved.is_active,
        )
