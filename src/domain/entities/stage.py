"""
Доменная сущность Stage (Этап).
Этап — упорядоченный шаг внутри воронки продаж Pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class Stage:
    """Упорядоченный шаг в воронке продаж.

    Инварианты:
    - name не может быть пустым
    - order >= 0
    - probability должна быть в диапазоне [0.0, 1.0]
    - pipeline_id обязателен при создании
    """

    id: UUID
    pipeline_id: UUID
    name: str
    order: int
    probability: float  # вероятность выигрыша: 0.0 → 1.0
    color: str | None = None  # HEX-цвет этапа, например "#00A8E8"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Название этапа не может быть пустым.")
        if self.order < 0:
            raise ValueError(f"Порядковый номер этапа должен быть >= 0, получено {self.order}.")
        if not (0.0 <= self.probability <= 1.0):
            raise ValueError(
                f"Вероятность этапа должна быть в [0.0, 1.0], получено {self.probability}."
            )

    # ── Фабрика ────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        pipeline_id: UUID,
        name: str,
        order: int,
        probability: float = 0.5,
        color: str | None = None,
    ) -> Stage:
        """Создаёт новый этап с генерируемым ID."""
        return cls(
            id=uuid4(),
            pipeline_id=pipeline_id,
            name=name.strip(),
            order=order,
            probability=probability,
            color=color,
        )

    # ── Поведение ──────────────────────────────────────────────────────────────

    def rename(self, new_name: str) -> None:
        """Переименовывает этап."""
        if not new_name.strip():
            raise ValueError("Название этапа не может быть пустым.")
        self.name = new_name.strip()

    def update_probability(self, probability: float) -> None:
        """Обновляет вероятность выигрыша этапа."""
        if not (0.0 <= probability <= 1.0):
            raise ValueError(
                f"Вероятность должна быть в [0.0, 1.0], получено {probability}."
            )
        self.probability = probability

    def __repr__(self) -> str:
        return f"Stage(id={self.id}, name='{self.name}', order={self.order})"
