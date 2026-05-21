from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security_constants import ALLOWED_ROLES, DEFAULT_USER_ROLE


class UserRegister(BaseModel):
    """Public registration — role cannot be supplied by clients."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(c.isdigit() for c in value) or not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter and one digit.")
        return value


class UserCreate(BaseModel):
    """Internal user creation (e.g. seed scripts)."""

    email: EmailStr
    password: str
    role: Optional[str] = DEFAULT_USER_ROLE

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> str:
        role = value or DEFAULT_USER_ROLE
        if role not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role. Allowed: {sorted(ALLOWED_ROLES)}")
        return role


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
