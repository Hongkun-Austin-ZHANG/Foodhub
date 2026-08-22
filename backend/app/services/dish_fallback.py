import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import (
    FallbackBatchRequest,
    FallbackBatchResponse,
)


load_dotenv()


SYSTEM_PROMPT = """
You are the unknown-dish fallback component of FoodHub.

You receive a batch of restaurant dishes that could not be matched
by the local database or TheMealDB.

Your job is to provide neutral, generic culinary knowledge for each dish.

EVIDENCE RULES:

1. Restaurant menu evidence is the source of truth.
   The following input fields are restaurant-specific evidence:
   - original_name
   - menu_description
   - explicit_ingredients
   - source_text

2. inferred_ingredients are generic culinary inference.
   - They are NOT restaurant-confirmed facts.
   - Do not repeat ingredients already present in explicit_ingredients.
   - Include only reasonably likely traditional ingredients.
   - When uncertain, omit the ingredient instead of guessing strongly.
   - Keep reasoning short.

3. canonical_name_en
   - Return a concise English canonical dish name.
   - Keep the interpretation conservative.

4. description
   - Return one short, neutral English explanation.
   - Do not claim inferred ingredients are definitely used by this restaurant.

5. aliases and cuisine
   - Return aliases only when useful and well known.
   - Return an empty list when no useful aliases are known.
   - Return null for cuisine when uncertain.

6. Do NOT provide:
   - allergen assessments
   - allergy safety decisions
   - dietary suitability
   - vegan / vegetarian / halal judgments
   - personalized recommendations
   - recommended / avoid decisions

7. Preserve every request_id exactly.
   Return exactly one result for every input dish.

Process the entire batch in one response.
"""


def fallback_dishes(
    request: FallbackBatchRequest,
) -> FallbackBatchResponse:
    """
    Generate structured culinary knowledge for all confirmed unmatched
    dishes using one OpenAI call.
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

    if not request.dishes:
        raise ValueError(
            "Fallback request must contain at least one dish."
        )

    client = OpenAI(api_key=api_key)

    response = client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Provide fallback culinary knowledge for the following "
                    "confirmed unmatched dishes.\n\n"
                    f"{request.model_dump_json(indent=2)}\n\n"
                    f"Use schema_version '1.1'. "
                    f"Echo batch_id '{request.batch_id}' exactly. "
                    f"Set model_id to '{model}' for every result."
                ),
            },
        ],
        text_format=FallbackBatchResponse,
    )

    parsed_result = response.output_parsed

    if parsed_result is None:
        raise RuntimeError(
            "The model did not return a valid structured fallback result."
        )

    expected_request_ids = {
        dish.request_id for dish in request.dishes
    }

    returned_request_ids = {
        result.request_id for result in parsed_result.results
    }

    if returned_request_ids != expected_request_ids:
        raise RuntimeError(
            "Fallback response request_ids do not match the input batch."
        )

    final_results = [
        result.model_copy(
            update={"model_id": model}
        )
        for result in parsed_result.results
    ]

    return parsed_result.model_copy(
        update={
            "schema_version": "1.1",
            "batch_id": request.batch_id,
            "results": final_results,
        }
    )