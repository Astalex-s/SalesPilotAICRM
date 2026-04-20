"""
Юнит-тесты объектов-значений домена: Email, Money, Phone.
"""
import pytest
from decimal import Decimal

from src.domain.exceptions import (
    InvalidEmailError,
    InvalidMoneyAmountError,
    InvalidPhoneError,
)
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money
from src.domain.value_objects.phone import Phone


# ── Email ──────────────────────────────────────────────────────────────────────

class TestEmail:
    def test_valid_email_created(self) -> None:
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_domain_property(self) -> None:
        email = Email("sales@crm.io")
        assert email.domain == "crm.io"

    def test_str_returns_value(self) -> None:
        assert str(Email("a@b.com")) == "a@b.com"

    def test_email_without_at_raises(self) -> None:
        with pytest.raises(InvalidEmailError):
            Email("notanemail")

    def test_empty_email_raises(self) -> None:
        with pytest.raises(InvalidEmailError):
            Email("")

    def test_email_without_tld_raises(self) -> None:
        with pytest.raises(InvalidEmailError):
            Email("user@nodot")

    def test_email_is_immutable(self) -> None:
        email = Email("x@y.com")
        with pytest.raises(Exception):
            email.value = "other@y.com"  # type: ignore[misc]

    def test_equal_emails_are_equal(self) -> None:
        assert Email("x@y.com") == Email("x@y.com")

    def test_different_emails_are_not_equal(self) -> None:
        assert Email("a@b.com") != Email("c@d.com")


# ── Money ──────────────────────────────────────────────────────────────────────

class TestMoney:
    def test_valid_money_created(self) -> None:
        m = Money(amount=Decimal("100.00"), currency="USD")
        assert m.amount == Decimal("100.00")
        assert m.currency == "USD"

    def test_zero_factory(self) -> None:
        assert Money.zero().amount == Decimal("0")

    def test_negative_amount_raises(self) -> None:
        with pytest.raises(InvalidMoneyAmountError):
            Money(amount=Decimal("-1"), currency="USD")

    def test_invalid_currency_raises(self) -> None:
        # Слишком короткий код валюты
        with pytest.raises(InvalidMoneyAmountError):
            Money(amount=Decimal("10"), currency="US")

    def test_addition_same_currency(self) -> None:
        a = Money(Decimal("50"), "USD")
        b = Money(Decimal("25"), "USD")
        assert (a + b).amount == Decimal("75")

    def test_addition_different_currency_raises(self) -> None:
        with pytest.raises(InvalidMoneyAmountError):
            Money(Decimal("10"), "USD") + Money(Decimal("10"), "EUR")

    def test_subtraction(self) -> None:
        result = Money(Decimal("100"), "USD") - Money(Decimal("40"), "USD")
        assert result.amount == Decimal("60")

    def test_subtraction_below_zero_raises(self) -> None:
        with pytest.raises(InvalidMoneyAmountError):
            Money(Decimal("10"), "USD") - Money(Decimal("20"), "USD")

    def test_multiplication(self) -> None:
        result = Money(Decimal("100"), "USD") * 1.5
        assert result.amount == Decimal("150.00")

    def test_comparison(self) -> None:
        assert Money(Decimal("100"), "USD") > Money(Decimal("50"), "USD")
        assert Money(Decimal("50"), "USD") >= Money(Decimal("50"), "USD")

    def test_str_representation(self) -> None:
        assert str(Money(Decimal("9.99"), "EUR")) == "9.99 EUR"

    def test_money_is_immutable(self) -> None:
        m = Money(Decimal("10"), "USD")
        with pytest.raises(Exception):
            m.amount = Decimal("99")  # type: ignore[misc]


# ── Phone ──────────────────────────────────────────────────────────────────────

class TestPhone:
    def test_valid_phone_created(self) -> None:
        phone = Phone("+1 555 123 4567")
        assert phone.value == "+1 555 123 4567"

    def test_digits_property(self) -> None:
        assert Phone("+1 555 123 4567").digits == "15551234567"

    def test_empty_phone_raises(self) -> None:
        with pytest.raises(InvalidPhoneError):
            Phone("")

    def test_phone_is_immutable(self) -> None:
        p = Phone("+1 555 000 0000")
        with pytest.raises(Exception):
            p.value = "+1 999 999 9999"  # type: ignore[misc]
