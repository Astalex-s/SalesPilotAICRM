"""
CloseDealUseCase — закрытие сделки как выигранной (won) или проигранной (lost).
"""
from __future__ import annotations

from src.application.dtos.deal_dtos import CloseDealInput, DealOutput
from src.application.exceptions import DealNotFoundError
from src.domain.entities.activity import Activity
from src.domain.repositories.activity_repository import IActivityRepository
from src.domain.repositories.deal_repository import IDealRepository


class CloseDealUseCase:
    """Закрывает сделку, переводя её в статус WON или LOST."""

    def __init__(
        self,
        deal_repo: IDealRepository,
        activity_repo: IActivityRepository,
    ) -> None:
        self._deal_repo = deal_repo
        self._activity_repo = activity_repo

    async def execute(self, data: CloseDealInput) -> DealOutput:
        deal = await self._deal_repo.get_by_id(data.deal_id)
        if deal is None:
            raise DealNotFoundError(data.deal_id)

        if data.outcome == "won":
            deal.win()
        else:
            deal.lose()

        performed_by = data.performed_by_id or deal.owner_id
        activity = Activity.log_status_change(
            entity_type="deal",
            entity_id=deal.id,
            performed_by_id=performed_by,
            from_status="open",
            to_status=data.outcome,
        )

        deal = await self._deal_repo.save(deal)
        await self._activity_repo.save(activity)

        return DealOutput.from_entity(deal)
