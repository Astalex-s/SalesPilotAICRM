"""Юнит-тесты use case NotifyDealStageChangeUseCase.
ITelegramService и IPipelineRepository заменены моками — зависимости от I/O отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.dtos.telegram_dtos import NotifyDealStageChangeInput
from src.application.exceptions import TelegramNotConfiguredError
from src.application.use_cases.notify_deal_stage_change import NotifyDealStageChangeUseCase


# ── Вспомогательные строители ───────────────────────────────────────────────────

def _make_stage(stage_id, name: str):
    """Создаёт мок-объект Stage."""
    stage = MagicMock()
    stage.id = stage_id
    stage.name = name
    return stage


def _make_pipeline(stage_id, stage_name: str):
    """Создаёт мок-объект Pipeline с одним этапом."""
    pipeline = MagicMock()
    pipeline.stages = [_make_stage(stage_id, stage_name)]
    return pipeline


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def telegram_service() -> MagicMock:
    """Мок ITelegramService — бот настроен по умолчанию."""
    svc = MagicMock()
    svc.is_configured.return_value = True
    svc.notify = AsyncMock()
    return svc


@pytest.fixture
def stage_id() -> object:
    return uuid4()


@pytest.fixture
def pipeline_repo(stage_id) -> AsyncMock:
    """Мок IPipelineRepository — возвращает воронку с одним этапом."""
    repo = AsyncMock()
    repo.get_by_id.return_value = _make_pipeline(stage_id, "Переговоры")
    return repo


@pytest.fixture
def use_case(telegram_service, pipeline_repo) -> NotifyDealStageChangeUseCase:
    return NotifyDealStageChangeUseCase(
        telegram_service=telegram_service,
        pipeline_repo=pipeline_repo,
    )


@pytest.fixture
def valid_input(stage_id) -> NotifyDealStageChangeInput:
    return NotifyDealStageChangeInput(
        deal_id=uuid4(),
        deal_title="Контракт с ООО Альфа",
        new_stage_id=stage_id,
        pipeline_id=uuid4(),
    )


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestNotifyDealStageChangeHappyPath:
    async def test_notify_called_once(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        telegram_service: MagicMock,
    ) -> None:
        """notify вызывается ровно один раз при корректных данных."""
        await use_case.execute(valid_input)
        telegram_service.notify.assert_called_once()

    async def test_message_contains_deal_title(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        telegram_service: MagicMock,
    ) -> None:
        """Текст уведомления содержит название сделки."""
        await use_case.execute(valid_input)
        text: str = telegram_service.notify.call_args[0][0]
        assert "Контракт с ООО Альфа" in text

    async def test_message_contains_stage_name(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        telegram_service: MagicMock,
    ) -> None:
        """Текст уведомления содержит имя нового этапа из воронки."""
        await use_case.execute(valid_input)
        text: str = telegram_service.notify.call_args[0][0]
        assert "Переговоры" in text

    async def test_pipeline_repo_called(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Репозиторий воронок вызывается для получения имени этапа."""
        await use_case.execute(valid_input)
        pipeline_repo.get_by_id.assert_called_once_with(valid_input.pipeline_id)

    async def test_fallback_to_uuid_when_pipeline_not_found(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        pipeline_repo: AsyncMock,
        telegram_service: MagicMock,
    ) -> None:
        """Если воронка не найдена — в тексте используется UUID этапа."""
        pipeline_repo.get_by_id.return_value = None
        await use_case.execute(valid_input)
        text: str = telegram_service.notify.call_args[0][0]
        assert str(valid_input.new_stage_id) in text

    async def test_fallback_to_uuid_when_stage_not_in_pipeline(
        self,
        telegram_service: MagicMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """Если этап не найден в воронке — используется UUID этапа."""
        unknown_stage_id = uuid4()
        data = NotifyDealStageChangeInput(
            deal_id=uuid4(),
            deal_title="Тестовая сделка",
            new_stage_id=unknown_stage_id,
            pipeline_id=uuid4(),
        )
        use_case = NotifyDealStageChangeUseCase(
            telegram_service=telegram_service,
            pipeline_repo=pipeline_repo,
        )
        await use_case.execute(data)
        text: str = telegram_service.notify.call_args[0][0]
        assert str(unknown_stage_id) in text


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestNotifyDealStageChangeGuards:
    async def test_not_configured_raises(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        telegram_service: MagicMock,
    ) -> None:
        """TelegramNotConfiguredError если сервис не настроен."""
        telegram_service.is_configured.return_value = False
        with pytest.raises(TelegramNotConfiguredError):
            await use_case.execute(valid_input)

    async def test_not_configured_does_not_call_notify(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        telegram_service: MagicMock,
    ) -> None:
        """При отсутствии конфигурации notify не вызывается."""
        telegram_service.is_configured.return_value = False
        with pytest.raises(TelegramNotConfiguredError):
            await use_case.execute(valid_input)
        telegram_service.notify.assert_not_called()

    async def test_not_configured_does_not_query_db(
        self,
        use_case: NotifyDealStageChangeUseCase,
        valid_input: NotifyDealStageChangeInput,
        telegram_service: MagicMock,
        pipeline_repo: AsyncMock,
    ) -> None:
        """При отсутствии конфигурации репозиторий воронок не вызывается."""
        telegram_service.is_configured.return_value = False
        with pytest.raises(TelegramNotConfiguredError):
            await use_case.execute(valid_input)
        pipeline_repo.get_by_id.assert_not_called()
