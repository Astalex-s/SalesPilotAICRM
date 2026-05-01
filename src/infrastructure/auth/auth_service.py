"""
AuthService — хэширование паролей и работа с JWT-токенами.
Инфраструктурный слой: зависит от passlib и python-jose.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.infrastructure.config.settings import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Возвращает bcrypt-хэш пароля."""
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет соответствие открытого пароля хэшу."""
    return _pwd_context.verify(plain, hashed)


def create_access_token(user_id: UUID, role: str) -> str:
    """Создаёт подписанный JWT access-токен (30 мин)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: UUID, role: str) -> str:
    """Создаёт подписанный JWT refresh-токен (30 дней)."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Декодирует JWT access-токен. Бросает JWTError при невалидном токене."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    """Декодирует JWT refresh-токен. Бросает JWTError если невалиден или тип не 'refresh'."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "refresh":
        raise JWTError("Not a refresh token")
    return payload


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
]
