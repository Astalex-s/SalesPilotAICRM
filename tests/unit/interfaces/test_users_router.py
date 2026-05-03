"""
Юнит-тесты роутера /api/v1/users.
Репозиторий и auth зависимости заменены моками.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.application.dtos.auth_dtos import UserOutput
from src.application.exceptions import InvalidCurrentPasswordError, UserNotFoundError
from src.domain.value_objects.enums import UserRole
from src.infrastructure.database.repositories.user_repository import SqlUserRepository
from src.interfaces.api.auth_dependencies import get_current_user, require_admin
from src.interfaces.api.v1.routers.users import router, _user_repo
from src.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.application.use_cases.change_user_password import ChangeUserPasswordUseCase


def _fake_user(role: UserRole = UserRole.MANAGER) -> UserOutput:
    return UserOutput(
        id=uuid4(), first_name="Test", last_name="User",
        email="tu@test.com", role=role, is_active=True,
    )


def _build_app(repo: AsyncMock, current_user: UserOutput | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[_user_repo] = lambda: repo
    user = current_user or _fake_user()
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[require_admin] = lambda: _fake_user(UserRole.ADMIN)
    return app


class TestUpdateMyProfile:
    def test_returns_200_on_success(self):
        repo = AsyncMock(spec=SqlUserRepository)
        user = _fake_user()
        updated = UserOutput(
            id=user.id, first_name="Updated", last_name="User",
            email="tu@test.com", role=UserRole.MANAGER, is_active=True,
        )
        with patch.object(UpdateUserProfileUseCase, "execute", return_value=updated):
            client = TestClient(_build_app(repo, current_user=user))
            resp = client.patch(
                "/api/v1/users/me",
                json={"first_name": "Updated", "last_name": "User"},
            )
        assert resp.status_code == 200

    def test_returns_404_when_user_not_found(self):
        repo = AsyncMock(spec=SqlUserRepository)
        user = _fake_user()
        with patch.object(UpdateUserProfileUseCase, "execute", side_effect=UserNotFoundError("not found")):
            client = TestClient(_build_app(repo, current_user=user))
            resp = client.patch(
                "/api/v1/users/me",
                json={"first_name": "X", "last_name": "Y"},
            )
        assert resp.status_code == 404


class TestChangeMyPassword:
    def test_returns_204_on_success(self):
        repo = AsyncMock(spec=SqlUserRepository)
        user = _fake_user()
        with patch.object(ChangeUserPasswordUseCase, "execute", return_value=None):
            client = TestClient(_build_app(repo, current_user=user))
            resp = client.post(
                "/api/v1/users/me/password",
                json={"current_password": "oldpass", "new_password": "newpass123"},
            )
        assert resp.status_code == 204

    def test_returns_404_when_user_not_found(self):
        repo = AsyncMock(spec=SqlUserRepository)
        user = _fake_user()
        with patch.object(ChangeUserPasswordUseCase, "execute", side_effect=UserNotFoundError("not found")):
            client = TestClient(_build_app(repo, current_user=user))
            resp = client.post(
                "/api/v1/users/me/password",
                json={"current_password": "oldpass", "new_password": "newpass123"},
            )
        assert resp.status_code == 404

    def test_returns_400_when_invalid_password(self):
        repo = AsyncMock(spec=SqlUserRepository)
        user = _fake_user()
        with patch.object(
            ChangeUserPasswordUseCase, "execute",
            side_effect=InvalidCurrentPasswordError(),
        ):
            client = TestClient(_build_app(repo, current_user=user))
            resp = client.post(
                "/api/v1/users/me/password",
                json={"current_password": "wrong", "new_password": "newpass123"},
            )
        assert resp.status_code == 400
