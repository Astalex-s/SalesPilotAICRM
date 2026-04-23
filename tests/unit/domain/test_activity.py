"""
Юнит-тесты доменной сущности Activity.
Проверяют: создание, фабрики, инварианты (append-only, пустой body).
"""
import pytest
from uuid import uuid4

from src.domain.entities.activity import Activity
from src.domain.value_objects.enums import ActivityType


@pytest.fixture
def entity_id():
    return uuid4()


@pytest.fixture
def performer_id():
    return uuid4()


# ── Создание ───────────────────────────────────────────────────────────────────

class TestActivityCreation:
    def test_create_generates_id(self, entity_id, performer_id) -> None:
        act = Activity.create("lead", entity_id, ActivityType.NOTE, performer_id, "Note body")
        assert act.id is not None

    def test_create_sets_fields(self, entity_id, performer_id) -> None:
        act = Activity.create("deal", entity_id, ActivityType.STAGE_CHANGE, performer_id, "Stage X → Y")
        assert act.entity_type == "deal"
        assert act.entity_id == entity_id
        assert act.activity_type == ActivityType.STAGE_CHANGE
        assert act.performed_by_id == performer_id
        assert act.body == "Stage X → Y"
        assert act.occurred_at is not None

    def test_empty_body_raises(self, entity_id, performer_id) -> None:
        with pytest.raises(ValueError):
            Activity.create("lead", entity_id, ActivityType.NOTE, performer_id, "   ")

    def test_frozen_immutable(self, entity_id, performer_id) -> None:
        act = Activity.create("lead", entity_id, ActivityType.NOTE, performer_id, "Test")
        with pytest.raises(Exception):
            act.body = "changed"  # type: ignore[misc]


# ── Фабрики ────────────────────────────────────────────────────────────────────

class TestActivityFactories:
    def test_log_note(self, entity_id, performer_id) -> None:
        act = Activity.log_note("lead", entity_id, performer_id, "Important note")
        assert act.activity_type == ActivityType.NOTE
        assert act.body == "Important note"
        assert act.entity_type == "lead"

    def test_log_status_change(self, entity_id, performer_id) -> None:
        act = Activity.log_status_change("lead", entity_id, performer_id, "new", "contacted")
        assert act.activity_type == ActivityType.STATUS_CHANGE
        assert "new" in act.body
        assert "contacted" in act.body

    def test_log_stage_change(self, performer_id) -> None:
        deal_id = uuid4()
        act = Activity.log_stage_change(deal_id, performer_id, "Prospect", "Qualified")
        assert act.activity_type == ActivityType.STAGE_CHANGE
        assert act.entity_type == "deal"
        assert act.entity_id == deal_id
        assert "Prospect" in act.body
        assert "Qualified" in act.body

    def test_log_lead_conversion(self, entity_id, performer_id) -> None:
        deal_id = uuid4()
        act = Activity.log_lead_conversion(
            lead_id=entity_id,
            deal_id=deal_id,
            performed_by_id=performer_id,
            lead_name="Alice",
            deal_title="Big Deal",
        )
        assert act.activity_type == ActivityType.LEAD_CONVERTED
        assert act.entity_type == "lead"
        assert "Alice" in act.body
        assert "Big Deal" in act.body
