"""
Фабрика асинхронного клиента Redis.
Управляет жизненным циклом соединения (init/close) и предоставляет зависимость FastAPI.
"""
from redis.asyncio import Redis

from src.infrastructure.config.settings import settings

_redis_client: Redis | None = None


async def init_redis() -> None:
    """Инициализирует пул соединений Redis при старте приложения."""
    global _redis_client
    _redis_client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        encoding="utf-8",
    )
    await _redis_client.ping()


async def close_redis() -> None:
    """Закрывает пул соединений Redis при остановке приложения."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


async def get_redis() -> Redis:
    """Зависимость FastAPI — возвращает общий клиент Redis."""
    if _redis_client is None:
        raise RuntimeError("Redis-клиент не инициализирован. Вызовите init_redis() первым.")
    return _redis_client
