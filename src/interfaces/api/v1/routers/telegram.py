"""
Роутер /api/v1/telegram.
Тонкие контроллеры: принять запрос → вызвать use case → вернуть DTO.
Никакой бизнес-логики, никаких ORM-объектов.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi import status as http_status

from src.application.dtos.telegram_dtos import (
    TelegramStatusOutput,
    TelegramWebhookSetInput,
    TelegramWebhookSetOutput,
)
from src.application.ports.telegram_service import ITelegramService
from src.application.use_cases.handle_bot_command import HandleBotCommandUseCase
from src.infrastructure.config.settings import settings
from src.interfaces.api.dependencies import get_handle_bot_command_use_case, get_telegram_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.post(
    "/webhook",
    status_code=http_status.HTTP_200_OK,
    summary="Telegram Webhook",
    description=(
        "Эндпоинт для получения Updates от Telegram. "
        "URL должен быть зарегистрирован через POST /telegram/set-webhook. "
        "Если задан TELEGRAM_WEBHOOK_SECRET — проверяется заголовок X-Telegram-Bot-Api-Secret-Token."
    ),
    include_in_schema=False,  # Скрыт из Swagger — вызывается Telegram, не клиентом
)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(
        default=None,
        alias="X-Telegram-Bot-Api-Secret-Token",
    ),
    telegram_service: ITelegramService = Depends(get_telegram_service),
    bot_command_use_case: HandleBotCommandUseCase = Depends(get_handle_bot_command_use_case),
) -> Response:
    """POST /api/v1/telegram/webhook — приём обновлений от Telegram."""
    # Проверка секретного токена, если настроен
    if settings.TELEGRAM_WEBHOOK_SECRET:
        if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
            logger.warning("Telegram webhook: неверный секретный токен")
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Неверный секретный токен вебхука.",
            )

    raw_update = await request.json()
    await telegram_service.process_update(raw_update)
    await bot_command_use_case.execute(raw_update)

    # Telegram требует HTTP 200 в ответ — иначе повторная доставка
    return Response(status_code=http_status.HTTP_200_OK)


@router.post(
    "/set-webhook",
    response_model=TelegramWebhookSetOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Установить Telegram Webhook",
    description=(
        "Регистрирует HTTPS URL как вебхук бота в Telegram. "
        "URL должен быть публично доступен и использовать HTTPS."
    ),
)
async def set_telegram_webhook(
    body: TelegramWebhookSetInput,
    telegram_service: ITelegramService = Depends(get_telegram_service),
) -> TelegramWebhookSetOutput:
    """POST /api/v1/telegram/set-webhook — регистрация вебхука."""
    url_str = str(body.url)
    await telegram_service.set_webhook(url=url_str, secret_token=body.secret_token)
    return TelegramWebhookSetOutput(
        success=True,
        message=f"Вебхук зарегистрирован: {url_str}",
    )


@router.get(
    "/status",
    response_model=TelegramStatusOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Статус Telegram-интеграции",
    description="Возвращает статус бота: настроен ли токен, URL вебхука, очередь входящих обновлений.",
)
async def telegram_status(
    telegram_service: ITelegramService = Depends(get_telegram_service),
) -> TelegramStatusOutput:
    """GET /api/v1/telegram/status — статус бота и вебхука."""
    if not telegram_service.is_configured():
        return TelegramStatusOutput(
            configured=False,
            webhook_url="",
            webhook_pending_updates=0,
        )

    try:
        info = await telegram_service.get_webhook_info()
        return TelegramStatusOutput(
            configured=True,
            webhook_url=info.url,
            webhook_pending_updates=info.pending_update_count,
        )
    except Exception as exc:
        logger.warning("Telegram get_webhook_info failed: %s", exc)
        return TelegramStatusOutput(
            configured=True,
            webhook_url="",
            webhook_pending_updates=0,
        )
