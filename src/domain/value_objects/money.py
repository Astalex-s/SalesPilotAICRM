"""
Объект-значение Money — неизменяемый, поддерживает арифметику.
Использует Decimal для точности финансовых расчётов.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.domain.exceptions import InvalidMoneyAmountError


@dataclass(frozen=True)
class Money:
    """Денежная сумма с указанием валюты.

    Неизменяем: арифметические операции возвращают новые экземпляры Money.
    Валюта должна быть трёхбуквенным кодом ISO 4217.
    """

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise InvalidMoneyAmountError(
                f"Денежная сумма не может быть отрицательной: {self.amount}"
            )
        if not self.currency or len(self.currency) != 3 or not self.currency.isalpha():
            raise InvalidMoneyAmountError(
                f"Валюта должна быть трёхбуквенным кодом ISO 4217, получено: '{self.currency}'"
            )

    # ── Арифметика ─────────────────────────────────────────────────────────────

    def __add__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        result = self.amount - other.amount
        if result < Decimal("0"):
            raise InvalidMoneyAmountError(
                f"Вычитание даёт отрицательную сумму: {self.amount} - {other.amount}"
            )
        return Money(amount=result, currency=self.currency)

    def __mul__(self, factor: int | float | Decimal) -> Money:
        return Money(
            amount=(self.amount * Decimal(str(factor))).quantize(Decimal("0.01")),
            currency=self.currency,
        )

    def __gt__(self, other: Money) -> bool:
        self._assert_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        self._assert_same_currency(other)
        return self.amount >= other.amount

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    # ── Вспомогательные методы ─────────────────────────────────────────────────

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise InvalidMoneyAmountError(
                f"Нельзя выполнять операции с разными валютами: {self.currency} и {other.currency}"
            )

    @classmethod
    def zero(cls, currency: str = "USD") -> Money:
        """Возвращает нулевую сумму для указанной валюты."""
        return cls(amount=Decimal("0"), currency=currency)
