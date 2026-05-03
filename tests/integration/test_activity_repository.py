"""
Интеграционные тесты SqlActivityRepository (SQLite in-memory).
"""
from __future__ import annotations

import pytest
from uuid import uuid4

from src.domain.entities.activity import Activity
from src.domain.value_objects.enums import ActivityType
from src.infrastructure.database.repositories.activity_repository import SqlActivityRepository


def _make_activity(entity_type: str = "lead", entity_id=None, performed_by_id=None) -> Activity:
    return Activity.log_note(
        entity_type=entity_type,
        entity_id=entity_id or uuid4(),
        performed_by_id=performed_by_id or uuid4(),
        body="Test note",
    )


@pytest.mark.asyncio
async def test_save_and_get_by_id(db_session):
    repo = SqlActivityRepository(db_session)
    activity = _make_activity()

    saved = await repo.save(activity)
    assert saved.id == activity.id

    found = await repo.get_by_id(activity.id)
    assert found is not None
    assert found.id == activity.id


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(db_session):
    repo = SqlActivityRepository(db_session)
    result = await repo.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_delete_raises_not_implemented(db_session):
    repo = SqlActivityRepository(db_session)
    with pytest.raises(NotImplementedError):
        await repo.delete(uuid4())


@pytest.mark.asyncio
async def test_find_by_entity(db_session):
    repo = SqlActivityRepository(db_session)
    entity_id = uuid4()
    a1 = _make_activity(entity_type="lead", entity_id=entity_id)
    a2 = _make_activity(entity_type="lead", entity_id=entity_id)
    other = _make_activity(entity_type="deal")
    await repo.save(a1)
    await repo.save(a2)
    await repo.save(other)

    results = await repo.find_by_entity("lead", entity_id)
    ids = [r.id for r in results]
    assert a1.id in ids
    assert a2.id in ids
    assert other.id not in ids


@pytest.mark.asyncio
async def test_find_by_entity_returns_empty_for_unknown(db_session):
    repo = SqlActivityRepository(db_session)
    result = await repo.find_by_entity("lead", uuid4())
    assert result == []


@pytest.mark.asyncio
async def test_find_by_type(db_session):
    repo = SqlActivityRepository(db_session)
    note = _make_activity()
    status_change = Activity.log_status_change(
        entity_type="deal",
        entity_id=uuid4(),
        performed_by_id=uuid4(),
        from_status="open",
        to_status="won",
    )
    await repo.save(note)
    await repo.save(status_change)

    notes = await repo.find_by_type(ActivityType.NOTE)
    assert any(a.id == note.id for a in notes)
    assert all(a.activity_type == ActivityType.NOTE for a in notes)


@pytest.mark.asyncio
async def test_find_by_performer(db_session):
    repo = SqlActivityRepository(db_session)
    performer = uuid4()
    a = _make_activity(performed_by_id=performer)
    other = _make_activity()
    await repo.save(a)
    await repo.save(other)

    results = await repo.find_by_performer(performer)
    assert any(r.id == a.id for r in results)
    assert all(r.performed_by_id == performer for r in results)


@pytest.mark.asyncio
async def test_gdpr_erase_by_entity(db_session):
    repo = SqlActivityRepository(db_session)
    entity_id = uuid4()
    a1 = _make_activity(entity_id=entity_id)
    a2 = _make_activity(entity_id=entity_id)
    await repo.save(a1)
    await repo.save(a2)

    count = await repo.gdpr_erase_by_entity(entity_id)
    assert count == 2

    results = await repo.find_by_entity("lead", entity_id)
    assert results == []


@pytest.mark.asyncio
async def test_gdpr_erase_by_performer(db_session):
    repo = SqlActivityRepository(db_session)
    performer = uuid4()
    a1 = _make_activity(performed_by_id=performer)
    a2 = _make_activity(performed_by_id=performer)
    await repo.save(a1)
    await repo.save(a2)

    count = await repo.gdpr_erase_by_performer(performer)
    assert count == 2

    results = await repo.find_by_performer(performer)
    assert results == []
