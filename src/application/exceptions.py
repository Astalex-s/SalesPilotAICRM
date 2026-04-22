"""
Исключения слоя Application.
Отделены от доменных исключений: отражают ошибки оркестрации use case,
а не нарушения бизнес-правил внутри домена.
"""
from uuid import UUID


class ApplicationError(Exception):
    """Базовый класс для всех ошибок слоя Application."""


# ── Ошибки поиска сущностей ────────────────────────────────────────────────────

class EntityNotFoundError(ApplicationError):
    """Запрошенная сущность не найдена в хранилище."""

    def __init__(self, entity_type: str, entity_id: UUID) -> None:
        super().__init__(f"{entity_type} с ID {entity_id} не найден.")
        self.entity_id = entity_id


class LeadNotFoundError(EntityNotFoundError):
    def __init__(self, lead_id: UUID) -> None:
        super().__init__("Lead", lead_id)


class DealNotFoundError(EntityNotFoundError):
    def __init__(self, deal_id: UUID) -> None:
        super().__init__("Deal", deal_id)


class PipelineNotFoundError(EntityNotFoundError):
    def __init__(self, pipeline_id: UUID) -> None:
        super().__init__("Pipeline", pipeline_id)


# ── Ошибки бизнес-ограничений уровня use case ──────────────────────────────────

class LeadEmailAlreadyExistsError(ApplicationError):
    """Лид с таким e-mail уже существует в системе."""

    def __init__(self, email: str) -> None:
        super().__init__(f"Лид с e-mail '{email}' уже существует.")
        self.email = email


class StageNotInPipelineError(ApplicationError):
    """Указанный этап не принадлежит указанной воронке."""

    def __init__(self, stage_id: UUID, pipeline_id: UUID) -> None:
        super().__init__(
            f"Этап {stage_id} не найден в воронке {pipeline_id}."
        )
        self.stage_id = stage_id
        self.pipeline_id = pipeline_id


# ── Ошибки Gmail-интеграции ────────────────────────────────────────────────────

class EmailMessageNotFoundError(EntityNotFoundError):
    """Письмо с указанным ID не найдено."""

    def __init__(self, email_message_id: UUID) -> None:
        super().__init__("EmailMessage", email_message_id)


class GmailNotAuthorizedError(ApplicationError):
    """Gmail не авторизован — необходимо пройти OAuth2-поток."""

    def __init__(self) -> None:
        super().__init__(
            "Gmail не авторизован. Перейдите по /api/v1/auth/gmail для авторизации."
        )


# ── Ошибки Telegram-интеграции ─────────────────────────────────────────────────

class TelegramNotConfiguredError(ApplicationError):
    """Telegram не настроен — TELEGRAM_BOT_TOKEN или TELEGRAM_NOTIFICATION_CHAT_ID не заданы."""

    def __init__(self) -> None:
        super().__init__(
            "Telegram не настроен. Задайте TELEGRAM_BOT_TOKEN и TELEGRAM_NOTIFICATION_CHAT_ID."
        )
