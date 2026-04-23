"""
Интеграционные тесты SqlDealRepository (SQLite in-memory).
"""
import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone

from src.domain.entities.deal import Deal
from src.domain.value_objects.money import Money
from src.infrastructure.database.repositories.deal_repository import SqlDealRepository
from src.infrastructure.database.models.pipeline_model import PipelineModel
from src.infrastructure.database.models.stage_model import StageModel


async def _insert_pipeline_and_stage(session):
    """Создаёт pipeline + stage в БД и возвращает их id."""
    now = datetime.now(timezone.utc)
    pipeline_id = uuid4()
    stage_id = uuid4()

    pipeline = PipelineModel(
        id=pipeline_id,
        name="Test Pipeline",
        owner_id=uuid4(),
        is_active=True,
        created_at=now,
    )
    stage = StageModel(
        id=stage_id,
        pipeline_id=pipeline_id,
        name="Stage 1",
        order=1,
        probability=0.5,
    )
    session.add(pipeline)
    session.add(stage)
    await session.flush()
    return pipeline_id, stage_id


@pytest.mark.asyncio
async def test_deal_save_and_get(db_session):
    pipeline_id, stage_id = await _insert_pipeline_and_stage(db_session)
    repo = SqlDealRepository(db_session)
    owner_id = uuid4()
    deal = Deal.create("Big Deal", owner_id, stage_id, pipeline_id, Money(Decimal("5000")))

    saved = await repo.save(deal)
    assert saved.id == deal.id

    found = await repo.get_by_id(deal.id)
    assert found is not None
    assert found.title == "Big Deal"
    assert found.pipeline_id == pipeline_id
    assert found.stage_id == stage_id
    assert float(found.value.amount) == 5000.0


@pytest.mark.asyncio
async def test_deal_find_by_owner(db_session):
    pipeline_id, stage_id = await _insert_pipeline_and_stage(db_session)
    repo = SqlDealRepository(db_session)
    owner_id = uuid4()
    other_owner = uuid4()

    d1 = Deal.create("D1", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
    d2 = Deal.create("D2", owner_id, stage_id, pipeline_id, Money(Decimal("200")))
    d3 = Deal.create("D3", other_owner, stage_id, pipeline_id, Money(Decimal("300")))

    for deal in [d1, d2, d3]:
        await repo.save(deal)

    results = await repo.find_by_owner(owner_id)
    assert len(results) == 2
    ids = {d.id for d in results}
    assert d1.id in ids
    assert d2.id in ids
    assert d3.id not in ids


@pytest.mark.asyncio
async def test_deal_find_by_pipeline(db_session):
    pipeline_id, stage_id = await _insert_pipeline_and_stage(db_session)
    repo = SqlDealRepository(db_session)
    owner_id = uuid4()

    deal = Deal.create("Pipeline Deal", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
    await repo.save(deal)

    results = await repo.find_by_pipeline(pipeline_id)
    assert len(results) == 1
    assert results[0].id == deal.id

    empty = await repo.find_by_pipeline(uuid4())
    assert empty == []


@pytest.mark.asyncio
async def test_deal_find_by_stage(db_session):
    pipeline_id, stage_id = await _insert_pipeline_and_stage(db_session)
    repo = SqlDealRepository(db_session)
    owner_id = uuid4()

    deal = Deal.create("Stage Deal", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
    await repo.save(deal)

    results = await repo.find_by_stage(stage_id)
    assert len(results) == 1
    assert results[0].id == deal.id


@pytest.mark.asyncio
async def test_deal_delete(db_session):
    pipeline_id, stage_id = await _insert_pipeline_and_stage(db_session)
    repo = SqlDealRepository(db_session)
    owner_id = uuid4()

    deal = Deal.create("To Delete", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
    await repo.save(deal)
    await repo.delete(deal.id)

    found = await repo.get_by_id(deal.id)
    assert found is None


@pytest.mark.asyncio
async def test_deal_get_by_id_not_found(db_session):
    repo = SqlDealRepository(db_session)
    found = await repo.get_by_id(uuid4())
    assert found is None


@pytest.mark.asyncio
async def test_deal_find_all(db_session):
    pipeline_id, stage_id = await _insert_pipeline_and_stage(db_session)
    repo = SqlDealRepository(db_session)
    owner_id = uuid4()

    d1 = Deal.create("D1", owner_id, stage_id, pipeline_id, Money(Decimal("100")))
    d2 = Deal.create("D2", owner_id, stage_id, pipeline_id, Money(Decimal("200")))
    await repo.save(d1)
    await repo.save(d2)

    all_deals = await repo.find_all()
    ids = {d.id for d in all_deals}
    assert d1.id in ids
    assert d2.id in ids
