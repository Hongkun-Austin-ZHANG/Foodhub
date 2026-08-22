from schemas.dish import IngredientEvidence, normalize_lookup_name
from schemas.safety import (
    AllergenAssessment,
    AllergenEvidenceSource,
    AllergenPresence,
)

GLUTEN_TERMS = {
    "barley",
    "bread",
    "breadcrumbs",
    "crouton",
    "croutons",
    "dough",
    "pasta",
    "rye",
    "sourdough",
    "sour dough",
    "wheat",
}

ALLERGEN_TERM_ALIASES = {
    "peanut": {"groundnut", "groundnuts", "peanut", "peanuts"},
    "tree_nuts": {
        "almond",
        "almonds",
        "cashew",
        "cashews",
        "hazelnut",
        "hazelnuts",
        "macadamia",
        "pecan",
        "pecans",
        "pine nut",
        "pine nuts",
        "pistachio",
        "pistachios",
        "tree nut",
        "tree nuts",
        "walnut",
        "walnuts",
    },
    "milk": {
        "butter",
        "casein",
        "cheese",
        "comte",
        "cream",
        "curd",
        "dairy",
        "fromage",
        "ghee",
        "goat curd",
        "goats curd",
        "gruyere",
        "milk",
        "whey",
        "yogurt",
    },
    "egg": {"egg", "eggs", "mayonnaise", "meringue"},
    "fish": {"anchovy", "cod", "fish", "salmon", "sardine", "tuna"},
    "shellfish": {
        "crab",
        "crayfish",
        "crustacean",
        "crustaceans",
        "lobster",
        "prawn",
        "prawns",
        "shellfish",
        "shrimp",
    },
    "molluscs": {
        "clam",
        "clams",
        "escargot",
        "mollusc",
        "molluscs",
        "mussel",
        "mussels",
        "octopus",
        "oyster",
        "oysters",
        "scallop",
        "scallops",
        "snail",
        "snails",
        "squid",
    },
    "gluten": GLUTEN_TERMS,
    "soy": {"miso", "soy", "soya", "tamari", "tempeh", "tofu"},
    "sesame": {"sesame", "tahini"},
    "mustard": {"dijon", "mustard", "mustard powder", "mustard seed"},
    "celery": {"celeriac", "celery", "celery salt", "celery seed"},
    "lupin": {"lupin", "lupine"},
    "sulfites": {"sulfite", "sulfites", "sulphite", "sulphites"},
}

ALLERGEN_EXCLUDED_PHRASES = {
    "milk": {"almond milk", "butter lettuce", "coconut milk", "oat milk", "soy milk"},
    "molluscs": {"oyster mushroom", "oyster mushrooms"},
}


def _contains_phrase(text: str, term: str) -> bool:
    return f" {term} " in f" {text} "


def find_allergen_matches(ingredients: list[str], code: str) -> list[str]:
    terms = ALLERGEN_TERM_ALIASES.get(code, set())
    excluded = ALLERGEN_EXCLUDED_PHRASES.get(code, set())
    matches: list[str] = []
    for ingredient in ingredients:
        normalized = normalize_lookup_name(ingredient)
        if any(_contains_phrase(normalized, phrase) for phrase in excluded):
            continue
        if any(_contains_phrase(normalized, term) for term in terms):
            matches.append(ingredient)
    return list(dict.fromkeys(matches))


def assess_allergens(
    explicit_ingredients: list[str],
    reference_ingredients: list[str],
    inferred_ingredients: list[IngredientEvidence],
) -> list[AllergenAssessment]:
    """Map dish-side ingredient evidence to allergens without user data."""

    assessments: list[AllergenAssessment] = []
    inferred_names = [ingredient.name for ingredient in inferred_ingredients]
    for code in ALLERGEN_TERM_ALIASES:
        explicit_matches = find_allergen_matches(explicit_ingredients, code)
        if explicit_matches:
            assessments.append(
                AllergenAssessment(
                    code=code,
                    status=AllergenPresence.CONTAINS,
                    evidence_source=AllergenEvidenceSource.MENU_EVIDENCE,
                    confidence=1.0,
                    reasoning=(
                        "The restaurant menu explicitly names: "
                        + ", ".join(explicit_matches)
                    ),
                )
            )
            continue

        reference_matches = find_allergen_matches(reference_ingredients, code)
        if reference_matches:
            assessments.append(
                AllergenAssessment(
                    code=code,
                    status=AllergenPresence.MAY_CONTAIN,
                    evidence_source=AllergenEvidenceSource.REFERENCE_RECIPE,
                    confidence=0.7,
                    reasoning=(
                        "A generic reference recipe includes: "
                        + ", ".join(reference_matches)
                    ),
                )
            )
            continue

        inferred_matches = find_allergen_matches(inferred_names, code)
        if inferred_matches:
            confidences = [
                ingredient.confidence
                for ingredient in inferred_ingredients
                if ingredient.name in inferred_matches
                and ingredient.confidence is not None
            ]
            assessments.append(
                AllergenAssessment(
                    code=code,
                    status=AllergenPresence.MAY_CONTAIN,
                    evidence_source=AllergenEvidenceSource.INFERRED,
                    confidence=max(confidences, default=0.5),
                    reasoning=(
                        "Backend B inferred possible ingredients: "
                        + ", ".join(inferred_matches)
                    ),
                )
            )
    return assessments
