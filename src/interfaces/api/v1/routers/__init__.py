"""
Агрегация всех v1 роутеров.
Импортировать отсюда и регистрировать в фабрике приложения.
"""
from src.interfaces.api.v1.routers.ai import router as ai_router
from src.interfaces.api.v1.routers.deals import router as deals_router
from src.interfaces.api.v1.routers.emails import router as emails_router
from src.interfaces.api.v1.routers.gmail_auth import router as gmail_auth_router
from src.interfaces.api.v1.routers.leads import router as leads_router
from src.interfaces.api.v1.routers.pipelines import router as pipelines_router

__all__ = [
    "ai_router",
    "deals_router",
    "emails_router",
    "gmail_auth_router",
    "leads_router",
    "pipelines_router",
]
