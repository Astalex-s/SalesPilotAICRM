"""
DTO для аутентификации и управления пользователями.
"""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.domain.value_objects.enums import UserRole


class RegisterInput(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.SALES_REP


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenOutput(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenInput(BaseModel):
    refresh_token: str


class ForgotPasswordInput(BaseModel):
    email: EmailStr


class ResetPasswordInput(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)


class UserOutput(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UpdateUserRoleInput(BaseModel):
    role: UserRole


class UpdateProfileInput(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class ChangePasswordInput(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)
