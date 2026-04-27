"""
Экспорт всех ORM-моделей.
Импорт этого модуля гарантирует регистрацию таблиц в Base.metadata —
это необходимо для работы Alembic autogenerate.
"""
from src.infrastructure.database.models.activity_model import ActivityModel
from src.infrastructure.database.models.deal_model import DealModel
from src.infrastructure.database.models.email_message_model import EmailMessageModel
from src.infrastructure.database.models.gdpr_audit_model import GdprAuditModel
from src.infrastructure.database.models.lead_model import LeadModel
from src.infrastructure.database.models.pipeline_model import PipelineModel
from src.infrastructure.database.models.stage_model import StageModel
from src.infrastructure.database.models.user_model import UserModel

__all__ = [
    "ActivityModel",
    "DealModel",
    "EmailMessageModel",
    "GdprAuditModel",
    "LeadModel",
    "PipelineModel",
    "StageModel",
    "UserModel",
]
