"""
Юнит-тесты мелких use cases:
- UpdatePipelineUseCase
- ListDealAttachmentsUseCase
- ListStoredEmailsUseCase
- TriggerEmailSyncUseCase
- BulkImportLeadsUseCase
- RefreshTokenUseCase
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.dtos.pipeline_dtos import UpdatePipelineInput
from src.application.dtos.email_message_dtos import ListStoredEmailsInput
from src.application.dtos.lead_dtos import BulkImportInput, BulkImportLeadRow
from src.application.dtos.auth_dtos import RefreshTokenInput
from src.application.exceptions import PipelineNotFoundError
from src.application.ports.task_service import EnqueuedTask
from src.application.use_cases.update_pipeline import UpdatePipelineUseCase
from src.application.use_cases.list_deal_attachments import ListDealAttachmentsUseCase
from src.application.use_cases.list_stored_emails import ListStoredEmailsUseCase
from src.application.use_cases.trigger_email_sync import TriggerEmailSyncUseCase
from src.application.use_cases.bulk_import_leads import BulkImportLeadsUseCase
from src.application.use_cases.refresh_token import RefreshTokenUseCase
from src.domain.entities.pipeline import Pipeline
from src.domain.entities.deal_attachment import DealAttachment
from src.domain.entities.email_message import EmailMessage
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.enums import EmailDirection, UserRole
from src.infrastructure.auth.auth_service import create_refresh_token


# ── UpdatePipelineUseCase ──────────────────────────────────────────────────────

class TestUpdatePipeline:
    @pytest.fixture
    def pipeline_repo(self):
        repo = AsyncMock()
        repo.save.side_effect = lambda e: e
        return repo

    async def test_renames_pipeline(self, pipeline_repo):
        pipeline = Pipeline.create(name="Old Name", owner_id=uuid4())
        pipeline_repo.get_by_id.return_value = pipeline
        uc = UpdatePipelineUseCase(pipeline_repo=pipeline_repo)

        result = await uc.execute(pipeline.id, UpdatePipelineInput(name="New Name"))
        assert result.name == "New Name"

    async def test_raises_when_not_found(self, pipeline_repo):
        pipeline_repo.get_by_id.return_value = None
        uc = UpdatePipelineUseCase(pipeline_repo=pipeline_repo)

        with pytest.raises(PipelineNotFoundError):
            await uc.execute(uuid4(), UpdatePipelineInput(name="X"))


# ── ListDealAttachmentsUseCase ─────────────────────────────────────────────────

class TestListDealAttachments:
    @pytest.fixture
    def att_repo(self):
        return AsyncMock()

    async def test_returns_empty_list(self, att_repo):
        att_repo.find_by_deal.return_value = []
        uc = ListDealAttachmentsUseCase(attachment_repo=att_repo)
        result = await uc.execute(uuid4())
        assert result == []

    async def test_returns_attachments(self, att_repo):
        att = DealAttachment.create(
            deal_id=uuid4(), filename="file.pdf",
            storage_path="/tmp/file.pdf", content_type="application/pdf",
            size_bytes=512, uploaded_by_id=uuid4(),
        )
        att_repo.find_by_deal.return_value = [att]
        uc = ListDealAttachmentsUseCase(attachment_repo=att_repo)

        result = await uc.execute(att.deal_id)
        assert len(result) == 1
        assert result[0].filename == "file.pdf"


# ── ListStoredEmailsUseCase ────────────────────────────────────────────────────

def _make_email_msg() -> EmailMessage:
    return EmailMessage(
        id=uuid4(), gmail_message_id=f"gm_{uuid4().hex[:8]}",
        gmail_thread_id="thr1", from_address="a@test.com",
        to_addresses=["b@test.com"], subject="Hi", body="Hello",
        direction=EmailDirection.INBOUND,
        received_at=datetime.now(timezone.utc),
    )


class TestListStoredEmails:
    @pytest.fixture
    def email_repo(self):
        return AsyncMock()

    async def test_returns_email_outputs(self, email_repo):
        msg = _make_email_msg()
        email_repo.find_all.return_value = [msg]
        uc = ListStoredEmailsUseCase(email_repo=email_repo)

        result = await uc.execute(ListStoredEmailsInput())
        assert len(result) == 1
        assert result[0].subject == "Hi"

    async def test_passes_pagination(self, email_repo):
        email_repo.find_all.return_value = []
        uc = ListStoredEmailsUseCase(email_repo=email_repo)
        await uc.execute(ListStoredEmailsInput(limit=10, offset=5))
        email_repo.find_all.assert_called_once_with(limit=10, offset=5)


# ── TriggerEmailSyncUseCase ────────────────────────────────────────────────────

class TestTriggerEmailSync:
    @pytest.fixture
    def task_service(self):
        svc = MagicMock()
        svc.enqueue_fetch_emails.return_value = EnqueuedTask(
            task_id="task-xyz", task_name="tasks.email.fetch"
        )
        return svc

    async def test_returns_task_id(self, task_service):
        uc = TriggerEmailSyncUseCase(task_service=task_service)
        result = await uc.execute(query="from:boss", max_results=20)
        assert result.task_id == "task-xyz"

    async def test_passes_query_params(self, task_service):
        uc = TriggerEmailSyncUseCase(task_service=task_service)
        await uc.execute(query="label:inbox", max_results=50)
        task_service.enqueue_fetch_emails.assert_called_once_with(
            query="label:inbox", max_results=50
        )


# ── BulkImportLeadsUseCase ─────────────────────────────────────────────────────

class TestBulkImportLeads:
    @pytest.fixture
    def lead_repo(self):
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        repo.save.side_effect = lambda e: e
        return repo

    def _row(self, email: str | None = None) -> BulkImportLeadRow:
        return BulkImportLeadRow(
            first_name="Test", last_name="Lead",
            email=email or f"test_{uuid4().hex[:6]}@example.com",
        )

    async def test_creates_leads(self, lead_repo):
        uc = BulkImportLeadsUseCase(lead_repo=lead_repo)
        data = BulkImportInput(rows=[self._row(), self._row()], owner_id=uuid4())

        result = await uc.execute(data)
        assert result.created == 2
        assert result.skipped == 0
        assert result.error_count == 0

    async def test_skips_duplicate_email(self, lead_repo):
        from src.domain.entities.lead import Lead
        existing = Lead.create(
            first_name="E", last_name="X",
            email=Email("dup@test.com"), owner_id=uuid4(),
            source="website",
        )
        lead_repo.find_by_email.return_value = existing
        uc = BulkImportLeadsUseCase(lead_repo=lead_repo)
        data = BulkImportInput(rows=[self._row("dup@test.com")], owner_id=uuid4())

        result = await uc.execute(data)
        assert result.created == 0
        assert result.skipped == 1

    async def test_records_error_for_invalid_row(self, lead_repo):
        lead_repo.find_by_email.side_effect = RuntimeError("DB error")
        uc = BulkImportLeadsUseCase(lead_repo=lead_repo)
        data = BulkImportInput(rows=[self._row()], owner_id=uuid4())

        result = await uc.execute(data)
        assert result.error_count == 1
        assert "DB error" in result.errors[0]


# ── RefreshTokenUseCase ────────────────────────────────────────────────────────

class TestRefreshToken:
    def _make_user(self) -> User:
        return User.create(
            first_name="T", last_name="U",
            email=Email("tu@example.com"), role=UserRole.MANAGER,
        )

    @pytest.fixture
    def user_repo(self):
        return AsyncMock()

    async def test_returns_new_tokens_on_valid_refresh(self, user_repo):
        user = self._make_user()
        user_repo.find_by_id.return_value = user
        token = create_refresh_token(user_id=user.id, role=user.role.value)
        uc = RefreshTokenUseCase(user_repo=user_repo)

        result = await uc.execute(RefreshTokenInput(refresh_token=token))
        assert result.access_token
        assert result.refresh_token

    async def test_raises_401_on_invalid_token(self, user_repo):
        uc = RefreshTokenUseCase(user_repo=user_repo)
        with pytest.raises(HTTPException) as exc_info:
            await uc.execute(RefreshTokenInput(refresh_token="invalid.token.here"))
        assert exc_info.value.status_code == 401

    async def test_raises_401_when_user_not_found(self, user_repo):
        user = self._make_user()
        token = create_refresh_token(user_id=user.id, role=user.role.value)
        user_repo.find_by_id.return_value = None
        uc = RefreshTokenUseCase(user_repo=user_repo)

        with pytest.raises(HTTPException) as exc_info:
            await uc.execute(RefreshTokenInput(refresh_token=token))
        assert exc_info.value.status_code == 401

    async def test_raises_401_when_user_inactive(self, user_repo):
        user = self._make_user()
        user.is_active = False
        user_repo.find_by_id.return_value = user
        token = create_refresh_token(user_id=user.id, role=user.role.value)
        uc = RefreshTokenUseCase(user_repo=user_repo)

        with pytest.raises(HTTPException) as exc_info:
            await uc.execute(RefreshTokenInput(refresh_token=token))
        assert exc_info.value.status_code == 401
