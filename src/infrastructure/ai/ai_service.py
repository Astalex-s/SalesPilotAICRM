"""
Заглушка адаптера AI-сервиса — слой Infrastructure.
Реализует порт AbstractAIService из слоя Application.
Конкретная логика LLM-провайдера будет добавлена на следующем шаге.
"""
from src.application.ports.ai_service import AbstractAIService


class OpenAIService(AbstractAIService):
    """Конкретный адаптер AI на базе OpenAI.

    Заглушка — полная реализация добавляется при разработке AI-фичи.
    """

    async def complete(self, prompt: str, *, model: str | None = None) -> str:
        raise NotImplementedError("OpenAIService.complete ещё не реализован.")

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("OpenAIService.embed ещё не реализован.")
