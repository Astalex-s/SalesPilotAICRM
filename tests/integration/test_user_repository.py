"""
Интеграционные тесты SqlUserRepository (SQLite in-memory).
"""
from __future__ import annotations

import pytest
from uuid import uuid4

from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole
from src.infrastructure.database.repositories.user_repository import SqlUserRepository


def _make_user(email: str | None = None, role: UserRole = UserRole.SALES_REP) -> User:
    return User.create(
        first_name="Ivan",
        last_name="Petrov",
        email=Email(email or f"user_{uuid4().hex[:8]}@test.com"),
        role=role,
    )


async def _save(session, email: str | None = None, role: UserRole = UserRole.SALES_REP) -> User:
    repo = SqlUserRepository(session)
    user = _make_user(email, role)
    return await repo.save_with_hash(user, "hashed_password")


@pytest.mark.asyncio
async def test_save_with_hash_and_find_by_id(db_session):
    saved = await _save(db_session)
    repo = SqlUserRepository(db_session)

    found = await repo.find_by_id(saved.id)
    assert found is not None
    assert found.id == saved.id
    assert str(found.email) == str(saved.email)


@pytest.mark.asyncio
async def test_get_by_id_delegates_to_find_by_id(db_session):
    saved = await _save(db_session)
    repo = SqlUserRepository(db_session)

    via_get = await repo.get_by_id(saved.id)
    assert via_get is not None
    assert via_get.id == saved.id


@pytest.mark.asyncio
async def test_find_by_id_returns_none_for_missing(db_session):
    repo = SqlUserRepository(db_session)
    result = await repo.find_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_find_by_email(db_session):
    email = f"find_by_email_{uuid4().hex[:6]}@test.com"
    await _save(db_session, email=email)
    repo = SqlUserRepository(db_session)

    found = await repo.find_by_email(email)
    assert found is not None
    assert str(found.email) == email


@pytest.mark.asyncio
async def test_find_by_email_returns_none_for_missing(db_session):
    repo = SqlUserRepository(db_session)
    result = await repo.find_by_email("nobody@nowhere.com")
    assert result is None


@pytest.mark.asyncio
async def test_find_by_email_with_hash(db_session):
    email = f"hash_{uuid4().hex[:6]}@test.com"
    await _save(db_session, email=email)
    repo = SqlUserRepository(db_session)

    result = await repo.find_by_email_with_hash(email)
    assert result is not None
    user, pw_hash = result
    assert str(user.email) == email
    assert pw_hash == "hashed_password"


@pytest.mark.asyncio
async def test_find_by_email_with_hash_returns_none_for_missing(db_session):
    repo = SqlUserRepository(db_session)
    result = await repo.find_by_email_with_hash("nobody@example.com")
    assert result is None


@pytest.mark.asyncio
async def test_find_by_id_with_hash(db_session):
    email = f"idhash_{uuid4().hex[:6]}@test.com"
    saved = await _save(db_session, email=email)
    repo = SqlUserRepository(db_session)

    result = await repo.find_by_id_with_hash(saved.id)
    assert result is not None
    user, pw_hash = result
    assert user.id == saved.id
    assert pw_hash == "hashed_password"


@pytest.mark.asyncio
async def test_find_by_id_with_hash_returns_none_for_missing(db_session):
    repo = SqlUserRepository(db_session)
    result = await repo.find_by_id_with_hash(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_find_active(db_session):
    repo = SqlUserRepository(db_session)
    saved = await _save(db_session)

    active = await repo.find_active()
    ids = [u.id for u in active]
    assert saved.id in ids


@pytest.mark.asyncio
async def test_find_all(db_session):
    repo = SqlUserRepository(db_session)
    saved = await _save(db_session)

    all_users = await repo.find_all()
    assert any(u.id == saved.id for u in all_users)


@pytest.mark.asyncio
async def test_update_password_hash(db_session):
    saved = await _save(db_session)
    repo = SqlUserRepository(db_session)

    updated = await repo.update_password_hash(saved.id, "new_hash")
    assert updated is True

    result = await repo.find_by_id_with_hash(saved.id)
    assert result is not None
    _, new_pw = result
    assert new_pw == "new_hash"


@pytest.mark.asyncio
async def test_update_password_hash_returns_false_for_missing(db_session):
    repo = SqlUserRepository(db_session)
    result = await repo.update_password_hash(uuid4(), "hash")
    assert result is False


@pytest.mark.asyncio
async def test_update_profile(db_session):
    saved = await _save(db_session)
    repo = SqlUserRepository(db_session)

    updated = await repo.update_profile(saved.id, "Aleksei", "Ivanov")
    assert updated is not None
    assert updated.first_name == "Aleksei"
    assert updated.last_name == "Ivanov"


@pytest.mark.asyncio
async def test_update_profile_returns_none_for_missing(db_session):
    repo = SqlUserRepository(db_session)
    result = await repo.update_profile(uuid4(), "A", "B")
    assert result is None


@pytest.mark.asyncio
async def test_update_role(db_session):
    saved = await _save(db_session, role=UserRole.SALES_REP)
    repo = SqlUserRepository(db_session)

    updated = await repo.update_role(saved.id, UserRole.MANAGER.value)
    assert updated is not None
    assert updated.role == UserRole.MANAGER


@pytest.mark.asyncio
async def test_update_role_returns_none_for_missing(db_session):
    repo = SqlUserRepository(db_session)
    result = await repo.update_role(uuid4(), UserRole.ADMIN.value)
    assert result is None


@pytest.mark.asyncio
async def test_delete(db_session):
    saved = await _save(db_session)
    repo = SqlUserRepository(db_session)

    await repo.delete(saved.id)
    found = await repo.find_by_id(saved.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_nonexistent_is_noop(db_session):
    repo = SqlUserRepository(db_session)
    await repo.delete(uuid4())  # should not raise


@pytest.mark.asyncio
async def test_save_raises_not_implemented(db_session):
    repo = SqlUserRepository(db_session)
    user = _make_user()
    with pytest.raises(NotImplementedError):
        await repo.save(user)
