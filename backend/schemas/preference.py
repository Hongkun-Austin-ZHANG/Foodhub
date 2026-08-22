import re
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PreferenceKind(StrEnum):
    ALLERGY = "allergy"
    DIETARY = "dietary"
    RELIGIOUS = "religious"
    AVOID = "avoid"
    PREFERENCE = "preference"


class PreferenceStrength(StrEnum):
    HARD = "hard"
    SOFT = "soft"


class PreferenceOptionGroup(StrEnum):
    ALLERGENS = "allergens"
    DIETARY = "dietary"
    RELIGIOUS = "religious"
    AVOID = "avoid"


PREFERENCE_CODE_ALIASES = {
    "crustacean": "shellfish",
    "crustaceans": "shellfish",
    "eggs": "egg",
    "mollusc": "molluscs",
    "peanuts": "peanut",
    "sulfite": "sulfites",
    "sulphite": "sulfites",
    "sulphites": "sulfites",
    "tree_nut": "tree_nuts",
}


def normalize_preference_code(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().casefold()).strip("_")
    if not normalized:
        raise ValueError("preference code must contain letters or numbers")
    return PREFERENCE_CODE_ALIASES.get(normalized, normalized)


def normalize_preference_codes(values: list[str]) -> list[str]:
    if len(values) > 50:
        raise ValueError("each preference group accepts at most 50 values")
    normalized: list[str] = []
    for value in values:
        if len(value) > 100:
            raise ValueError("preference values must not exceed 100 characters")
        code = normalize_preference_code(value)
        if code not in normalized:
            normalized.append(code)
    return normalized


class UserPreference(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    kind: PreferenceKind
    strength: PreferenceStrength
    enabled: bool = True

    @field_validator("code")
    @classmethod
    def clean_code(cls, value: str) -> str:
        return normalize_preference_code(value)


class DailyPreferenceOverride(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    enabled: bool

    @field_validator("code")
    @classmethod
    def clean_code(cls, value: str) -> str:
        return normalize_preference_code(value)


class PreferenceContext(BaseModel):
    """Persistent preferences plus temporary choices for the current scan."""

    persistent: list[UserPreference] = Field(default_factory=list)
    daily_overrides: list[DailyPreferenceOverride] = Field(default_factory=list)


class PreferenceProfile(BaseModel):
    """Frontend-friendly grouped representation of a user's saved preferences."""

    allergies: list[str] = Field(default_factory=list)
    dietary_restrictions: list[str] = Field(default_factory=list)
    religious_restrictions: list[str] = Field(default_factory=list)
    preferred_proteins: list[str] = Field(default_factory=list)
    preferred_flavours: list[str] = Field(default_factory=list)
    preferred_textures: list[str] = Field(default_factory=list)
    spice_level: str | None = Field(default=None, max_length=100)
    disliked_ingredients: list[str] = Field(default_factory=list)

    @field_validator(
        "allergies",
        "dietary_restrictions",
        "religious_restrictions",
        "preferred_proteins",
        "preferred_flavours",
        "preferred_textures",
        "disliked_ingredients",
    )
    @classmethod
    def clean_group(cls, value: list[str]) -> list[str]:
        return normalize_preference_codes(value)

    @field_validator("spice_level")
    @classmethod
    def clean_spice_level(cls, value: str | None) -> str | None:
        return normalize_preference_code(value) if value is not None else None


class EffectivePreferences(BaseModel):
    preferences: list[UserPreference]


class PreferenceUpdateRequest(BaseModel):
    kind: PreferenceKind | None = None
    strength: PreferenceStrength | None = None
    enabled: bool | None = None

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> "PreferenceUpdateRequest":
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class StoredPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    kind: PreferenceKind
    strength: PreferenceStrength
    enabled: bool
    created_at: datetime
    updated_at: datetime


class PreferenceOption(BaseModel):
    code: str
    group: PreferenceOptionGroup
    kind: PreferenceKind
    default_strength: PreferenceStrength
    allows_daily_override: bool
    label_en: str
    description_en: str
