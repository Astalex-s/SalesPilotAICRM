"""
Порт AI-сервиса (интерфейс) — определён в слое Application.
Конкретные реализации находятся в слое Infrastructure.
Обеспечивает соблюдение принципа инверсии зависимостей (DIP).
"""
from abc import ABC, abstractmethod


class AbstractAIService(ABC):
    """Определение порта для AI-операций.

    Use Cases в слое Application зависят ТОЛЬКО от этого интерфейса.
    Infrastructure предоставляет конкретный адаптер (OpenAI, Anthropic и т.д.).
    """

    @abstractmethod
    async def complete(self, prompt: str, *, model: str | None = None) -> str:
        """Генерирует текстовое завершение для переданного промпта."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Генерирует векторное представление (эмбеддинг) для переданного текста."""
        ...
