"""
GmailService — реализация IEmailService через Google Gmail API.
Ответственность: HTTP-взаимодействие с Gmail, OAuth2-поток, парсинг писем.
Никакой бизнес-логики — только I/O через google-api-python-client.

Примечание: google-api-python-client синхронен.
Все вызовы API выполняются через asyncio.get_running_loop().run_in_executor().
"""
from __future__ import annotations

import asyncio
import base64
import email as email_lib
import logging
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.application.ports.email_service import (
    FetchedEmail,
    IEmailService,
    SentEmailResult,
)
from src.infrastructure.gmail.token_storage import GMAIL_SCOPES, FileTokenStorage

logger = logging.getLogger(__name__)


class GmailService(IEmailService):
    """Адаптер Gmail API.

    Все запросы к API:
    - выполняются в executor (sync → async)
    - логируют результат на уровне DEBUG и ошибки на ERROR
    - возвращают строго типизированные result dataclasses
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        token_storage: FileTokenStorage,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._token_storage = token_storage

    # ── Публичный API ─────────────────────────────────────────────────────────

    async def is_authorized(self) -> bool:
        """Проверяет наличие действующих токенов."""
        creds = await self._get_credentials()
        return creds is not None and (not creds.expired or creds.refresh_token is not None)

    async def get_auth_url(self) -> str:
        """Возвращает URL для OAuth2-авторизации пользователя."""
        flow = self._create_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        logger.debug("Gmail OAuth2 URL сгенерирован.")
        return auth_url

    async def exchange_code(self, code: str) -> None:
        """Обменивает authorization code на токены и сохраняет их."""
        loop = asyncio.get_running_loop()
        flow = self._create_flow()

        # fetch_token синхронный — запускаем в executor
        await loop.run_in_executor(
            None,
            lambda: flow.fetch_token(code=code),
        )
        await self._token_storage.save(flow.credentials)
        logger.info("Gmail OAuth2: токены успешно получены и сохранены.")

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: str | None = None,
    ) -> SentEmailResult:
        """Отправляет письмо через Gmail API."""
        logger.debug("Gmail: отправка письма на '%s', тема='%s'", to, subject)

        service = await self._get_service()
        message_body = self._build_raw_message(to=to, subject=subject, body=body)
        request_body: dict[str, Any] = {"raw": message_body}
        if thread_id:
            request_body["threadId"] = thread_id

        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: service.users()
                    .messages()
                    .send(userId="me", body=request_body)
                    .execute(),
            )
        except HttpError as exc:
            logger.error("Gmail: ошибка отправки письма: %s", exc)
            raise

        logger.debug(
            "Gmail: письмо отправлено, message_id=%s, thread_id=%s",
            result["id"],
            result["threadId"],
        )
        return SentEmailResult(
            gmail_message_id=result["id"],
            thread_id=result["threadId"],
        )

    async def fetch_emails(
        self,
        query: str = "",
        max_results: int = 50,
    ) -> list[FetchedEmail]:
        """Загружает письма из Gmail по поисковому запросу."""
        logger.debug(
            "Gmail: загрузка писем, query='%s', max=%d", query, max_results
        )

        service = await self._get_service()
        loop = asyncio.get_running_loop()

        # Получаем список ID сообщений
        try:
            list_result = await loop.run_in_executor(
                None,
                lambda: service.users()
                    .messages()
                    .list(userId="me", q=query, maxResults=max_results)
                    .execute(),
            )
        except HttpError as exc:
            logger.error("Gmail: ошибка получения списка писем: %s", exc)
            raise

        messages_meta = list_result.get("messages", [])
        if not messages_meta:
            return []

        # Загружаем полное содержимое каждого письма
        fetched: list[FetchedEmail] = []
        for meta in messages_meta:
            try:
                msg_data = await loop.run_in_executor(
                    None,
                    lambda m=meta: service.users()
                        .messages()
                        .get(userId="me", id=m["id"], format="full")
                        .execute(),
                )
                parsed = self._parse_message(msg_data)
                if parsed is not None:
                    fetched.append(parsed)
            except HttpError as exc:
                logger.warning(
                    "Gmail: не удалось загрузить письмо id=%s: %s",
                    meta["id"],
                    exc,
                )
                continue

        logger.debug("Gmail: загружено %d писем.", len(fetched))
        return fetched

    # ── Внутренние методы ─────────────────────────────────────────────────────

    def _create_flow(self) -> Flow:
        """Создаёт OAuth2-поток из конфигурации (без файла credentials.json)."""
        client_config = {
            "web": {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "redirect_uris": [self._redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        return Flow.from_client_config(
            client_config,
            scopes=GMAIL_SCOPES,
            redirect_uri=self._redirect_uri,
        )

    async def _get_credentials(self) -> Credentials | None:
        """Загружает и при необходимости обновляет токены."""
        creds = await self._token_storage.load()
        if creds is None:
            return None

        # Refresh если истёк, но есть refresh_token
        if creds.expired and creds.refresh_token:
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(
                    None,
                    lambda: creds.refresh(Request()),
                )
                await self._token_storage.save(creds)
                logger.debug("Gmail: токен обновлён (refresh).")
            except Exception as exc:
                logger.warning("Gmail: не удалось обновить токен: %s", exc)
                return None

        return creds

    async def _get_service(self) -> Any:
        """Создаёт авторизованный клиент Gmail API."""
        creds = await self._get_credentials()
        if creds is None:
            from src.application.exceptions import GmailNotAuthorizedError
            raise GmailNotAuthorizedError()

        loop = asyncio.get_running_loop()
        service = await loop.run_in_executor(
            None,
            lambda: build("gmail", "v1", credentials=creds, cache_discovery=False),
        )
        return service

    @staticmethod
    def _build_raw_message(to: str, subject: str, body: str) -> str:
        """Кодирует письмо в формат Base64URL для Gmail API."""
        mime = MIMEText(body, "plain", "utf-8")
        mime["to"] = to
        mime["subject"] = subject
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode("utf-8")
        return raw

    @staticmethod
    def _parse_message(msg_data: dict[str, Any]) -> FetchedEmail | None:
        """Парсит ответ Gmail API в FetchedEmail.

        Извлекает заголовки From/To/Subject/Date и тело (plain text).
        Возвращает None если письмо не удалось распарсить.
        """
        try:
            headers: dict[str, str] = {
                h["name"].lower(): h["value"]
                for h in msg_data.get("payload", {}).get("headers", [])
            }

            from_address = headers.get("from", "")
            to_raw = headers.get("to", "")
            subject = headers.get("subject", "(без темы)")
            date_str = headers.get("date", "")

            # Парсинг даты из заголовка
            try:
                parsed_date = email_lib.utils.parsedate_to_datetime(date_str)
                received_at = parsed_date.astimezone(timezone.utc)
            except Exception:
                received_at = datetime.now(timezone.utc)

            # Список адресатов (может содержать несколько через запятую)
            to_addresses = [addr.strip() for addr in to_raw.split(",") if addr.strip()]
            if not to_addresses:
                to_addresses = ["unknown"]

            # Извлечение тела письма
            body = GmailService._extract_body(msg_data.get("payload", {}))

            return FetchedEmail(
                gmail_message_id=msg_data["id"],
                thread_id=msg_data.get("threadId", ""),
                from_address=from_address or "unknown",
                to_addresses=to_addresses,
                subject=subject,
                body=body,
                received_at=received_at,
            )
        except Exception as exc:
            logger.warning("Gmail: ошибка парсинга письма id=%s: %s", msg_data.get("id"), exc)
            return None

    @staticmethod
    def _extract_body(payload: dict[str, Any]) -> str:
        """Рекурсивно извлекает plain-text тело письма из payload."""
        mime_type = payload.get("mimeType", "")

        # Простое текстовое письмо
        if mime_type == "text/plain":
            data = payload.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

        # Составное письмо — рекурсивно ищем text/plain
        if mime_type.startswith("multipart/"):
            for part in payload.get("parts", []):
                result = GmailService._extract_body(part)
                if result:
                    return result

        return ""
