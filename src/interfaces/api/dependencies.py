"""
Общие зависимости FastAPI для слоя Interfaces.
Контроллеры инжектируют инфраструктуру только через эти функции — прямые импорты запрещены.
"""
from collections.abc import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.cache.redis_client import get_redis
from src.infrastructure.database.session import get_db


async def get_session(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет асинхронную сессию БД обработчикам маршрутов."""
    return session


async def get_cache(
    redis: Redis = Depends(get_redis),
) -> Redis:
    """Предоставляет клиент Redis обработчикам маршрутов."""
    return redis
