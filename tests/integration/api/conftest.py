"""
Общие фикстуры для API интеграционных тестов.

Каждый тестовый модуль получает изолированную SQLite in-memory БД
(module-scoped engine), тестовое FastAPI-приложение без lifespan
(get_db переопределён) и зарегистрированного admin-пользователя + JWT-токен.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import src.infrastructure.database.models  # noqa — регистрирует ORM-модели
from src.infrastructure.database.base import Base
from src.infrastructure.database.session import get_db
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.v1.routers import (
    analytics_router,
    auth_router,
    deals_router,
    gdpr_router,
    leads_router,
    pipelines_router,
    users_router,
)

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
_ADMIN_EMAIL = "admin_api@test.com"
_ADMIN_PASSWORD = "adminpass123"


# ── Engine / session ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="module")
async def test_engine():
    """Один SQLite-движок на тестовый модуль — таблицы создаются один раз."""
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
def session_factory(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


# ── Test app ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def test_app(session_factory):
    """FastAPI-приложение без lifespan, get_db → SQLite."""
    application = FastAPI()
    register_exception_handlers(application)

    prefix = "/api/v1"
    for rtr in (
        auth_router,
        analytics_router,
        deals_router,
        gdpr_router,
        leads_router,
        pipelines_router,
        users_router,
    ):
        application.include_router(rtr, prefix=prefix)

    async def _get_db_override() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    application.dependency_overrides[get_db] = _get_db_override
    return application


@pytest_asyncio.fixture
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac


# ── Admin user + auth headers ─────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="module")
async def admin_user(test_app):
    """Регистрирует admin-пользователя один раз для модуля и возвращает UserOutput."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        resp = await ac.post("/api/v1/auth/register", json={
            "first_name": "Admin",
            "last_name": "Test",
            "email": _ADMIN_EMAIL,
            "password": _ADMIN_PASSWORD,
            "role": "admin",
        })
        assert resp.status_code in (201, 409), resp.text
        if resp.status_code == 201:
            return resp.json()

        # Уже существует — получаем через login + /auth/me
        login = await ac.post("/api/v1/auth/login", json={
            "email": _ADMIN_EMAIL, "password": _ADMIN_PASSWORD,
        })
        token = login.json()["access_token"]
        me = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        return me.json()


@pytest_asyncio.fixture(scope="module")
async def admin_token(test_app, admin_user):
    """Получает JWT-токен для admin-пользователя."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        resp = await ac.post("/api/v1/auth/login", json={
            "email": _ADMIN_EMAIL,
            "password": _ADMIN_PASSWORD,
        })
        assert resp.status_code == 200, resp.text
        return resp.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
