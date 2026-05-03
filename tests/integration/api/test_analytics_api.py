"""
API интеграционные тесты /api/v1/analytics.
Проверяет all 5 endpoints включая CSV экспорт.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestAnalyticsOverview:
    async def test_overview_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "total_leads" in body
        assert "total_deals" in body
        assert "overall_win_rate" in body
        assert "conversion_funnel" in body
        assert "pipeline_stats" in body

    async def test_overview_win_rate_in_range(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics", headers=auth_headers)
        body = resp.json()
        assert 0.0 <= body["overall_win_rate"] <= 100.0
        assert 0.0 <= body["conversion_rate"] <= 100.0

    async def test_overview_funnel_statuses(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics", headers=auth_headers)
        funnel = resp.json()["conversion_funnel"]
        statuses = {step["status"] for step in funnel}
        assert statuses <= {"new", "contacted", "qualified", "unqualified", "converted"}

    async def test_overview_no_auth_still_works(self, client: AsyncClient) -> None:
        """GET /analytics не требует авторизации."""
        resp = await client.get("/api/v1/analytics")
        assert resp.status_code == 200


class TestRevenueForecast:
    async def test_forecast_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/forecast", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "closed_revenue" in body
        assert "pipeline_value" in body
        assert "weighted_forecast" in body
        assert "by_pipeline" in body
        assert "by_stage" in body

    async def test_forecast_values_non_negative(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/forecast", headers=auth_headers)
        body = resp.json()
        assert body["closed_revenue"] >= 0
        assert body["pipeline_value"] >= 0
        assert body["weighted_forecast"] >= 0

    async def test_forecast_no_auth_still_works(self, client: AsyncClient) -> None:
        """GET /analytics/forecast не требует авторизации."""
        resp = await client.get("/api/v1/analytics/forecast")
        assert resp.status_code == 200


class TestDashboardAnalytics:
    async def test_dashboard_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "total_leads" in body
        assert "total_deals" in body
        assert "pipeline_value" in body
        assert "leads_by_status" in body
        assert "deals_by_status" in body

    async def test_dashboard_leads_by_status_structure(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        lbs = resp.json()["leads_by_status"]
        for key in ("new", "contacted", "qualified", "unqualified", "converted"):
            assert key in lbs
            assert lbs[key] >= 0


class TestManagersReport:
    async def test_managers_report_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/managers", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "managers" in body
        assert "total_managers" in body
        assert isinstance(body["managers"], list)

    async def test_managers_report_structure(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/managers", headers=auth_headers)
        managers = resp.json()["managers"]
        for m in managers:
            assert "manager_name" in m
            assert "manager_email" in m
            assert "win_rate" in m
            assert 0.0 <= m["win_rate"] <= 100.0

    async def test_managers_report_no_auth_still_works(self, client: AsyncClient) -> None:
        """GET /analytics/managers не требует авторизации."""
        resp = await client.get("/api/v1/analytics/managers")
        assert resp.status_code == 200


class TestAnalyticsCsvExport:
    async def test_export_csv_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/export/csv", headers=auth_headers)
        assert resp.status_code == 200

    async def test_export_csv_content_type(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/export/csv", headers=auth_headers)
        assert "text/csv" in resp.headers["content-type"]

    async def test_export_csv_has_attachment_header(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/export/csv", headers=auth_headers)
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert ".csv" in resp.headers.get("content-disposition", "")

    async def test_export_csv_contains_sections(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/analytics/export/csv", headers=auth_headers)
        content = resp.text
        assert "# OVERVIEW" in content
        assert "# CONVERSION FUNNEL" in content
        assert "# PIPELINE BREAKDOWN" in content
        assert "# REVENUE FORECAST" in content
        assert "# MANAGERS REPORT" in content

    async def test_export_csv_unauthorized_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/analytics/export/csv")
        assert resp.status_code == 401
