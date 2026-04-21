"""
Роутер /api/v1/auth/gmail — OAuth2-авторизация Gmail.
Тонкие контроллеры: инициация потока и обмен кода на токены.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from src.application.dtos.email_message_dtos import (
    GmailAuthStatusOutput,
    GmailAuthUrlOutput,
)
from src.interfaces.api.dependencies import get_gmail_service

router = APIRouter(prefix="/auth/gmail", tags=["Gmail OAuth2"])


@router.get(
    "",
    response_model=GmailAuthUrlOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Получить URL для авторизации Gmail",
    description=(
        "Возвращает URL для OAuth2-авторизации Google. "
        "Перейдите по ссылке для выдачи разрешений приложению."
    ),
)
async def get_auth_url(
    gmail_service=Depends(get_gmail_service),
) -> GmailAuthUrlOutput:
    """GET /api/v1/auth/gmail — URL авторизации Gmail."""
    auth_url = await gmail_service.get_auth_url()
    return GmailAuthUrlOutput(auth_url=auth_url)


@router.get(
    "/callback",
    response_model=GmailAuthStatusOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Callback OAuth2 от Google",
    description=(
        "Принимает authorization code от Google, обменивает на токены. "
        "URL автоматически вызывается Google после подтверждения разрешений."
    ),
)
async def oauth_callback(
    code: str = Query(..., description="Authorization code от Google OAuth2"),
    gmail_service=Depends(get_gmail_service),
) -> GmailAuthStatusOutput:
    """GET /api/v1/auth/gmail/callback — обработка OAuth2 callback."""
    await gmail_service.exchange_code(code)
    return GmailAuthStatusOutput(
        authorized=True,
        message="Gmail успешно авторизован. Токены сохранены.",
    )


@router.get(
    "/status",
    response_model=GmailAuthStatusOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Статус авторизации Gmail",
    description="Проверяет, есть ли действующие токены для работы с Gmail.",
)
async def auth_status(
    gmail_service=Depends(get_gmail_service),
) -> GmailAuthStatusOutput:
    """GET /api/v1/auth/gmail/status — проверка авторизации."""
    authorized = await gmail_service.is_authorized()
    message = (
        "Gmail авторизован и готов к работе."
        if authorized
        else "Gmail не авторизован. Перейдите на /api/v1/auth/gmail для авторизации."
    )
    return GmailAuthStatusOutput(authorized=authorized, message=message)
