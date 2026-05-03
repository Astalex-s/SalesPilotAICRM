"""
Юнит-тесты LoginUserUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.application.dtos.auth_dtos import LoginInput
from src.application.exceptions import InvalidCredentialsError
from src.application.use_cases.login_user import LoginUserUseCase
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole
from src.infrastructure.auth.auth_service import hash_password


def _make_user(is_active: bool = True) -> User:
    return User.create(
        first_name="Ivan",
        last_name="Petrov",
        email=Email("ivan@example.com"),
        role=UserRole.MANAGER,
    )


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(user_repo) -> LoginUserUseCase:
    return LoginUserUseCase(user_repo=user_repo)


class TestLoginSuccess:
    async def test_returns_tokens_on_valid_credentials(self, use_case, user_repo):
        user = _make_user()
        pw_hash = hash_password("secret123")
        user_repo.find_by_email_with_hash.return_value = (user, pw_hash)

        result = await use_case.execute(LoginInput(email="ivan@example.com", password="secret123"))
        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"


class TestLoginFailure:
    async def test_raises_when_user_not_found(self, use_case, user_repo):
        user_repo.find_by_email_with_hash.return_value = None
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(LoginInput(email="ghost@example.com", password="any"))

    async def test_raises_when_wrong_password(self, use_case, user_repo):
        user = _make_user()
        pw_hash = hash_password("correct_password")
        user_repo.find_by_email_with_hash.return_value = (user, pw_hash)

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(LoginInput(email="ivan@example.com", password="wrong_password"))

    async def test_raises_when_user_inactive(self, use_case, user_repo):
        user = _make_user()
        user.is_active = False
        pw_hash = hash_password("secret123")
        user_repo.find_by_email_with_hash.return_value = (user, pw_hash)

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(LoginInput(email="ivan@example.com", password="secret123"))
