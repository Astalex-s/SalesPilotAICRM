"""
GetManagersReportUseCase — детальный отчёт по менеджерам.

Для каждого активного пользователя агрегирует:
  - лиды (total, converted, conversion_rate)
  - сделки (open, won, lost, win_rate)
  - финансы (pipeline_value, won_revenue, avg_deal_size)
  - риски (overdue_deals)
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

from src.application.dtos.analytics_dtos import ManagerReportEntry, ManagersReportOutput
from src.domain.repositories.deal_repository import IDealRepository
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.value_objects.enums import DealStatus, LeadStatus


class GetManagersReportUseCase:
    """Агрегирует детальную аналитику по каждому менеджеру."""

    def __init__(
        self,
        user_repo: IUserRepository,
        lead_repo: ILeadRepository,
        deal_repo: IDealRepository,
    ) -> None:
        self._user_repo = user_repo
        self._lead_repo = lead_repo
        self._deal_repo = deal_repo

    async def execute(self) -> ManagersReportOutput:
        """Загружает пользователей, лиды, сделки и формирует отчёт."""
        now = datetime.now(timezone.utc)

        users = await self._user_repo.find_all()
        leads = await self._lead_repo.find_all()
        deals = await self._deal_repo.find_all()
        overdue = await self._deal_repo.find_overdue(now)

        # Индексируем по owner_id для O(n) группировки
        leads_by_owner: dict[UUID, list] = defaultdict(list)
        for lead in leads:
            leads_by_owner[lead.owner_id].append(lead)

        deals_by_owner: dict[UUID, list] = defaultdict(list)
        for deal in deals:
            deals_by_owner[deal.owner_id].append(deal)

        overdue_by_owner: dict[UUID, int] = defaultdict(int)
        for deal in overdue:
            overdue_by_owner[deal.owner_id] += 1

        entries: list[ManagerReportEntry] = []
        for user in users:
            u_leads = leads_by_owner.get(user.id, [])
            u_deals = deals_by_owner.get(user.id, [])

            # Лиды
            converted = sum(1 for l in u_leads if l.status == LeadStatus.CONVERTED)
            conversion_rate = round(converted / len(u_leads) * 100.0, 1) if u_leads else 0.0

            # Сделки
            open_deals = [d for d in u_deals if d.status == DealStatus.OPEN]
            won_deals  = [d for d in u_deals if d.status == DealStatus.WON]
            lost_deals = [d for d in u_deals if d.status == DealStatus.LOST]

            decided = len(won_deals) + len(lost_deals)
            win_rate = round(len(won_deals) / decided * 100.0, 1) if decided > 0 else 0.0

            # Финансы
            pipeline_value = sum(float(d.value.amount) for d in open_deals)
            won_revenue    = sum(float(d.value.amount) for d in won_deals)
            avg_deal_size  = round(pipeline_value / len(open_deals), 2) if open_deals else 0.0

            entries.append(
                ManagerReportEntry(
                    manager_id=user.id,
                    manager_name=f"{user.first_name} {user.last_name}",
                    manager_email=user.email.value,
                    total_leads=len(u_leads),
                    converted_leads=converted,
                    conversion_rate=conversion_rate,
                    total_deals=len(u_deals),
                    open_deals=len(open_deals),
                    won_deals=len(won_deals),
                    lost_deals=len(lost_deals),
                    win_rate=win_rate,
                    pipeline_value=round(pipeline_value, 2),
                    won_revenue=round(won_revenue, 2),
                    avg_deal_size=avg_deal_size,
                    overdue_deals=overdue_by_owner.get(user.id, 0),
                )
            )

        # Сортируем по выручке (WON) убыванием
        entries.sort(key=lambda e: e.won_revenue, reverse=True)

        return ManagersReportOutput(
            managers=entries,
            total_managers=len(entries),
        )
