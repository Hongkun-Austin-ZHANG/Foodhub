from enum import Enum

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