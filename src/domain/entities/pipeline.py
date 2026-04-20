"""
Доменная сущность Pipeline (Воронка продаж).
Воронка владеет упорядоченным набором этапов Stage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.entities.stage import Stage
from src.domain.exceptions import PipelineStageOrderError, StageNotFoundError


@dataclass
class Pipeline:
    """Упорядоченная последовательность этапов для отслеживания сделок.

    Инварианты:
    - name не может быть пустым
    - Порядковые номера этапов внутри воронки должны быть уникальными
    - Добавляемый этап должен иметь pipeline_id == self.id
    """

    id: UUID
    name: str
    owner_id: UUID
    stages: list[Stage] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Название воронки не может быть пустым.")

    # ── Фабрика ────────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, name: str, owner_id: UUID) -> Pipeline:
        """Создаёт новую пустую воронку с генерируемым ID."""
        return cls(id=uuid4(), name=name.strip(), owner_id=owner_id)

    # ── Управление этапами ─────────────────────────────────────────────────────

    def add_stage(self, stage: Stage) -> None:
        """Добавляет этап в воронку.

        Вызывает:
            PipelineStageOrderError: Если stage.pipeline_id != self.id или конфликт порядка.
        """
        if stage.pipeline_id != self.id:
            raise PipelineStageOrderError(
                f"Этап '{stage.name}' (pipeline_id={stage.pipeline_id}) "
                f"не принадлежит воронке '{self.name}' (id={self.id})."
            )
        if any(s.order == stage.order for s in self.stages):
            raise PipelineStageOrderError(
                f"Порядковый номер {stage.order} уже существует в воронке '{self.name}'."
            )
        self.stages.append(stage)
        self.stages.sort(key=lambda s: s.order)

    def remove_stage(self, stage_id: UUID) -> None:
        """Удаляет этап по ID.

        Вызывает:
            StageNotFoundError: Если этап с указанным ID не найден.
        """
        for i, stage in enumerate(self.stages):
            if stage.id == stage_id:
                self.stages.pop(i)
                return
        raise StageNotFoundError(
            f"Этап id={stage_id} не найден в воронке '{self.name}'."
        )

    def get_stage_by_id(self, stage_id: UUID) -> Stage | None:
        """Возвращает этап по ID или None, если не найден."""
        return next((s for s in self.stages if s.id == stage_id), None)

    def has_stage(self, stage_id: UUID) -> bool:
        """Проверяет, принадлежит ли этап данной воронке."""
        return any(s.id == stage_id for s in self.stages)

    # ── Свойства ───────────────────────────────────────────────────────────────

    @property
    def first_stage(self) -> Stage | None:
        """Первый этап воронки (с наименьшим order) или None, если пусто."""
        return self.stages[0] if self.stages else None

    @property
    def last_stage(self) -> Stage | None:
        """Последний этап воронки (с наибольшим order) или None, если пусто."""
        return self.stages[-1] if self.stages else None

    @property
    def stage_count(self) -> int:
        """Количество этапов в воронке."""
        return len(self.stages)

    def deactivate(self) -> None:
        """Деактивирует воронку."""
        self.is_active = False

    def __repr__(self) -> str:
        return (
            f"Pipeline(id={self.id}, name='{self.name}', "
            f"stages={self.stage_count})"
        )
