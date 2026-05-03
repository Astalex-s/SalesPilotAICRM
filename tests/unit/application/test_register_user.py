"""
Юнит-тесты RegisterUserUseCase.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.auth_dtos import RegisterInput
from src.application.exceptions import UserAlreadyExistsError
from src.application.use_cases.register_user import RegisterUserUseCase
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole


def _make_user() -> User:
    return User.create(
        first_name="Alice",
        last_name="Brown",
        email=Email("alice@example.com"),
        role=UserRole.SALES_REP,
    )


@pytest.fixture
def user_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.find_by_email.return_value = None
    repo.save_with_hash.side_effect = lambda user, _hash: user
    return repo


@pytest.fixture
def use_case(user_repo) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo=user_repo)


class TestRegisterSuccess:
    async def test_returns_user_output(self, use_case, user_repo):
        result = await use_case.execute(
            RegisterInput(
                first_name="Alice",
                last_name="Brown",
                email="alice@example.com",
                password="secret123",
            )
        )
        assert result.first_name == "Alice"
        assert result.email == "alice@example.com"
        assert result.role == UserRole.SALES_REP

    async def test_calls_save_with_hash(self, use_case, user_repo):
        await use_case.execute(
            RegisterInput(
                first_name="Bob",
                last_name="Smith",
                email="bob@example.com",
                password="pass123",
            )
        )
        user_repo.save_with_hash.assert_called_once()


class TestRegisterDuplicate:
    async def test_raises_when_email_exists(self, use_case, user_repo):
        user_repo.find_by_email.return_value = _make_user()

        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(
                RegisterInput(
                    first_name="Alice",
                    last_name="Brown",
                    email="alice@example.com",
                    password="secret123",
                )
            )
