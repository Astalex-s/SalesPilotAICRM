"""
Юнит-тесты ChangeUserPasswordUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.auth_dtos import ChangePasswordInput
from src.application.exceptions import InvalidCurrentPasswordError, UserNotFoundError
from src.application.use_cases.change_user_password import ChangeUserPasswordUseCase
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole
from src.infrastructure.auth.auth_service import hash_password


def _make_user() -> User:
    return User.create(
        first_name="Test",
        last_name="User",
        email=Email("test@example.com"),
        role=UserRole.MANAGER,
    )


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(user_repo) -> ChangeUserPasswordUseCase:
    return ChangeUserPasswordUseCase(user_repo=user_repo)


class TestChangePasswordSuccess:
    async def test_updates_password_on_valid_current(self, use_case, user_repo):
        user = _make_user()
        current_hash = hash_password("old_password")
        user_repo.find_by_id_with_hash.return_value = (user, current_hash)

        await use_case.execute(
            user.id,
            ChangePasswordInput(current_password="old_password", new_password="new_pass123"),
        )
        user_repo.update_password_hash.assert_called_once()


class TestChangePasswordFailure:
    async def test_raises_when_user_not_found(self, use_case, user_repo):
        user_repo.find_by_id_with_hash.return_value = None

        with pytest.raises(UserNotFoundError):
            await use_case.execute(
                uuid4(),
                ChangePasswordInput(current_password="any", new_password="new123"),
            )

    async def test_raises_on_wrong_current_password(self, use_case, user_repo):
        user = _make_user()
        current_hash = hash_password("correct_password")
        user_repo.find_by_id_with_hash.return_value = (user, current_hash)

        with pytest.raises(InvalidCurrentPasswordError):
            await use_case.execute(
                user.id,
                ChangePasswordInput(current_password="wrong_password", new_password="new123"),
            )
