"""
Юнит-тесты для Celery задач.
Все внешние зависимости (сессия БД, сервисы) замокированы.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── deal_tasks ─────────────────────────────────────────────────────────────────

class TestNotifyOverdueDealsTask:
    def test_task_success(self) -> None:
        """Задача успешно выполняется и возвращает overdue_count."""
        from src.infrastructure.celery.tasks.deal_tasks import notify_overdue_deals_task

        mock_result = {"overdue_count": 3}
        with (
            patch("src.infrastructure.celery.tasks.deal_tasks.asyncio.run", return_value=mock_result),
            patch("src.infrastructure.celery.tasks.deal_tasks.get_task_session"),
            patch("src.infrastructure.celery.tasks.deal_tasks.TelegramService"),
            patch("src.infrastructure.celery.tasks.deal_tasks.NotifyOverdueDealsUseCase"),
        ):
            result = notify_overdue_deals_task()

        assert result == {"overdue_count": 3}

    def test_task_telegram_not_configured(self) -> None:
        """Когда Telegram не настроен, возвращает overdue_count=0."""
        from src.application.exceptions import TelegramNotConfiguredError
        from src.infrastructure.celery.tasks.deal_tasks import notify_overdue_deals_task

        with patch(
            "src.infrastructure.celery.tasks.deal_tasks.asyncio.run",
            side_effect=TelegramNotConfiguredError(),
        ):
            result = notify_overdue_deals_task()

        assert result == {"overdue_count": 0}

    def test_task_retries_on_exception(self) -> None:
        """При неожиданной ошибке задача вызывает self.retry."""
        from src.infrastructure.celery.tasks.deal_tasks import notify_overdue_deals_task

        with (
            patch("src.infrastructure.celery.tasks.deal_tasks.asyncio.run", side_effect=RuntimeError("DB down")),
            patch.object(notify_overdue_deals_task, "retry", side_effect=RuntimeError("retry")) as mock_retry,
        ):
            with pytest.raises(RuntimeError, match="retry"):
                notify_overdue_deals_task()

        mock_retry.assert_called_once()


# ── gdpr_tasks ─────────────────────────────────────────────────────────────────

class TestApplyRetentionPolicyTask:
    def test_task_success(self) -> None:
        """Задача успешно применяет retention policy."""
        from src.infrastructure.celery.tasks.gdpr_tasks import apply_retention_policy_task

        mock_result = {
            "leads_deleted": 2,
            "deals_deleted": 1,
            "retention_days": 730,
            "emails_deleted": 0,
            "activities_erased": 0,
            "audit_entry_id": "00000000-0000-0000-0000-000000000001",
        }
        with patch("src.infrastructure.celery.tasks.gdpr_tasks.asyncio.run", return_value=mock_result):
            result = apply_retention_policy_task()

        assert result["leads_deleted"] == 2
        assert result["deals_deleted"] == 1

    def test_task_retries_on_exception(self) -> None:
        """При ошибке задача вызывает self.retry."""
        from src.infrastructure.celery.tasks.gdpr_tasks import apply_retention_policy_task

        with (
            patch("src.infrastructure.celery.tasks.gdpr_tasks.asyncio.run", side_effect=ConnectionError("DB down")),
            patch.object(apply_retention_policy_task, "retry", side_effect=ConnectionError("retry")) as mock_retry,
        ):
            with pytest.raises(ConnectionError, match="retry"):
                apply_retention_policy_task()

        mock_retry.assert_called_once()


# ── sync_tasks ─────────────────────────────────────────────────────────────────

class TestFetchEmailsPeriodicTask:
    def test_task_enqueues_fetch_task(self) -> None:
        """Периодическая задача ставит fetch_emails_task в очередь."""
        mock_async_result = MagicMock()
        mock_async_result.id = "test-task-id-123"

        with patch(
            "src.infrastructure.celery.tasks.email_tasks.fetch_emails_task.delay",
            return_value=mock_async_result,
        ):
            from src.infrastructure.celery.tasks.sync_tasks import fetch_emails_periodic_task
            result = fetch_emails_periodic_task(query="", max_results=50)

        assert "enqueued_task_id" in result

    def test_task_passes_query_and_max_results(self) -> None:
        """Параметры query и max_results передаются в fetch_emails_task.delay."""
        mock_async_result = MagicMock()
        mock_async_result.id = "abc"

        with patch(
            "src.infrastructure.celery.tasks.email_tasks.fetch_emails_task.delay",
            return_value=mock_async_result,
        ) as mock_delay:
            from src.infrastructure.celery.tasks.sync_tasks import fetch_emails_periodic_task
            fetch_emails_periodic_task(query="from:boss", max_results=10)

        mock_delay.assert_called_once_with(query="from:boss", max_results=10)
