"""
Корневой conftest.py — общие фикстуры для всех тестовых наборов.
Фикстуры, специфичные для фич, добавляются рядом с соответствующими use cases.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Асинхронный HTTP-клиент для интеграционных тестов через ASGI."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
