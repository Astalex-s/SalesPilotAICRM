"""
BulkImportLeadsUseCase — массовый импорт лидов из CSV.

Итерирует по строкам, переиспользует CreateLeadUseCase для каждой.
Дубли (уже существующий e-mail) — пропускаются, не являются ошибкой.
"""
from __future__ import annotations

from src.application.dtos.lead_dtos import (
    BulkImportInput,
    BulkImportResult,
    CreateLeadInput,
    LeadOutput,
)
from src.application.exceptions import LeadEmailAlreadyExistsError
from src.application.use_cases.create_lead import CreateLeadUseCase
from src.domain.repositories.lead_repository import ILeadRepository


class BulkImportLeadsUseCase:
    """Массовый импорт лидов с обработкой дублей и ошибок валидации."""

    def __init__(self, lead_repo: ILeadRepository) -> None:
        self._lead_repo = lead_repo
        self._create_uc = CreateLeadUseCase(lead_repo)

    async def execute(self, data: BulkImportInput) -> BulkImportResult:
        """Создаёт лидов построчно; собирает статистику created/skipped/errors."""
        created = 0
        skipped = 0
        errors: list[str] = []
        leads: list[LeadOutput] = []

        for i, row in enumerate(data.rows, start=1):
            try:
                lead_input = CreateLeadInput(
                    first_name=row.first_name,
                    last_name=row.last_name,
                    email=row.email,
                    phone=row.phone,
                    company=row.company,
                    source=row.source,
                    owner_id=data.owner_id,
                )
                lead = await self._create_uc.execute(lead_input)
                leads.append(lead)
                created += 1
            except LeadEmailAlreadyExistsError:
                skipped += 1
            except Exception as exc:
                errors.append(f"Row {i} ({row.email}): {exc}")

        return BulkImportResult(
            created=created,
            skipped=skipped,
            error_count=len(errors),
            errors=errors,
            leads=leads,
        )
