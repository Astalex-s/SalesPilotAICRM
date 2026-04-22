"""
GetGdprAuditLogUseCase — чтение журнала аудита GDPR с пагинацией.
"""
from __future__ import annotations

from src.application.dtos.gdpr_dtos import GdprAuditEntryOutput, GdprAuditLogOutput
from src.domain.repositories.gdpr_audit_repository import IGdprAuditRepository


class GetGdprAuditLogUseCase:
    """Возвращает страницу журнала аудита GDPR."""

    def __init__(self, gdpr_audit_repo: IGdprAuditRepository) -> None:
        self._gdpr_audit_repo = gdpr_audit_repo

    async def execute(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> GdprAuditLogOutput:
        """Загружает страницу журнала; total — количество записей на странице."""
        entries = await self._gdpr_audit_repo.find_all(limit=limit, offset=offset)
        return GdprAuditLogOutput(
            entries=[
                GdprAuditEntryOutput(
                    id=e.id,
                    event_type=e.event_type,
                    target_type=e.target_type,
                    target_id=e.target_id,
                    summary=e.summary,
                    performed_at=e.performed_at,
                    performed_by_id=e.performed_by_id,
                )
                for e in entries
            ],
            total=len(entries),
            limit=limit,
            offset=offset,
        )
