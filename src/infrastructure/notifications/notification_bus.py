"""
NotificationBus — in-memory pub/sub шина для SSE-уведомлений.

Один глобальный синглтон на процесс. Каждый подключённый SSE-клиент
получает свою asyncio.Queue; publish() рассылает сообщения всем подписчикам.

Ограничение: работает только в рамках одного процесса (single-worker uvicorn).
Для горизонтального масштабирования нужен Redis Pub/Sub (Redis уже в стеке).
"""
from __future__ import annotations

import asyncio
import json
import logging

logger = logging.getLogger(__name__)

_QUEUE_MAX_SIZE = 50  # защита от медленных клиентов


class NotificationBus:
    """Pub/sub шина для SSE: subscribe → queue, publish → broadcast."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()

    def subscribe(self) -> asyncio.Queue[str]:
        """Регистрирует нового подписчика, возвращает его очередь."""
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=_QUEUE_MAX_SIZE)
        self._subscribers.add(q)
        logger.debug("SSE subscriber added. Total: %d", len(self._subscribers))
        return q

    def unsubscribe(self, q: asyncio.Queue[str]) -> None:
        """Удаляет подписчика (вызывается при разрыве соединения)."""
        self._subscribers.discard(q)
        logger.debug("SSE subscriber removed. Total: %d", len(self._subscribers))

    async def publish(self, event: dict) -> None:
        """Рассылает событие всем подписчикам.

        Медленные/отставшие клиенты (QueueFull) тихо удаляются.
        """
        data = json.dumps(event, ensure_ascii=False, default=str)
        dead: list[asyncio.Queue[str]] = []
        for q in list(self._subscribers):
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                logger.warning("SSE queue full — dropping slow subscriber.")
                dead.append(q)
        for q in dead:
            self._subscribers.discard(q)


# Синглтон — один на весь процесс, импортируется напрямую
bus: NotificationBus = NotificationBus()
