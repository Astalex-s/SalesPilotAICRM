"""
Реэкспорт BaseRepository из доменного слоя.

Use Cases в слое Application импортируют отсюда, чтобы зависеть только
от границы слоя Application и не обращаться к внутренностям домена напрямую.
"""
from src.domain.repositories.base import BaseRepository

__all__ = ["BaseRepository"]
