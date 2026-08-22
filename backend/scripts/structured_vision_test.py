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

Extract restaurant-specific information from exactly one menu image
and return it using the provided schema.

CORE PRINCIPLE:
The restaurant menu is the source of truth.
Restaurant-specific evidence always takes priority over generic
culinary knowledge.

EXTRACTION RULES:

1. original_name
   - Preserve the dish name as written on the menu.
   - Do not translate or rewrite it.

2. canonical_guess
   - Return a short, standard, commonly recognised dish name that is
     useful as a database matching key.
   - Prefer the generic dish family/name rather than rewriting the full
     restaurant description.
   - Translation into English is allowed when unambiguous.
   - Do not add preparation details, sauces, sides, or ingredients
     unless they are essential to the standard dish name.
   - Return null when uncertain.
   - Never invent details.

   Examples:
   "Steak Frites, Sauce Béarnaise" -> "Steak Frites"
   "Tartare de Boeuf" -> "Beef Tartare"
   "Poulet Rôti" -> "Roast Chicken"

3. menu_description
   - Preserve the restaurant-written description.
   - Do not add information that is not visible on the menu.

4. explicit_ingredients
   - Include only food ingredients or dish components that are
     explicitly written in the dish name or description.
   - Never infer ingredients from general culinary knowledge.
   - Do not expand a named sauce, butter, puree, condiment, or dish
     into ingredients that are not written.
   - Preserve restaurant wording where practical.
   - Do not include cooking-method words such as grilled, roasted,
     braised, baked, or flambé as ingredients.
   - If no explicit ingredient/component information is written,
     return an empty list.

5. source_text
   - Preserve the visible menu evidence supporting the extraction.
   - Do not add reconstructed or inferred text.

6. menu_language
   - Identify all languages clearly used for dish names or
     descriptions on the page.
   - If both French and English are clearly present, return
     "French / English".

7. extraction_confidence
   - Use only high, medium, or low.
   - Confidence refers to extraction accuracy from the image,
     not confidence in general culinary knowledge.

8. Extract all clearly visible orderable menu items.

9. Do not provide recommendations, allergen judgments, dietary
   suitability, inferred ingredients, taste, texture, or other
   culinary interpretation.

IMPORTANT EXAMPLE:

If the menu only says:

Ratatouille 10

return:

explicit_ingredients = []

Do NOT add tomato, eggplant, zucchini, or any other typical
Ratatouille ingredients.

If the menu says:

Lamb Shoulder, Smoked Eggplant Puree, Fregola, Confit Tomatoes

those components may be extracted because they are explicitly written.
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
                            "Parse this restaurant menu image into the "
                            "FoodHub menu extraction schema."
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