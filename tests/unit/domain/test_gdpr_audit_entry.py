"""
Юнит-тесты доменной сущности GdprAuditEntry.
Проверяют: создание, иммутабельность (frozen=True), поля.
"""
import pytest
from uuid import uuid4
from datetime import timezone

from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.value_objects.enums import GdprEventType


class TestGdprAuditEntryCreation:
    def test_create_generates_id(self) -> None:
        entry = GdprAuditEntry.create(
            event_type=GdprEventType.USER_DATA_DELETED,
            target_type="user",
            target_id=uuid4(),
            summary="User deleted",
        )
        assert entry.id is not None

    def test_create_sets_fields(self) -> None:
        target_id = uuid4()
        performer_id = uuid4()
        entry = GdprAuditEntry.create(
            event_type=GdprEventType.LEAD_ANONYMIZED,
            target_type="lead",
            target_id=target_id,
            summary="Lead anonymized",
            performed_by_id=performer_id,
        )
        assert entry.event_type == GdprEventType.LEAD_ANONYMIZED
        assert entry.target_type == "lead"
        assert entry.target_id == target_id
        assert entry.summary == "Lead anonymized"
        assert entry.performed_by_id == performer_id

    def test_performed_at_is_utc(self) -> None:
        entry = GdprAuditEntry.create(
            event_type=GdprEventType.USER_DATA_DELETED,
            target_type="user",
            target_id=uuid4(),
            summary="Test",
        )
        assert entry.performed_at.tzinfo == timezone.utc

    def test_performed_by_id_defaults_to_none(self) -> None:
        entry = GdprAuditEntry.create(
            event_type=GdprEventType.USER_DATA_DELETED,
            target_type="user",
            target_id=uuid4(),
            summary="System action",
        )
        assert entry.performed_by_id is None

    def test_frozen_immutable(self) -> None:
        entry = GdprAuditEntry.create(
            event_type=GdprEventType.USER_DATA_DELETED,
            target_type="user",
            target_id=uuid4(),
            summary="Test",
        )
        with pytest.raises(Exception):
            entry.summary = "changed"  # type: ignore[misc]

    def test_each_create_has_unique_id(self) -> None:
        target_id = uuid4()
        e1 = GdprAuditEntry.create(GdprEventType.USER_DATA_DELETED, "user", target_id, "A")
        e2 = GdprAuditEntry.create(GdprEventType.USER_DATA_DELETED, "user", target_id, "B")
        assert e1.id != e2.id
