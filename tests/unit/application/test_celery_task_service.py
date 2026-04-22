"""Юнит-тесты CeleryTaskService.
Celery задачи заменены моками — брокер и воркер не нужны.
Проверяем: корректность вызова .delay(), маппинг статусов AsyncResult.
"""
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.application.ports.task_service import EnqueuedTask, TaskStatus
from src.infrastructure.celery.celery_task_service import CeleryTaskService


# ── Вспомогательная фабрика мока AsyncResult ────────────────────────────────────

def _make_async_result(
    task_id: str = "test-task-id",
    status: str = "PENDING",
    result=None,
) -> MagicMock:
    """Создаёт мок celery.result.AsyncResult."""
    ar = MagicMock()
    ar.id = task_id
    ar.status = status
    ar.result = result
    ar.successful.return_value = status == "SUCCESS"
    ar.failed.return_value = status == "FAILURE"
    return ar


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def service() -> CeleryTaskService:
    return CeleryTaskService()


# ── Постановка AI задач в очередь ──────────────────────────────────────────────

class TestEnqueueAITasks:
    def test_enqueue_score_lead_returns_enqueued_task(
        self, service: CeleryTaskService
    ) -> None:
        """enqueue_score_lead возвращает EnqueuedTask с task_id."""
        lead_id = uuid4()
        mock_result = MagicMock()
        mock_result.id = "score-task-abc"

        with patch(
            "src.infrastructure.celery.celery_task_service.score_lead_task"
        ) as mock_task:
            mock_task.delay.return_value = mock_result
            result = service.enqueue_score_lead(lead_id)

        assert isinstance(result, EnqueuedTask)
        assert result.task_id == "score-task-abc"
        assert result.task_name == "tasks.ai.score_lead"

    def test_enqueue_score_lead_calls_delay_with_string_uuid(
        self, service: CeleryTaskService
    ) -> None:
        """delay вызывается с lead_id как строкой (JSON-сериализуемо)."""
        lead_id = uuid4()
        mock_result = MagicMock()
        mock_result.id = "abc"

        with patch(
            "src.infrastructure.celery.celery_task_service.score_lead_task"
        ) as mock_task:
            mock_task.delay.return_value = mock_result
            service.enqueue_score_lead(lead_id)

        mock_task.delay.assert_called_once_with(str(lead_id))

    def test_enqueue_forecast_deal_returns_enqueued_task(
        self, service: CeleryTaskService
    ) -> None:
        """enqueue_forecast_deal возвращает EnqueuedTask."""
        deal_id = uuid4()
        mock_result = MagicMock()
        mock_result.id = "forecast-task-xyz"

        with patch(
            "src.infrastructure.celery.celery_task_service.forecast_deal_task"
        ) as mock_task:
            mock_task.delay.return_value = mock_result
            result = service.enqueue_forecast_deal(deal_id)

        assert result.task_name == "tasks.ai.forecast_deal"
        assert result.task_id == "forecast-task-xyz"

    def test_enqueue_generate_email_passes_tone_and_context(
        self, service: CeleryTaskService
    ) -> None:
        """enqueue_generate_email передаёт tone и extra_context в delay."""
        lead_id = uuid4()
        mock_result = MagicMock()
        mock_result.id = "email-gen-task"

        with patch(
            "src.infrastructure.celery.celery_task_service.generate_email_task"
        ) as mock_task:
            mock_task.delay.return_value = mock_result
            service.enqueue_generate_email(
                lead_id=lead_id,
                tone="formal",
                extra_context="Особые условия",
            )

        mock_task.delay.assert_called_once_with(
            lead_id=str(lead_id),
            tone="formal",
            extra_context="Особые условия",
        )

    def test_enqueue_next_best_action_passes_entity_type(
        self, service: CeleryTaskService
    ) -> None:
        """enqueue_next_best_action передаёт entity_type и entity_id как строки."""
        entity_id = uuid4()
        mock_result = MagicMock()
        mock_result.id = "nba-task"

        with patch(
            "src.infrastructure.celery.celery_task_service.next_best_action_task"
        ) as mock_task:
            mock_task.delay.return_value = mock_result
            service.enqueue_next_best_action(entity_type="lead", entity_id=entity_id)

        mock_task.delay.assert_called_once_with(
            entity_type="lead",
            entity_id=str(entity_id),
        )


