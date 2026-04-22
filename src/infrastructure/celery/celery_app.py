"""
Экземпляр Celery-приложения и его конфигурация.

Находится в слое Infrastructure.
Импортируется воркером и CeleryTaskService.
Не содержит бизнес-логики.
"""
from celery import Celery

from src.infrastructure.config.settings import settings

# ── Создание экземпляра ────────────────────────────────────────────────────────

celery_app = Celery(
    "salespilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "src.infrastructure.celery.tasks.ai_tasks",
        "src.infrastructure.celery.tasks.email_tasks",
        "src.infrastructure.celery.tasks.sync_tasks",
    ],
)

# ── Конфигурация ───────────────────────────────────────────────────────────────

celery_app.conf.update(
    # Сериализация — только JSON (безопасно, переносимо)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Временная зона
    timezone="UTC",
    enable_utc=True,

    # Отслеживание состояния STARTED
    task_track_started=True,

    # Хранить результаты 1 час
    result_expires=3600,

    # Ack задачи только после успешного выполнения (защита от потери)
    task_acks_late=True,

    # Не префетчировать задачи (воркер берёт по одной)
    worker_prefetch_multiplier=1,

    # Расписание периодических задач (Celery Beat)
    beat_schedule={
        "sync-emails-periodic": {
            "task": "tasks.sync.fetch_emails_periodic",
            "schedule": settings.CELERY_EMAIL_SYNC_INTERVAL_SECONDS,
            "kwargs": {"query": "", "max_results": 100},
        },
    },
)
