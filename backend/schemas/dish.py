import re
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator

from schemas.safety import AllergenAssessment


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def normalize_lookup_name(value: str) -> str:
    normalized = normalize_text(value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


class EvidenceSource(StrEnum):
    MENU = "menu"
    THEMEALDB = "themealdb"
    LLM = "llm"
    LOCAL_FALLBACK = "local_fallback"


class EvidenceLevel(StrEnum):
    EXPLICIT = "explicit"
    REFERENCE_RECIPE = "reference_recipe"
    INFERRED = "inferred"
    CACHED_INFERENCE = "cached_inference"


class IngredientEvidence(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    source: EvidenceSource
    evidence_level: EvidenceLevel
    confidence: float | None = Field(default=None, ge=0, le=1)
    reasoning: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return normalize_text(value)


class ParsedDish(BaseModel):
    """Normalized menu dish shared by Backend B, C, and the frontend."""

    dish_id: UUID = Field(default_factory=uuid4)
    original_name: str = Field(min_length=1, max_length=200)
    translated_name: str | None = Field(default=None, max_length=200)
    canonical_name_en: str = Field(min_length=1, max_length=200)
    menu_description: str | None = Field(default=None, max_length=600)
    translated_description: str | None = Field(default=None, max_length=600)
    explicit_ingredients: list[str] = Field(default_factory=list)
    price: Decimal | None = Field(default=None, ge=0)
    price_text: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    source_text: str | None = Field(default=None, max_length=2000)
    extraction_confidence: float = Field(ge=0, le=1)

    @field_validator("original_name", "canonical_name_en")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return normalize_text(value)

    @field_validator(
        "translated_name",
        "menu_description",
        "translated_description",
        "price_text",
        "source_text",
    )
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return normalize_text(value) if value else None

    @field_validator("explicit_ingredients")
    @classmethod
    def clean_ingredients(cls, values: list[str]) -> list[str]:
        unique: dict[str, str] = {}
        for value in values:
            cleaned = normalize_text(value)
            if cleaned:
                unique.setdefault(cleaned.casefold(), cleaned)
        return list(unique.values())

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str | None) -> str | None:
        return value.upper() if value else None


class ExternalDishCandidate(BaseModel):
    external_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    area: str | None = None
    category: str | None = None
    image_url: HttpUrl | None = None
    ingredients: list[str] = Field(default_factory=list)
    source: EvidenceSource = EvidenceSource.THEMEALDB


class FallbackDishRecord(BaseModel):
    """LLM result that will be stored locally when TheMealDB cannot match a dish."""

    record_id: UUID = Field(default_factory=uuid4)
    canonical_name_en: str = Field(min_length=1, max_length=200)
    normalized_name: str = Field(min_length=1, max_length=200)
    aliases: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1, max_length=1000)
    cuisine: str | None = Field(default=None, max_length=100)
    ingredients: list[IngredientEvidence] = Field(default_factory=list)
    allergen_assessments: list[AllergenAssessment] = Field(default_factory=list)
    image_url: HttpUrl | None = None
    confidence: float = Field(ge=0, le=1)
    model_id: str | None = Field(default=None, max_length=100)
    generated_by: EvidenceSource = EvidenceSource.LLM
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("normalized_name")
    @classmethod
    def validate_normalized_name(cls, value: str) -> str:
        normalized = normalize_lookup_name(value)
        if not normalized:
            raise ValueError("normalized_name must contain letters or numbers")
        return normalized
