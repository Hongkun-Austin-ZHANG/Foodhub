from decimal import Decimal, InvalidOperation
from typing import Literal
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from schemas.dish import ParsedDish, normalize_text

CONFIDENCE_SCORES = {
    "high": 0.9,
    "medium": 0.6,
    "low": 0.3,
}


def normalize_source_language(value: str) -> str:
    language_names = {
        "english": "en",
        "french": "fr",
        "chinese": "zh",
        "german": "de",
        "italian": "it",
        "japanese": "ja",
        "korean": "ko",
        "spanish": "es",
    }
    parts = [part.strip().casefold() for part in value.split("/") if part.strip()]
    normalized = [language_names.get(part, part) for part in parts]
    return "/".join(dict.fromkeys(normalized))


def parse_backend_a_price(
    value: str | Decimal | None,
) -> tuple[Decimal | None, str | None]:
    if value is None:
        return None, None
    price_text = normalize_text(str(value))
    try:
        price = Decimal(price_text)
    except InvalidOperation:
        return None, price_text
    return price, price_text


class MenuParseResult(BaseModel):
    """Normalized menu used internally after Backend B parsing."""

    schema_version: Literal["1.0"] = "1.0"
    menu_id: UUID = Field(default_factory=uuid4)
    source_language: str = Field(min_length=2, max_length=20)
    output_language: str = Field(default="en", min_length=2, max_length=20)
    dishes: list[ParsedDish] = Field(min_length=1)

    @field_validator("source_language", "output_language")
    @classmethod
    def normalize_language(cls, value: str) -> str:
        return value.strip().lower()

    @computed_field
    @property
    def target_language(self) -> str:
        """Schema v2 display-language name retained beside the legacy field."""

        return self.output_language


class MenuValidationResponse(BaseModel):
    accepted: bool
    menu: MenuParseResult


class BackendBDishPayload(BaseModel):
    """Menu-understanding payload produced by Backend B."""

    model_config = ConfigDict(extra="forbid")

    original_name: str = Field(min_length=1, max_length=200)
    translated_name: str | None = Field(default=None, max_length=200)
    canonical_guess: str | None = Field(default=None, max_length=200)
    price: str | Decimal | None = None
    menu_description: str | None = Field(default=None, max_length=600)
    translated_description: str | None = Field(default=None, max_length=600)
    explicit_ingredients: list[str] = Field(default_factory=list)
    source_text: str | None = Field(default=None, max_length=2000)
    extraction_confidence: float | Literal["high", "medium", "low"]

    @field_validator(
        "original_name",
        "translated_name",
        "canonical_guess",
        "menu_description",
        "translated_description",
        mode="before",
    )
    @classmethod
    def clean_names(cls, value: str | None) -> str | None:
        return normalize_text(value) if value else None

    @field_validator("extraction_confidence", mode="before")
    @classmethod
    def normalize_confidence_band(cls, value: object) -> object:
        return value.strip().casefold() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_numeric_confidence(self) -> "BackendBDishPayload":
        if isinstance(self.extraction_confidence, float) and not (
            0 <= self.extraction_confidence <= 1
        ):
            raise ValueError("numeric extraction_confidence must be between 0 and 1")
        return self

    def to_parsed_dish(self) -> ParsedDish:
        price, price_text = parse_backend_a_price(self.price)
        confidence = (
            CONFIDENCE_SCORES[self.extraction_confidence]
            if isinstance(self.extraction_confidence, str)
            else self.extraction_confidence
        )
        return ParsedDish(
            original_name=self.original_name,
            translated_name=self.translated_name or self.original_name,
            canonical_name_en=self.canonical_guess or self.original_name,
            price=price,
            price_text=price_text,
            menu_description=self.menu_description,
            translated_description=self.translated_description,
            explicit_ingredients=self.explicit_ingredients,
            source_text=self.source_text,
            extraction_confidence=confidence,
        )


class BackendBMenuPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    menu_language: str | None = Field(default=None, max_length=100)
    target_language: str = Field(default="en", min_length=2, max_length=20)
    dishes: list[BackendBDishPayload] = Field(min_length=1)

    def to_menu_parse_result(self) -> MenuParseResult:
        return MenuParseResult(
            source_language=(
                normalize_source_language(self.menu_language)
                if self.menu_language
                else "unknown"
            ),
            output_language=self.target_language,
            dishes=[dish.to_parsed_dish() for dish in self.dishes],
        )


BackendADishPayload = BackendBDishPayload
BackendAMenuPayload = BackendBMenuPayload
MenuPayload = MenuParseResult | BackendBMenuPayload


def normalize_menu_payload(menu: MenuPayload) -> MenuParseResult:
    return (
        menu.to_menu_parse_result() if isinstance(menu, BackendBMenuPayload) else menu
    )
