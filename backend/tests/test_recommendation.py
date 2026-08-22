from schemas.dish import ParsedDish
from schemas.preference import (
    DailyPreferenceOverride,
    PreferenceContext,
    PreferenceKind,
    PreferenceStrength,
    UserPreference,
)
from schemas.recommendation import RecommendationStatus
from services.recommendation.engine import recommend_dish
from services.recommendation.reconciler import resolve_preferences


def test_daily_override_cannot_disable_hard_allergy() -> None:
    context = PreferenceContext(
        persistent=[
            UserPreference(
                code="peanut",
                kind=PreferenceKind.ALLERGY,
                strength=PreferenceStrength.HARD,
            )
        ],
        daily_overrides=[DailyPreferenceOverride(code="peanut", enabled=False)],
    )

    result = resolve_preferences(context)

    assert [preference.code for preference in result.preferences] == ["peanut"]


def test_explicit_hard_conflict_returns_avoid() -> None:
    dish = ParsedDish(
        original_name="Poulet Satay",
        canonical_name_en="Chicken Satay",
        explicit_ingredients=["chicken", "peanut sauce"],
        extraction_confidence=0.95,
    )
    preferences = [
        UserPreference(
            code="peanut",
            kind=PreferenceKind.ALLERGY,
            strength=PreferenceStrength.HARD,
        )
    ]

    result = recommend_dish(dish, preferences)

    assert result.decision.status == RecommendationStatus.AVOID


def test_new_daily_catalog_option_keeps_its_rule_metadata() -> None:
    context = PreferenceContext(
        daily_overrides=[DailyPreferenceOverride(code="no_pork", enabled=True)]
    )

    result = resolve_preferences(context)

    assert result.preferences[0].kind == PreferenceKind.RELIGIOUS
    assert result.preferences[0].strength == PreferenceStrength.HARD


def test_frontend_allergy_aliases_are_canonicalized() -> None:
    preferences = [
        UserPreference(
            code="peanuts",
            kind=PreferenceKind.ALLERGY,
            strength=PreferenceStrength.HARD,
        ),
        UserPreference(
            code="sulphites",
            kind=PreferenceKind.ALLERGY,
            strength=PreferenceStrength.HARD,
        ),
    ]

    assert [preference.code for preference in preferences] == ["peanut", "sulfites"]


def test_molluscs_and_crustacean_shellfish_are_separate_rules() -> None:
    dish = ParsedDish(
        original_name="Calamari",
        canonical_name_en="Fried Calamari",
        explicit_ingredients=["squid"],
        extraction_confidence=0.95,
    )
    mollusc_result = recommend_dish(
        dish,
        [
            UserPreference(
                code="molluscs",
                kind=PreferenceKind.ALLERGY,
                strength=PreferenceStrength.HARD,
            )
        ],
    )
    shellfish_result = recommend_dish(
        dish,
        [
            UserPreference(
                code="shellfish",
                kind=PreferenceKind.ALLERGY,
                strength=PreferenceStrength.HARD,
            )
        ],
    )

    assert mollusc_result.decision.status == RecommendationStatus.AVOID
    assert shellfish_result.decision.status == RecommendationStatus.GOOD_MATCH


def test_plant_milk_and_butter_lettuce_do_not_trigger_milk_allergy() -> None:
    dish = ParsedDish(
        original_name="Vegan Salad",
        canonical_name_en="Vegan Salad",
        explicit_ingredients=["coconut milk", "butter lettuce"],
        extraction_confidence=0.95,
    )
    result = recommend_dish(
        dish,
        [
            UserPreference(
                code="milk",
                kind=PreferenceKind.ALLERGY,
                strength=PreferenceStrength.HARD,
            )
        ],
    )

    assert result.decision.status == RecommendationStatus.GOOD_MATCH


def test_common_menu_terms_map_to_milk_and_gluten_allergens() -> None:
    dish = ParsedDish(
        original_name="Cheese course",
        canonical_name_en="Gruyere and Goats Curd",
        explicit_ingredients=["aged Gruyere", "goats curd", "sour dough croutons"],
        extraction_confidence=0.95,
    )
    result = recommend_dish(
        dish,
        [
            UserPreference(
                code="milk",
                kind=PreferenceKind.ALLERGY,
                strength=PreferenceStrength.HARD,
            ),
            UserPreference(
                code="gluten",
                kind=PreferenceKind.ALLERGY,
                strength=PreferenceStrength.HARD,
            ),
        ],
    )

    assert result.decision.status == RecommendationStatus.AVOID
    assert any("milk" in reason for reason in result.decision.reasons)
    assert any("gluten" in reason for reason in result.decision.reasons)
