from schemas.dish import ParsedDish, normalize_lookup_name
from schemas.preference import PreferenceKind, PreferenceStrength, UserPreference
from schemas.recommendation import (
    DishDecision,
    DishEvidence,
    RecommendationStatus,
    RecommendedDish,
)
from schemas.resolution import DishResolutionStatus
from schemas.safety import AllergenPresence
from services.recommendation.allergen_mapper import (
    ALLERGEN_TERM_ALIASES,
    GLUTEN_TERMS,
    assess_allergens,
    find_allergen_matches,
)
from services.recommendation.ingredient_localizer import localize_ingredients
from services.recommendation.localization import message

PORK_TERMS = {"pork", "bacon", "ham", "prosciutto", "pancetta", "lard"}
BEEF_TERMS = {"beef", "ribeye", "steak", "veal"}
FISH_AND_SEAFOOD_TERMS = {
    "cod",
    "fish",
    "salmon",
    "sardine",
    "tuna",
    "prawn",
    "seafood",
    "shrimp",
    "shellfish",
}
MEAT_TERMS = PORK_TERMS | {
    "beef",
    "chicken",
    "duck",
    "fish",
    "lamb",
    "prawn",
    "seafood",
    "shrimp",
    "turkey",
}
ANIMAL_PRODUCT_TERMS = MEAT_TERMS | {
    "butter",
    "cheese",
    "cream",
    "egg",
    "milk",
    "yogurt",
}
ALCOHOL_TERMS = {"alcohol", "beer", "brandy", "rum", "wine"}
PREFERENCE_TERM_ALIASES = {
    **ALLERGEN_TERM_ALIASES,
    "wheat": {"bread", "breadcrumbs", "flour", "pasta", "wheat"},
    "alcohol": ALCOHOL_TERMS,
    "spicy": {"chilli", "chili", "hot sauce", "spicy"},
    "mushroom": {"mushroom", "mushrooms", "truffle", "truffles"},
}


def _contains_phrase(text: str, term: str) -> bool:
    return f" {term} " in f" {text} "


def _find_matches(ingredients: set[str], terms: set[str]) -> list[str]:
    return sorted(
        ingredient
        for ingredient in ingredients
        if any(_contains_phrase(ingredient, term) for term in terms)
    )


