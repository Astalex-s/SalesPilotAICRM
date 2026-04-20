"""
Доменная сущность Deal (Сделка).
Активная коммерческая возможность, которая всегда принадлежит
конкретному этапу Stage внутри воронки Pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.exceptions import DealAlreadyClosedError, InvalidStageForPipelineError
from src.domain.value_objects.enums import DealStatus
from src.domain.value_objects.money import Money


@dataclass
class Deal:
    """Активная сделка в воронке продаж.

    Инварианты:
    - title не может быть пустым
    - stage_id и pipeline_id обязательны
    - Только OPEN-сделки могут менять этап или сумму
    - Выигранную (WON) сделку нельзя переоткрыть; проигранную (LOST) — можно
    """

    id: UUID
    title: str
    owner_id: UUID
    stage_id: UUID
    pipeline_id: UUID
    value: Money
    status: DealStatus = DealStatus.OPEN
    contact_name: str | None = None
    company: str | None = None
    source_lead_id: UUID | None = None          # заполняется при создании из лида
    expected_close_date: datetime | None = None
    closed_at: datetime | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Название сделки не может быть пустым.")

    # ── Фабрика ────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        title: str,
        owner_id: UUID,
        stage_id: UUID,
        pipeline_id: UUID,
        value: Money,
        contact_name: str | None = None,
        company: str | None = None,
        source_lead_id: UUID | None = None,
        expected_close_date: datetime | None = None,
    ) -> Deal:
        """Создаёт новую открытую сделку с генерируемым ID."""
        return cls(
            id=uuid4(),
            title=title.strip(),
            owner_id=owner_id,
            stage_id=stage_id,
            pipeline_id=pipeline_id,
            value=value,
            contact_name=contact_name,
            company=company,
            source_lead_id=source_lead_id,
            expected_close_date=expected_close_date,
        )

    # ── Свойства ───────────────────────────────────────────────────────────────

    @property
    def is_open(self) -> bool:
        """Открыта ли сделка."""
        return self.status == DealStatus.OPEN

    @property
    def is_closed(self) -> bool:
        """Закрыта ли сделка (выиграна или проиграна)."""
        return self.status in (DealStatus.WON, DealStatus.LOST)

    # ── Переход по этапам ──────────────────────────────────────────────────────

    def move_to_stage(self, new_stage_id: UUID, pipeline_id: UUID) -> None:
        """Перемещает сделку на новый этап внутри той же воронки.

        Вызывает:
            DealAlreadyClosedError: Если сделка не OPEN.
            InvalidStageForPipelineError: Если pipeline_id не совпадает.
        """
        self._assert_open("переместить на новый этап")
        if pipeline_id != self.pipeline_id:
            raise InvalidStageForPipelineError(
                f"Воронка этапа ({pipeline_id}) не совпадает с воронкой сделки ({self.pipeline_id})."
            )
        self.stage_id = new_stage_id
        self._touch()

    # ── Жизненный цикл ─────────────────────────────────────────────────────────

    def win(self) -> None:
        """Закрывает сделку как выигранную (WON).

        Вызывает:
            DealAlreadyClosedError: Если сделка уже закрыта.
        """
        self._assert_open("пометить как выигранную")
        self.status = DealStatus.WON
        self.closed_at = datetime.now(timezone.utc)
        self._touch()

    def lose(self) -> None:
        """Закрывает сделку как проигранную (LOST).

        Вызывает:
            DealAlreadyClosedError: Если сделка уже закрыта.
        """
        self._assert_open("пометить как проигранную")
        self.status = DealStatus.LOST
        self.closed_at = datetime.now(timezone.utc)
        self._touch()

    def reopen(self) -> None:
        """Переоткрывает проигранную сделку для повторной работы.

        Только LOST-сделки можно переоткрыть; WON — финальный статус.

        Вызывает:
            ValueError: Если сделка OPEN или WON.
        """
        if self.status == DealStatus.OPEN:
            raise ValueError("Сделка уже открыта.")
        if self.status == DealStatus.WON:
            raise ValueError("Выигранную сделку нельзя переоткрыть.")
        self.status = DealStatus.OPEN
        self.closed_at = None
        self._touch()

    # ── Управление суммой ──────────────────────────────────────────────────────

    def update_value(self, new_value: Money) -> None:
        """Обновляет сумму сделки. Разрешено только для OPEN-сделок.

        Вызывает:
            DealAlreadyClosedError: Если сделка не OPEN.
        """
        self._assert_open("обновить сумму")
        self.value = new_value
        self._touch()

    def update_expected_close(self, close_date: datetime) -> None:
        """Обновляет ожидаемую дату закрытия. Разрешено только для OPEN-сделок."""
        self._assert_open("обновить дату закрытия")
        self.expected_close_date = close_date
        self._touch()

    # ── Внутренние методы ──────────────────────────────────────────────────────

    def _assert_open(self, action: str) -> None:
        """Проверяет, что сделка открыта; иначе выбрасывает исключение."""
        if not self.is_open:
            raise DealAlreadyClosedError(
                f"Нельзя {action} для {self.status.value}-сделки (id={self.id})."
            )

    def _touch(self) -> None:
        """Обновляет временную метку последнего изменения."""
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f"Deal(id={self.id}, title='{self.title}', "
            f"status={self.status.value}, value={self.value})"
        )
