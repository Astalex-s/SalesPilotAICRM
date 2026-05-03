"""
API интеграционные тесты /api/v1/pipelines.
Покрывает: list, create, get, update, delete pipeline + add/update/delete stage.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ── Module-scoped pipeline fixture ────────────────────────────────────────────

@pytest_asyncio.fixture(scope="module")
async def pipeline(test_app, auth_headers):
    """Создаёт pipeline с одним этапом, возвращает словарь с id."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        p = await ac.post(
            "/api/v1/pipelines",
            json={"name": "Pipelines Test Pipeline"},
            headers=auth_headers,
        )
        assert p.status_code == 201, p.text
        pid = p.json()["id"]

        s = await ac.post(
            f"/api/v1/pipelines/{pid}/stages",
            json={"name": "Stage One", "probability": 0.5},
            headers=auth_headers,
        )
        assert s.status_code == 201, s.text
        # POST /pipelines/{id}/stages returns PipelineOutput → stage id in stages list
        sid = s.json()["stages"][-1]["id"]

    return {"pipeline_id": pid, "stage_id": sid}


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestListPipelines:
    async def test_list_pipelines_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/pipelines", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_pipelines_unauthorized_returns_401(
        self, client: AsyncClient
    ) -> None:
        resp = await client.get("/api/v1/pipelines")
        assert resp.status_code == 401


class TestCreatePipeline:
    async def test_create_pipeline_returns_201(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.post(
            "/api/v1/pipelines",
            json={"name": "New Pipeline"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "New Pipeline"
        assert "id" in body
        assert isinstance(body["stages"], list)

    async def test_create_pipeline_missing_name_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.post(
            "/api/v1/pipelines",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_create_pipeline_unauthorized_returns_401(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            "/api/v1/pipelines",
            json={"name": "Unauth Pipeline"},
        )
        assert resp.status_code == 401


class TestGetPipeline:
    async def test_get_pipeline_returns_200(
        self, client: AsyncClient, auth_headers: dict, pipeline: dict
    ) -> None:
        resp = await client.get(
            f"/api/v1/pipelines/{pipeline['pipeline_id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == pipeline["pipeline_id"]
        assert isinstance(body["stages"], list)

    async def test_get_pipeline_not_found_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get(
            f"/api/v1/pipelines/{uuid4()}",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_get_pipeline_unauthorized_returns_401(
        self, client: AsyncClient, pipeline: dict
    ) -> None:
        resp = await client.get(f"/api/v1/pipelines/{pipeline['pipeline_id']}")
        assert resp.status_code == 401


class TestUpdatePipeline:
    async def test_update_pipeline_returns_200(
        self, client: AsyncClient, auth_headers: dict, pipeline: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/pipelines/{pipeline['pipeline_id']}",
            json={"name": "Renamed Pipeline"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed Pipeline"

    async def test_update_pipeline_not_found_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/pipelines/{uuid4()}",
            json={"name": "Ghost"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestStageManagement:
    async def test_add_stage_returns_201(
        self, client: AsyncClient, auth_headers: dict, pipeline: dict
    ) -> None:
        resp = await client.post(
            f"/api/v1/pipelines/{pipeline['pipeline_id']}/stages",
            json={"name": "New Stage", "probability": 0.8},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        stages = resp.json()["stages"]
        names = [s["name"] for s in stages]
        assert "New Stage" in names

    async def test_update_stage_returns_200(
        self, client: AsyncClient, auth_headers: dict, pipeline: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/pipelines/{pipeline['pipeline_id']}/stages/{pipeline['stage_id']}",
            json={"name": "Updated Stage", "probability": 0.9},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        stages = resp.json()["stages"]
        names = [s["name"] for s in stages]
        assert "Updated Stage" in names

    async def test_delete_stage_returns_200(
        self, client: AsyncClient, auth_headers: dict, pipeline: dict
    ) -> None:
        # Create a temporary stage to delete
        add_resp = await client.post(
            f"/api/v1/pipelines/{pipeline['pipeline_id']}/stages",
            json={"name": "Temp Stage", "probability": 0.1},
            headers=auth_headers,
        )
        temp_stage_id = add_resp.json()["stages"][-1]["id"]

        resp = await client.delete(
            f"/api/v1/pipelines/{pipeline['pipeline_id']}/stages/{temp_stage_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        stage_ids = [s["id"] for s in resp.json()["stages"]]
        assert temp_stage_id not in stage_ids

    async def test_add_stage_unauthorized_returns_401(
        self, client: AsyncClient, pipeline: dict
    ) -> None:
        resp = await client.post(
            f"/api/v1/pipelines/{pipeline['pipeline_id']}/stages",
            json={"name": "Unauth Stage", "probability": 0.5},
        )
        assert resp.status_code == 401


class TestDeletePipeline:
    async def test_delete_pipeline_returns_204(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        # Create a throwaway pipeline
        create = await client.post(
            "/api/v1/pipelines",
            json={"name": "To Delete"},
            headers=auth_headers,
        )
        pid = create.json()["id"]

        resp = await client.delete(
            f"/api/v1/pipelines/{pid}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

    async def test_delete_pipeline_not_found_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.delete(
            f"/api/v1/pipelines/{uuid4()}",
            headers=auth_headers,
        )
        assert resp.status_code == 404
