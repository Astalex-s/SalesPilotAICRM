"""
Роутер /api/v1/users — управление пользователями.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.auth_dtos import (
    ChangePasswordInput,
    UpdateProfileInput,
    UpdateUserRoleInput,
    UserOutput,
)
from src.application.exceptions import InvalidCurrentPasswordError, UserNotFoundError
from src.application.use_cases.change_user_password import ChangeUserPasswordUseCase
from src.application.use_cases.list_users import ListUsersUseCase
from src.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.application.use_cases.update_user_role import UpdateUserRoleUseCase
from src.infrastructure.database.repositories.user_repository import SqlUserRepository
from src.infrastructure.database.session import get_db
from src.interfaces.api.auth_dependencies import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Пользователи"])


def _user_repo(session: AsyncSession = Depends(get_db)) -> SqlUserRepository:
    return SqlUserRepository(session)


@router.get(
    "",
    response_model=list[UserOutput],
    summary="Список пользователей (только ADMIN)",
)
async def list_users(
    repo: SqlUserRepository = Depends(_user_repo),
    _: UserOutput = Depends(require_admin),
) -> list[UserOutput]:
    return await ListUsersUseCase(repo).execute()


@router.patch(
    "/me",
    response_model=UserOutput,
    summary="Обновить профиль текущего пользователя",
)
async def update_my_profile(
    body: UpdateProfileInput,
    repo: SqlUserRepository = Depends(_user_repo),
    current_user: UserOutput = Depends(get_current_user),
) -> UserOutput:
    try:
        return await UpdateUserProfileUseCase(repo).execute(current_user.id, body)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/me/password",
    status_code=http_status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Сменить пароль текущего пользователя",
)
async def change_my_password(
    body: ChangePasswordInput,
    repo: SqlUserRepository = Depends(_user_repo),
    current_user: UserOutput = Depends(get_current_user),
) -> None:
    try:
        await ChangeUserPasswordUseCase(repo).execute(current_user.id, body)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))
    except InvalidCurrentPasswordError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch(
    "/{user_id}/role",
    response_model=UserOutput,
    summary="Изменить роль пользователя (только ADMIN)",
)
async def update_role(
    user_id: UUID,
    body: UpdateUserRoleInput,
    repo: SqlUserRepository = Depends(_user_repo),
    _: UserOutput = Depends(require_admin),
) -> UserOutput:
    return await UpdateUserRoleUseCase(repo).execute(user_id, body)
