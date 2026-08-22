from dataclasses import dataclass

from schemas.dish import normalize_lookup_name
from schemas.frontend import (
    CurrentMealPreference,
    DishPreferenceTags,
    RankedRecommendation,
)
from schemas.preference import UserPreference
from schemas.recommendation import AnalyzedDish, DishDecision, RecommendationStatus
from services.recommendation.engine import decide_dish
from services.recommendation.localization import message

PROTEIN_TERMS = {
    "beef": {"beef", "fillet", "ribeye", "scotch fillet", "steak", "tartare"},
    "lamb": {"lamb", "mutton"},
    "chicken": {"chicken", "poulet"},
    "duck": {"duck"},
    "pork": {"bacon", "ham", "pancetta", "pork", "prosciutto"},
    "fish": {"cod", "fish", "salmon", "sardine", "tuna"},
    "shellfish": {
        "clam",
        "crab",
        "lobster",
        "mussel",
        "octopus",
        "oyster",
        "prawn",
        "scallop",
        "shrimp",
        "snail",
        "squid",
    },
}
PLANT_TERMS = {
    "aubergine",
    "bean",
    "beet",
    "broccoli",
    "courgette",
    "lentil",
    "mushroom",
    "pea",
    "potato",
    "ratatouille",
    "salad",
    "tofu",
    "vegetable",
}
FLAVOUR_TERMS = {
    "savoury": {
        "beef",
        "broth",
        "cheese",
        "chicken",
        "fish",
        "lamb",
        "mushroom",
        "pork",
        "steak",
    },
    "rich": {"butter", "cheese", "chocolate", "cream", "pork belly"},
    "light": {"citrus", "fish", "lettuce", "salad", "sorbet", "vegetable"},
    "creamy": {"butter", "cheese", "cream", "curd", "mash", "mousse"},
    "herby": {"basil", "herb", "parsley", "rosemary", "thyme"},
    "smoky": {"char grilled", "chargrilled", "grilled", "smoked"},
    "tangy": {"caper", "lemon", "lime", "pickle", "vinegar"},
    "sweet": {"berry", "cake", "chocolate", "dessert", "fruit", "honey", "sugar"},
}
TEXTURE_TERMS = {
    "crispy": {"crisp", "crispy", "fried", "fries"},
    "tender": {"braised", "fillet", "slow cooked", "tender"},
    "creamy": {"cream", "creamy", "curd", "mash", "mousse"},
    "crunchy": {"crumb", "crouton", "nuts", "pickle"},
    "soft": {"braised", "gnocchi", "mash", "mousse", "soup"},
    "chewy": {"bread", "sourdough", "steak"},
    "brothy": {"broth", "soup"},
}
HOT_TERMS = {"chilli", "chili", "espelette", "hot sauce", "nduja"}
MEDIUM_TERMS = HOT_TERMS | {"pepper sauce", "peppercorn", "spicy"}


def _dish_text(dish: AnalyzedDish) -> str:
    values = [
        dish.dish.original_name,
        dish.dish.translated_name or "",
        dish.dish.canonical_name_en,
        dish.dish.menu_description or "",
        dish.dish.translated_description or "",
        dish.dish.source_text or "",
        *dish.evidence.explicit_ingredients,
        *dish.evidence.reference_ingredients,
        *(ingredient.name for ingredient in dish.evidence.inferred_ingredients),
    ]
    return normalize_lookup_name(" ".join(values))


def _contains(text: str, term: str) -> bool:
    return f" {normalize_lookup_name(term)} " in f" {text} "


def _matching_tags(text: str, catalog: dict[str, set[str]]) -> list[str]:
    return sorted(
        tag
        for tag, terms in catalog.items()
        if any(_contains(text, term) for term in terms)
    )


def classify_dish_preferences(dish: AnalyzedDish) -> DishPreferenceTags:
    text = _dish_text(dish)
    proteins = _matching_tags(text, PROTEIN_TERMS)
    if not proteins and any(_contains(text, term) for term in PLANT_TERMS):
        proteins = ["plant_based"]
    spice_level = (
        "hot"
        if any(_contains(text, term) for term in HOT_TERMS)
        else "medium"
        if any(_contains(text, term) for term in MEDIUM_TERMS)
        else "mild"
    )
    return DishPreferenceTags(
        proteins=proteins,
        flavours=_matching_tags(text, FLAVOUR_TERMS),
        textures=_matching_tags(text, TEXTURE_TERMS),
        spice_level=spice_level,
    )


