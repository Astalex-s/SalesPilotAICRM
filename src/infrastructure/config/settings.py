"""
Настройки приложения, загружаемые из переменных окружения.
Находится в слое Infrastructure — читает внешнюю конфигурацию, бизнес-логики нет.
"""
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Приложение
    APP_NAME: str = "SalesPilot AI CRM"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # База данных
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/salespilot"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Безопасность
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL должен использовать драйвер postgresql+asyncpg://")
        return v


settings = Settings()
