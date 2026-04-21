"""
Агрегация всех v1 роутеров.
Импортировать отсюда и регистрировать в фабрике приложения.
"""
from src.interfaces.api.v1.routers.deals import router as deals_router
from src.interfaces.api.v1.routers.leads import router as leads_router
from src.interfaces.api.v1.routers.pipelines import router as pipelines_router

__all__ = ["deals_router", "leads_router", "pipelines_router"]