# ── Постановка Email задач в очередь ──────────────────────────────────────────

class TestEnqueueEmailTasks:
    def test_enqueue_send_email_passes_payload(
        self, service: CeleryTaskService
    ) -> None:
        """enqueue_send_email передаёт payload без изменений."""
        payload = {"to": "client@example.com", "subject": "Тема", "body": "Тело"}
        mock_result = MagicMock()
        mock_result.id = "send-task-1"

        with patch(
            "src.infrastructure.celery.celery_task_service.send_email_task"
        ) as mock_task:
            mock_task.delay.return_value = mock_result
            result = service.enqueue_send_email(payload)

        assert result.task_name == "tasks.email.send"
        mock_task.delay.assert_called_once_with(payload=payload)

    def test_enqueue_fetch_emails_passes_params(
        self, service: CeleryTaskService
    ) -> None:
        """enqueue_fetch_emails передаёт query и max_results."""
        mock_result = MagicMock()
        mock_result.id = "fetch-task-1"

        with patch(
            "src.infrastructure.celery.celery_task_service.fetch_emails_task"
        ) as mock_task:
            mock_task.delay.return_value = mock_result
            result = service.enqueue_fetch_emails(query="from:client@test.com", max_results=25)

        assert result.task_name == "tasks.email.fetch"
        mock_task.delay.assert_called_once_with(
            query="from:client@test.com", max_results=25
        )


# ── Статус задачи ──────────────────────────────────────────────────────────────

class TestGetTaskStatus:
    def test_pending_status(self, service: CeleryTaskService) -> None:
        """PENDING: result=None, error=None."""
        with patch.object(
            service._CeleryTaskService__class__  # noqa: private access in test
            if False else type(service),
            "get_task_status",
        ):
            pass  # Используем patch на celery_app.AsyncResult

        with patch(
            "src.infrastructure.celery.celery_task_service.celery_app"
        ) as mock_app:
            mock_app.AsyncResult.return_value = _make_async_result(
                task_id="t1", status="PENDING"
            )
            status = service.get_task_status("t1")

        assert isinstance(status, TaskStatus)
        assert status.status == "PENDING"
        assert status.result is None
        assert status.error is None

    def test_success_status_returns_result(self, service: CeleryTaskService) -> None:
        """SUCCESS: result содержит словарь, error=None."""
        with patch(
            "src.infrastructure.celery.celery_task_service.celery_app"
        ) as mock_app:
            mock_app.AsyncResult.return_value = _make_async_result(
                task_id="t2",
                status="SUCCESS",
                result={"score": 0.85, "reasoning": "Хорошие показатели"},
            )
            status = service.get_task_status("t2")

        assert status.status == "SUCCESS"
        assert status.result == {"score": 0.85, "reasoning": "Хорошие показатели"}
        assert status.error is None

    def test_failure_status_returns_error(self, service: CeleryTaskService) -> None:
        """FAILURE: error содержит сообщение об ошибке, result=None."""
        exc = RuntimeError("Lead не найден")
        with patch(
            "src.infrastructure.celery.celery_task_service.celery_app"
        ) as mock_app:
            mock_app.AsyncResult.return_value = _make_async_result(
                task_id="t3",
                status="FAILURE",
                result=exc,
            )
            status = service.get_task_status("t3")

        assert status.status == "FAILURE"
        assert status.result is None
        assert "Lead не найден" in status.error

    def test_started_status(self, service: CeleryTaskService) -> None:
        """STARTED: result=None, error=None."""
        with patch(
            "src.infrastructure.celery.celery_task_service.celery_app"
        ) as mock_app:
            mock_app.AsyncResult.return_value = _make_async_result(
                task_id="t4", status="STARTED"
            )
            status = service.get_task_status("t4")

        assert status.status == "STARTED"
        assert status.result is None
        assert status.error is None

    def test_task_id_preserved(self, service: CeleryTaskService) -> None:
        """task_id из запроса совпадает с task_id в ответе."""
        with patch(
            "src.infrastructure.celery.celery_task_service.celery_app"
        ) as mock_app:
            mock_app.AsyncResult.return_value = _make_async_result(task_id="my-task-id")
            status = service.get_task_status("my-task-id")

        assert status.task_id == "my-task-id"
