from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from core.language import normalize_language_code


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        pattern=r"^[A-Za-z0-9_.-]+$",
    )
    name: str | None = Field(default=None, min_length=1, max_length=100)
    preferred_language: str = Field(default="en", min_length=2, max_length=16)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username", "name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None

    @field_validator("preferred_language")
    @classmethod
    def clean_language(cls, value: str) -> str:
        return normalize_language_code(value)

    @model_validator(mode="after")
    def require_name_or_username(self) -> "RegisterRequest":
        if self.name is None and self.username is None:
            raise ValueError("name or username is required")
        return self


class LoginRequest(BaseModel):
    identifier: str | None = Field(default=None, min_length=1, max_length=320)
    email: EmailStr | None = None
    password: str = Field(min_length=1, max_length=128)

    @field_validator("identifier")
    @classmethod
    def clean_identifier(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def require_identifier(self) -> "LoginRequest":
        if self.identifier is None and self.email is None:
            raise ValueError("email or identifier is required")
        return self

    @property
    def login_identifier(self) -> str:
        return self.identifier or str(self.email)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    is_active: bool


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse


class LogoutResponse(BaseModel):
    logged_out: bool = True
