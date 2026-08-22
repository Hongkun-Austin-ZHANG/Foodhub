from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from core.language import normalize_language_code


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    return cleaned or None


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    gender: str | None = Field(default=None, max_length=50)
    religion: str | None = Field(default=None, max_length=100)
    preferred_language: str | None = Field(default=None, min_length=2, max_length=16)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("display_name", "gender", "religion", mode="before")
    @classmethod
    def clean_profile_text(cls, value: str | None) -> str | None:
        return clean_optional_text(value)

    @field_validator("timezone", mode="before")
    @classmethod
    def clean_required_text(cls, value: str | None) -> str | None:
        return " ".join(value.strip().split()) if value is not None else None

    @field_validator("preferred_language", mode="before")
    @classmethod
    def clean_language(cls, value: str | None) -> str | None:
        return normalize_language_code(value) if value is not None else None

    @model_validator(mode="after")
    def prevent_null_required_fields(self) -> "ProfileUpdateRequest":
        for field in ("preferred_language", "timezone"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    display_name: str | None
    gender: str | None
    religion: str | None
    preferred_language: str
    timezone: str
    created_at: datetime
    updated_at: datetime
