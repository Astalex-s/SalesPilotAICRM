"""
Фикстуры для интеграционных тестов БД.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.infrastructure.database.base import Base
# Необходимо импортировать модели, чтобы они зарегистрировались в Base.metadata
import src.infrastructure.database.models # noqa

@pytest_asyncio.fixture
async def db_session():
    """Создаёт сессию для SQLite в памяти для тестов."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with factory() as session:
        yield session

    await engine.dispose()
