"""
Юнит-тесты ResetPasswordUseCase.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.auth_dtos import ResetPasswordInput
from src.application.use_cases.reset_password import ResetPasswordUseCase


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def redis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(user_repo, redis) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(user_repo=user_repo, redis=redis)


class TestResetPasswordSuccess:
    async def test_updates_password_and_deletes_token(self, use_case, user_repo, redis):
        user_id = uuid4()
        redis.get.return_value = str(user_id)
        user_repo.update_password_hash.return_value = True

        await use_case.execute(ResetPasswordInput(token="valid_token", new_password="newpass123"))

        user_repo.update_password_hash.assert_called_once()
        redis.delete.assert_called_once()


class TestResetPasswordInvalidToken:
    async def test_raises_400_when_token_not_in_redis(self, use_case, redis):
        redis.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await use_case.execute(ResetPasswordInput(token="bad_token", new_password="newpass123"))

        assert exc_info.value.status_code == 400


class TestResetPasswordUserNotFound:
    async def test_raises_400_when_user_not_found(self, use_case, user_repo, redis):
        redis.get.return_value = str(uuid4())
        user_repo.update_password_hash.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await use_case.execute(ResetPasswordInput(token="valid_token", new_password="newpass123"))

        assert exc_info.value.status_code == 400
        redis.delete.assert_not_called()
