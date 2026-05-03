"""
Интеграционные тесты SqlGdprAuditRepository (SQLite in-memory).
"""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.value_objects.enums import GdprEventType
from src.infrastructure.database.repositories.gdpr_audit_repository import SqlGdprAuditRepository


def _make_entry(
    event_type: GdprEventType = GdprEventType.USER_DATA_DELETED,
    target_type: str = "lead",
    target_id=None,
) -> GdprAuditEntry:
    return GdprAuditEntry.create(
        event_type=event_type,
        target_type=target_type,
        target_id=target_id or uuid4(),
        summary="Test audit event",
        performed_by_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_save_and_get_by_id(db_session):
    repo = SqlGdprAuditRepository(db_session)
    entry = _make_entry()

    saved = await repo.save(entry)
    assert saved.id == entry.id

    found = await repo.get_by_id(entry.id)
    assert found is not None
    assert found.summary == "Test audit event"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(db_session):
    repo = SqlGdprAuditRepository(db_session)
    result = await repo.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_delete_raises_not_implemented(db_session):
    repo = SqlGdprAuditRepository(db_session)
    with pytest.raises(NotImplementedError):
        await repo.delete(uuid4())


@pytest.mark.asyncio
async def test_find_all(db_session):
    repo = SqlGdprAuditRepository(db_session)
    e1 = _make_entry()
    e2 = _make_entry()
    await repo.save(e1)
    await repo.save(e2)

    results = await repo.find_all(limit=100, offset=0)
    ids = [r.id for r in results]
    assert e1.id in ids
    assert e2.id in ids


@pytest.mark.asyncio
async def test_find_all_with_pagination(db_session):
    repo = SqlGdprAuditRepository(db_session)
    for _ in range(3):
        await repo.save(_make_entry())

    page1 = await repo.find_all(limit=2, offset=0)
    page2 = await repo.find_all(limit=2, offset=2)
    assert len(page1) <= 2
    # pages should not overlap
    ids1 = {r.id for r in page1}
    ids2 = {r.id for r in page2}
    assert ids1.isdisjoint(ids2)


@pytest.mark.asyncio
async def test_find_by_event_type(db_session):
    repo = SqlGdprAuditRepository(db_session)
    deleted_entry = _make_entry(event_type=GdprEventType.USER_DATA_DELETED)
    anonymized_entry = _make_entry(event_type=GdprEventType.LEAD_ANONYMIZED)
    await repo.save(deleted_entry)
    await repo.save(anonymized_entry)

    results = await repo.find_by_event_type(GdprEventType.USER_DATA_DELETED)
    ids = [r.id for r in results]
    assert deleted_entry.id in ids
    assert anonymized_entry.id not in ids


@pytest.mark.asyncio
async def test_find_by_target(db_session):
    repo = SqlGdprAuditRepository(db_session)
    target_id = uuid4()
    entry = _make_entry(target_type="lead", target_id=target_id)
    other = _make_entry(target_type="user")
    await repo.save(entry)
    await repo.save(other)

    results = await repo.find_by_target("lead", target_id)
    assert len(results) == 1
    assert results[0].id == entry.id


@pytest.mark.asyncio
async def test_find_by_target_empty_for_unknown(db_session):
    repo = SqlGdprAuditRepository(db_session)
    results = await repo.find_by_target("lead", uuid4())
    assert results == []


@pytest.mark.asyncio
async def test_find_since(db_session):
    repo = SqlGdprAuditRepository(db_session)
    entry = _make_entry()
    await repo.save(entry)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    results = await repo.find_since(cutoff)
    ids = [r.id for r in results]
    assert entry.id in ids


@pytest.mark.asyncio
async def test_find_since_excludes_old_entries(db_session):
    repo = SqlGdprAuditRepository(db_session)
    future_cutoff = datetime.now(timezone.utc) + timedelta(hours=1)

    results = await repo.find_since(future_cutoff)
    assert results == []
