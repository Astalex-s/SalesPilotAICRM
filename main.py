"""
Точка входа приложения — только инициализация FastAPI.
Бизнес-логики нет. Роутеры и обработчики регистрируются в фабрике.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from src.infrastructure.cache.redis_client import close_redis, init_redis
from src.infrastructure.config.settings import settings
from src.infrastructure.database.session import engine
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.v1.routers import (
    ai_router,
    deals_router,
    emails_router,
    gmail_auth_router,
    leads_router,
    pipelines_router,
)


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

    # Регистрация обработчиков исключений (до роутеров)
    register_exception_handlers(application)

    # Регистрация роутеров v1
    _api_prefix = "/api/v1"
    application.include_router(leads_router, prefix=_api_prefix)
    application.include_router(deals_router, prefix=_api_prefix)
    application.include_router(pipelines_router, prefix=_api_prefix)
    application.include_router(ai_router, prefix=_api_prefix)
    application.include_router(gmail_auth_router, prefix=_api_prefix)
    application.include_router(emails_router, prefix=_api_prefix)

    return application


app = create_app()
