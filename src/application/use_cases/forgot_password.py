"""
ForgotPasswordUseCase — генерирует токен сброса пароля и отправляет email.
Намеренно не раскрывает, существует ли пользователь с таким email (против перебора).
"""
from __future__ import annotations

import logging
import uuid

from redis.asyncio import Redis

from src.application.dtos.auth_dtos import ForgotPasswordInput
from src.infrastructure.config.settings import settings
from src.infrastructure.database.repositories.user_repository import SqlUserRepository
from src.infrastructure.email.smtp_service import send_password_reset_email

logger = logging.getLogger(__name__)

_REDIS_PREFIX = "pwd_reset:"


class ForgotPasswordUseCase:
    def __init__(self, user_repo: SqlUserRepository, redis: Redis) -> None:
        self._user_repo = user_repo
        self._redis = redis

    async def execute(self, data: ForgotPasswordInput) -> None:
        user = await self._user_repo.find_by_email(data.email)
        if user is None:
            # Не раскрываем, что email не зарегистрирован
            return

        token = str(uuid.uuid4())
        ttl = settings.PASSWORD_RESET_EXPIRE_MINUTES * 60
        await self._redis.set(f"{_REDIS_PREFIX}{token}", str(user.id), ex=ttl)

        await send_password_reset_email(to_email=data.email, reset_token=token)
