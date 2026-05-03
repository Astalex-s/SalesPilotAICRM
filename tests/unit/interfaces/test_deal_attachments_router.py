"""
Юнит-тесты роутера /api/v1/deals/{deal_id}/attachments.
Use cases заменены AsyncMock; auth dependency перекрыт.
"""
from __future__ import annotations

import io
import tempfile
import os
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from src.application.dtos.auth_dtos import UserOutput
from src.application.dtos.deal_attachment_dtos import DealAttachmentOutput
from src.application.exceptions import DealNotFoundError
from src.domain.value_objects.enums import UserRole
from src.interfaces.api.auth_dependencies import get_current_user
from src.interfaces.api.dependencies import (
    get_attachment_repo,
    get_delete_attachment_use_case,
    get_list_attachments_use_case,
    get_upload_attachment_use_case,
)
from src.interfaces.api.v1.routers.deal_attachments import router


def _fake_user() -> UserOutput:
    return UserOutput(
        id=uuid4(), first_name="T", last_name="U",
        email="tu@test.com", role=UserRole.MANAGER, is_active=True,
    )


def _fake_attachment(deal_id=None) -> DealAttachmentOutput:
    from datetime import datetime, timezone
    return DealAttachmentOutput(
        id=uuid4(),
        deal_id=deal_id or uuid4(),
        filename="test.pdf",
        content_type="application/pdf",
        size_bytes=512,
        uploaded_by_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )


def _build_app(upload_uc=None, list_uc=None, delete_uc=None, att_repo=None) -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: _fake_user()
    if upload_uc is not None:
        app.dependency_overrides[get_upload_attachment_use_case] = lambda: upload_uc
    if list_uc is not None:
        app.dependency_overrides[get_list_attachments_use_case] = lambda: list_uc
    if delete_uc is not None:
        app.dependency_overrides[get_delete_attachment_use_case] = lambda: delete_uc
    if att_repo is not None:
        app.dependency_overrides[get_attachment_repo] = lambda: att_repo
    return app


class TestUploadAttachment:
    def test_returns_201_on_success(self):
        upload_uc = AsyncMock()
        deal_id = uuid4()
        upload_uc.execute.return_value = _fake_attachment(deal_id)
        client = TestClient(_build_app(upload_uc=upload_uc))

        resp = client.post(
            f"/api/v1/deals/{deal_id}/attachments",
            files={"file": ("doc.pdf", b"content", "application/pdf")},
        )
        assert resp.status_code == 201
        assert resp.json()["filename"] == "test.pdf"

    def test_returns_404_when_deal_not_found(self):
        upload_uc = AsyncMock()
        upload_uc.execute.side_effect = DealNotFoundError("not found")
        client = TestClient(_build_app(upload_uc=upload_uc))

        resp = client.post(
            f"/api/v1/deals/{uuid4()}/attachments",
            files={"file": ("doc.pdf", b"content", "application/pdf")},
        )
        assert resp.status_code == 404

    def test_returns_400_on_value_error(self):
        upload_uc = AsyncMock()
        upload_uc.execute.side_effect = ValueError("максимальный размер")
        client = TestClient(_build_app(upload_uc=upload_uc))

        resp = client.post(
            f"/api/v1/deals/{uuid4()}/attachments",
            files={"file": ("big.pdf", b"x" * 10, "application/pdf")},
        )
        assert resp.status_code == 400


class TestListAttachments:
    def test_returns_200_with_list(self):
        list_uc = AsyncMock()
        deal_id = uuid4()
        list_uc.execute.return_value = [_fake_attachment(deal_id)]
        client = TestClient(_build_app(list_uc=list_uc))

        resp = client.get(f"/api/v1/deals/{deal_id}/attachments")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestDeleteAttachment:
    def test_returns_204(self):
        delete_uc = AsyncMock()
        delete_uc.execute.return_value = None
        client = TestClient(_build_app(delete_uc=delete_uc))

        resp = client.delete(f"/api/v1/deals/{uuid4()}/attachments/{uuid4()}")
        assert resp.status_code == 204


class TestDownloadAttachment:
    def test_returns_404_when_not_found(self):
        att_repo = AsyncMock()
        att_repo.get_by_id.return_value = None
        client = TestClient(_build_app(att_repo=att_repo))

        resp = client.get(f"/api/v1/deals/{uuid4()}/attachments/{uuid4()}/download")
        assert resp.status_code == 404

    def test_returns_404_when_wrong_deal(self):
        att_repo = AsyncMock()
        att = _fake_attachment(deal_id=uuid4())
        att_repo.get_by_id.return_value = att
        client = TestClient(_build_app(att_repo=att_repo))

        # Pass different deal_id than the attachment's deal_id
        resp = client.get(f"/api/v1/deals/{uuid4()}/attachments/{att.id}/download")
        assert resp.status_code == 404
