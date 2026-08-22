from app.schemas import (
    UnknownDishInput,
    FallbackBatchRequest,
)
from app.services.dish_fallback import fallback_dishes


def main():
    request = FallbackBatchRequest(
        schema_version="1.1",
        batch_id="fallback-test-batch-001",
        dishes=[
            UnknownDishInput(
                request_id="dish-request-001",
                original_name="Escargots Persillade",
                canonical_name_en="Escargots",
                menu_description="Escargot, Garlic and Parsley Crumbs",
                explicit_ingredients=[
                    "Escargot",
                    "Garlic",
                    "Parsley Crumbs",
                ],
                source_text=(
                    "Escargots Persillade - "
                    "Escargot, Garlic and Parsley Crumbs"
                ),
            ),
            UnknownDishInput(
                request_id="dish-request-002",
                original_name="Bombe Alaska",
                canonical_name_en="Baked Alaska",
                menu_description="Coconut Sorbet, Passion Fruit Puree",
                explicit_ingredients=[
                    "Coconut Sorbet",
                    "Passion Fruit Puree",
                ],
                source_text=(
                    "Bombe Alaska - Coconut Sorbet, "
                    "Passion Fruit Puree"
                ),
            ),
        ],
    )

    result = fallback_dishes(request)

    print("\n=== FoodHub B/C v1.1 Fallback Test ===\n")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()