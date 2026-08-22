from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from schemas.dish import ParsedDish
from schemas.preference import UserPreference, normalize_preference_codes
from schemas.recommendation import DishDecision, DishEvidence
from schemas.resolution import DishResolutionStatus


class CurrentMealPreference(BaseModel):
    preferred_proteins: list[str] = Field(default_factory=list)
    preferred_flavours: list[str] = Field(default_factory=list)
    preferred_textures: list[str] = Field(default_factory=list)
    spice_level: str | None = Field(default=None, max_length=100)

    @field_validator(
        "preferred_proteins",
        "preferred_flavours",
        "preferred_textures",
    )
    @classmethod
    def clean_groups(cls, values: list[str]) -> list[str]:
        return normalize_preference_codes(values)

    @field_validator("spice_level")
    @classmethod
    def clean_spice(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = normalize_preference_codes([value])[0]
        if normalized not in {"mild", "medium", "hot"}:
            raise ValueError("spice_level must be mild, medium, hot, or null")
        return normalized


class DishPreferenceTags(BaseModel):
    proteins: list[str] = Field(default_factory=list)
    flavours: list[str] = Field(default_factory=list)
    textures: list[str] = Field(default_factory=list)
    spice_level: str = "mild"


class MenuRecommendationsRequest(BaseModel):
    menu_id: UUID
    current_preference: CurrentMealPreference = Field(
        default_factory=CurrentMealPreference
    )


class RankedRecommendation(BaseModel):
    rank: int = Field(ge=1)
    preference_score: float = Field(ge=0, le=1)
    matched_preferences: list[str] = Field(default_factory=list)
    preference_tags: DishPreferenceTags
    dish: ParsedDish
    resolution_status: DishResolutionStatus
    match_score: float | None = Field(default=None, ge=0, le=1)
    image_url: HttpUrl | None = None
    image_is_reference: bool = False
    evidence: DishEvidence
    decision: DishDecision


class MenuRecommendationsResponse(BaseModel):
    menu_id: UUID
    target_language: str
    effective_preferences: list[UserPreference]
    effective_current_preference: CurrentMealPreference
    recommendations: list[RankedRecommendation]
