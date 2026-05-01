"""
ResetPasswordUseCase — валидирует токен из Redis и обновляет хэш пароля.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from redis.asyncio import Redis

from src.application.dtos.auth_dtos import ResetPasswordInput
from src.infrastructure.auth.auth_service import hash_password
from src.infrastructure.database.repositories.user_repository import SqlUserRepository

_REDIS_PREFIX = "pwd_reset:"


class ResetPasswordUseCase:
    def __init__(self, user_repo: SqlUserRepository, redis: Redis) -> None:
        self._user_repo = user_repo
        self._redis = redis

    async def execute(self, data: ResetPasswordInput) -> None:
        redis_key = f"{_REDIS_PREFIX}{data.token}"
        user_id_str: str | None = await self._redis.get(redis_key)

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Токен недействителен или истёк.",
            )

        new_hash = hash_password(data.new_password)
        updated = await self._user_repo.update_password_hash(UUID(user_id_str), new_hash)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не найден.",
            )

        # Токен одноразовый — удаляем сразу после использования
        await self._redis.delete(redis_key)
