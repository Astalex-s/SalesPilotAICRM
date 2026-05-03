"""
API интеграционные тесты /api/v1/auth.
БД: SQLite in-memory. JWT декодируется реальным AuthService.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestRegister:
    async def test_register_success(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/register", json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice_reg@test.com",
            "password": "pass1234",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "alice_reg@test.com"
        assert body["first_name"] == "Alice"
        assert body["is_active"] is True

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient) -> None:
        payload = {
            "first_name": "Bob",
            "last_name": "Dup",
            "email": "dup@test.com",
            "password": "pass1234",
        }
        await client.post("/api/v1/auth/register", json=payload)
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409

    async def test_register_weak_password_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/register", json={
            "first_name": "C",
            "last_name": "D",
            "email": "short@test.com",
            "password": "abc",   # < 6 chars
        })
        assert resp.status_code == 422

    async def test_register_invalid_email_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/register", json={
            "first_name": "E",
            "last_name": "F",
            "email": "not-an-email",
            "password": "pass1234",
        })
        assert resp.status_code == 422

    async def test_register_default_role_is_sales_rep(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/register", json={
            "first_name": "G",
            "last_name": "H",
            "email": "g.h@test.com",
            "password": "pass1234",
        })
        assert resp.status_code == 201
        assert resp.json()["role"] == "sales_rep"


class TestLogin:
    async def test_login_success_returns_tokens(self, client: AsyncClient) -> None:
        email, pwd = "loginok@test.com", "pass1234"
        await client.post("/api/v1/auth/register", json={
            "first_name": "L", "last_name": "O", "email": email, "password": pwd,
        })
        resp = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_wrong_password_returns_401(self, client: AsyncClient) -> None:
        email = "wrongpwd@test.com"
        await client.post("/api/v1/auth/register", json={
            "first_name": "W", "last_name": "P", "email": email, "password": "pass1234",
        })
        resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "wrongXXX"})
        assert resp.status_code == 401

    async def test_login_unknown_email_returns_401(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@nowhere.com", "password": "pass1234",
        })
        assert resp.status_code == 401


class TestGetMe:
    async def test_get_me_returns_current_user(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "email" in body
        assert "role" in body

    async def test_get_me_without_token_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_get_me_with_invalid_token_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401


class TestRefreshToken:
    async def test_refresh_returns_new_tokens(self, client: AsyncClient) -> None:
        email, pwd = "refresh_user@test.com", "pass1234"
        await client.post("/api/v1/auth/register", json={
            "first_name": "R", "last_name": "T", "email": email, "password": pwd,
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        refresh_token = login_resp.json()["refresh_token"]

        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_refresh_with_invalid_token_returns_401(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "bad.token"})
        assert resp.status_code == 401
