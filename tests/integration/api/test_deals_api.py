"""
API интеграционные тесты /api/v1/deals.
Для создания сделки нужны: pipeline + stage + qualified lead.
Все создаются через API в module-scoped фикстурах.

Правильные поля запросов (из DTO/схем):
  POST /deals:       lead_id, stage_id, pipeline_id, deal_title, deal_value_amount
  PATCH /{id}/stage: new_stage_id, pipeline_id, performed_by_id
  PATCH /{id}/close: outcome
"""
from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _create_qualified_lead(
    client: AsyncClient, auth_headers: dict, owner_id: str | None = None
) -> str:
    """Создаёт лида и переводит его в qualified. Возвращает lead id."""
    payload: dict = {"first_name": "Q", "last_name": "L", "email": f"q_{uuid4().hex[:8]}@t.com"}
    if owner_id:
        payload["owner_id"] = owner_id
    resp = await client.post("/api/v1/leads", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    lid = resp.json()["id"]
    await client.patch(f"/api/v1/leads/{lid}", json={"status": "contacted"}, headers=auth_headers)
    await client.patch(f"/api/v1/leads/{lid}", json={"status": "qualified"}, headers=auth_headers)
    return lid


# ── Module-scoped setup: pipeline + 2 stages ─────────────────────────────────

@pytest_asyncio.fixture(scope="module")
async def pipeline(test_app, auth_headers):
    """Создаёт pipeline + 2 этапа через API."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        p = await ac.post(
            "/api/v1/pipelines",
            json={"name": "Deals Test Pipeline"},
            headers=auth_headers,
        )
        assert p.status_code == 201, p.text
        pid = p.json()["id"]

        s1 = await ac.post(
            f"/api/v1/pipelines/{pid}/stages",
            json={"name": "Stage A", "probability": 0.3},
            headers=auth_headers,
        )
        assert s1.status_code == 201, s1.text
        # POST /pipelines/{id}/stages returns PipelineOutput — stage id is in stages list
        sid1 = s1.json()["stages"][-1]["id"]

        s2 = await ac.post(
            f"/api/v1/pipelines/{pid}/stages",
            json={"name": "Stage B", "probability": 0.7},
            headers=auth_headers,
        )
        assert s2.status_code == 201, s2.text
        sid2 = s2.json()["stages"][-1]["id"]

    return {"pipeline_id": pid, "stage_id": sid1, "stage2_id": sid2}


@pytest_asyncio.fixture(scope="module")
async def qualified_lead(test_app, auth_headers, admin_user):
    """Квалифицированный лид для тестов создания сделок."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        return await _create_qualified_lead(ac, auth_headers, admin_user["id"])


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCreateDeal:
    async def test_create_deal_returns_201(
        self, client: AsyncClient, auth_headers: dict, pipeline: dict, qualified_lead: str
    ) -> None:
        resp = await client.post(
            "/api/v1/deals",
            json={
                "lead_id": qualified_lead,
                "pipeline_id": pipeline["pipeline_id"],
                "stage_id": pipeline["stage_id"],
                "deal_title": "Big Deal",
                "deal_value_amount": "5000.00",
                "deal_value_currency": "USD",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["title"] == "Big Deal"
        assert body["status"] == "open"

    async def test_create_deal_unqualified_lead_returns_error(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict, pipeline: dict
    ) -> None:
        """Неквалифицированный лид не конвертируется в сделку."""
        cr = await client.post(
            "/api/v1/leads",
            json={"first_name": "U", "last_name": "L", "email": f"uql_{uuid4().hex[:6]}@t.com", "owner_id": admin_user["id"]},
            headers=auth_headers,
        )
        lid = cr.json()["id"]
        resp = await client.post(
            "/api/v1/deals",
            json={
                "lead_id": lid,
                "pipeline_id": pipeline["pipeline_id"],
                "stage_id": pipeline["stage_id"],
                "deal_title": "Should Fail",
                "deal_value_amount": "100",
            },
            headers=auth_headers,
        )
        assert resp.status_code in (400, 422)

    async def test_create_deal_missing_required_fields_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """POST /deals без обязательных полей возвращает 422."""
        resp = await client.post("/api/v1/deals", json={}, headers=auth_headers)
        assert resp.status_code == 422


class TestListDeals:
    async def test_list_deals_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/deals", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_deals_filter_by_pipeline(
        self, client: AsyncClient, auth_headers: dict, pipeline: dict
    ) -> None:
        resp = await client.get(
            f"/api/v1/deals?pipeline_id={pipeline['pipeline_id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        for deal in resp.json():
            assert deal["pipeline_id"] == pipeline["pipeline_id"]

    async def test_list_deals_no_auth_still_works(self, client: AsyncClient) -> None:
        """GET /deals не требует авторизации."""
        resp = await client.get("/api/v1/deals")
        assert resp.status_code == 200


class TestMoveDealStage:
    async def test_move_deal_stage_returns_200(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict, pipeline: dict
    ) -> None:
        lid = await _create_qualified_lead(client, auth_headers, admin_user["id"])
        cr = await client.post(
            "/api/v1/deals",
            json={
                "lead_id": lid,
                "pipeline_id": pipeline["pipeline_id"],
                "stage_id": pipeline["stage_id"],
                "deal_title": "Movable",
                "deal_value_amount": "1000",
            },
            headers=auth_headers,
        )
        deal_id = cr.json()["id"]

        resp = await client.patch(
            f"/api/v1/deals/{deal_id}/stage",
            json={
                "new_stage_id": pipeline["stage2_id"],
                "pipeline_id": pipeline["pipeline_id"],
                "performed_by_id": admin_user["id"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["stage_id"] == pipeline["stage2_id"]

    async def test_move_deal_stage_not_found_returns_404(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict, pipeline: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/deals/{uuid4()}/stage",
            json={
                "new_stage_id": pipeline["stage_id"],
                "pipeline_id": pipeline["pipeline_id"],
                "performed_by_id": admin_user["id"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestCloseDeal:
    async def test_close_deal_won_returns_200(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict, pipeline: dict
    ) -> None:
        lid = await _create_qualified_lead(client, auth_headers, admin_user["id"])
        cr = await client.post(
            "/api/v1/deals",
            json={
                "lead_id": lid,
                "pipeline_id": pipeline["pipeline_id"],
                "stage_id": pipeline["stage_id"],
                "deal_title": "Won Deal",
                "deal_value_amount": "3000",
            },
            headers=auth_headers,
        )
        deal_id = cr.json()["id"]

        resp = await client.patch(
            f"/api/v1/deals/{deal_id}/close",
            json={"outcome": "won"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "won"

    async def test_close_deal_lost_returns_200(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict, pipeline: dict
    ) -> None:
        lid = await _create_qualified_lead(client, auth_headers, admin_user["id"])
        cr = await client.post(
            "/api/v1/deals",
            json={
                "lead_id": lid,
                "pipeline_id": pipeline["pipeline_id"],
                "stage_id": pipeline["stage_id"],
                "deal_title": "Lost Deal",
                "deal_value_amount": "500",
            },
            headers=auth_headers,
        )
        deal_id = cr.json()["id"]

        resp = await client.patch(
            f"/api/v1/deals/{deal_id}/close",
            json={"outcome": "lost"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "lost"

    async def test_close_already_closed_deal_returns_400(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict, pipeline: dict
    ) -> None:
        lid = await _create_qualified_lead(client, auth_headers, admin_user["id"])
        cr = await client.post(
            "/api/v1/deals",
            json={
                "lead_id": lid,
                "pipeline_id": pipeline["pipeline_id"],
                "stage_id": pipeline["stage_id"],
                "deal_title": "Double Close",
                "deal_value_amount": "100",
            },
            headers=auth_headers,
        )
        did = cr.json()["id"]
        await client.patch(f"/api/v1/deals/{did}/close", json={"outcome": "won"}, headers=auth_headers)

        resp = await client.patch(
            f"/api/v1/deals/{did}/close",
            json={"outcome": "lost"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    async def test_close_deal_not_found_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/deals/{uuid4()}/close",
            json={"outcome": "lost"},
            headers=auth_headers,
        )
        assert resp.status_code == 404
