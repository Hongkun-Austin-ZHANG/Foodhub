from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ConfidenceLevel(str, Enum):
    """
    Allowed confidence levels for menu extraction.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DishExtraction(BaseModel):
    """
    Structured representation of one dish extracted from a menu image.

    Restaurant-specific menu evidence is the source of truth.
    User-facing translations and database matching fields are kept
    separate because they serve different purposes.
    """

    model_config = ConfigDict(extra="forbid")

    original_name: str = Field(
        min_length=1,
        description="Exact dish name as written on the restaurant menu.",
    )

    translated_name: str = Field(
        min_length=1,
        description=(
            "User-facing translation of the dish name into the requested "
            "target language. This field is for display, not database matching."
        ),
    )

    canonical_guess: str | None = Field(
        default=None,
        description=(
            "Short, conservative English canonical dish name used only "
            "for database matching. Return null when uncertain."
        ),
    )

    price: str | None = Field(
        default=None,
        description=(
            "Price as shown on the menu. Stored as text because menus "
            "may use formats such as '18', '$24', 'MP', or '14/24'."
        ),
    )

    menu_description: str | None = Field(
        default=None,
        description="Restaurant-written dish description in its original language.",
    )

    translated_description: str | None = Field(
        default=None,
        description=(
            "Translation of menu_description into the requested target language. "
            "Return null when menu_description is null."
        ),
    )

    explicit_ingredients: list[str] = Field(
        default_factory=list,
        description=(
            "Food ingredients or dish components explicitly written on the menu. "
            "Do not infer unstated ingredients from culinary knowledge."
        ),
    )

    source_text: str = Field(
        min_length=1,
        description=(
            "Visible menu text supporting this extraction. "
            "Used for traceability and debugging."
        ),
    )

    extraction_confidence: ConfidenceLevel = Field(
        description=(
            "Confidence in extraction accuracy from the menu image: "
            "high, medium, or low."
        ),
    )


class MenuParseResponse(BaseModel):
    """
    Structured output for parsing one menu page.
    """

    model_config = ConfigDict(extra="forbid")

    menu_language: str | None = Field(
        default=None,
        description=(
            "Language or languages visibly used on the menu page, "
            "for example 'French / English'."
        ),
    )

    target_language: str = Field(
        min_length=2,
        description=(
            "Language used for translated_name and translated_description, "
            "for example 'en', 'zh', or 'fr'."
        ),
    )

    dishes: list[DishExtraction] = Field(
        default_factory=list,
        description="All clearly visible orderable dishes extracted from this page.",
    )

class UnknownDishInput(BaseModel):
    """
    One dish that could not be matched by the local database or TheMealDB.

    Restaurant-specific menu evidence is preserved as context for
    the AI fallback step.
    """

    model_config = ConfigDict(extra="forbid")

    dish_id: str = Field(
        min_length=1,
        description="Stable identifier used to map the result back to the dish.",
    )

    original_name: str = Field(
        min_length=1,
        description="Dish name exactly as written on the restaurant menu.",
    )

    canonical_guess: str | None = Field(
        default=None,
        description=(
            "Conservative English canonical dish name produced during "
            "menu parsing, if available."
        ),
    )

    menu_description: str | None = Field(
        default=None,
        description="Restaurant-written menu description, if available.",
    )

    explicit_ingredients: list[str] = Field(
        default_factory=list,
        description=(
            "Ingredients or dish components explicitly written on the "
            "restaurant menu. These are restaurant-specific evidence."
        ),
    )

    source_text: str = Field(
        min_length=1,
        description="Visible restaurant menu evidence for this dish.",
    )


class FallbackBatchRequest(BaseModel):
    """
    Batch request containing all dishes that remained unmatched after
    local database and TheMealDB lookup.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(
        min_length=1,
        description="Identifier for the whole fallback batch.",
    )

    dishes: list[UnknownDishInput] = Field(
        min_length=1,
        description="All unmatched dishes to process in one LLM call.",
    )


class InferredIngredient(BaseModel):
    """
    Ingredient inferred from general culinary knowledge.

    This is not restaurant-confirmed information.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        description="Likely ingredient or dish component.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in this inferred ingredient.",
    )


class FallbackDishResult(BaseModel):
    """
    Neutral culinary knowledge returned for one unknown dish.

    This output must not contain user-specific recommendation decisions.
    """

    model_config = ConfigDict(extra="forbid")

    dish_id: str = Field(
        min_length=1,
        description="Echoes the dish_id from the request.",
    )

    canonical_name_en: str = Field(
        min_length=1,
        description="Best neutral English canonical name for the dish.",
    )

    description: str = Field(
        min_length=1,
        description="Short neutral English explanation of the dish.",
    )

    inferred_ingredients: list[InferredIngredient] = Field(
        default_factory=list,
        description=(
            "Likely ingredients inferred from generic culinary knowledge. "
            "These must remain separate from explicit_ingredients."
        ),
    )

    taste: list[str] = Field(
        default_factory=list,
        description="Short neutral taste descriptors.",
    )

    texture: list[str] = Field(
        default_factory=list,
        description="Short neutral texture descriptors.",
    )

    cooking_method: str | None = Field(
        default=None,
        description="Typical cooking method, if reasonably identifiable.",
    )

    spice_level: Literal[
        "none",
        "mild",
        "medium",
        "hot",
        "unknown",
    ] = "unknown"

    dish_family: str | None = Field(
        default=None,
        description="Broad dish category, such as 'snail dish' or 'roasted fish'.",
    )

    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in the AI fallback interpretation.",
    )

    source: Literal["ai"] = "ai"


class FallbackBatchResponse(BaseModel):
    """
    Structured result for one batch of unknown dishes.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(
        min_length=1,
        description="Echoes the request_id from the batch request.",
    )

    dishes: list[FallbackDishResult] = Field(
        default_factory=list,
        description="Fallback results for all unknown dishes in the batch.",
    )