def merge_current_preference(
    persistent: list[UserPreference],
    current: CurrentMealPreference,
) -> CurrentMealPreference:
    stored = CurrentMealPreference()
    for preference in persistent:
        if preference.code.startswith("protein_"):
            stored.preferred_proteins.append(preference.code.removeprefix("protein_"))
        elif preference.code.startswith("flavour_"):
            stored.preferred_flavours.append(preference.code.removeprefix("flavour_"))
        elif preference.code.startswith("texture_"):
            stored.preferred_textures.append(preference.code.removeprefix("texture_"))
        elif preference.code.startswith("spice_level_"):
            stored.spice_level = preference.code.removeprefix("spice_level_")

    return CurrentMealPreference(
        preferred_proteins=(
            current.preferred_proteins
            if current.preferred_proteins
            else stored.preferred_proteins
        ),
        preferred_flavours=(
            current.preferred_flavours
            if current.preferred_flavours
            else stored.preferred_flavours
        ),
        preferred_textures=(
            current.preferred_textures
            if current.preferred_textures
            else stored.preferred_textures
        ),
        spice_level=current.spice_level or stored.spice_level,
    )


def score_preference_match(
    tags: DishPreferenceTags,
    preference: CurrentMealPreference,
    language: str,
) -> tuple[float, list[str], list[str]]:
    group_scores: list[float] = []
    matched_codes: list[str] = []
    reasons: list[str] = []
    groups = (
        (
            "protein",
            preference.preferred_proteins,
            tags.proteins,
            "matches_protein",
        ),
        (
            "flavour",
            preference.preferred_flavours,
            tags.flavours,
            "matches_flavour",
        ),
        (
            "texture",
            preference.preferred_textures,
            tags.textures,
            "matches_texture",
        ),
    )
    for prefix, selected, available, message_key in groups:
        if not selected:
            continue
        matches = sorted(set(selected) & set(available))
        group_scores.append(len(matches) / len(selected))
        for value in matches:
            matched_codes.append(f"{prefix}_{value}")
            reasons.append(message(message_key, language, value=value))

    if preference.spice_level is not None:
        spice_match = preference.spice_level == tags.spice_level
        group_scores.append(1.0 if spice_match else 0.0)
        if spice_match:
            matched_codes.append(f"spice_level_{preference.spice_level}")
            reasons.append(
                message(
                    "matches_spice",
                    language,
                    value=preference.spice_level,
                )
            )

    score = sum(group_scores) / len(group_scores) if group_scores else 0.0
    return round(score, 3), matched_codes, reasons


@dataclass(slots=True)
class _ScoredDish:
    dish: AnalyzedDish
    tags: DishPreferenceTags
    score: float
    matched: list[str]
    decision: DishDecision


def rank_dishes(
    dishes: list[AnalyzedDish],
    preferences: list[UserPreference],
    current: CurrentMealPreference,
    language: str,
) -> list[RankedRecommendation]:
    scored: list[_ScoredDish] = []
    for dish in dishes:
        tags = classify_dish_preferences(dish)
        score, matched, match_reasons = score_preference_match(
            tags,
            current,
            language,
        )
        decision = decide_dish(
            dish.evidence,
            preferences,
            dish.resolution_status,
            language,
        )
        if match_reasons:
            decision = decision.model_copy(
                update={"reasons": [*match_reasons, *decision.reasons]}
            )
        scored.append(
            _ScoredDish(
                dish=dish,
                tags=tags,
                score=score,
                matched=matched,
                decision=decision,
            )
        )

    safety_order = {
        RecommendationStatus.GOOD_MATCH: 0,
        RecommendationStatus.CHECK_WITH_STAFF: 1,
        RecommendationStatus.AVOID: 2,
    }
    scored.sort(
        key=lambda item: (
            safety_order[item.decision.status],
            -item.score,
            (item.dish.dish.translated_name or item.dish.dish.original_name).casefold(),
        )
    )

    return [
        RankedRecommendation(
            rank=index,
            preference_score=item.score,
            matched_preferences=item.matched,
            preference_tags=item.tags,
            dish=item.dish.dish,
            resolution_status=item.dish.resolution_status,
            match_score=item.dish.match_score,
            image_url=item.dish.image_url,
            image_is_reference=item.dish.image_is_reference,
            evidence=item.dish.evidence,
            decision=item.decision,
        )
        for index, item in enumerate(scored, start=1)
    ]
