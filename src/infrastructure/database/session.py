"""
Фабрика асинхронных сессий базы данных.
Предоставляет зависимость get_db() для инъекции в маршруты FastAPI.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость FastAPI — возвращает транзакционную асинхронную сессию БД.

    Транзакция автоматически коммитится при успешном завершении запроса.
    При исключении выполняется rollback.
    Репозитории используют flush() — commit происходит здесь, на границе запроса.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
