"""
Провайдеры зависимостей FastAPI для слоя Interfaces.
Контроллеры получают готовые use case — инфраструктура инкапсулирована здесь.
Прямые импорты инфраструктуры в контроллерах запрещены.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.bulk_import_leads import BulkImportLeadsUseCase
from src.application.use_cases.convert_lead_to_deal import ConvertLeadToDealUseCase
from src.application.use_cases.create_lead import CreateLeadUseCase
from src.application.use_cases.get_analytics_overview import GetAnalyticsOverviewUseCase
from src.application.use_cases.get_dashboard_analytics import GetDashboardAnalyticsUseCase
from src.application.use_cases.get_lead import GetLeadUseCase
from src.application.use_cases.get_revenue_forecast import GetRevenueForecastUseCase
from src.application.use_cases.list_deals import ListDealsUseCase
from src.application.use_cases.list_lead_activities import ListLeadActivitiesUseCase
from src.application.use_cases.fetch_emails import FetchEmailsUseCase
from src.application.use_cases.forecast_deal import ForecastDealUseCase
from src.application.use_cases.generate_email import GenerateEmailUseCase
from src.application.use_cases.get_next_best_action import GetNextBestActionUseCase
from src.application.use_cases.get_pipeline import GetPipelineUseCase
from src.application.use_cases.list_pipelines import ListPipelinesUseCase
from src.application.use_cases.create_pipeline import CreatePipelineUseCase
from src.application.use_cases.update_pipeline import UpdatePipelineUseCase
from src.application.use_cases.delete_pipeline import DeletePipelineUseCase
from src.application.use_cases.add_stage import AddStageUseCase
from src.application.use_cases.update_stage import UpdateStageUseCase
from src.application.use_cases.delete_stage import DeleteStageUseCase
from src.application.use_cases.link_email_to_lead import LinkEmailToLeadUseCase
from src.application.use_cases.list_leads import ListLeadsUseCase
from src.application.use_cases.update_lead import UpdateLeadUseCase
from src.application.use_cases.move_deal_stage import MoveDealStageUseCase
from src.application.use_cases.anonymize_lead import AnonymizeLeadUseCase
from src.application.use_cases.delete_user_data import DeleteUserDataUseCase
from src.application.use_cases.get_gdpr_audit_log import GetGdprAuditLogUseCase
from src.application.use_cases.notify_deal_stage_change import NotifyDealStageChangeUseCase
from src.application.use_cases.notify_new_lead import NotifyNewLeadUseCase
from src.application.use_cases.score_lead import ScoreLeadUseCase
from src.application.use_cases.send_email import SendEmailUseCase
from src.infrastructure.ai.ai_service import OpenAIService
from src.infrastructure.database.repositories.activity_repository import SqlActivityRepository
from src.infrastructure.database.repositories.deal_repository import SqlDealRepository
from src.infrastructure.database.repositories.email_message_repository import SqlEmailMessageRepository
from src.infrastructure.database.repositories.gdpr_audit_repository import SqlGdprAuditRepository
from src.infrastructure.database.repositories.lead_repository import SqlLeadRepository
from src.infrastructure.database.repositories.pipeline_repository import SqlPipelineRepository
from src.infrastructure.database.session import get_db
from src.infrastructure.gmail.gmail_service import GmailService
from src.infrastructure.gmail.token_storage import FileTokenStorage
from src.infrastructure.celery.celery_task_service import CeleryTaskService
from src.infrastructure.telegram.telegram_service import TelegramService
from src.infrastructure.config.settings import settings
from src.domain.services.lead_anonymization_service import LeadAnonymizationService


# ── AI сервис (singleton-like через lru_cache не нужен — AsyncOpenAI сам управляет пулом) ──

def get_ai_service() -> OpenAIService:
    """Фабрика OpenAIService — вызывается один раз за запрос через Depends."""
    return OpenAIService()


# ── Gmail сервис ───────────────────────────────────────────────────────────────

def get_gmail_service() -> GmailService:
    """Фабрика GmailService с токен-хранилищем из настроек."""
    token_storage = FileTokenStorage(settings.GMAIL_TOKEN_FILE)
    return GmailService(
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        redirect_uri=settings.GMAIL_REDIRECT_URI,
        token_storage=token_storage,
    )


# ── Сессия БД ─────────────────────────────────────────────────────────────────

async def get_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    """Предоставляет асинхронную сессию БД обработчикам маршрутов."""
    return session


# ── Use Case провайдеры ───────────────────────────────────────────────────────

def get_create_lead_use_case(
    session: AsyncSession = Depends(get_session),
) -> CreateLeadUseCase:
    """Фабрика CreateLeadUseCase с инжектированными репозиториями."""
    return CreateLeadUseCase(lead_repo=SqlLeadRepository(session))


def get_bulk_import_leads_use_case(
    session: AsyncSession = Depends(get_session),
) -> BulkImportLeadsUseCase:
    """Фабрика BulkImportLeadsUseCase."""
    return BulkImportLeadsUseCase(lead_repo=SqlLeadRepository(session))


def get_list_leads_use_case(
    session: AsyncSession = Depends(get_session),
) -> ListLeadsUseCase:
    """Фабрика ListLeadsUseCase с инжектированными репозиториями."""
    return ListLeadsUseCase(lead_repo=SqlLeadRepository(session))


def get_update_lead_use_case(
    session: AsyncSession = Depends(get_session),
) -> UpdateLeadUseCase:
    """Фабрика UpdateLeadUseCase."""
    return UpdateLeadUseCase(lead_repo=SqlLeadRepository(session))


def get_analytics_overview_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetAnalyticsOverviewUseCase:
    """Фабрика GetAnalyticsOverviewUseCase."""
    return GetAnalyticsOverviewUseCase(
        lead_repo=SqlLeadRepository(session),
        deal_repo=SqlDealRepository(session),
        pipeline_repo=SqlPipelineRepository(session),
    )


def get_revenue_forecast_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetRevenueForecastUseCase:
    """Фабрика GetRevenueForecastUseCase."""
    return GetRevenueForecastUseCase(
        deal_repo=SqlDealRepository(session),
        pipeline_repo=SqlPipelineRepository(session),
    )


def get_dashboard_analytics_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetDashboardAnalyticsUseCase:
    """Фабрика GetDashboardAnalyticsUseCase."""
    return GetDashboardAnalyticsUseCase(
        lead_repo=SqlLeadRepository(session),
        deal_repo=SqlDealRepository(session),
        pipeline_repo=SqlPipelineRepository(session),
    )


def get_lead_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetLeadUseCase:
    """Фабрика GetLeadUseCase."""
    return GetLeadUseCase(lead_repo=SqlLeadRepository(session))


def get_list_lead_activities_use_case(
    session: AsyncSession = Depends(get_session),
) -> ListLeadActivitiesUseCase:
    """Фабрика ListLeadActivitiesUseCase."""
    return ListLeadActivitiesUseCase(activity_repo=SqlActivityRepository(session))


def get_list_deals_use_case(
    session: AsyncSession = Depends(get_session),
) -> ListDealsUseCase:
    """Фабрика ListDealsUseCase с инжектированным репозиторием сделок."""
    return ListDealsUseCase(deal_repo=SqlDealRepository(session))


def get_convert_lead_use_case(
    session: AsyncSession = Depends(get_session),
) -> ConvertLeadToDealUseCase:
    """Фабрика ConvertLeadToDealUseCase с инжектированными репозиториями."""
    return ConvertLeadToDealUseCase(
        lead_repo=SqlLeadRepository(session),
        deal_repo=SqlDealRepository(session),
        activity_repo=SqlActivityRepository(session),
        pipeline_repo=SqlPipelineRepository(session),
    )


def get_move_deal_stage_use_case(
    session: AsyncSession = Depends(get_session),
) -> MoveDealStageUseCase:
    """Фабрика MoveDealStageUseCase с инжектированными репозиториями."""
    return MoveDealStageUseCase(
        deal_repo=SqlDealRepository(session),
        pipeline_repo=SqlPipelineRepository(session),
        activity_repo=SqlActivityRepository(session),
    )


def get_pipeline_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetPipelineUseCase:
    """Фабрика GetPipelineUseCase с инжектированными репозиториями."""
    return GetPipelineUseCase(pipeline_repo=SqlPipelineRepository(session))


def get_list_pipelines_use_case(
    session: AsyncSession = Depends(get_session),
) -> ListPipelinesUseCase:
    """Фабрика ListPipelinesUseCase."""
    return ListPipelinesUseCase(pipeline_repo=SqlPipelineRepository(session))


def get_create_pipeline_use_case(
    session: AsyncSession = Depends(get_session),
) -> CreatePipelineUseCase:
    """Фабрика CreatePipelineUseCase."""
    return CreatePipelineUseCase(pipeline_repo=SqlPipelineRepository(session))


def get_update_pipeline_use_case(
    session: AsyncSession = Depends(get_session),
) -> UpdatePipelineUseCase:
    """Фабрика UpdatePipelineUseCase."""
    return UpdatePipelineUseCase(pipeline_repo=SqlPipelineRepository(session))


def get_delete_pipeline_use_case(
    session: AsyncSession = Depends(get_session),
) -> DeletePipelineUseCase:
    """Фабрика DeletePipelineUseCase."""
    return DeletePipelineUseCase(pipeline_repo=SqlPipelineRepository(session))


def get_add_stage_use_case(
    session: AsyncSession = Depends(get_session),
) -> AddStageUseCase:
    """Фабрика AddStageUseCase."""
    return AddStageUseCase(pipeline_repo=SqlPipelineRepository(session))


def get_update_stage_use_case(
    session: AsyncSession = Depends(get_session),
) -> UpdateStageUseCase:
    """Фабрика UpdateStageUseCase."""
    return UpdateStageUseCase(pipeline_repo=SqlPipelineRepository(session))


def get_delete_stage_use_case(
    session: AsyncSession = Depends(get_session),
) -> DeleteStageUseCase:
    """Фабрика DeleteStageUseCase."""
    return DeleteStageUseCase(pipeline_repo=SqlPipelineRepository(session))


# ── AI Use Case провайдеры ────────────────────────────────────────────────────

def get_score_lead_use_case(
    session: AsyncSession = Depends(get_session),
    ai_service: OpenAIService = Depends(get_ai_service),
) -> ScoreLeadUseCase:
    """Фабрика ScoreLeadUseCase."""
    return ScoreLeadUseCase(
        lead_repo=SqlLeadRepository(session),
        ai_service=ai_service,
    )


def get_forecast_deal_use_case(
    session: AsyncSession = Depends(get_session),
    ai_service: OpenAIService = Depends(get_ai_service),
) -> ForecastDealUseCase:
    """Фабрика ForecastDealUseCase."""
    return ForecastDealUseCase(
        deal_repo=SqlDealRepository(session),
        ai_service=ai_service,
    )


def get_next_best_action_use_case(
    session: AsyncSession = Depends(get_session),
    ai_service: OpenAIService = Depends(get_ai_service),
) -> GetNextBestActionUseCase:
    """Фабрика GetNextBestActionUseCase."""
    return GetNextBestActionUseCase(
        lead_repo=SqlLeadRepository(session),
        deal_repo=SqlDealRepository(session),
        ai_service=ai_service,
    )


def get_generate_email_use_case(
    session: AsyncSession = Depends(get_session),
    ai_service: OpenAIService = Depends(get_ai_service),
) -> GenerateEmailUseCase:
    """Фабрика GenerateEmailUseCase."""
    return GenerateEmailUseCase(
        lead_repo=SqlLeadRepository(session),
        ai_service=ai_service,
    )


# ── Gmail Use Case провайдеры ─────────────────────────────────────────────────

def get_send_email_use_case(
    session: AsyncSession = Depends(get_session),
    gmail_service: GmailService = Depends(get_gmail_service),
) -> SendEmailUseCase:
    """Фабрика SendEmailUseCase."""
    return SendEmailUseCase(
        email_service=gmail_service,
        email_repo=SqlEmailMessageRepository(session),
        lead_repo=SqlLeadRepository(session),
        activity_repo=SqlActivityRepository(session),
    )


def get_fetch_emails_use_case(
    session: AsyncSession = Depends(get_session),
    gmail_service: GmailService = Depends(get_gmail_service),
) -> FetchEmailsUseCase:
    """Фабрика FetchEmailsUseCase."""
    return FetchEmailsUseCase(
        email_service=gmail_service,
        email_repo=SqlEmailMessageRepository(session),
        lead_repo=SqlLeadRepository(session),
    )


def get_link_email_to_lead_use_case(
    session: AsyncSession = Depends(get_session),
) -> LinkEmailToLeadUseCase:
    """Фабрика LinkEmailToLeadUseCase."""
    return LinkEmailToLeadUseCase(
        email_repo=SqlEmailMessageRepository(session),
        lead_repo=SqlLeadRepository(session),
    )


# ── Telegram Use Case провайдеры ──────────────────────────────────────────────

def get_telegram_service() -> TelegramService:
    """Фабрика TelegramService из настроек окружения."""
    return TelegramService(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
        notification_chat_id=settings.TELEGRAM_NOTIFICATION_CHAT_ID,
    )


def get_notify_new_lead_use_case(
    telegram_service: TelegramService = Depends(get_telegram_service),
) -> NotifyNewLeadUseCase:
    """Фабрика NotifyNewLeadUseCase."""
    return NotifyNewLeadUseCase(telegram_service=telegram_service)


def get_task_service() -> CeleryTaskService:
    """Фабрика CeleryTaskService — точка входа в очередь задач."""
    return CeleryTaskService()


def get_notify_deal_stage_change_use_case(
    session: AsyncSession = Depends(get_session),
    telegram_service: TelegramService = Depends(get_telegram_service),
) -> NotifyDealStageChangeUseCase:
    """Фабрика NotifyDealStageChangeUseCase."""
    return NotifyDealStageChangeUseCase(
        telegram_service=telegram_service,
        pipeline_repo=SqlPipelineRepository(session),
    )


# ── GDPR Use Case провайдеры ──────────────────────────────────────────────────

def get_delete_user_data_use_case(
    session: AsyncSession = Depends(get_session),
) -> DeleteUserDataUseCase:
    """Фабрика DeleteUserDataUseCase — GDPR Right to Erasure для пользователя."""
    return DeleteUserDataUseCase(
        lead_repo=SqlLeadRepository(session),
        deal_repo=SqlDealRepository(session),
        email_repo=SqlEmailMessageRepository(session),
        activity_repo=SqlActivityRepository(session),
        gdpr_audit_repo=SqlGdprAuditRepository(session),
    )


def get_anonymize_lead_use_case(
    session: AsyncSession = Depends(get_session),
) -> AnonymizeLeadUseCase:
    """Фабрика AnonymizeLeadUseCase — GDPR псевдонимизация PII лида."""
    return AnonymizeLeadUseCase(
        lead_repo=SqlLeadRepository(session),
        email_repo=SqlEmailMessageRepository(session),
        activity_repo=SqlActivityRepository(session),
        gdpr_audit_repo=SqlGdprAuditRepository(session),
        anonymization_service=LeadAnonymizationService(),
    )


def get_gdpr_audit_log_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetGdprAuditLogUseCase:
    """Фабрика GetGdprAuditLogUseCase — чтение журнала аудита GDPR."""
    return GetGdprAuditLogUseCase(
        gdpr_audit_repo=SqlGdprAuditRepository(session),
    )
