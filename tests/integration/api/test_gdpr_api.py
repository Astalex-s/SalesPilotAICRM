"""
API интеграционные тесты /api/v1/gdpr.
Покрывает: delete_user_data, anonymize_lead, audit_log, export_user_data, retention_policy.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ── Module-scoped fixtures ─────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="module")
async def disposable_user(test_app, auth_headers):
    """Пользователь с лидом для удаления через GDPR — создаётся один раз."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        reg = await ac.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Delete",
                "last_name": "Me",
                "email": f"disposable_{uuid4().hex[:6]}@test.com",
                "password": "Pass123!",
            },
        )
        assert reg.status_code == 201, reg.text
        user = reg.json()
        # Create a lead for this user so delete_user_data has something to delete
        lead = await ac.post(
            "/api/v1/leads",
            json={
                "first_name": "To",
                "last_name": "Delete",
                "email": f"todelete_{uuid4().hex[:6]}@test.com",
                "owner_id": user["id"],
            },
        )
        assert lead.status_code == 201, lead.text
        return user


@pytest_asyncio.fixture(scope="module")
async def lead_for_anonymize(test_app, auth_headers, admin_user):
    """Лид для анонимизации — создаётся один раз."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/v1/leads",
            json={
                "first_name": "Jane",
                "last_name": "PII",
                "email": f"pii_{uuid4().hex[:6]}@test.com",
                "owner_id": admin_user["id"],
                "phone": "+79999999999",
                "company": "PII Corp",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        return resp.json()


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestExportUserData:
    async def test_export_returns_200(
        self, client: AsyncClient, admin_user: dict
    ) -> None:
        resp = await client.get(f"/api/v1/gdpr/users/{admin_user['id']}/export")
        assert resp.status_code == 200

    async def test_export_content_disposition(
        self, client: AsyncClient, admin_user: dict
    ) -> None:
        resp = await client.get(f"/api/v1/gdpr/users/{admin_user['id']}/export")
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert "gdpr_export" in resp.headers.get("content-disposition", "")

    async def test_export_json_structure(
        self, client: AsyncClient, admin_user: dict
    ) -> None:
        resp = await client.get(f"/api/v1/gdpr/users/{admin_user['id']}/export")
        body = resp.json()
        assert "user_id" in body
        assert "exported_at" in body
        assert "leads" in body
        assert "deals" in body


class TestAnonymizeLead:
    async def test_anonymize_lead_returns_200(
        self, client: AsyncClient, lead_for_anonymize: dict
    ) -> None:
        resp = await client.post(
            f"/api/v1/gdpr/leads/{lead_for_anonymize['id']}/anonymize"
        )
        assert resp.status_code == 200

    async def test_anonymize_lead_response_structure(
        self, client: AsyncClient, lead_for_anonymize: dict, auth_headers: dict
    ) -> None:
        # Lead was already anonymized in previous test — check its current state
        resp = await client.get(
            f"/api/v1/leads/{lead_for_anonymize['id']}", headers=auth_headers
        )
        assert resp.status_code == 200

    async def test_anonymize_nonexistent_lead_returns_error(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(f"/api/v1/gdpr/leads/{uuid4()}/anonymize")
        assert resp.status_code in (400, 404)


class TestGdprAuditLog:
    async def test_audit_log_returns_200(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/gdpr/audit-log")
        assert resp.status_code == 200

    async def test_audit_log_structure(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/gdpr/audit-log")
        body = resp.json()
        assert "entries" in body
        assert "total" in body
        assert isinstance(body["entries"], list)

    async def test_audit_log_pagination(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/gdpr/audit-log?limit=5&offset=0")
        assert resp.status_code == 200

    async def test_audit_log_invalid_limit_returns_422(
        self, client: AsyncClient
    ) -> None:
        resp = await client.get("/api/v1/gdpr/audit-log?limit=0")
        assert resp.status_code == 422


class TestApplyRetentionPolicy:
    async def test_retention_policy_returns_200(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/gdpr/retention/apply")
        assert resp.status_code == 200

    async def test_retention_policy_response_structure(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post("/api/v1/gdpr/retention/apply")
        body = resp.json()
        assert "leads_deleted" in body
        assert "deals_deleted" in body
        assert "retention_days" in body
        assert isinstance(body["leads_deleted"], int)
        assert isinstance(body["deals_deleted"], int)


class TestDeleteUserData:
    async def test_delete_user_data_returns_200(
        self, client: AsyncClient, disposable_user: dict
    ) -> None:
        resp = await client.post(
            f"/api/v1/gdpr/users/{disposable_user['id']}/delete"
        )
        assert resp.status_code == 200

    async def test_delete_user_data_structure(
        self, client: AsyncClient, disposable_user: dict
    ) -> None:
        # Use a new user with a lead (disposable was deleted, create fresh one)
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Del2",
                "last_name": "User",
                "email": f"del2_{uuid4().hex[:6]}@test.com",
                "password": "Pass123!",
            },
        )
        uid = reg.json()["id"]
        await client.post(
            "/api/v1/leads",
            json={
                "first_name": "Lead",
                "last_name": "ForDelete",
                "email": f"leadfordel_{uuid4().hex[:6]}@test.com",
                "owner_id": uid,
            },
        )
        resp = await client.post(f"/api/v1/gdpr/users/{uid}/delete")
        assert resp.status_code == 200
        body = resp.json()
        assert "user_id" in body
        assert "leads_deleted" in body
        assert "deals_deleted" in body
