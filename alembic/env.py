"""
Alembic environment — async-aware (asyncpg).

Запуск:
  alembic revision --autogenerate -m "describe change"
  alembic upgrade head
  alembic downgrade -1
  alembic history --verbose
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Регистрируем все ORM-модели в Base.metadata (необходимо для autogenerate)
from src.infrastructure.database.base import Base
import src.infrastructure.database.models  # noqa: F401 — side-effect import
from src.infrastructure.config.settings import settings

# ── Alembic Config object ────────────────────────────────────────────────────

config = context.config

# Настраиваем logging из alembic.ini (если файл конфигурации задан)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Переопределяем URL из настроек приложения (asyncpg)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Метаданные для autogenerate
target_metadata = Base.metadata


# ── Offline mode (генерирует SQL без подключения к БД) ──────────────────────

def run_migrations_offline() -> None:
    """Generate SQL script without a live DB connection.

    Useful for preview or deploying to environments without direct DB access.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (async, asyncpg) ─────────────────────────────────────────────

def do_run_migrations(connection) -> None:
    """Configure and run migrations on an active connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine, connect, and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online mode — wraps async runner in asyncio.run()."""
    asyncio.run(run_async_migrations())


# ── Dispatch ─────────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
