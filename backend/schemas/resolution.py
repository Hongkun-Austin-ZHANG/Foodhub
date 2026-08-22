from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.dish import ExternalDishCandidate, FallbackDishRecord
from schemas.unknown_dish import FallbackDishBatchRequest


class DishResolutionStatus(StrEnum):
    LOCAL_FALLBACK = "local_fallback"
    LLM_FALLBACK = "llm_fallback"
    THEMEALDB_MATCH = "themealdb_match"
    NEEDS_LLM = "needs_llm"
    LOOKUP_UNAVAILABLE = "lookup_unavailable"


class DishResolution(BaseModel):
    dish_id: UUID
    canonical_name_en: str
    status: DishResolutionStatus
    match_score: float | None = Field(default=None, ge=0, le=1)
    themealdb_candidate: ExternalDishCandidate | None = None
    local_fallback: FallbackDishRecord | None = None
    fallback_request_id: UUID | None = None
    error: str | None = None


class MenuResolutionResponse(BaseModel):
    menu_id: UUID
    dishes: list[DishResolution]
    fallback_batch_request: FallbackDishBatchRequest | None = None
