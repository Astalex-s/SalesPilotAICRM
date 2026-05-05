"""
Экземпляр Celery-приложения и его конфигурация.

Находится в слое Infrastructure.
Импортируется воркером и CeleryTaskService.
Не содержит бизнес-логики.
"""
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from src.infrastructure.config.settings import settings
from src.infrastructure.logging.setup import configure_logging


@after_setup_logger.connect
@after_setup_task_logger.connect
def _setup_celery_json_logging(logger, **kwargs):  # noqa: ARG001
    """Replace Celery's default formatter with our JSON formatter."""
    configure_logging(settings.LOG_LEVEL)

# ── Создание экземпляра ────────────────────────────────────────────────────────

celery_app = Celery(
    "salespilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "src.infrastructure.celery.tasks.ai_tasks",
        "src.infrastructure.celery.tasks.deal_tasks",
        "src.infrastructure.celery.tasks.email_tasks",
        "src.infrastructure.celery.tasks.gdpr_tasks",
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
        "gdpr-retention-policy-daily": {
            "task": "tasks.gdpr.apply_retention_policy",
            "schedule": settings.CELERY_RETENTION_CHECK_INTERVAL,
        },
        "notify-overdue-deals-daily": {
            "task": "tasks.deals.notify_overdue",
            "schedule": settings.CELERY_OVERDUE_DEALS_CHECK_INTERVAL,
        },
    },
)
