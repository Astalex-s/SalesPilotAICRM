"""
Роутер /api/v1/tasks — постановка задач в фоновую очередь и мониторинг.

Тонкие контроллеры: принять запрос → поставить задачу → вернуть task_id.
Никакой бизнес-логики. AI и Email use cases выполняются в Celery воркерах.
"""
from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.application.dtos.task_dtos import (
    EnqueueFetchEmailsInput,
    EnqueueSendEmailInput,
    TaskEnqueuedOutput,
    TaskStatusOutput,
)
from src.application.ports.task_service import ITaskService
from src.interfaces.api.dependencies import get_task_service

router = APIRouter(prefix="/tasks", tags=["Фоновые задачи"])


# ── AI задачи ──────────────────────────────────────────────────────────────────

@router.post(
    "/ai/leads/{lead_id}/score",
    response_model=TaskEnqueuedOutput,
    status_code=http_status.HTTP_202_ACCEPTED,
    summary="[Async] AI-оценка лида",
    description=(
        "Ставит в очередь задачу AI-оценки лида. "
        "Результат доступен через GET /tasks/{task_id}/status после завершения."
    ),
)
async def enqueue_score_lead(
    lead_id: UUID,
    task_service: ITaskService = Depends(get_task_service),
) -> TaskEnqueuedOutput:
    """POST /api/v1/tasks/ai/leads/{lead_id}/score."""
    task = task_service.enqueue_score_lead(lead_id)
    return TaskEnqueuedOutput(
        task_id=task.task_id,
        task_name=task.task_name,
        message=f"Задача AI-оценки лида {lead_id} поставлена в очередь.",
    )


@router.post(
    "/ai/deals/{deal_id}/forecast",
    response_model=TaskEnqueuedOutput,
    status_code=http_status.HTTP_202_ACCEPTED,
    summary="[Async] AI-прогноз сделки",
    description=(
        "Ставит в очередь задачу AI-прогноза вероятности закрытия сделки. "
        "Результат доступен через GET /tasks/{task_id}/status после завершения."
    ),
)
async def enqueue_forecast_deal(
    deal_id: UUID,
    task_service: ITaskService = Depends(get_task_service),
) -> TaskEnqueuedOutput:
    """POST /api/v1/tasks/ai/deals/{deal_id}/forecast."""
    task = task_service.enqueue_forecast_deal(deal_id)
    return TaskEnqueuedOutput(
        task_id=task.task_id,
        task_name=task.task_name,
        message=f"Задача AI-прогноза сделки {deal_id} поставлена в очередь.",
    )


@router.post(
    "/ai/leads/{lead_id}/generate-email",
    response_model=TaskEnqueuedOutput,
    status_code=http_status.HTTP_202_ACCEPTED,
    summary="[Async] AI-генерация письма",
    description=(
        "Ставит в очередь задачу AI-генерации письма для лида. "
        "Результат доступен через GET /tasks/{task_id}/status после завершения."
    ),
)
async def enqueue_generate_email(
    lead_id: UUID,
    tone: Literal["formal", "friendly", "assertive"] = "friendly",
    extra_context: str | None = None,
    task_service: ITaskService = Depends(get_task_service),
) -> TaskEnqueuedOutput:
    """POST /api/v1/tasks/ai/leads/{lead_id}/generate-email."""
    task = task_service.enqueue_generate_email(
        lead_id=lead_id,
        tone=tone,
        extra_context=extra_context,
    )
    return TaskEnqueuedOutput(
        task_id=task.task_id,
        task_name=task.task_name,
        message=f"Задача генерации письма для лида {lead_id} поставлена в очередь.",
    )


@router.post(
    "/ai/{entity_type}/{entity_id}/next-action",
    response_model=TaskEnqueuedOutput,
    status_code=http_status.HTTP_202_ACCEPTED,
    summary="[Async] AI-следующее действие",
    description=(
        "Ставит в очередь задачу AI-рекомендации следующего действия. "
        "entity_type: 'lead' или 'deal'. "
        "Результат доступен через GET /tasks/{task_id}/status."
    ),
)
async def enqueue_next_best_action(
    entity_type: Literal["lead", "deal"],
    entity_id: UUID,
    task_service: ITaskService = Depends(get_task_service),
) -> TaskEnqueuedOutput:
    """POST /api/v1/tasks/ai/{entity_type}/{entity_id}/next-action."""
    task = task_service.enqueue_next_best_action(
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return TaskEnqueuedOutput(
        task_id=task.task_id,
        task_name=task.task_name,
        message=(
            f"Задача Next Best Action для {entity_type} {entity_id} "
            "поставлена в очередь."
        ),
    )


# ── Email задачи ───────────────────────────────────────────────────────────────

@router.post(
    "/email/send",
    response_model=TaskEnqueuedOutput,
    status_code=http_status.HTTP_202_ACCEPTED,
    summary="[Async] Отправка письма",
    description=(
        "Ставит в очередь задачу отправки письма через Gmail. "
        "Результат (EmailMessageOutput) доступен через GET /tasks/{task_id}/status."
    ),
)
async def enqueue_send_email(
    body: EnqueueSendEmailInput,
    task_service: ITaskService = Depends(get_task_service),
) -> TaskEnqueuedOutput:
    """POST /api/v1/tasks/email/send."""
    task = task_service.enqueue_send_email(
        payload=body.model_dump(mode="json")
    )
    return TaskEnqueuedOutput(
        task_id=task.task_id,
        task_name=task.task_name,
        message=f"Задача отправки письма на {body.to} поставлена в очередь.",
    )


@router.post(
    "/email/fetch",
    response_model=TaskEnqueuedOutput,
    status_code=http_status.HTTP_202_ACCEPTED,
    summary="[Async] Синхронизация писем",
    description=(
        "Ставит в очередь задачу синхронизации писем из Gmail. "
        "Результат (список новых писем) доступен через GET /tasks/{task_id}/status."
    ),
)
async def enqueue_fetch_emails(
    body: EnqueueFetchEmailsInput,
    task_service: ITaskService = Depends(get_task_service),
) -> TaskEnqueuedOutput:
    """POST /api/v1/tasks/email/fetch."""
    task = task_service.enqueue_fetch_emails(
        query=body.query,
        max_results=body.max_results,
    )
    return TaskEnqueuedOutput(
        task_id=task.task_id,
        task_name=task.task_name,
        message="Задача синхронизации писем из Gmail поставлена в очередь.",
    )


# ── Статус задачи ──────────────────────────────────────────────────────────────

@router.get(
    "/{task_id}/status",
    response_model=TaskStatusOutput,
    status_code=http_status.HTTP_200_OK,
    summary="Статус задачи",
    description=(
        "Возвращает текущий статус фоновой задачи. "
        "Статусы: PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED."
    ),
)
async def get_task_status(
    task_id: str,
    task_service: ITaskService = Depends(get_task_service),
) -> TaskStatusOutput:
    """GET /api/v1/tasks/{task_id}/status."""
    status = task_service.get_task_status(task_id)
    return TaskStatusOutput(
        task_id=status.task_id,
        status=status.status,
        result=status.result,
        error=status.error,
    )
