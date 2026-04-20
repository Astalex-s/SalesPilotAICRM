"""
Объект-значение Phone — неизменяемый, мягкая валидация международного формата.
"""
import re
from dataclasses import dataclass
from typing import ClassVar

from src.domain.exceptions import InvalidPhoneError


@dataclass(frozen=True)
class Phone:
    """Валидированный номер телефона.

    Принимает международные форматы: +1 (555) 123-4567, +7 999 000 11 22 и т.д.
    Хранит исходную строку; используйте `.digits` для нормализованного вида (только цифры).
    """

    value: str

    # Допускает +, цифры, пробелы, тире, точки, скобки; 7–20 символов после зачистки
    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^\+?[\d\s\-\.\(\)]{7,20}$"
    )

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise InvalidPhoneError("Номер телефона не может быть пустым.")
        if not self._PATTERN.match(self.value.strip()):
            raise InvalidPhoneError(
                f"Некорректный формат номера телефона: '{self.value}'. "
                "Ожидается международный формат, например: +7 999 000 11 22"
            )

    def __str__(self) -> str:
        return self.value

    @property
    def digits(self) -> str:
        """Возвращает номер только из цифр (удобно для сравнения и хранения)."""
        return re.sub(r"\D", "", self.value)
