"""
NotifyDealStageChangeUseCase — отправляет Telegram-уведомление при смене этапа сделки.

Единственная ответственность: получить имя нового этапа из воронки,
сформировать текст уведомления и передать его в ITelegramService.notify().
"""
from __future__ import annotations

from src.application.dtos.telegram_dtos import NotifyDealStageChangeInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.ports.telegram_service import ITelegramService
from src.domain.repositories.pipeline_repository import IPipelineRepository


class NotifyDealStageChangeUseCase:
    """Отправляет уведомление о смене этапа сделки в Telegram."""

    def __init__(
        self,
        telegram_service: ITelegramService,
        pipeline_repo: IPipelineRepository,
    ) -> None:
        self._telegram = telegram_service
        self._pipeline_repo = pipeline_repo

    async def execute(self, data: NotifyDealStageChangeInput) -> None:
        """Выполняет отправку уведомления о смене этапа.

        Последовательность:
        1. Проверяет, что Telegram настроен — иначе TelegramNotConfiguredError.
        2. Загружает воронку для разрешения имени нового этапа.
        3. Формирует текст уведомления.
        4. Отправляет уведомление через ITelegramService.

        Вызывает:
            TelegramNotConfiguredError: если бот не настроен.
        """
        # Шаг 1: проверка конфигурации
        if not self._telegram.is_configured():
            raise TelegramNotConfiguredError()

        # Шаг 2: получение имени этапа из воронки
        stage_name = str(data.new_stage_id)  # fallback — UUID
        pipeline = await self._pipeline_repo.get_by_id(data.pipeline_id)
        if pipeline is not None:
            stage_map = {s.id: s for s in pipeline.stages}
            stage = stage_map.get(data.new_stage_id)
            if stage is not None:
                stage_name = stage.name

        # Шаг 3: формирование текста уведомления
        text = (
            "<b>📊 Смена этапа сделки</b>\n\n"
            f"💼 <b>{data.deal_title}</b>\n"
            f"🔄 Новый этап: {stage_name}"
        )

        # Шаг 4: отправка
        await self._telegram.notify(text)
