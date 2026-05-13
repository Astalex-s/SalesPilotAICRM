"""
Юнит-тесты роутера /api/v1/tasks.
CeleryTaskService заменён MagicMock-ом — Celery не инициализируется.
"""
from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.ports.task_service import EnqueuedTask, TaskStatus
from src.interfaces.api.dependencies import get_task_service
from src.interfaces.api.v1.routers.tasks import router


def _fake_enqueued(task_name: str = "tasks.ai.score_lead") -> EnqueuedTask:
    return EnqueuedTask(task_id="test-task-id-123", task_name=task_name)


def _build_app(task_svc: MagicMock) -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_task_service] = lambda: task_svc
    return app


@pytest.fixture
def task_service() -> MagicMock:
    svc = MagicMock()
    svc.enqueue_score_lead.return_value = _fake_enqueued("tasks.ai.score_lead")
    svc.enqueue_forecast_deal.return_value = _fake_enqueued("tasks.ai.forecast_deal")
    svc.enqueue_generate_email.return_value = _fake_enqueued("tasks.ai.generate_email")
    svc.enqueue_next_best_action.return_value = _fake_enqueued("tasks.ai.next_best_action")
    svc.enqueue_send_email.return_value = _fake_enqueued("tasks.email.send")
    svc.enqueue_fetch_emails.return_value = _fake_enqueued("tasks.email.fetch")
    svc.get_task_status.return_value = TaskStatus(
        task_id="test-task-id-123",
        status="SUCCESS",
        result={"score": 85},
        error=None,
    )
    return svc


@pytest.fixture
def client(task_service) -> TestClient:
    return TestClient(_build_app(task_service))


class TestEnqueueScoreLead:
    def test_returns_202_with_task_id(self, client):
        resp = client.post(f"/api/v1/jobs/ai/leads/{uuid4()}/score")
        assert resp.status_code == 202
        assert resp.json()["task_id"] == "test-task-id-123"
        assert resp.json()["status"] == "ENQUEUED"


class TestEnqueueForecastDeal:
    def test_returns_202(self, client):
        resp = client.post(f"/api/v1/jobs/ai/deals/{uuid4()}/forecast")
        assert resp.status_code == 202
        assert "task_id" in resp.json()


class TestEnqueueGenerateEmail:
    def test_returns_202(self, client):
        resp = client.post(f"/api/v1/jobs/ai/leads/{uuid4()}/generate-email")
        assert resp.status_code == 202

    def test_accepts_tone_param(self, client, task_service):
        lead_id = uuid4()
        client.post(f"/api/v1/jobs/ai/leads/{lead_id}/generate-email?tone=formal")
        task_service.enqueue_generate_email.assert_called_once_with(
            lead_id=lead_id, tone="formal", extra_context=None
        )


class TestEnqueueNextBestAction:
    def test_returns_202_for_lead(self, client):
        resp = client.post(f"/api/v1/jobs/ai/lead/{uuid4()}/next-action")
        assert resp.status_code == 202

    def test_returns_202_for_deal(self, client):
        resp = client.post(f"/api/v1/jobs/ai/deal/{uuid4()}/next-action")
        assert resp.status_code == 202


class TestEnqueueSendEmail:
    def test_returns_202(self, client):
        resp = client.post("/api/v1/jobs/email/send", json={
            "to": "recipient@test.com",
            "subject": "Hello",
            "body": "World",
            "performed_by_id": str(uuid4()),
        })
        assert resp.status_code == 202


class TestEnqueueFetchEmails:
    def test_returns_202(self, client):
        resp = client.post("/api/v1/jobs/email/fetch", json={})
        assert resp.status_code == 202


class TestGetTaskStatus:
    def test_returns_task_status(self, client):
        resp = client.get("/api/v1/jobs/test-task-id-123/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["task_id"] == "test-task-id-123"
        assert body["status"] == "SUCCESS"
        assert body["result"] == {"score": 85}