def _preference_terms(preference: UserPreference) -> tuple[set[str], bool]:
    code = preference.code
    if preference.kind in {PreferenceKind.ALLERGY, PreferenceKind.AVOID}:
        return PREFERENCE_TERM_ALIASES.get(code, {normalize_lookup_name(code)}), False
    if code == "no_pork":
        return PORK_TERMS, False
    if code == "vegetarian":
        return MEAT_TERMS, False
    if code == "pescatarian":
        return MEAT_TERMS - FISH_AND_SEAFOOD_TERMS, False
    if code == "vegan":
        return ANIMAL_PRODUCT_TERMS, False
    if code == "gluten_free":
        return GLUTEN_TERMS, False
    if code in {"dairy_free", "lactose_free"}:
        return ALLERGEN_TERM_ALIASES["milk"], False
    if code == "egg_free":
        return ALLERGEN_TERM_ALIASES["egg"], False
    if code in {"halal", "halal_required"}:
        return PORK_TERMS | ALCOHOL_TERMS, True
    if code == "kosher_required":
        return set(), True
    if code == "no_beef":
        return BEEF_TERMS, False
    if code == "no_alcohol":
        return ALCOHOL_TERMS, False
    return set(), False


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def decide_dish(
    evidence: DishEvidence,
    preferences: list[UserPreference],
    resolution_status: DishResolutionStatus | None = None,
    language: str = "en",
) -> DishDecision:
    explicit = {normalize_lookup_name(value) for value in evidence.explicit_ingredients}
    reference = {
        normalize_lookup_name(value) for value in evidence.reference_ingredients
    }
    inferred = {
        normalize_lookup_name(value.name) for value in evidence.inferred_ingredients
    }
    hard_conflicts: list[str] = []
    cautions: list[str] = []

    for preference in preferences:
        matching_assessments = [
            assessment
            for assessment in evidence.allergen_assessments
            if assessment.code == preference.code
        ]
        if preference.kind == PreferenceKind.ALLERGY and matching_assessments:
            for assessment in matching_assessments:
                reason = message(
                    "allergen_evidence",
                    language,
                    code=preference.code,
                    status=assessment.status.value,
                    source=assessment.evidence_source.value,
                    reasoning=assessment.reasoning,
                )
                if (
                    assessment.status == AllergenPresence.CONTAINS
                    and preference.strength == PreferenceStrength.HARD
                ):
                    _append_unique(hard_conflicts, reason)
                elif assessment.status in {
                    AllergenPresence.CONTAINS,
                    AllergenPresence.MAY_CONTAIN,
                    AllergenPresence.UNKNOWN,
                }:
                    _append_unique(cautions, reason)
            continue

        terms, requires_confirmation = _preference_terms(preference)
        if (
            preference.kind == PreferenceKind.ALLERGY
            and preference.code in ALLERGEN_TERM_ALIASES
        ):
            explicit_matches = find_allergen_matches(
                evidence.explicit_ingredients,
                preference.code,
            )
            reference_matches = find_allergen_matches(
                evidence.reference_ingredients,
                preference.code,
            )
            inferred_matches = find_allergen_matches(
                [ingredient.name for ingredient in evidence.inferred_ingredients],
                preference.code,
            )
        else:
            explicit_matches = _find_matches(explicit, terms)
            reference_matches = _find_matches(reference, terms)
            inferred_matches = _find_matches(inferred, terms)

        if explicit_matches:
            reason = message(
                "explicit_conflict",
                language,
                code=preference.code,
                ingredients=", ".join(localize_ingredients(explicit_matches, language)),
            )
            target = (
                hard_conflicts
                if preference.strength == PreferenceStrength.HARD
                else cautions
            )
            _append_unique(target, reason)

        if reference_matches:
            _append_unique(
                cautions,
                message(
                    "reference_conflict",
                    language,
                    code=preference.code,
                    ingredients=", ".join(
                        localize_ingredients(reference_matches, language)
                    ),
                ),
            )

        if inferred_matches:
            _append_unique(
                cautions,
                message(
                    "inferred_conflict",
                    language,
                    code=preference.code,
                    ingredients=", ".join(
                        localize_ingredients(inferred_matches, language)
                    ),
                ),
            )

        if requires_confirmation and not explicit_matches:
            _append_unique(
                cautions,
                message(
                    "requires_confirmation",
                    language,
                    code=preference.code,
                ),
            )

    if resolution_status == DishResolutionStatus.NEEDS_LLM:
        _append_unique(cautions, message("needs_llm", language))
    elif resolution_status == DishResolutionStatus.LOOKUP_UNAVAILABLE:
        _append_unique(cautions, message("lookup_unavailable", language))

    if hard_conflicts:
        return DishDecision(
            status=RecommendationStatus.AVOID,
            reasons=hard_conflicts,
            warnings=[message("confirm_allergy", language)],
        )
    if cautions:
        return DishDecision(
            status=RecommendationStatus.CHECK_WITH_STAFF,
            reasons=cautions,
            warnings=[message("incomplete_evidence", language)],
        )
    return DishDecision(
        status=RecommendationStatus.GOOD_MATCH,
        reasons=[message("no_conflict", language)],
        warnings=[message("not_guarantee", language)],
    )


def recommend_dish(
    dish: ParsedDish,
    preferences: list[UserPreference],
    language: str = "en",
) -> RecommendedDish:
    evidence = DishEvidence(explicit_ingredients=dish.explicit_ingredients)
    evidence.allergen_assessments = assess_allergens(
        evidence.explicit_ingredients,
        [],
        [],
    )
    return RecommendedDish(
        dish=dish,
        decision=decide_dish(evidence, preferences, language=language),
    )
