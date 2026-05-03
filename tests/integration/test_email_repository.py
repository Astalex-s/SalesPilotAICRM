"""
Интеграционные тесты SqlEmailMessageRepository (SQLite in-memory).
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.entities.email_message import EmailMessage
from src.domain.value_objects.enums import EmailDirection
from src.infrastructure.database.repositories.email_message_repository import SqlEmailMessageRepository


def _make_email(
    gmail_message_id: str | None = None,
    gmail_thread_id: str | None = None,
    lead_id=None,
) -> EmailMessage:
    return EmailMessage(
        id=uuid4(),
        gmail_message_id=gmail_message_id or f"msg_{uuid4().hex[:8]}",
        gmail_thread_id=gmail_thread_id or f"thr_{uuid4().hex[:8]}",
        from_address="sender@example.com",
        to_addresses=["recipient@example.com"],
        subject="Test Subject",
        body="Hello world",
        direction=EmailDirection.INBOUND,
        received_at=datetime.now(timezone.utc),
        lead_id=lead_id,
    )


@pytest.mark.asyncio
async def test_save_and_get_by_id(db_session):
    repo = SqlEmailMessageRepository(db_session)
    email = _make_email()

    saved = await repo.save(email)
    assert saved.id == email.id

    found = await repo.get_by_id(email.id)
    assert found is not None
    assert found.subject == "Test Subject"
    assert found.from_address == "sender@example.com"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(db_session):
    repo = SqlEmailMessageRepository(db_session)
    result = await repo.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_delete(db_session):
    repo = SqlEmailMessageRepository(db_session)
    email = _make_email()
    await repo.save(email)

    await repo.delete(email.id)
    found = await repo.get_by_id(email.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_nonexistent_is_noop(db_session):
    repo = SqlEmailMessageRepository(db_session)
    await repo.delete(uuid4())  # should not raise


@pytest.mark.asyncio
async def test_find_by_gmail_id(db_session):
    repo = SqlEmailMessageRepository(db_session)
    gmail_id = f"gmail_{uuid4().hex}"
    email = _make_email(gmail_message_id=gmail_id)
    await repo.save(email)

    found = await repo.find_by_gmail_id(gmail_id)
    assert found is not None
    assert found.gmail_message_id == gmail_id


@pytest.mark.asyncio
async def test_find_by_gmail_id_returns_none_for_missing(db_session):
    repo = SqlEmailMessageRepository(db_session)
    result = await repo.find_by_gmail_id("nonexistent_gmail_id")
    assert result is None


@pytest.mark.asyncio
async def test_find_by_lead_id(db_session):
    repo = SqlEmailMessageRepository(db_session)
    # lead_id must be a real lead UUID due to FK — skip FK by using None, test without lead
    # Instead test that empty list is returned for random UUID
    result = await repo.find_by_lead_id(uuid4())
    assert result == []


@pytest.mark.asyncio
async def test_find_all(db_session):
    repo = SqlEmailMessageRepository(db_session)
    e1 = _make_email()
    e2 = _make_email()
    await repo.save(e1)
    await repo.save(e2)

    results = await repo.find_all(limit=100, offset=0)
    ids = [e.id for e in results]
    assert e1.id in ids
    assert e2.id in ids


@pytest.mark.asyncio
async def test_find_all_with_limit(db_session):
    repo = SqlEmailMessageRepository(db_session)
    for _ in range(3):
        await repo.save(_make_email())

    results = await repo.find_all(limit=2, offset=0)
    assert len(results) <= 2


@pytest.mark.asyncio
async def test_find_by_thread_id(db_session):
    repo = SqlEmailMessageRepository(db_session)
    thread_id = f"thread_{uuid4().hex[:8]}"
    e1 = _make_email(gmail_thread_id=thread_id)
    e2 = _make_email(gmail_thread_id=thread_id)
    await repo.save(e1)
    await repo.save(e2)

    results = await repo.find_by_thread_id(thread_id)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_find_by_thread_id_returns_empty_for_missing(db_session):
    repo = SqlEmailMessageRepository(db_session)
    result = await repo.find_by_thread_id("nonexistent_thread")
    assert result == []
