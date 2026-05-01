"""
RefreshTokenUseCase — валидирует refresh-токен и выдаёт новую пару токенов.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError

from src.application.dtos.auth_dtos import RefreshTokenInput, TokenOutput
from src.infrastructure.auth.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from src.infrastructure.database.repositories.user_repository import SqlUserRepository

_INVALID_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Refresh-токен недействителен или истёк.",
    headers={"WWW-Authenticate": "Bearer"},
)


class RefreshTokenUseCase:
    def __init__(self, user_repo: SqlUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, data: RefreshTokenInput) -> TokenOutput:
        try:
            payload = decode_refresh_token(data.refresh_token)
        except JWTError:
            raise _INVALID_EXC

        user_id_str: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if not user_id_str or not role:
            raise _INVALID_EXC

        user = await self._user_repo.find_by_id(UUID(user_id_str))
        if user is None or not user.is_active:
            raise _INVALID_EXC

        access_token = create_access_token(user_id=user.id, role=user.role.value)
        refresh_token = create_refresh_token(user_id=user.id, role=user.role.value)
        return TokenOutput(access_token=access_token, refresh_token=refresh_token)
