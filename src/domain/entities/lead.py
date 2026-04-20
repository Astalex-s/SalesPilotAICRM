"""
Доменная сущность Lead (Лид).
Потенциальный клиент, который проходит квалификацию
и в итоге может быть конвертирован в сделку Deal.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.exceptions import (
    InvalidLeadTransitionError,
    LeadAlreadyConvertedError,
    LeadNotQualifiedError,
)
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import LeadSource, LeadStatus
from src.domain.value_objects.phone import Phone

# ── Машина состояний ───────────────────────────────────────────────────────────
# Определяет допустимые переходы между статусами лида.
_VALID_TRANSITIONS: dict[LeadStatus, frozenset[LeadStatus]] = {
    LeadStatus.NEW: frozenset({
        LeadStatus.CONTACTED,
        LeadStatus.QUALIFIED,
        LeadStatus.UNQUALIFIED,
    }),
    LeadStatus.CONTACTED: frozenset({
        LeadStatus.QUALIFIED,
        LeadStatus.UNQUALIFIED,
    }),
    LeadStatus.QUALIFIED: frozenset({
        LeadStatus.UNQUALIFIED,
        # CONVERTED устанавливается только через mark_converted(), вызываемый LeadConversionService
    }),
    LeadStatus.UNQUALIFIED: frozenset({
        LeadStatus.QUALIFIED,   # повторная квалификация разрешена
        LeadStatus.CONTACTED,
    }),
    LeadStatus.CONVERTED: frozenset(),  # терминальный статус — изменения запрещены
}


@dataclass
class Lead:
    """Потенциальный клиент в CRM-воронке.

    Инварианты:
    - first_name и last_name не могут быть пустыми
    - Переходы статусов строго по _VALID_TRANSITIONS
    - Конвертация разрешена только из статуса QUALIFIED
    - Конвертированный лид не может менять статус
    """

    id: UUID
    first_name: str
    last_name: str
    email: Email
    owner_id: UUID
    status: LeadStatus = LeadStatus.NEW
    source: LeadSource = LeadSource.OTHER
    phone: Phone | None = None
    company: str | None = None
    notes: str | None = None
    converted_deal_id: UUID | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.first_name.strip():
            raise ValueError("Имя лида не может быть пустым.")
        if not self.last_name.strip():
            raise ValueError("Фамилия лида не может быть пустой.")

    # ── Фабрика ────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: Email,
        owner_id: UUID,
        source: LeadSource = LeadSource.OTHER,
        phone: Phone | None = None,
        company: str | None = None,
    ) -> Lead:
        """Создаёт нового лида с генерируемым ID и статусом NEW."""
        return cls(
            id=uuid4(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email,
            owner_id=owner_id,
            source=source,
            phone=phone,
            company=company,
        )

    # ── Свойства ───────────────────────────────────────────────────────────────

    @property
    def full_name(self) -> str:
        """Полное имя лида."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_converted(self) -> bool:
        """Конвертирован ли лид в сделку."""
        return self.status == LeadStatus.CONVERTED

    @property
    def is_qualified(self) -> bool:
        """Квалифицирован ли лид."""
        return self.status == LeadStatus.QUALIFIED

    # ── Переходы статусов ──────────────────────────────────────────────────────

    def contact(self) -> None:
        """Помечает лид как контактированный (выполнен первый контакт)."""
        self._transition_to(LeadStatus.CONTACTED)

    def qualify(self) -> None:
        """Помечает лид как квалифицированный (готов к конвертации)."""
        self._transition_to(LeadStatus.QUALIFIED)

    def disqualify(self) -> None:
        """Помечает лид как неквалифицированный (не подходит)."""
        self._transition_to(LeadStatus.UNQUALIFIED)

    def mark_converted(self, deal_id: UUID) -> None:
        """Помечает лид как конвертированный в сделку.

        Метод предназначен для вызова исключительно из LeadConversionService,
        чтобы гарантировать соблюдение всех инвариантов конвертации.

        Вызывает:
            LeadAlreadyConvertedError: Если лид уже конвертирован.
            LeadNotQualifiedError: Если статус лида не QUALIFIED.
        """
        if self.is_converted:
            raise LeadAlreadyConvertedError(
                f"Лид '{self.full_name}' (id={self.id}) уже конвертирован."
            )
        if not self.is_qualified:
            raise LeadNotQualifiedError(
                f"Лид '{self.full_name}' должен быть QUALIFIED перед конвертацией. "
                f"Текущий статус: '{self.status.value}'."
            )
        self.status = LeadStatus.CONVERTED
        self.converted_deal_id = deal_id
        self._touch()

    def add_note(self, note: str) -> None:
        """Добавляет произвольную заметку к лиду."""
        if not note.strip():
            raise ValueError("Заметка не может быть пустой.")
        self.notes = note.strip()
        self._touch()

    # ── Внутренние методы ──────────────────────────────────────────────────────

    def _transition_to(self, new_status: LeadStatus) -> None:
        """Выполняет переход статуса согласно машине состояний."""
        if self.is_converted:
            raise LeadAlreadyConvertedError(
                f"Лид '{self.full_name}' уже конвертирован — изменение статуса невозможно."
            )
        allowed = _VALID_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise InvalidLeadTransitionError(
                f"Переход лида из '{self.status.value}' в '{new_status.value}' не разрешён."
            )
        self.status = new_status
        self._touch()

    def _touch(self) -> None:
        """Обновляет временную метку последнего изменения."""
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f"Lead(id={self.id}, name='{self.full_name}', "
            f"status={self.status.value})"
        )
