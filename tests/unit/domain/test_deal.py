"""
Юнит-тесты доменной сущности Deal.
Проверяют: создание, смену этапов, жизненный цикл, управление суммой.
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.deal import Deal
from src.domain.exceptions import DealAlreadyClosedError, InvalidStageForPipelineError
from src.domain.value_objects.enums import DealStatus
from src.domain.value_objects.money import Money


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def pipeline_id():
    return uuid4()


@pytest.fixture
def stage_id():
    return uuid4()


@pytest.fixture
def open_deal(pipeline_id, stage_id):
    return Deal.create(
        title="Enterprise SaaS Upsell",
        owner_id=uuid4(),
        stage_id=stage_id,
        pipeline_id=pipeline_id,
        value=Money(Decimal("15000"), "USD"),
        contact_name="Jane Smith",
        company="Acme Corp",
    )


# ── Создание ───────────────────────────────────────────────────────────────────

class TestDealCreation:
    def test_deal_created_as_open(self, open_deal: Deal) -> None:
        assert open_deal.status == DealStatus.OPEN
        assert open_deal.is_open

    def test_deal_id_generated(self, open_deal: Deal) -> None:
        assert open_deal.id is not None

    def test_deal_title_stripped(self, pipeline_id, stage_id) -> None:
        deal = Deal.create(
            title="  Padded Title  ",
            owner_id=uuid4(),
            stage_id=stage_id,
            pipeline_id=pipeline_id,
            value=Money.zero(),
        )
        assert deal.title == "Padded Title"

    def test_empty_title_raises(self, pipeline_id, stage_id) -> None:
        with pytest.raises(ValueError):
            Deal.create(
                title="",
                owner_id=uuid4(),
                stage_id=stage_id,
                pipeline_id=pipeline_id,
                value=Money.zero(),
            )


# ── Смена этапа ────────────────────────────────────────────────────────────────

class TestDealStageMovement:
    def test_move_to_stage_same_pipeline(self, open_deal: Deal, pipeline_id) -> None:
        new_stage_id = uuid4()
        open_deal.move_to_stage(new_stage_id, pipeline_id)
        assert open_deal.stage_id == new_stage_id

    def test_move_to_different_pipeline_raises(self, open_deal: Deal) -> None:
        with pytest.raises(InvalidStageForPipelineError):
            open_deal.move_to_stage(uuid4(), uuid4())

    def test_closed_deal_cannot_move_stage(self, open_deal: Deal, pipeline_id) -> None:
        open_deal.win()
        with pytest.raises(DealAlreadyClosedError):
            open_deal.move_to_stage(uuid4(), pipeline_id)


# ── Жизненный цикл ─────────────────────────────────────────────────────────────

class TestDealLifecycle:
    def test_win_sets_status_and_closed_at(self, open_deal: Deal) -> None:
        open_deal.win()
        assert open_deal.status == DealStatus.WON
        assert open_deal.closed_at is not None
        assert not open_deal.is_open

    def test_lose_sets_status_and_closed_at(self, open_deal: Deal) -> None:
        open_deal.lose()
        assert open_deal.status == DealStatus.LOST
        assert open_deal.closed_at is not None

    def test_double_win_raises(self, open_deal: Deal) -> None:
        open_deal.win()
        with pytest.raises(DealAlreadyClosedError):
            open_deal.win()

    def test_double_lose_raises(self, open_deal: Deal) -> None:
        open_deal.lose()
        with pytest.raises(DealAlreadyClosedError):
            open_deal.lose()

    def test_reopen_lost_deal(self, open_deal: Deal) -> None:
        open_deal.lose()
        open_deal.reopen()
        assert open_deal.is_open
        assert open_deal.closed_at is None

    def test_cannot_reopen_won_deal(self, open_deal: Deal) -> None:
        open_deal.win()
        with pytest.raises(ValueError):
            open_deal.reopen()

    def test_cannot_reopen_already_open_deal(self, open_deal: Deal) -> None:
        with pytest.raises(ValueError):
            open_deal.reopen()


# ── Управление суммой ──────────────────────────────────────────────────────────

class TestDealValue:
    def test_update_value_on_open_deal(self, open_deal: Deal) -> None:
        new_value = Money(Decimal("20000"), "USD")
        open_deal.update_value(new_value)
        assert open_deal.value.amount == Decimal("20000")

    def test_update_value_on_closed_deal_raises(self, open_deal: Deal) -> None:
        open_deal.win()
        with pytest.raises(DealAlreadyClosedError):
            open_deal.update_value(Money(Decimal("1"), "USD"))


# ── DealAttachment domain validators ──────────────────────────────────────────

class TestDealAttachmentValidators:
    def test_empty_filename_raises(self) -> None:
        from src.domain.entities.deal_attachment import DealAttachment
        with pytest.raises(ValueError, match="Имя файла не может быть пустым"):
            DealAttachment(
                id=uuid4(), deal_id=uuid4(), filename="   ",
                storage_path="/tmp/f", content_type="application/pdf",
                size_bytes=100, uploaded_by_id=uuid4(),
            )

    def test_negative_size_raises(self) -> None:
        from src.domain.entities.deal_attachment import DealAttachment
        with pytest.raises(ValueError, match="Размер файла не может быть отрицательным"):
            DealAttachment(
                id=uuid4(), deal_id=uuid4(), filename="file.pdf",
                storage_path="/tmp/f", content_type="application/pdf",
                size_bytes=-1, uploaded_by_id=uuid4(),
            )
