"""
IEmailService — порт приложения для отправки и получения писем.
Абстракция изолирует бизнес-логику от Gmail и любого другого провайдера.
Реализация (GmailService) находится в Infrastructure — не здесь.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ── Результирующие структуры данных ────────────────────────────────────────────

@dataclass(frozen=True)
class SentEmailResult:
    """Результат отправки письма через провайдера."""

    gmail_message_id: str
    thread_id: str


@dataclass(frozen=True)
class FetchedEmail:
    """Письмо, полученное из почтового ящика провайдера."""

    gmail_message_id: str
    thread_id: str
    from_address: str
    to_addresses: list[str]
    subject: str
    body: str
    received_at: datetime


# ── Абстрактный интерфейс ──────────────────────────────────────────────────────

class IEmailService(ABC):
    """Порт для работы с внешним почтовым провайдером.

    Контракт:
    - send_email / fetch_emails — операции с почтой
    - get_auth_url / exchange_code / is_authorized — управление OAuth2-авторизацией
    """

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: str | None = None,
    ) -> SentEmailResult:
        """Отправляет письмо и возвращает идентификаторы Gmail.

        Args:
            to: e-mail получателя.
            subject: тема письма.
            body: тело письма (plain text).
            thread_id: ID треда для ответа в существующем диалоге.
        """
        ...

    @abstractmethod
    async def fetch_emails(
        self,
        query: str = "",
        max_results: int = 50,
    ) -> list[FetchedEmail]:
        """Получает письма из почтового ящика.

        Args:
            query: строка поиска Gmail (например, 'from:client@example.com').
            max_results: максимальное количество писем.
        """
        ...

    @abstractmethod
    async def get_auth_url(self) -> str:
        """Возвращает URL для инициации OAuth2-авторизации пользователем."""
        ...

    @abstractmethod
    async def exchange_code(self, code: str) -> None:
        """Обменивает authorization code на токены и сохраняет их.

        Args:
            code: код из callback-редиректа от Google.
        """
        ...

    @abstractmethod
    async def is_authorized(self) -> bool:
        """Проверяет, есть ли действующие токены для работы с API."""
        ...
