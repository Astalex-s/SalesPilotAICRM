"""
Доменная сущность User.
Представляет внутреннего пользователя CRM (менеджер, продавец, администратор).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole


@dataclass
class User:
    """Пользователь системы CRM с ролевой моделью доступа.

    Инварианты:
    - first_name и last_name не могут быть пустыми
    - email должен быть валидным объектом-значением Email
    - ADMIN не может быть понижен через promote_to_manager()
    """

    id: UUID
    first_name: str
    last_name: str
    email: Email
    role: UserRole
    is_active: bool = True
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.first_name.strip():
            raise ValueError("Имя пользователя не может быть пустым.")
        if not self.last_name.strip():
            raise ValueError("Фамилия пользователя не может быть пустой.")

    # ── Фабрика ────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: Email,
        role: UserRole = UserRole.SALES_REP,
    ) -> User:
        """Создаёт нового активного пользователя с генерируемым ID."""
        return cls(
            id=uuid4(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email,
            role=role,
        )

    # ── Свойства ───────────────────────────────────────────────────────────────

    @property
    def full_name(self) -> str:
        """Полное имя пользователя."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        """Является ли пользователь администратором."""
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self) -> bool:
        """Является ли пользователь менеджером или администратором."""
        return self.role in (UserRole.ADMIN, UserRole.MANAGER)

    # ── Поведение ──────────────────────────────────────────────────────────────

    def deactivate(self) -> None:
        """Мягкое удаление: блокирует вход без уничтожения истории."""
        self.is_active = False

    def activate(self) -> None:
        """Восстанавливает доступ пользователя."""
        self.is_active = True

    def promote_to_manager(self) -> None:
        """Повышает SALES_REP до MANAGER.

        Вызывает:
            ValueError: Если пользователь уже является ADMIN.
        """
        if self.role == UserRole.ADMIN:
            raise ValueError("Нельзя изменить роль ADMIN через повышение.")
        self.role = UserRole.MANAGER

    def __repr__(self) -> str:
        return f"User(id={self.id}, name='{self.full_name}', role={self.role.value})"
