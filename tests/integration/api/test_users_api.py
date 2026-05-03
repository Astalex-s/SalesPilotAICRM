"""
API интеграционные тесты /api/v1/users.
Покрывает: list, update_profile, change_password, update_role.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestListUsers:
    async def test_list_users_admin_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/users", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_users_contains_admin(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        resp = await client.get("/api/v1/users", headers=auth_headers)
        ids = [u["id"] for u in resp.json()]
        assert admin_user["id"] in ids

    async def test_list_users_unauthorized_returns_401(
        self, client: AsyncClient
    ) -> None:
        resp = await client.get("/api/v1/users")
        assert resp.status_code == 401


class TestUpdateMyProfile:
    async def test_update_profile_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.patch(
            "/api/v1/users/me",
            json={"first_name": "Updated", "last_name": "Name"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["first_name"] == "Updated"
        assert body["last_name"] == "Name"

    async def test_update_profile_missing_fields_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.patch(
            "/api/v1/users/me",
            json={"first_name": "Only"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_update_profile_unauthorized_returns_401(
        self, client: AsyncClient
    ) -> None:
        resp = await client.patch(
            "/api/v1/users/me",
            json={"first_name": "A", "last_name": "B"},
        )
        assert resp.status_code == 401


class TestChangePassword:
    async def test_change_password_returns_204(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.post(
            "/api/v1/users/me/password",
            json={"current_password": "adminpass123", "new_password": "NewPass456!"},
            headers=auth_headers,
        )
        assert resp.status_code == 204

    async def test_change_password_wrong_current_returns_400(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.post(
            "/api/v1/users/me/password",
            json={"current_password": "WrongPassword", "new_password": "NewPass456!"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    async def test_change_password_short_new_password_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.post(
            "/api/v1/users/me/password",
            json={"current_password": "adminpass123", "new_password": "123"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_change_password_unauthorized_returns_401(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            "/api/v1/users/me/password",
            json={"current_password": "adminpass123", "new_password": "NewPass456!"},
        )
        assert resp.status_code == 401


class TestUpdateUserRole:
    async def test_update_role_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        # Register a separate user to change role (keeps admin as admin)
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Role",
                "last_name": "Target",
                "email": f"roletarget_{uuid4().hex[:6]}@test.com",
                "password": "Pass123!",
            },
        )
        target_id = reg.json()["id"]

        resp = await client.patch(
            f"/api/v1/users/{target_id}/role",
            json={"role": "admin"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    async def test_update_role_invalid_role_returns_422(
        self, client: AsyncClient, auth_headers: dict, admin_user: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/users/{admin_user['id']}/role",
            json={"role": "superuser"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_update_role_unauthorized_returns_401(
        self, client: AsyncClient, admin_user: dict
    ) -> None:
        resp = await client.patch(
            f"/api/v1/users/{admin_user['id']}/role",
            json={"role": "admin"},
        )
        assert resp.status_code == 401
