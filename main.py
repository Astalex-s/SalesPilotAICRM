"""
Точка входа приложения — только инициализация FastAPI.
Бизнес-логики нет. Роутеры и обработчики регистрируются в фабрике.
"""
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import sentry_sdk
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from src.infrastructure.logging.setup import configure_logging

from src.infrastructure.cache.redis_client import close_redis, init_redis
from src.infrastructure.config.settings import settings
from src.infrastructure.database.session import engine
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.middleware.request_id import RequestIdMiddleware
from src.interfaces.api.v1.routers import (
    ai_router,
    analytics_router,
    auth_router,
    deal_attachments_router,
    deals_router,
    emails_router,
    gdpr_router,
    gmail_auth_router,
    leads_router,
    notifications_router,
    pipelines_router,
    tasks_router,
    telegram_router,
    users_router,
)


configure_logging(settings.LOG_LEVEL)

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        release=settings.APP_VERSION,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        send_default_pii=False,
    )


def _run_migrations() -> None:
    """Apply pending Alembic migrations synchronously.

    Called from a thread-pool executor inside lifespan so it doesn't
    block the event loop.  env.py uses asyncio.run() internally, which
    requires a thread without a running event loop — the executor provides that.
    """
    cfg = AlembicConfig("alembic.ini")
    alembic_command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управляет запуском и корректным завершением работы инфраструктурных соединений."""
    # --- Запуск ---
    # Применяем миграции в отдельном потоке (env.py вызывает asyncio.run() внутри)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run_migrations)
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

    # Middleware (порядок важен: внешний → внутренний)
    application.add_middleware(RequestIdMiddleware)

    # Регистрация обработчиков исключений (до роутеров)
    register_exception_handlers(application)

    # Prometheus — expose /metrics (internal only, not routed through nginx)
    Instrumentator(excluded_handlers=["/metrics"]).instrument(application).expose(
        application,
        include_in_schema=False,
        tags=["monitoring"],
    )

    # Регистрация роутеров v1
    _api_prefix = "/api/v1"
    application.include_router(auth_router, prefix=_api_prefix)
    application.include_router(users_router, prefix=_api_prefix)
    application.include_router(leads_router, prefix=_api_prefix)
    application.include_router(deals_router, prefix=_api_prefix)
    application.include_router(deal_attachments_router, prefix=_api_prefix)
    application.include_router(analytics_router, prefix=_api_prefix)
    application.include_router(pipelines_router, prefix=_api_prefix)
    application.include_router(ai_router, prefix=_api_prefix)
    application.include_router(gmail_auth_router, prefix=_api_prefix)
    application.include_router(emails_router, prefix=_api_prefix)
    application.include_router(telegram_router, prefix=_api_prefix)
    application.include_router(notifications_router, prefix=_api_prefix)
    application.include_router(tasks_router, prefix=_api_prefix)
    application.include_router(gdpr_router, prefix=_api_prefix)

    return application


app = create_app()
