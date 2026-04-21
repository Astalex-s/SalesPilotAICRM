"""
FileTokenStorage — хранение OAuth2-токенов в JSON-файле.
Ответственность: чтение/запись Credentials. Никакой бизнес-логики.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

# Scopes, которые должны совпадать при загрузке токена из файла
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


class FileTokenStorage:
    """Хранит OAuth2-токены в локальном JSON-файле.

    В production токены должны храниться в зашифрованном виде в БД
    с привязкой к пользователю. Для текущего этапа достаточно файла.
    """

    def __init__(self, token_file: str) -> None:
        self._token_file = Path(token_file)

    async def load(self) -> Credentials | None:
        """Загружает токены из файла. Возвращает None если файл не найден."""
        if not self._token_file.exists():
            logger.debug("Файл токенов '%s' не найден.", self._token_file)
            return None

        try:
            with self._token_file.open() as f:
                data = json.load(f)
            creds = Credentials.from_authorized_user_info(data, GMAIL_SCOPES)
            logger.debug("Токены Gmail загружены из '%s'.", self._token_file)
            return creds
        except Exception as exc:
            logger.warning("Ошибка загрузки токенов Gmail: %s", exc)
            return None

    async def save(self, credentials: Credentials) -> None:
        """Сохраняет токены в JSON-файл."""
        try:
            self._token_file.parent.mkdir(parents=True, exist_ok=True)
            with self._token_file.open("w") as f:
                f.write(credentials.to_json())
            logger.debug("Токены Gmail сохранены в '%s'.", self._token_file)
        except Exception as exc:
            logger.error("Ошибка сохранения токенов Gmail: %s", exc)
            raise

    async def delete(self) -> None:
        """Удаляет файл токенов (деавторизация)."""
        if self._token_file.exists():
            self._token_file.unlink()
            logger.info("Токены Gmail удалены.")
