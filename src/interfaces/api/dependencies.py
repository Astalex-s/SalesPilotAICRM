"""
Провайдеры зависимостей FastAPI для слоя Interfaces.
Контроллеры получают готовые use case — инфраструктура инкапсулирована здесь.
Прямые импорты инфраструктуры в контроллерах запрещены.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.convert_lead_to_deal import ConvertLeadToDealUseCase
from src.application.use_cases.create_lead import CreateLeadUseCase
from src.application.use_cases.get_pipeline import GetPipelineUseCase
from src.application.use_cases.list_leads import ListLeadsUseCase
from src.application.use_cases.move_deal_stage import MoveDealStageUseCase
from src.infrastructure.database.repositories.activity_repository import SqlActivityRepository
from src.infrastructure.database.repositories.deal_repository import SqlDealRepository
from src.infrastructure.database.repositories.lead_repository import SqlLeadRepository
from src.infrastructure.database.repositories.pipeline_repository import SqlPipelineRepository
from src.infrastructure.database.session import get_db


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


def get_list_leads_use_case(
    session: AsyncSession = Depends(get_session),
) -> ListLeadsUseCase:
    """Фабрика ListLeadsUseCase с инжектированными репозиториями."""
    return ListLeadsUseCase(lead_repo=SqlLeadRepository(session))


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
