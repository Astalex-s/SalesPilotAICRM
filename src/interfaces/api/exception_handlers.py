"""
Обработчики исключений FastAPI.
Транслируют доменные и application-исключения в HTTP-ответы.
Регистрируются в фабрике приложения — не в контроллерах.
"""
from fastapi import Request
from fastapi.responses import JSONResponse

from src.application.exceptions import (
    ApplicationError,
    EntityNotFoundError,
    GmailNotAuthorizedError,
    LeadEmailAlreadyExistsError,
    StageNotInPipelineError,
)
from src.domain.exceptions import DomainError


async def handle_entity_not_found(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    """404 — запрошенная сущность не найдена."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def handle_email_conflict(request: Request, exc: LeadEmailAlreadyExistsError) -> JSONResponse:
    """409 — лид с таким e-mail уже существует."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def handle_stage_not_in_pipeline(request: Request, exc: StageNotInPipelineError) -> JSONResponse:
    """422 — этап не принадлежит указанной воронке."""
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    """422 — нарушение доменного инварианта (неверный переход, закрытая сделка и т.д.)."""
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def handle_gmail_not_authorized(request: Request, exc: GmailNotAuthorizedError) -> JSONResponse:
    """401 — Gmail не авторизован, требуется OAuth2."""
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
    """400 — прочие ошибки слоя Application."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


def register_exception_handlers(app: object) -> None:
    """Регистрирует все обработчики на экземпляре FastAPI.

    Порядок важен: подклассы должны регистрироваться раньше базового класса.
    """
    app.add_exception_handler(EntityNotFoundError, handle_entity_not_found)
    app.add_exception_handler(LeadEmailAlreadyExistsError, handle_email_conflict)
    app.add_exception_handler(StageNotInPipelineError, handle_stage_not_in_pipeline)
    app.add_exception_handler(GmailNotAuthorizedError, handle_gmail_not_authorized)
    app.add_exception_handler(DomainError, handle_domain_error)
    # ApplicationError должен быть последним — он базовый для всех выше
    app.add_exception_handler(ApplicationError, handle_application_error)
