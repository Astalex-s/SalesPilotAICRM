"""
Декларативная база SQLAlchemy.
Все ORM-модели наследуются от этого Base.
Base находится в слое Infrastructure — никогда не импортируется из Domain или Application.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей SQLAlchemy."""
    pass
