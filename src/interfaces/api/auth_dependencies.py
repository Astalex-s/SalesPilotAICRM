"""
Зависимости FastAPI для аутентификации и авторизации.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.auth_dtos import UserOutput
from src.domain.value_objects.enums import UserRole
from src.infrastructure.auth.auth_service import decode_access_token
from src.infrastructure.database.repositories.user_repository import SqlUserRepository
from src.infrastructure.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен недействителен или истёк.",
    headers={"WWW-Authenticate": "Bearer"},
)

_FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Недостаточно прав для выполнения операции.",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> UserOutput:
    """Декодирует JWT и возвращает текущего пользователя."""
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise _CREDENTIALS_EXCEPTION
    except JWTError:
        raise _CREDENTIALS_EXCEPTION

    from uuid import UUID
    repo = SqlUserRepository(session)
    user = await repo.find_by_id(UUID(user_id))
    if user is None or not user.is_active:
        raise _CREDENTIALS_EXCEPTION

    return UserOutput(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=str(user.email),
        role=user.role,
        is_active=user.is_active,
    )


def require_admin(current_user: UserOutput = Depends(get_current_user)) -> UserOutput:
    """Проверяет, что текущий пользователь — ADMIN."""
    if current_user.role != UserRole.ADMIN:
        raise _FORBIDDEN_EXCEPTION
    return current_user


def require_manager(current_user: UserOutput = Depends(get_current_user)) -> UserOutput:
    """Проверяет, что текущий пользователь — ADMIN или MANAGER."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise _FORBIDDEN_EXCEPTION
    return current_user
