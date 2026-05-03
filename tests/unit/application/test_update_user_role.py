"""
Юнит-тесты UpdateUserRoleUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.auth_dtos import UpdateUserRoleInput
from src.application.exceptions import UserNotFoundError
from src.application.use_cases.update_user_role import UpdateUserRoleUseCase
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole


def _make_user(role: UserRole = UserRole.SALES_REP) -> User:
    return User.create(
        first_name="Test",
        last_name="User",
        email=Email("test@example.com"),
        role=role,
    )


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(user_repo) -> UpdateUserRoleUseCase:
    return UpdateUserRoleUseCase(user_repo=user_repo)


class TestUpdateRoleSuccess:
    async def test_returns_updated_user_with_new_role(self, use_case, user_repo):
        user = _make_user(UserRole.SALES_REP)
        updated = User(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            role=UserRole.MANAGER,
        )
        user_repo.update_role.return_value = updated

        result = await use_case.execute(user.id, UpdateUserRoleInput(role=UserRole.MANAGER))
        assert result.role == UserRole.MANAGER


class TestUpdateRoleNotFound:
    async def test_raises_when_user_not_found(self, use_case, user_repo):
        user_repo.update_role.return_value = None

        with pytest.raises(UserNotFoundError):
            await use_case.execute(uuid4(), UpdateUserRoleInput(role=UserRole.ADMIN))
