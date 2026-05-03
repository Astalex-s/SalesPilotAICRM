"""
Юнит-тесты ForgotPasswordUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.application.dtos.auth_dtos import ForgotPasswordInput
from src.application.use_cases.forgot_password import ForgotPasswordUseCase
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole


def _make_user() -> User:
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
def redis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(user_repo, redis) -> ForgotPasswordUseCase:
    return ForgotPasswordUseCase(user_repo=user_repo, redis=redis)


class TestForgotPasswordUserExists:
    async def test_stores_token_in_redis_and_sends_email(self, use_case, user_repo, redis):
        user = _make_user()
        user_repo.find_by_email.return_value = user

        with patch("src.application.use_cases.forgot_password.send_password_reset_email") as mock_send:
            mock_send.return_value = None
            await use_case.execute(ForgotPasswordInput(email="ivan@example.com"))

        redis.set.assert_called_once()
        mock_send.assert_called_once()

    async def test_redis_key_contains_token_and_user_id(self, use_case, user_repo, redis):
        user = _make_user()
        user_repo.find_by_email.return_value = user

        with patch("src.application.use_cases.forgot_password.send_password_reset_email"):
            await use_case.execute(ForgotPasswordInput(email="ivan@example.com"))

        call_args = redis.set.call_args
        key = call_args[0][0]
        value = call_args[0][1]
        assert key.startswith("pwd_reset:")
        assert str(user.id) == value


class TestForgotPasswordUserNotExists:
    async def test_silently_returns_when_email_not_found(self, use_case, user_repo, redis):
        user_repo.find_by_email.return_value = None

        # Should not raise, should not call redis or send email
        await use_case.execute(ForgotPasswordInput(email="nobody@example.com"))
        redis.set.assert_not_called()
