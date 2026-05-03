"""
Юнит-тесты UploadDealAttachmentUseCase и DeleteDealAttachmentUseCase.
"""
from __future__ import annotations

import os
import pytest
import tempfile
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from src.application.exceptions import DealNotFoundError
from src.application.use_cases.upload_deal_attachment import UploadDealAttachmentUseCase, MAX_FILE_SIZE
from src.application.use_cases.delete_deal_attachment import DeleteDealAttachmentUseCase
from src.domain.entities.deal import Deal
from src.domain.entities.deal_attachment import DealAttachment
from src.domain.value_objects.money import Money


def _make_deal() -> Deal:
    return Deal.create("Test Deal", uuid4(), uuid4(), uuid4(), Money(Decimal("1000")))


def _make_attachment(deal_id=None, storage_path="/tmp/test.pdf") -> DealAttachment:
    return DealAttachment.create(
        deal_id=deal_id or uuid4(),
        filename="test.pdf",
        storage_path=storage_path,
        content_type="application/pdf",
        size_bytes=1024,
        uploaded_by_id=uuid4(),
    )


# ── UploadDealAttachmentUseCase ────────────────────────────────────────────────

@pytest.fixture
def deal_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def attachment_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def upload_use_case(deal_repo, attachment_repo) -> UploadDealAttachmentUseCase:
    with tempfile.TemporaryDirectory() as tmpdir:
        yield UploadDealAttachmentUseCase(
            deal_repo=deal_repo,
            attachment_repo=attachment_repo,
            uploads_dir=tmpdir,
        )


class TestUploadDealAttachment:
    async def test_raises_when_deal_not_found(self, deal_repo, attachment_repo):
        deal_repo.get_by_id.return_value = None
        with tempfile.TemporaryDirectory() as tmpdir:
            uc = UploadDealAttachmentUseCase(deal_repo, attachment_repo, tmpdir)
            with pytest.raises(DealNotFoundError):
                await uc.execute(uuid4(), "file.pdf", "application/pdf", b"data", uuid4())

    async def test_raises_when_file_too_large(self, deal_repo, attachment_repo):
        deal_repo.get_by_id.return_value = _make_deal()
        oversized = b"x" * (MAX_FILE_SIZE + 1)
        with tempfile.TemporaryDirectory() as tmpdir:
            uc = UploadDealAttachmentUseCase(deal_repo, attachment_repo, tmpdir)
            with pytest.raises(ValueError, match="максимальный размер"):
                await uc.execute(uuid4(), "big.pdf", "application/pdf", oversized, uuid4())

    async def test_saves_file_and_returns_output(self, deal_repo, attachment_repo):
        deal = _make_deal()
        deal_repo.get_by_id.return_value = deal

        with tempfile.TemporaryDirectory() as tmpdir:
            uc = UploadDealAttachmentUseCase(deal_repo, attachment_repo, tmpdir)
            result = await uc.execute(deal.id, "doc.pdf", "application/pdf", b"content", uuid4())

        assert result.filename == "doc.pdf"
        assert result.size_bytes == len(b"content")
        attachment_repo.save.assert_called_once()


# ── DeleteDealAttachmentUseCase ────────────────────────────────────────────────

@pytest.fixture
def delete_attachment_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def delete_use_case(delete_attachment_repo) -> DeleteDealAttachmentUseCase:
    return DeleteDealAttachmentUseCase(attachment_repo=delete_attachment_repo)


class TestDeleteDealAttachment:
    async def test_idempotent_when_not_found(self, delete_use_case, delete_attachment_repo):
        delete_attachment_repo.get_by_id.return_value = None
        await delete_use_case.execute(uuid4())
        delete_attachment_repo.delete.assert_not_called()

    async def test_deletes_file_and_db_record(self, delete_use_case, delete_attachment_repo):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
            f.write(b"test")

        try:
            att = _make_attachment(storage_path=path)
            delete_attachment_repo.get_by_id.return_value = att

            await delete_use_case.execute(att.id)

            assert not os.path.exists(path)
            delete_attachment_repo.delete.assert_called_once_with(att.id)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    async def test_logs_warning_when_file_not_on_disk(self, delete_use_case, delete_attachment_repo):
        att = _make_attachment(storage_path="/nonexistent/path/file.pdf")
        delete_attachment_repo.get_by_id.return_value = att

        # Should not raise even if file doesn't exist
        await delete_use_case.execute(att.id)
        delete_attachment_repo.delete.assert_called_once()

    async def test_handles_os_error_gracefully(self, delete_use_case, delete_attachment_repo):
        att = _make_attachment(storage_path="/some/path.pdf")
        delete_attachment_repo.get_by_id.return_value = att

        with patch("src.application.use_cases.delete_deal_attachment.os.path.exists", return_value=True), \
             patch("src.application.use_cases.delete_deal_attachment.os.remove", side_effect=OSError("Permission denied")):
            await delete_use_case.execute(att.id)  # should not raise

        delete_attachment_repo.delete.assert_called_once()
