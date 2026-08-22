import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import MenuParseResponse


load_dotenv()


SUPPORTED_IMAGE_TYPES = {
    "image/jpeg",   # covers both .jpg and .jpeg
    "image/png",
    "image/webp",
}


SYSTEM_PROMPT = """
You are the menu extraction component of FoodHub.

Extract structured information from exactly one restaurant menu image
using the provided schema.

CORE RULE:
The restaurant menu is the source of truth.
Do not infer unstated ingredients or culinary facts.

FIELD RULES:

1. original_name
   - Preserve the dish name as written on the menu.

2. translated_name / translated_description
   - Translate into the requested target language.
   - Do not add information not present in the menu.
   - If menu_description is null, translated_description must be null.

3. canonical_guess
   - Return a short English standard dish name for database matching.
   - Keep it conservative.
   - Return null when uncertain.

4. menu_description
   - Preserve the restaurant-written description.

5. explicit_ingredients
   - Include only ingredients or dish components explicitly written
     in the dish name or description.
   - Do not infer typical ingredients.
   - Do not expand named sauces, purees, butters, or condiments.
   - Cooking methods are not ingredients by themselves.
   - If no explicit ingredient/component is written, return [].

6. source_text
   - Preserve visible menu evidence for the dish.

7. menu_language
   - Identify all clearly visible languages.

8. extraction_confidence
   - Use only high, medium, or low.

Extract all clearly visible orderable menu items.

Do not provide recommendations, allergen judgments, dietary suitability,
taste, texture, or inferred culinary information.

If the menu only says "Ratatouille 10",
explicit_ingredients must be [].
"""


def parse_menu(
    image_bytes: bytes,
    preferred_language: str,
    mime_type: str,
) -> MenuParseResponse:
    """
    Parse one restaurant menu image into FoodHub's structured schema.

    Args:
        image_bytes:
            Raw bytes of the uploaded menu image.

        preferred_language:
            Target language for user-facing translations,
            for example "en" or "zh".

        mime_type:
            MIME type of the uploaded image.
            Supported: image/jpeg, image/png, image/webp.

    Returns:
        A validated MenuParseResponse.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from the environment."
        )

    if not model:
        raise RuntimeError(
            "OPENAI_MODEL is missing from the environment."
        )

    if not image_bytes:
        raise ValueError("Menu image is empty.")

    if not preferred_language:
        raise ValueError("preferred_language is required.")

    if mime_type not in SUPPORTED_IMAGE_TYPES:
        raise ValueError(
            f"Unsupported image type: {mime_type}. "
            "Supported types are image/jpeg, image/png, and image/webp."
        )

    client = OpenAI(api_key=api_key)

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    image_data_url = (
        f"data:{mime_type};base64,{image_base64}"
    )

    response = client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Parse this menu into the FoodHub schema. "
                            f"Use '{preferred_language}' as the target "
                            "language for user-facing translations."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_data_url,
                    },
                ],
            },
        ],
        text_format=MenuParseResponse,
    )

    parsed_menu = response.output_parsed

    if parsed_menu is None:
        raise RuntimeError(
            "The model did not return a valid structured menu result."
        )

    return parsed_menu.model_copy(
        update={"target_language": preferred_language}
    )