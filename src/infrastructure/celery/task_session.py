"""
Фабрика сессий БД для Celery задач.

Использует NullPool — соединение создаётся и закрывается за одну задачу.
Это безопасно для asyncio.run() в Celery воркерах: каждый вызов
asyncio.run() создаёт новый event loop, пул NullPool не привязан к loop.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.infrastructure.config.settings import settings


@asynccontextmanager
async def get_task_session() -> AsyncGenerator[AsyncSession, None]:
    """Создаёт одноразовую сессию БД для Celery задачи.

    Движок создаётся и утилизируется при каждом вызове.
    NullPool гарантирует отсутствие утечек соединений между event loop'ами.

    Транзакция коммитится при успешном выходе из контекста,
    при исключении выполняется rollback.
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False,
    )
    try:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        await engine.dispose()
