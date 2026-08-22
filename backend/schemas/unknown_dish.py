from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schemas.dish import (
    EvidenceLevel,
    EvidenceSource,
    FallbackDishRecord,
    IngredientEvidence,
    ParsedDish,
    normalize_lookup_name,
    normalize_text,
)
from schemas.safety import AllergenAssessment


class FallbackContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UnknownDishAnalysisRequest(FallbackContractModel):
    request_id: UUID = Field(default_factory=uuid4)
    original_name: str = Field(min_length=1, max_length=200)
    canonical_name_en: str = Field(min_length=1, max_length=200)
    menu_description: str | None = Field(default=None, max_length=600)
    explicit_ingredients: list[str] = Field(default_factory=list)
    source_text: str = Field(min_length=1, max_length=2000)

    @classmethod
    def from_dish(cls, dish: ParsedDish) -> "UnknownDishAnalysisRequest":
        return cls(
            original_name=dish.original_name,
            canonical_name_en=dish.canonical_name_en,
            menu_description=dish.menu_description,
            explicit_ingredients=dish.explicit_ingredients,
            source_text=dish.source_text or dish.original_name,
        )


class InferredIngredient(FallbackContractModel):
    name: str = Field(min_length=1, max_length=120)
    confidence: float = Field(ge=0, le=1)
    reasoning: str | None = Field(default=None, min_length=1, max_length=500)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return normalize_text(value)


class UnknownDishAnalysisResponse(FallbackContractModel):
    request_id: UUID
    canonical_name_en: str = Field(min_length=1, max_length=200)
    aliases: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1, max_length=1000)
    cuisine: str | None = Field(default=None, max_length=100)
    inferred_ingredients: list[InferredIngredient] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0, le=1)
    model_id: str = Field(min_length=1, max_length=100)

    def to_fallback_record(
        self,
        allergen_assessments: list[AllergenAssessment] | None = None,
    ) -> FallbackDishRecord:
        return FallbackDishRecord(
            canonical_name_en=self.canonical_name_en,
            normalized_name=normalize_lookup_name(self.canonical_name_en),
            aliases=self.aliases,
            description=self.description,
            cuisine=self.cuisine,
            ingredients=[
                IngredientEvidence(
                    name=ingredient.name,
                    source=EvidenceSource.LLM,
                    evidence_level=EvidenceLevel.INFERRED,
                    confidence=ingredient.confidence,
                    reasoning=ingredient.reasoning,
                )
                for ingredient in self.inferred_ingredients
            ],
            allergen_assessments=allergen_assessments or [],
            confidence=self.overall_confidence,
            model_id=self.model_id,
        )


class FallbackDishBatchRequest(FallbackContractModel):
    schema_version: Literal["1.1"] = "1.1"
    batch_id: UUID = Field(default_factory=uuid4)
    dishes: list[UnknownDishAnalysisRequest] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def require_unique_request_ids(self) -> "FallbackDishBatchRequest":
        request_ids = [dish.request_id for dish in self.dishes]
        if len(request_ids) != len(set(request_ids)):
            raise ValueError("request_id must be unique within a batch")
        return self


class FallbackDishBatchResponse(FallbackContractModel):
    schema_version: Literal["1.1"] = "1.1"
    batch_id: UUID
    results: list[UnknownDishAnalysisResponse] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def require_unique_request_ids(self) -> "FallbackDishBatchResponse":
        request_ids = [result.request_id for result in self.results]
        if len(request_ids) != len(set(request_ids)):
            raise ValueError("request_id must be unique within a batch")
        return self


class FallbackDishBatchValidationResponse(FallbackContractModel):
    accepted: bool = True
    batch: FallbackDishBatchResponse
