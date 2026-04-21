"""
Экспорт всех ORM-моделей.
Импорт этого модуля гарантирует регистрацию таблиц в Base.metadata —
это необходимо для работы Alembic autogenerate.
"""
from src.infrastructure.database.models.activity_model import ActivityModel
from src.infrastructure.database.models.deal_model import DealModel
from src.infrastructure.database.models.lead_model import LeadModel
from src.infrastructure.database.models.pipeline_model import PipelineModel
from src.infrastructure.database.models.stage_model import StageModel

__all__ = [
    "ActivityModel",
    "DealModel",
    "LeadModel",
    "PipelineModel",
    "StageModel",
]
