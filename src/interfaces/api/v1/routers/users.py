"""
Роутер /api/v1/users — управление пользователями (только ADMIN).
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.auth_dtos import UpdateUserRoleInput, UserOutput
from src.application.use_cases.list_users import ListUsersUseCase
from src.application.use_cases.update_user_role import UpdateUserRoleUseCase
from src.infrastructure.database.repositories.user_repository import SqlUserRepository
from src.infrastructure.database.session import get_db
from src.interfaces.api.auth_dependencies import require_admin

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
