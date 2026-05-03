"""
API интеграционные тесты /api/v1/leads.
Реальные use cases + SQLite in-memory.

Правильные поля:
  POST /leads:              first_name, last_name, email, owner_id (обязателен)
  POST /leads/bulk-import:  multipart file= CSV
  BulkImportResult:         created, skipped, error_count, errors, leads
"""
from __future__ import annotations

import io
from uuid import uuid4

import pytest
from httpx import AsyncClient


def _lead_payload(owner_id: str, **kwargs) -> dict:
    """Минимальный payload для создания лида."""
    base = {
        "first_name": "Test",
        "last_name": "Lead",
        "email": f"lead_{uuid4().hex[:8]}@test.com",
        "owner_id": owner_id,
    }
    base.update(kwargs)
    return base


class TestCreateLead:
    async def test_create_lead_returns_201(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        resp = await client.post(
            "/api/v1/leads", json=_lead_payload(admin_user["id"]), headers=auth_headers
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["status"] == "new"
        assert "id" in body

    async def test_create_lead_with_optional_fields(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        payload = _lead_payload(
            admin_user["id"],
            phone="+79001234567",
            company="ACME Corp",
            source="referral",
        )
        resp = await client.post("/api/v1/leads", json=payload, headers=auth_headers)
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["company"] == "ACME Corp"
        assert body["source"] == "referral"

    async def test_create_lead_duplicate_email_returns_409(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        email = f"dup_{uuid4().hex[:8]}@test.com"
        payload = _lead_payload(admin_user["id"], email=email)
        await client.post("/api/v1/leads", json=payload, headers=auth_headers)
        resp = await client.post("/api/v1/leads", json=payload, headers=auth_headers)
        assert resp.status_code == 409

    async def test_create_lead_no_auth_still_works(
        self, client: AsyncClient, admin_user: dict
    ) -> None:
        """POST /leads не требует авторизации (публичный endpoint)."""
        resp = await client.post("/api/v1/leads", json=_lead_payload(admin_user["id"]))
        assert resp.status_code == 201

    async def test_create_lead_invalid_email_returns_422(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        resp = await client.post(
            "/api/v1/leads",
            json=_lead_payload(admin_user["id"], email="not-an-email"),
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestListLeads:
    async def test_list_leads_returns_200(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        # Ensure at least one lead exists
        await client.post(
            "/api/v1/leads", json=_lead_payload(admin_user["id"]), headers=auth_headers
        )
        resp = await client.get("/api/v1/leads", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_leads_filter_by_status(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/leads?lead_status=new", headers=auth_headers)
        assert resp.status_code == 200
        for lead in resp.json():
            assert lead["status"] == "new"

    async def test_list_leads_no_auth_still_works(self, client: AsyncClient) -> None:
        """GET /leads не требует авторизации (публичный endpoint)."""
        resp = await client.get("/api/v1/leads")
        assert resp.status_code == 200


class TestGetLead:
    async def test_get_lead_by_id(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        create_resp = await client.post(
            "/api/v1/leads", json=_lead_payload(admin_user["id"]), headers=auth_headers
        )
        lead_id = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/leads/{lead_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == lead_id

    async def test_get_lead_not_found_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get(f"/api/v1/leads/{uuid4()}", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateLeadStatus:
    async def test_qualify_lead(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        create_resp = await client.post(
            "/api/v1/leads", json=_lead_payload(admin_user["id"]), headers=auth_headers
        )
        lead_id = create_resp.json()["id"]

        # new → contacted → qualified
        await client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"status": "contacted"},
            headers=auth_headers,
        )
        resp = await client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"status": "qualified"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "qualified"

    async def test_invalid_status_transition_returns_422(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        create_resp = await client.post(
            "/api/v1/leads", json=_lead_payload(admin_user["id"]), headers=auth_headers
        )
        lead_id = create_resp.json()["id"]

        # new → qualified (valid), then qualified → contacted (invalid per domain FSM)
        await client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"status": "qualified"},
            headers=auth_headers,
        )
        resp = await client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"status": "contacted"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_update_lead_not_found_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/leads/{uuid4()}",
            json={"status": "contacted"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestBulkImportLeads:
    async def test_bulk_import_csv_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        csv_content = (
            "first_name,last_name,email,company,phone,source\n"
            f"Ivan,Petrov,ivan_{uuid4().hex[:6]}@test.com,OOO Romashka,+79001111111,website\n"
            f"Maria,Sidorova,maria_{uuid4().hex[:6]}@test.com,IP Sidorov,,referral\n"
        )
        files = {"file": ("leads.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        resp = await client.post(
            "/api/v1/leads/bulk-import", files=files, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["created"] == 2
        assert body["skipped"] == 0

    async def test_bulk_import_skips_duplicate_emails(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        email = f"once_{uuid4().hex[:6]}@test.com"
        csv1 = f"first_name,last_name,email\nFirst,Last,{email}\n"
        await client.post(
            "/api/v1/leads/bulk-import",
            files={"file": ("a.csv", io.BytesIO(csv1.encode()), "text/csv")},
            headers=auth_headers,
        )
        # Second import with same email → skipped
        csv2 = f"first_name,last_name,email\nFirst2,Last2,{email}\n"
        resp = await client.post(
            "/api/v1/leads/bulk-import",
            files={"file": ("b.csv", io.BytesIO(csv2.encode()), "text/csv")},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["created"] == 0
        assert body["skipped"] == 1
