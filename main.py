"""
Точка входа приложения — только инициализация FastAPI.
Бизнес-логики нет. Роутеры регистрируются по мере реализации фич.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from src.infrastructure.cache.redis_client import close_redis, init_redis
from src.infrastructure.config.settings import settings
from src.infrastructure.database.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управляет запуском и корректным завершением работы инфраструктурных соединений."""
    # --- Запуск ---
    await init_redis()

    yield

    # --- Завершение ---
    await close_redis()
    await engine.dispose()


def create_app() -> FastAPI:
    """Фабрика приложения — создаёт и настраивает экземпляр FastAPI."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Роутеры регистрируются здесь по мере реализации фич:
    # from src.interfaces.api.v1.routers import contacts, deals, ai_insights
    # application.include_router(contacts.router, prefix="/api/v1")
    # application.include_router(deals.router, prefix="/api/v1")

    return application


app = create_app()
