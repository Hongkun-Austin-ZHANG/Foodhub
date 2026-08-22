from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from schemas.dish import EvidenceSource, IngredientEvidence, ParsedDish
from schemas.menu import MenuParseResult, MenuPayload
from schemas.preference import (
    DailyPreferenceOverride,
    PreferenceContext,
    UserPreference,
)
from schemas.resolution import DishResolutionStatus
from schemas.safety import AllergenAssessment
from schemas.unknown_dish import FallbackDishBatchRequest


class RecommendationStatus(StrEnum):
    GOOD_MATCH = "good_match"
    CHECK_WITH_STAFF = "check_with_staff"
    AVOID = "avoid"


class DishDecision(BaseModel):
    status: RecommendationStatus
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class RecommendedDish(BaseModel):
    dish: ParsedDish
    image_url: HttpUrl | None = None
    image_is_reference: bool = False
    enrichment_source: EvidenceSource | None = None
    decision: DishDecision


class RecommendationPreviewRequest(BaseModel):
    menu: MenuParseResult
    preferences: PreferenceContext = Field(default_factory=PreferenceContext)


class MenuRecommendationResponse(BaseModel):
    menu_id: UUID
    effective_preferences: list[UserPreference]
    dishes: list[RecommendedDish]


class RecommendationAnalyzeRequest(BaseModel):
    menu: MenuPayload
    daily_overrides: list[DailyPreferenceOverride] = Field(default_factory=list)


class IngredientEvidenceDisplay(BaseModel):
    name: str
    reasoning: str | None = None


class DishEvidenceDisplay(BaseModel):
    explicit_ingredients: list[str] = Field(default_factory=list)
    reference_ingredients: list[str] = Field(default_factory=list)
    inferred_ingredients: list[IngredientEvidenceDisplay] = Field(default_factory=list)


class DishEvidence(BaseModel):
    explicit_ingredients: list[str] = Field(default_factory=list)
    reference_ingredients: list[str] = Field(default_factory=list)
    inferred_ingredients: list[IngredientEvidence] = Field(default_factory=list)
    allergen_assessments: list[AllergenAssessment] = Field(default_factory=list)
    display: DishEvidenceDisplay = Field(default_factory=DishEvidenceDisplay)


class DishEnrichment(BaseModel):
    summary: str | None = None
    display_summary: str | None = None
    cuisine: str | None = None
    display_cuisine: str | None = None
    source: Literal[
        "menu_only",
        "themealdb",
        "llm",
        "local_fallback",
        "demo_database",
    ] = "menu_only"
    confidence: float | None = Field(default=None, ge=0, le=1)


class AnalyzedDish(BaseModel):
    dish: ParsedDish
    resolution_status: DishResolutionStatus
    match_score: float | None = Field(default=None, ge=0, le=1)
    image_url: HttpUrl | None = None
    image_is_reference: bool = False
    enrichment: DishEnrichment = Field(default_factory=DishEnrichment)
    evidence: DishEvidence
    decision: DishDecision


class RecommendationAnalyzeResponse(BaseModel):
    menu_id: UUID
    source_language: str
    target_language: str
    mode: Literal["live", "demo"] = "live"
    analysis_complete: bool
    effective_preferences: list[UserPreference]
    dishes: list[AnalyzedDish]
    fallback_batch_request: FallbackDishBatchRequest | None = None
