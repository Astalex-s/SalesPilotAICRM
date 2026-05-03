"""
Юнит-тесты auth_dependencies: get_current_user, require_admin, require_manager.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from src.application.dtos.auth_dtos import UserOutput
from src.domain.value_objects.enums import UserRole
from src.interfaces.api.auth_dependencies import get_current_user, require_admin, require_manager


def _make_user_mock(role: UserRole = UserRole.MANAGER, is_active: bool = True) -> MagicMock:
    u = MagicMock()
    u.id = uuid4()
    u.first_name = "T"
    u.last_name = "U"
    u.email = MagicMock(__str__=lambda self: "tu@test.com")
    u.role = role
    u.is_active = is_active
    return u


class TestGetCurrentUser:
    def test_raises_401_when_no_sub_in_payload(self):
        """Токен валиден, но payload не содержит sub."""
        app = FastAPI()

        @app.get("/test")
        async def route(user: UserOutput = Depends(get_current_user)):
            return {"ok": True}

        with patch("src.interfaces.api.auth_dependencies.decode_access_token") as mock_decode:
            mock_decode.return_value = {}  # no "sub" key
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/test", headers={"Authorization": "Bearer faketoken"})

        assert resp.status_code == 401

    def test_raises_401_when_user_not_found(self):
        """Токен валиден, но пользователь не найден в БД."""
        app = FastAPI()

        @app.get("/test")
        async def route(user: UserOutput = Depends(get_current_user)):
            return {"ok": True}

        with (
            patch("src.interfaces.api.auth_dependencies.decode_access_token") as mock_decode,
            patch("src.interfaces.api.auth_dependencies.SqlUserRepository") as MockRepo,
        ):
            mock_decode.return_value = {"sub": str(uuid4())}
            mock_repo_instance = AsyncMock()
            mock_repo_instance.find_by_id.return_value = None
            MockRepo.return_value = mock_repo_instance

            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/test", headers={"Authorization": "Bearer faketoken"})

        assert resp.status_code == 401

    def test_raises_401_when_user_inactive(self):
        """Токен валиден, пользователь найден, но неактивен."""
        app = FastAPI()

        @app.get("/test")
        async def route(user: UserOutput = Depends(get_current_user)):
            return {"ok": True}

        with (
            patch("src.interfaces.api.auth_dependencies.decode_access_token") as mock_decode,
            patch("src.interfaces.api.auth_dependencies.SqlUserRepository") as MockRepo,
        ):
            mock_decode.return_value = {"sub": str(uuid4())}
            mock_repo_instance = AsyncMock()
            inactive_user = _make_user_mock(is_active=False)
            mock_repo_instance.find_by_id.return_value = inactive_user
            MockRepo.return_value = mock_repo_instance

            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/test", headers={"Authorization": "Bearer faketoken"})

        assert resp.status_code == 401


class TestRequireAdmin:
    def test_raises_403_when_manager(self):
        """MANAGER не должен проходить require_admin."""
        manager = UserOutput(
            id=uuid4(), first_name="M", last_name="G",
            email="m@test.com", role=UserRole.MANAGER, is_active=True,
        )
        app = FastAPI()
        app.dependency_overrides[get_current_user] = lambda: manager

        @app.get("/test")
        async def route(user=Depends(require_admin)):
            return {"role": user.role.value}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/test", headers={"Authorization": "Bearer fake"})
        assert resp.status_code == 403

    def test_passes_for_admin(self):
        """ADMIN должен проходить require_admin."""
        admin = UserOutput(
            id=uuid4(), first_name="A", last_name="D",
            email="a@test.com", role=UserRole.ADMIN, is_active=True,
        )
        app = FastAPI()
        app.dependency_overrides[get_current_user] = lambda: admin

        @app.get("/test")
        async def route(user=Depends(require_admin)):
            return {"role": user.role.value}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/test", headers={"Authorization": "Bearer fake"})
        assert resp.status_code == 200


class TestRequireManager:
    def test_raises_403_when_not_manager_or_admin(self):
        """Пользователь с неизвестной ролью не должен проходить require_manager."""
        from unittest.mock import MagicMock
        # Create a UserOutput-like object with an unknown role
        fake_user = MagicMock(spec=UserOutput)
        fake_user.role = MagicMock()
        fake_user.role.__eq__ = lambda self, other: False  # not ADMIN, not MANAGER

        app = FastAPI()
        app.dependency_overrides[get_current_user] = lambda: fake_user

        @app.get("/test")
        async def route(user=Depends(require_manager)):
            return {"role": str(user.role)}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/test", headers={"Authorization": "Bearer fake"})
        assert resp.status_code == 403

    def test_passes_for_manager(self):
        """MANAGER должен проходить require_manager."""
        manager = UserOutput(
            id=uuid4(), first_name="M", last_name="G",
            email="m@test.com", role=UserRole.MANAGER, is_active=True,
        )
        app = FastAPI()
        app.dependency_overrides[get_current_user] = lambda: manager

        @app.get("/test")
        async def route(user=Depends(require_manager)):
            return {"role": user.role.value}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/test", headers={"Authorization": "Bearer fake"})
        assert resp.status_code == 200

    def test_passes_for_admin(self):
        """ADMIN тоже проходит require_manager."""
        admin = UserOutput(
            id=uuid4(), first_name="A", last_name="D",
            email="a@test.com", role=UserRole.ADMIN, is_active=True,
        )
        app = FastAPI()
        app.dependency_overrides[get_current_user] = lambda: admin

        @app.get("/test")
        async def route(user=Depends(require_manager)):
            return {"role": user.role.value}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/test", headers={"Authorization": "Bearer fake"})
        assert resp.status_code == 200
