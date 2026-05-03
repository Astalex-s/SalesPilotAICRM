"""
Юнит-тесты для Celery email задач (send_email_task, fetch_emails_task).
Все внешние зависимости замокированы через asyncio.run.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch


class TestSendEmailTask:
    def test_success_returns_result(self) -> None:
        from src.infrastructure.celery.tasks.email_tasks import send_email_task

        mock_result = {"id": "msg-001", "subject": "Hello"}
        with patch(
            "src.infrastructure.celery.tasks.email_tasks.asyncio.run",
            return_value=mock_result,
        ):
            result = send_email_task({"to": "user@test.com", "subject": "Hello", "body": "World"})

        assert result == mock_result

    def test_retries_on_exception(self) -> None:
        from src.infrastructure.celery.tasks.email_tasks import send_email_task

        with (
            patch(
                "src.infrastructure.celery.tasks.email_tasks.asyncio.run",
                side_effect=ConnectionError("SMTP down"),
            ),
            patch.object(
                send_email_task, "retry", side_effect=ConnectionError("retry")
            ) as mock_retry,
        ):
            with pytest.raises(ConnectionError, match="retry"):
                send_email_task({"to": "user@test.com"})

        mock_retry.assert_called_once()


class TestFetchEmailsTask:
    def test_success_returns_list(self) -> None:
        from src.infrastructure.celery.tasks.email_tasks import fetch_emails_task

        mock_result = [{"id": "msg-001"}, {"id": "msg-002"}]
        with patch(
            "src.infrastructure.celery.tasks.email_tasks.asyncio.run",
            return_value=mock_result,
        ):
            result = fetch_emails_task(query="from:boss", max_results=10)

        assert result == mock_result

    def test_retries_on_exception(self) -> None:
        from src.infrastructure.celery.tasks.email_tasks import fetch_emails_task

        with (
            patch(
                "src.infrastructure.celery.tasks.email_tasks.asyncio.run",
                side_effect=RuntimeError("Gmail error"),
            ),
            patch.object(
                fetch_emails_task, "retry", side_effect=RuntimeError("retry")
            ) as mock_retry,
        ):
            with pytest.raises(RuntimeError, match="retry"):
                fetch_emails_task()

        mock_retry.assert_called_once()

    def test_default_params(self) -> None:
        from src.infrastructure.celery.tasks.email_tasks import fetch_emails_task

        with patch(
            "src.infrastructure.celery.tasks.email_tasks.asyncio.run",
            return_value=[],
        ) as mock_run:
            fetch_emails_task()

        mock_run.assert_called_once()
