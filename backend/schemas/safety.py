from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schemas.preference import normalize_preference_code


class AllergenPresence(StrEnum):
    CONTAINS = "contains"
    MAY_CONTAIN = "may_contain"
    NOT_IDENTIFIED = "not_identified"
    UNKNOWN = "unknown"


class AllergenEvidenceSource(StrEnum):
    MENU_EVIDENCE = "menu_evidence"
    REFERENCE_RECIPE = "reference_recipe"
    INFERRED = "inferred"


class AllergenAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=100)
    status: AllergenPresence
    evidence_source: AllergenEvidenceSource
    confidence: float = Field(ge=0, le=1)
    reasoning: str = Field(min_length=1, max_length=500)

    @field_validator("code")
    @classmethod
    def clean_code(cls, value: str) -> str:
        return normalize_preference_code(value)

    @model_validator(mode="after")
    def prevent_inferred_contains_claim(self) -> "AllergenAssessment":
        if (
            self.evidence_source != AllergenEvidenceSource.MENU_EVIDENCE
            and self.status == AllergenPresence.CONTAINS
        ):
            raise ValueError("only menu evidence can claim contains")
        return self
