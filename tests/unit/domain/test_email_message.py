"""Юнит-тесты доменной сущности EmailMessage.
Проверяют: создание (inbound/outbound), инварианты, привязку к лиду.
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.entities.email_message import EmailMessage
from src.domain.value_objects.enums import EmailDirection


# ── Фикстуры ───────────────────────────────────────────────────────────────────

NOW = datetime.now(timezone.utc)


@pytest.fixture
def lead_id():
    return uuid4()


@pytest.fixture
def inbound_message(self) -> EmailMessage:
    """Фабрика входящего письма."""
    return EmailMessage.create_inbound(
        gmail_message_id="msg_001",
        gmail_thread_id="thr_001",
        from_address="client@example.com",
        to_addresses=["manager@crm.com"],
        subject="Вопрос по сделке",
        body="Здравствуйте, хочу обсудить условия.",
        received_at=NOW,
    )


@pytest.fixture
def outbound_message() -> EmailMessage:
    """Фабрика исходящего письма."""
    return EmailMessage.create_outbound(
        gmail_message_id="msg_002",
        gmail_thread_id="thr_002",
        from_address="manager@crm.com",
        to_addresses=["client@example.com"],
        subject="Re: Вопрос по сделке",
        body="Добрый день! Уточняю условия.",
    )


# ── Создание inbound ──────────────────────────────────────────────────────────

class TestEmailMessageCreateInbound:
    def test_creates_with_inbound_direction(self) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        assert msg.direction == EmailDirection.INBOUND

    def test_id_is_generated(self) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        assert msg.id is not None

    def test_fields_assigned_correctly(self) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com", "e@f.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        assert msg.gmail_message_id == "m1"
        assert msg.gmail_thread_id == "t1"
        assert msg.from_address == "a@b.com"
        assert msg.to_addresses == ["c@d.com", "e@f.com"]
        assert msg.subject == "Тема"
        assert msg.body == "Тело"
        assert msg.received_at == NOW

    def test_lead_id_default_none(self) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        assert msg.lead_id is None


# ── Создание outbound ──────────────────────────────────────────────────────────

class TestEmailMessageCreateOutbound:
    def test_creates_with_outbound_direction(self) -> None:
        msg = EmailMessage.create_outbound(
            gmail_message_id="m2",
            gmail_thread_id="t2",
            from_address="me@crm.com",
            to_addresses=["client@x.com"],
            subject="Предложение",
            body="Отправляю КП.",
        )
        assert msg.direction == EmailDirection.OUTBOUND

    def test_received_at_auto_set(self) -> None:
        msg = EmailMessage.create_outbound(
            gmail_message_id="m2",
            gmail_thread_id="t2",
            from_address="me@crm.com",
            to_addresses=["client@x.com"],
            subject="Предложение",
            body="КП.",
        )
        assert msg.received_at is not None

    def test_lead_id_can_be_set_on_creation(self, lead_id) -> None:
        msg = EmailMessage.create_outbound(
            gmail_message_id="m2",
            gmail_thread_id="t2",
            from_address="me@crm.com",
            to_addresses=["client@x.com"],
            subject="Предложение",
            body="КП.",
            lead_id=lead_id,
        )
        assert msg.lead_id == lead_id


# ── Инварианты ─────────────────────────────────────────────────────────────────

class TestEmailMessageInvariants:
    def test_empty_from_address_raises(self) -> None:
        with pytest.raises(ValueError, match="Адрес отправителя"):
            EmailMessage.create_inbound(
                gmail_message_id="m1",
                gmail_thread_id="t1",
                from_address="  ",
                to_addresses=["c@d.com"],
                subject="Тема",
                body="Тело",
                received_at=NOW,
            )

    def test_empty_subject_raises(self) -> None:
        with pytest.raises(ValueError, match="Тема письма"):
            EmailMessage.create_inbound(
                gmail_message_id="m1",
                gmail_thread_id="t1",
                from_address="a@b.com",
                to_addresses=["c@d.com"],
                subject="",
                body="Тело",
                received_at=NOW,
            )

    def test_empty_to_addresses_raises(self) -> None:
        with pytest.raises(ValueError, match="Список адресатов"):
            EmailMessage(
                id=uuid4(),
                gmail_message_id="m1",
                gmail_thread_id="t1",
                from_address="a@b.com",
                to_addresses=[],
                subject="Тема",
                body="Тело",
                direction=EmailDirection.INBOUND,
                received_at=NOW,
            )


# ── Привязка к лиду ───────────────────────────────────────────────────────────

class TestEmailMessageLinkToLead:
    def test_link_to_lead_sets_lead_id(self, lead_id) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        msg.link_to_lead(lead_id)
        assert msg.lead_id == lead_id

    def test_link_same_lead_id_idempotent(self, lead_id) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        msg.link_to_lead(lead_id)
        msg.link_to_lead(lead_id)  # повторно тот же лид — ок
        assert msg.lead_id == lead_id

    def test_link_different_lead_raises(self, lead_id) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        msg.link_to_lead(lead_id)
        other_lead_id = uuid4()
        with pytest.raises(ValueError, match="уже привязано"):
            msg.link_to_lead(other_lead_id)

    def test_unlink_from_lead(self, lead_id) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Тема",
            body="Тело",
            received_at=NOW,
        )
        msg.link_to_lead(lead_id)
        msg.unlink_from_lead()
        assert msg.lead_id is None


# ── Repr ───────────────────────────────────────────────────────────────────────

class TestEmailMessageRepr:
    def test_repr_contains_subject_and_direction(self) -> None:
        msg = EmailMessage.create_inbound(
            gmail_message_id="m1",
            gmail_thread_id="t1",
            from_address="a@b.com",
            to_addresses=["c@d.com"],
            subject="Очень длинная тема письма для проверки обрезки",
            body="Тело",
            received_at=NOW,
        )
        r = repr(msg)
        assert "EmailMessage" in r
        assert "inbound" in r
