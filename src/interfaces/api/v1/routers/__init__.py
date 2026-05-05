"""
Агрегация всех v1 роутеров.
Импортировать отсюда и регистрировать в фабрике приложения.
"""
from src.interfaces.api.v1.routers.ai import router as ai_router
from src.interfaces.api.v1.routers.crm_tasks import router as crm_tasks_router
from src.interfaces.api.v1.routers.meetings import router as meetings_router
from src.interfaces.api.v1.routers.analytics import router as analytics_router
from src.interfaces.api.v1.routers.auth import router as auth_router
from src.interfaces.api.v1.routers.deal_attachments import router as deal_attachments_router
from src.interfaces.api.v1.routers.deals import router as deals_router
from src.interfaces.api.v1.routers.emails import router as emails_router
from src.interfaces.api.v1.routers.gdpr import router as gdpr_router
from src.interfaces.api.v1.routers.gmail_auth import router as gmail_auth_router
from src.interfaces.api.v1.routers.leads import router as leads_router
from src.interfaces.api.v1.routers.notifications import router as notifications_router
from src.interfaces.api.v1.routers.pipelines import router as pipelines_router
from src.interfaces.api.v1.routers.tasks import router as tasks_router
from src.interfaces.api.v1.routers.telegram import router as telegram_router
from src.interfaces.api.v1.routers.users import router as users_router

__all__ = [
    "ai_router",
    "crm_tasks_router",
    "analytics_router",
    "auth_router",
    "deal_attachments_router",
    "deals_router",
    "emails_router",
    "gdpr_router",
    "gmail_auth_router",
    "leads_router",
    "meetings_router",
    "notifications_router",
    "pipelines_router",
    "tasks_router",
    "telegram_router",
    "users_router",
]
