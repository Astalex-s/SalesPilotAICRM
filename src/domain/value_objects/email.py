"""
Объект-значение Email — неизменяемый, самовалидирующийся.
Нет зависимостей на инфраструктуру или фреймворки.
"""
import re
from dataclasses import dataclass
from typing import ClassVar

from src.domain.exceptions import InvalidEmailError


@dataclass(frozen=True)
class Email:
    """Валидированный адрес электронной почты.

    Неизменяем по замыслу: изменённый e-mail — это новый объект-значение.
    """

    value: str

    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    )

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise InvalidEmailError("Адрес электронной почты не может быть пустым.")
        if not self._PATTERN.match(self.value.strip()):
            raise InvalidEmailError(f"Некорректный адрес e-mail: '{self.value}'")

    def __str__(self) -> str:
        return self.value

    @property
    def domain(self) -> str:
        """Возвращает доменную часть адреса (например, 'example.com')."""
        return self.value.split("@", 1)[1]
