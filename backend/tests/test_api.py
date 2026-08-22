from uuid import uuid4

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_capabilities_do_not_expose_provider_configuration() -> None:
    response = client.get("/api/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["demo_available"] is True
    assert body["supported_languages"] == ["en", "zh", "fr"]
    assert "api_key" not in body
    assert "model" not in body


def test_menu_validation_contract() -> None:
    response = client.post(
        "/api/menu/validate",
        json={
            "schema_version": "1.0",
            "source_language": "fr",
            "dishes": [
                {
                    "original_name": "Soupe à l'oignon",
                    "canonical_name_en": "French Onion Soup",
                    "explicit_ingredients": ["onion"],
                    "extraction_confidence": 0.9,
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_backend_b_payload_is_accepted_and_normalized() -> None:
    response = client.post(
        "/api/menu/validate",
        json={
            "menu_language": "French / English",
            "dishes": [
                {
                    "original_name": "Soup à l'oignon",
                    "canonical_guess": "French Onion Soup",
                    "price": "18",
                    "menu_description": "French Onion Soup, Gruyere Croutons",
                    "explicit_ingredients": ["French Onion Soup", "Gruyere Croutons"],
                    "source_text": "Soup à l'oignon 18",
                    "extraction_confidence": "high",
                }
            ],
        },
    )

    assert response.status_code == 200
    normalized = response.json()["menu"]
    assert normalized["source_language"] == "fr/en"
    assert normalized["dishes"][0]["canonical_name_en"] == "French Onion Soup"
    assert normalized["dishes"][0]["price"] == "18"


def test_fallback_dish_batch_contract_validation() -> None:
    batch_id = str(uuid4())
    response = client.post(
        "/api/menu/fallback-dishes/validate",
        json={
            "batch_id": batch_id,
            "results": [
                {
                    "request_id": str(uuid4()),
                    "canonical_name_en": "Escargots Persillade",
                    "aliases": [],
                    "description": "A French snail dish.",
                    "cuisine": "French",
                    "inferred_ingredients": [],
                    "overall_confidence": 0.7,
                    "model_id": "test-model-v1",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["batch"]["schema_version"] == "1.1"
    assert response.json()["batch"]["batch_id"] == batch_id


def test_preference_option_catalog_is_available_to_frontend() -> None:
    response = client.get("/api/preferences/options")

    assert response.status_code == 200
    options = {option["code"]: option for option in response.json()}
    assert options["peanut"]["kind"] == "allergy"
    assert options["peanut"]["allows_daily_override"] is False
    assert options["spicy"]["allows_daily_override"] is True
    assert {
        code for code, option in options.items() if option["group"] == "allergens"
    } == {
        "peanut",
        "tree_nuts",
        "milk",
        "egg",
        "fish",
        "shellfish",
        "molluscs",
        "gluten",
        "soy",
        "sesame",
        "mustard",
        "celery",
        "lupin",
        "sulfites",
    }
