import pytest
from pydantic import ValidationError

from app.schemas import DishExtraction, MenuParseResponse


def test_valid_menu_response():
    """
    A valid menu payload should pass schema validation.
    """
    data = {
        "menu_language": "French",
        "dishes": [
            {
                "original_name": "Ratatouille Maison",
                "canonical_guess": "Ratatouille",
                "price": "18",
                "menu_description": (
                    "Agneau, aubergine, courgette, tomate"
                ),
                "explicit_ingredients": [
                    "lamb",
                    "aubergine",
                    "courgette",
                    "tomato",
                ],
                "source_text": (
                    "Ratatouille Maison — "
                    "Agneau, aubergine, courgette, tomate — 18"
                ),
                "extraction_confidence": "high",
            }
        ],
    }

    result = MenuParseResponse.model_validate(data)

    assert result.menu_language == "French"
    assert len(result.dishes) == 1

    dish = result.dishes[0]

    assert dish.original_name == "Ratatouille Maison"
    assert dish.canonical_guess == "Ratatouille"
    assert dish.price == "18"
    assert "lamb" in dish.explicit_ingredients


def test_canonical_guess_can_be_null():
    """
    The AI should be allowed to return null when it cannot safely
    infer a canonical dish name.
    """
    dish = DishExtraction(
        original_name="Le Secret de Mamie",
        canonical_guess=None,
        price="22",
        menu_description=None,
        explicit_ingredients=[],
        source_text="Le Secret de Mamie — 22",
        extraction_confidence="medium",
    )

    assert dish.canonical_guess is None
    assert dish.explicit_ingredients == []


def test_invalid_confidence_is_rejected():
    """
    Confidence must be one of: high, medium, low.
    """
    with pytest.raises(ValidationError):
        DishExtraction(
            original_name="Ratatouille",
            canonical_guess="Ratatouille",
            price="18",
            menu_description=None,
            explicit_ingredients=[],
            source_text="Ratatouille — 18",
            extraction_confidence="very_high",
        )


def test_unknown_fields_are_rejected():
    """
    Unexpected fields should fail validation so that the B -> C
    contract does not silently change.
    """
    data = {
        "menu_language": "French",
        "dishes": [],
        "recommendation_score": 99,
    }

    with pytest.raises(ValidationError):
        MenuParseResponse.model_validate(data)