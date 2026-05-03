"""
ListEmailThreadsUseCase — группирует сохранённые письма по gmail_thread_id.
Возвращает список краткой информации о тредах (от новых к старым).
"""
from __future__ import annotations

from src.application.dtos.email_message_dtos import EmailThreadSummary
from src.domain.repositories.email_message_repository import IEmailMessageRepository


class ListEmailThreadsUseCase:
    """Возвращает список тредов, сгруппированных по gmail_thread_id."""

    def __init__(self, email_repo: IEmailMessageRepository) -> None:
        self._email_repo = email_repo

    async def execute(self) -> list[EmailThreadSummary]:
        """Загружает все письма из БД и группирует их в треды."""
        messages = await self._email_repo.find_all(limit=500, offset=0)

        # Группируем по thread_id
        threads: dict[str, list] = {}
        for msg in messages:
            threads.setdefault(msg.gmail_thread_id, []).append(msg)

        result: list[EmailThreadSummary] = []
        for thread_id, msgs in threads.items():
            # Самое последнее письмо
            latest = max(msgs, key=lambda m: m.received_at)

            # Уникальные участники
            participants: list[str] = []
            seen: set[str] = set()
            for m in msgs:
                for addr in [m.from_address] + m.to_addresses:
                    clean = addr.strip().lower()
                    if clean and clean not in seen:
                        seen.add(clean)
                        participants.append(addr.strip())

            # lead_id — берём первый непустой
            lead_id = next((m.lead_id for m in msgs if m.lead_id is not None), None)

            result.append(EmailThreadSummary(
                thread_id=thread_id,
                subject=latest.subject,
                message_count=len(msgs),
                last_message_at=latest.received_at,
                participants=participants[:5],   # максимум 5 адресов в превью
                lead_id=lead_id,
            ))

        # Сортируем по дате последнего сообщения (новые первыми)
        result.sort(key=lambda t: t.last_message_at, reverse=True)
        return result
