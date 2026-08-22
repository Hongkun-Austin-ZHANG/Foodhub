from uuid import uuid4

import pytest
from pydantic import ValidationError

from schemas.dish import EvidenceLevel, EvidenceSource
from schemas.unknown_dish import (
    FallbackDishBatchRequest,
    UnknownDishAnalysisRequest,
    UnknownDishAnalysisResponse,
)
from services.recommendation.allergen_mapper import assess_allergens


def test_unknown_dish_response_converts_to_cache_record() -> None:
    response = UnknownDishAnalysisResponse.model_validate(
        {
            "request_id": str(uuid4()),
            "canonical_name_en": "Escargots Persillade",
            "aliases": ["Garlic Parsley Snails"],
            "description": "French snails prepared with garlic and parsley.",
            "cuisine": "French",
            "inferred_ingredients": [
                {
                    "name": "Butter",
                    "confidence": 0.9,
                    "reasoning": "The traditional preparation commonly uses butter.",
                }
            ],
            "overall_confidence": 0.85,
            "model_id": "test-model-v1",
        }
    )

    ingredient_record = response.to_fallback_record()
    record = response.to_fallback_record(
        assess_allergens([], [], ingredient_record.ingredients)
    )

    assert record.normalized_name == "escargots persillade"
    assert record.ingredients[0].source == EvidenceSource.LLM
    assert record.ingredients[0].evidence_level == EvidenceLevel.INFERRED
    assert record.allergen_assessments[0].code == "milk"
    assert record.model_id == "test-model-v1"


def test_backend_b_cannot_return_allergen_assessments() -> None:
    with pytest.raises(ValidationError, match="allergen_assessments"):
        UnknownDishAnalysisResponse.model_validate(
            {
                "request_id": str(uuid4()),
                "canonical_name_en": "House Dish",
                "description": "A house dish.",
                "allergen_assessments": [
                    {
                        "code": "milk",
                        "status": "contains",
                        "evidence_source": "inferred",
                        "confidence": 0.7,
                        "reasoning": "Traditional recipes often use butter.",
                    }
                ],
                "overall_confidence": 0.7,
                "model_id": "test-model-v1",
            }
        )


def test_batch_rejects_duplicate_request_ids() -> None:
    request_id = uuid4()
    dish = UnknownDishAnalysisRequest(
        request_id=request_id,
        original_name="House Dish",
        canonical_name_en="House Dish",
        source_text="House Dish",
    )

    with pytest.raises(ValidationError, match="unique within a batch"):
        FallbackDishBatchRequest(dishes=[dish, dish])

    assert FallbackDishBatchRequest(dishes=[dish]).schema_version == "1.1"


def test_deprecated_dietary_assessments_are_rejected() -> None:
    with pytest.raises(ValidationError, match="dietary_assessments"):
        UnknownDishAnalysisResponse.model_validate(
            {
                "request_id": str(uuid4()),
                "canonical_name_en": "House Dish",
                "description": "A house dish.",
                "dietary_assessments": [],
                "overall_confidence": 0.7,
                "model_id": "test-model-v1",
            }
        )
