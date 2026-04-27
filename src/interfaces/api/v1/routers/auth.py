"""
Роутер /api/v1/auth — регистрация, вход, текущий пользователь.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.auth_dtos import LoginInput, RegisterInput, TokenOutput, UserOutput
from src.application.use_cases.login_user import LoginUserUseCase
from src.application.use_cases.register_user import RegisterUserUseCase
from src.infrastructure.database.repositories.user_repository import SqlUserRepository
from src.infrastructure.database.session import get_db
from src.interfaces.api.auth_dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


def _user_repo(session: AsyncSession = Depends(get_db)) -> SqlUserRepository:
    return SqlUserRepository(session)


@router.post(
    "/register",
    response_model=UserOutput,
    status_code=http_status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register(
    body: RegisterInput,
    repo: SqlUserRepository = Depends(_user_repo),
) -> UserOutput:
    return await RegisterUserUseCase(repo).execute(body)


@router.post(
    "/login",
    response_model=TokenOutput,
    summary="Вход в систему",
)
async def login(
    body: LoginInput,
    repo: SqlUserRepository = Depends(_user_repo),
) -> TokenOutput:
    return await LoginUserUseCase(repo).execute(body)


@router.get(
    "/me",
    response_model=UserOutput,
    summary="Текущий пользователь",
)
async def me(current_user: UserOutput = Depends(get_current_user)) -> UserOutput:
    return current_user
