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

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT: float = 30.0

    # Gmail OAuth2
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/gmail/callback"
    GMAIL_TOKEN_FILE: str = "gmail_token.json"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_NOTIFICATION_CHAT_ID: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_EMAIL_SYNC_INTERVAL_SECONDS: int = 600  # 10 минут

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL должен использовать драйвер postgresql+asyncpg://")
        return v


settings = Settings()
