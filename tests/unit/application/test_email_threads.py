"""
Юнит-тесты ListEmailThreadsUseCase и GetEmailThreadUseCase.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.get_email_thread import GetEmailThreadUseCase
from src.application.use_cases.list_email_threads import ListEmailThreadsUseCase
from src.domain.entities.email_message import EmailMessage
from src.domain.value_objects.enums import EmailDirection


def _make_email(
    thread_id: str = "thread1",
    subject: str = "Hello",
    from_address: str = "sender@test.com",
    received_offset_seconds: int = 0,
    lead_id=None,
) -> EmailMessage:
    return EmailMessage(
        id=uuid4(),
        gmail_message_id=f"msg_{uuid4().hex[:8]}",
        gmail_thread_id=thread_id,
        from_address=from_address,
        to_addresses=["recipient@test.com"],
        subject=subject,
        body="Body text",
        direction=EmailDirection.INBOUND,
        received_at=datetime.now(timezone.utc) + timedelta(seconds=received_offset_seconds),
        lead_id=lead_id,
    )


# ── ListEmailThreadsUseCase ────────────────────────────────────────────────────

@pytest.fixture
def email_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def list_use_case(email_repo) -> ListEmailThreadsUseCase:
    return ListEmailThreadsUseCase(email_repo=email_repo)


class TestListEmailThreads:
    async def test_returns_empty_when_no_emails(self, list_use_case, email_repo):
        email_repo.find_all.return_value = []
        result = await list_use_case.execute()
        assert result == []

    async def test_groups_emails_by_thread(self, list_use_case, email_repo):
        t1_msg1 = _make_email(thread_id="t1", received_offset_seconds=0)
        t1_msg2 = _make_email(thread_id="t1", received_offset_seconds=60)
        t2_msg1 = _make_email(thread_id="t2")
        email_repo.find_all.return_value = [t1_msg1, t1_msg2, t2_msg1]

        result = await list_use_case.execute()
        assert len(result) == 2
        t1 = next(t for t in result if t.thread_id == "t1")
        assert t1.message_count == 2

    async def test_latest_message_determines_subject(self, list_use_case, email_repo):
        old = _make_email(thread_id="t1", subject="Old Subject", received_offset_seconds=-100)
        new = _make_email(thread_id="t1", subject="New Subject", received_offset_seconds=0)
        email_repo.find_all.return_value = [old, new]

        result = await list_use_case.execute()
        assert result[0].subject == "New Subject"

    async def test_sorted_newest_first(self, list_use_case, email_repo):
        old = _make_email(thread_id="old_thread", received_offset_seconds=-3600)
        new = _make_email(thread_id="new_thread", received_offset_seconds=0)
        email_repo.find_all.return_value = [old, new]

        result = await list_use_case.execute()
        assert result[0].thread_id == "new_thread"

    async def test_picks_lead_id_from_messages(self, list_use_case, email_repo):
        lead_id = uuid4()
        m1 = _make_email(thread_id="t1", lead_id=None)
        m2 = _make_email(thread_id="t1", lead_id=lead_id)
        email_repo.find_all.return_value = [m1, m2]

        result = await list_use_case.execute()
        assert result[0].lead_id == lead_id

    async def test_deduplicates_participants(self, list_use_case, email_repo):
        msg = _make_email(thread_id="t1", from_address="a@test.com")
        msg.to_addresses = ["a@test.com", "b@test.com"]
        email_repo.find_all.return_value = [msg]

        result = await list_use_case.execute()
        participants = result[0].participants
        # "a@test.com" appears as sender and recipient — should be deduplicated
        assert participants.count("a@test.com") == 1


# ── GetEmailThreadUseCase ──────────────────────────────────────────────────────

@pytest.fixture
def thread_use_case(email_repo) -> GetEmailThreadUseCase:
    return GetEmailThreadUseCase(email_repo=email_repo)


class TestGetEmailThread:
    async def test_returns_thread_with_messages(self, thread_use_case, email_repo):
        m1 = _make_email(thread_id="t1", subject="Hello")
        email_repo.find_by_thread_id.return_value = [m1]

        result = await thread_use_case.execute("t1")
        assert result.thread_id == "t1"
        assert result.subject == "Hello"
        assert len(result.messages) == 1

    async def test_empty_thread_returns_placeholder_subject(self, thread_use_case, email_repo):
        email_repo.find_by_thread_id.return_value = []

        result = await thread_use_case.execute("missing_thread")
        assert result.subject == "(пустой тред)"
        assert result.messages == []
