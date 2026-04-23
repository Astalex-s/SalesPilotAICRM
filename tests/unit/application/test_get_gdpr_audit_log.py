"""
Юнит-тесты GetGdprAuditLogUseCase.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.get_gdpr_audit_log import GetGdprAuditLogUseCase
from src.domain.entities.gdpr_audit_entry import GdprAuditEntry
from src.domain.value_objects.enums import GdprEventType


@pytest.fixture
def gdpr_audit_repo():
    return AsyncMock()


@pytest.fixture
def use_case(gdpr_audit_repo):
    return GetGdprAuditLogUseCase(gdpr_audit_repo)


class TestGetGdprAuditLogUseCase:
    async def test_empty_log_returns_zero_total(self, use_case, gdpr_audit_repo) -> None:
        gdpr_audit_repo.find_all.return_value = []

        result = await use_case.execute()

        assert result.total == 0
        assert result.entries == []

    async def test_returns_all_entries(self, use_case, gdpr_audit_repo) -> None:
        entries = [
            GdprAuditEntry.create(GdprEventType.USER_DATA_DELETED, "user", uuid4(), "User 1 deleted"),
            GdprAuditEntry.create(GdprEventType.LEAD_ANONYMIZED, "lead", uuid4(), "Lead 1 anon"),
        ]
        gdpr_audit_repo.find_all.return_value = entries

        result = await use_case.execute()

        assert result.total == 2
        assert len(result.entries) == 2

    async def test_pagination_params_forwarded(self, use_case, gdpr_audit_repo) -> None:
        gdpr_audit_repo.find_all.return_value = []

        await use_case.execute(limit=50, offset=100)

        gdpr_audit_repo.find_all.assert_called_once_with(limit=50, offset=100)

    async def test_output_dto_fields_mapped(self, use_case, gdpr_audit_repo) -> None:
        target_id = uuid4()
        performer_id = uuid4()
        entry = GdprAuditEntry.create(
            GdprEventType.LEAD_ANONYMIZED, "lead", target_id, "summary text", performer_id
        )
        gdpr_audit_repo.find_all.return_value = [entry]

        result = await use_case.execute()

        dto = result.entries[0]
        assert dto.id == entry.id
        assert dto.event_type == GdprEventType.LEAD_ANONYMIZED
        assert dto.target_type == "lead"
        assert dto.target_id == target_id
        assert dto.summary == "summary text"
        assert dto.performed_by_id == performer_id

    async def test_default_pagination(self, use_case, gdpr_audit_repo) -> None:
        gdpr_audit_repo.find_all.return_value = []

        result = await use_case.execute()

        assert result.limit == 100
        assert result.offset == 0
