import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import MenuParseResponse


# Root directory of backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# Local test menu image
IMAGE_PATH = BASE_DIR / "samples" / "menu_test.jpg"
TARGET_LANGUAGE = "en"


def encode_image(image_path: Path) -> str:
    """
    Convert a local image into a Base64 string for API input.
    """
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main() -> None:
    """
    Parse one menu image into the FoodHub structured menu schema.
    """

    # Load environment variables from backend/.env
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from backend/.env"
        )

    if not model:
        raise RuntimeError(
            "OPENAI_MODEL is missing from backend/.env"
        )

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Menu image not found: {IMAGE_PATH}"
        )

    client = OpenAI(api_key=api_key)

    image_base64 = encode_image(IMAGE_PATH)

    system_prompt = """

You are the menu extraction component of FoodHub.

Extract structured information from exactly one restaurant menu image
using the provided schema.

CORE RULE:
The restaurant menu is the source of truth.
Do not infer unstated ingredients or culinary facts.

FIELD RULES:

1. original_name
   - Preserve the dish name exactly as written.

2. translated_name / translated_description
   - Translate into the requested target language.
   - Do not add information not present in the menu.
   - If menu_description is null, translated_description must be null.

3. canonical_guess
   - Return a short English standard dish name for database matching.
   - Keep it conservative and generic.
   - Do not add sauces, sides, ingredients, or preparation details unless essential.
   - Return null when uncertain.

4. menu_description
   - Preserve the restaurant-written description.

5. explicit_ingredients
   - Include only ingredients or dish components explicitly written
     in the dish name or description.
   - Do not infer typical ingredients.
   - Do not expand named sauces, purées, butters, or condiments.
   - Cooking-method words such as grilled, roasted, baked, braised,
     smoked, or flambé are not ingredients by themselves.
   - If no explicit ingredient/component is written, return [].

6. source_text
   - Preserve the visible menu evidence for the dish.

7. menu_language
   - Identify all clearly visible languages, e.g. "French / English".

8. extraction_confidence
   - Use only: high, medium, low.

Extract all clearly visible orderable menu items.

Do not provide recommendations, allergen judgments, dietary suitability,
taste, texture, or inferred culinary information.

Example:
If the menu only says "Ratatouille 10",
explicit_ingredients must be [].
"""

    response = client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                             "Parse this restaurant menu image into the FoodHub menu "
                            f"extraction schema. Use '{TARGET_LANGUAGE}' as the target "
                             "language for user-facing translations."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:image/jpeg;base64,{image_base64}"
                        ),
                    },
                ],
            },
        ],
        text_format=MenuParseResponse,
    )

    parsed_menu = response.output_parsed

    if parsed_menu is None:
        raise RuntimeError(
            "The model did not return a valid structured menu response."
        )

    print("\n=== FoodHub Structured Menu ===\n")

    print(
        parsed_menu.model_dump_json(
            indent=2,
            exclude_none=False,
        )
    )

    if response.usage:
        print("\n=== Usage ===")
        print(response.usage)


if __name__ == "__main__":
    main()