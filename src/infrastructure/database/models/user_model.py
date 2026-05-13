"""
UserModel — ORM-модель таблицы users.
Хранит хэш пароля в БД; доменная сущность User пароля не знает.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import UserRole
from src.infrastructure.database.base import Base


class UserModel(Base):
    """ORM-модель для таблицы users."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole", values_callable=lambda e: [x.value for x in e]),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ── Маппинг ────────────────────────────────────────────────────────────────

    def to_entity(self) -> User:
        """Преобразует ORM-строку в доменную сущность User (без пароля)."""
        return User(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=Email(self.email),
            role=self.role,
            is_active=self.is_active,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, user: User, password_hash: str) -> UserModel:
        """Создаёт ORM-модель из доменной сущности и хэша пароля."""
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=str(user.email),
            password_hash=password_hash,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )
