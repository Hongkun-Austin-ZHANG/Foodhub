import json
from pathlib import Path

from schemas.menu import BackendBMenuPayload, MenuParseResult


def test_normalized_menu_contract_accepts_fixture() -> None:
    fixture_path = Path(__file__).parent / "test_menus" / "french_menu.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    menu = MenuParseResult.model_validate(payload)

    assert menu.schema_version == "1.0"
    assert menu.dishes[0].canonical_name_en == "French Onion Soup"
    assert menu.dishes[0].currency == "AUD"


def test_backend_b_payload_preserves_translation_and_multi_price() -> None:
    payload = BackendBMenuPayload.model_validate(
        {
            "menu_language": "French / English",
            "target_language": "zh",
            "dishes": [
                {
                    "original_name": "Escargots Persillade",
                    "translated_name": "蒜香欧芹蜗牛",
                    "canonical_guess": "Escargots",
                    "price": "14/24",
                    "menu_description": "Escargot, Garlic and Parsley Crumbs",
                    "translated_description": "蜗牛、蒜和欧芹面包屑",
                    "explicit_ingredients": ["Escargot", "Garlic and Parsley Crumbs"],
                    "source_text": "Escargots Persillade 14/24",
                    "extraction_confidence": "high",
                },
                {
                    "original_name": "Paris Mash",
                    "canonical_guess": None,
                    "price": "9",
                    "explicit_ingredients": ["Paris Mash"],
                    "source_text": "Paris Mash 9",
                    "extraction_confidence": "medium",
                },
            ],
        }
    )

    menu = payload.to_menu_parse_result()

    assert menu.source_language == "fr/en"
    assert menu.output_language == "zh"
    assert menu.target_language == "zh"
    assert menu.dishes[0].canonical_name_en == "Escargots"
    assert menu.dishes[0].translated_name == "蒜香欧芹蜗牛"
    assert menu.dishes[0].translated_description == "蜗牛、蒜和欧芹面包屑"
    assert menu.dishes[0].price is None
    assert menu.dishes[0].price_text == "14/24"
    assert menu.dishes[0].extraction_confidence == 0.9
    assert menu.dishes[1].canonical_name_en == "Paris Mash"
    assert menu.dishes[1].price == 9
