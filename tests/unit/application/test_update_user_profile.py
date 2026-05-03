"""
Юнит-тесты UpdateUserProfileUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.auth_dtos import UpdateProfileInput
from src.application.exceptions import UserNotFoundError
from src.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole


def _make_user() -> User:
    return User.create(
        first_name="Maria",
        last_name="Ivanova",
        email=Email("maria@example.com"),
        role=UserRole.MANAGER,
    )


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(user_repo) -> UpdateUserProfileUseCase:
    return UpdateUserProfileUseCase(user_repo=user_repo)


class TestUpdateProfileSuccess:
    async def test_returns_updated_user(self, use_case, user_repo):
        user = _make_user()
        updated = User(
            id=user.id,
            first_name="Aleksei",
            last_name="Petrov",
            email=user.email,
            role=user.role,
        )
        user_repo.update_profile.return_value = updated

        result = await use_case.execute(user.id, UpdateProfileInput(first_name="Aleksei", last_name="Petrov"))
        assert result.first_name == "Aleksei"
        assert result.last_name == "Petrov"


class TestUpdateProfileNotFound:
    async def test_raises_when_user_not_found(self, use_case, user_repo):
        user_repo.update_profile.return_value = None

        with pytest.raises(UserNotFoundError):
            await use_case.execute(
                uuid4(), UpdateProfileInput(first_name="X", last_name="Y")
            )
