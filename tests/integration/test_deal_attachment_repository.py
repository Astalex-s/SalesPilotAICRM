"""
Интеграционные тесты SqlDealAttachmentRepository (SQLite in-memory).
Создаёт pipeline + stage + deal как FK-зависимости перед тестом вложений.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.deal import Deal
from src.domain.entities.deal_attachment import DealAttachment
from src.domain.value_objects.money import Money
from src.infrastructure.database.models.pipeline_model import PipelineModel
from src.infrastructure.database.models.stage_model import StageModel
from src.infrastructure.database.repositories.deal_attachment_repository import SqlDealAttachmentRepository
from src.infrastructure.database.repositories.deal_repository import SqlDealRepository


async def _create_deal(session) -> Deal:
    now = datetime.now(timezone.utc)
    pipeline_id = uuid4()
    stage_id = uuid4()
    session.add(PipelineModel(id=pipeline_id, name="P", owner_id=uuid4(), is_active=True, created_at=now))
    session.add(StageModel(id=stage_id, pipeline_id=pipeline_id, name="S", order=0, probability=0.5))
    await session.flush()

    deal = Deal.create("Deal", uuid4(), stage_id, pipeline_id, Money(Decimal("1000")))
    repo = SqlDealRepository(session)
    return await repo.save(deal)


def _make_attachment(deal_id) -> DealAttachment:
    return DealAttachment.create(
        deal_id=deal_id,
        filename="test.pdf",
        storage_path="/app/uploads/deals/test.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        uploaded_by_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_save_and_get_by_id(db_session):
    deal = await _create_deal(db_session)
    repo = SqlDealAttachmentRepository(db_session)
    att = _make_attachment(deal.id)

    saved = await repo.save(att)
    assert saved.id == att.id

    found = await repo.get_by_id(att.id)
    assert found is not None
    assert found.filename == "test.pdf"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(db_session):
    repo = SqlDealAttachmentRepository(db_session)
    result = await repo.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_delete(db_session):
    deal = await _create_deal(db_session)
    repo = SqlDealAttachmentRepository(db_session)
    att = _make_attachment(deal.id)
    await repo.save(att)

    await repo.delete(att.id)
    found = await repo.get_by_id(att.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_nonexistent_is_noop(db_session):
    repo = SqlDealAttachmentRepository(db_session)
    await repo.delete(uuid4())  # should not raise


@pytest.mark.asyncio
async def test_find_by_deal(db_session):
    deal = await _create_deal(db_session)
    repo = SqlDealAttachmentRepository(db_session)
    a1 = _make_attachment(deal.id)
    a2 = _make_attachment(deal.id)
    await repo.save(a1)
    await repo.save(a2)

    results = await repo.find_by_deal(deal.id)
    ids = [r.id for r in results]
    assert a1.id in ids
    assert a2.id in ids


@pytest.mark.asyncio
async def test_find_by_deal_returns_empty_for_unknown(db_session):
    repo = SqlDealAttachmentRepository(db_session)
    result = await repo.find_by_deal(uuid4())
    assert result == []
