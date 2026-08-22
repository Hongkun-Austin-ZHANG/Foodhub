from app.schemas import (
    UnknownDishInput,
    FallbackBatchRequest,
)
from app.services.dish_fallback import fallback_dishes


def main():
    request = FallbackBatchRequest(
        request_id="fallback-test-001",
        dishes=[
            UnknownDishInput(
                dish_id="dish-001",
                original_name="Escargots Persillade",
                canonical_guess="Escargots",
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
                dish_id="dish-002",
                original_name="Bombe Alaska",
                canonical_guess="Baked Alaska",
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

    print("\n=== FoodHub Unknown Dish Fallback Test ===\n")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()