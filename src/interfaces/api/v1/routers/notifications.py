"""
Роутер /api/v1/notifications.
Предоставляет Server-Sent Events (SSE) поток уведомлений в реальном времени.

Аутентификация через query-параметр token= (JWT access token),
потому что браузерный EventSource не поддерживает кастомные заголовки.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from jose import JWTError

from src.infrastructure.auth.auth_service import decode_access_token
from src.infrastructure.notifications.notification_bus import bus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Уведомления"])

_HEARTBEAT_INTERVAL = 15  # секунд — не даёт nginx/браузеру закрыть idle-соединение


async def _sse_stream(token: str) -> AsyncGenerator[str, None]:
    """Генератор SSE-событий для одного подключённого клиента."""
    # Шаг 1: валидация JWT при подключении
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            yield 'event: error\ndata: {"detail": "Unauthorized"}\n\n'
            return
    except JWTError:
        yield 'event: error\ndata: {"detail": "Unauthorized"}\n\n'
        return

    # Шаг 2: подписка на шину
    q = bus.subscribe()
    try:
        # Подтверждаем успешное подключение
        yield ": connected\n\n"
        while True:
            try:
                # Ждём следующее событие или истечения таймаута для heartbeat
                data = await asyncio.wait_for(q.get(), timeout=float(_HEARTBEAT_INTERVAL))
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                # Heartbeat — держит соединение живым
                yield ": heartbeat\n\n"
    except asyncio.CancelledError:
        # Клиент отключился
        pass
    finally:
        bus.unsubscribe(q)


@router.get(
    "/stream",
    summary="SSE-поток уведомлений в реальном времени",
    description=(
        "Server-Sent Events поток. Клиент подключается и получает push-события: "
        "создание лида, смена этапа сделки, закрытие сделки и т.д. "
        "Аутентификация: передать JWT access token в query-параметре token=."
    ),
    response_class=StreamingResponse,
)
async def notification_stream(
    token: str = Query(..., description="JWT access token"),
) -> StreamingResponse:
    """GET /api/v1/notifications/stream — SSE endpoint."""
    return StreamingResponse(
        _sse_stream(token),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # отключает буферизацию nginx
            "Connection": "keep-alive",
        },
    )
