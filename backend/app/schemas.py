from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ConfidenceLevel(str, Enum):
    """
    Allowed confidence levels for menu extraction.

    Using an Enum keeps the API output consistent and prevents
    arbitrary values such as "very high" or "quite confident".
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DishExtraction(BaseModel):
    """
    Structured representation of one dish extracted from a menu image.

    Important rule:
    Restaurant-specific menu evidence is the source of truth.

    In particular, explicit_ingredients must contain only ingredients
    that are explicitly written on the menu. Generic culinary knowledge
    must not be used during the extraction stage.
    """

    # Reject unexpected fields.
    # This helps catch accidental schema drift early.
    model_config = ConfigDict(extra="forbid")

    original_name: str = Field(
        min_length=1,
        description="Exact dish name as written on the restaurant menu.",
    )

    canonical_guess: str | None = Field(
        default=None,
        description=(
            "Conservative standard dish name for database matching. "
            "Use null if the canonical dish name is uncertain."
        ),
    )

    price: str | None = Field(
        default=None,
        description=(
            "Price as shown on the menu. "
            "Stored as text because menus may use formats such as "
            "'18', '$24', '18€', 'MP', or '25 / 36'."
        ),
    )

    menu_description: str | None = Field(
        default=None,
        description="Restaurant-provided description of the dish.",
    )

    explicit_ingredients: list[str] = Field(
    default_factory=list,
    description=(
        "Food ingredients or dish components explicitly written in "
        "the menu text. Do not infer unstated ingredients. Preserve "
        "restaurant wording and do not decompose sauces, purées, "
        "butters, or other components into assumed ingredients."
    ),
)

    source_text: str = Field(
        min_length=1,
        description=(
            "Raw menu text that supports this extraction. "
            "Used as traceable evidence for downstream processing."
        ),
    )

    extraction_confidence: ConfidenceLevel = Field(
        description=(
            "Confidence in the accuracy of the menu extraction: "
            "high, medium, or low."
        ),
    )


class MenuParseResponse(BaseModel):
    """
    Standard output for parsing one menu page.

    Each request processes one image only.
    Multi-page menu merging and deduplication are handled elsewhere.
    """

    model_config = ConfigDict(extra="forbid")

    menu_language: str | None = Field(
    default=None,
    description=(
        "Language or languages visibly used on the menu page. "
        "If multiple languages are clearly present, include them "
        "using a format such as 'French / English'."
    ),
)

    dishes: list[DishExtraction] = Field(
        default_factory=list,
        description="All dishes extracted from this menu page.",
    )