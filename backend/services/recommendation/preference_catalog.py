from schemas.preference import (
    PreferenceKind,
    PreferenceOption,
    PreferenceOptionGroup,
    PreferenceStrength,
)


def option(
    code: str,
    group: PreferenceOptionGroup,
    kind: PreferenceKind,
    label: str,
    description: str,
    strength: PreferenceStrength = PreferenceStrength.HARD,
) -> PreferenceOption:
    return PreferenceOption(
        code=code,
        group=group,
        kind=kind,
        default_strength=strength,
        allows_daily_override=strength == PreferenceStrength.SOFT,
        label_en=label,
        description_en=description,
    )


PREFERENCE_OPTIONS = [
    option(
        "peanut",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Peanut",
        "Avoid peanuts and peanut-derived ingredients.",
    ),
    option(
        "tree_nuts",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Tree nuts",
        "Avoid almonds, cashews, walnuts and other tree nuts.",
    ),
    option(
        "milk",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Milk",
        "Avoid milk and dairy-derived ingredients.",
    ),
    option(
        "egg",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Egg",
        "Avoid egg and egg-derived ingredients.",
    ),
    option(
        "fish",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Fish",
        "Avoid fish and fish-derived ingredients.",
    ),
    option(
        "shellfish",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Shellfish",
        "Avoid crustaceans such as prawns, crab and lobster.",
    ),
    option(
        "molluscs",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Molluscs",
        "Avoid molluscs such as mussels, oysters, squid and snails.",
    ),
    option(
        "gluten",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Wheat / Gluten",
        "Avoid wheat and other gluten-containing cereals and ingredients.",
    ),
    option(
        "soy",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Soy",
        "Avoid soy and soy-derived ingredients.",
    ),
    option(
        "sesame",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Sesame",
        "Avoid sesame seeds and sesame-derived ingredients.",
    ),
    option(
        "mustard",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Mustard",
        "Avoid mustard seeds, powder, paste and mustard-derived ingredients.",
    ),
    option(
        "celery",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Celery",
        "Avoid celery, celeriac and celery-derived ingredients.",
    ),
    option(
        "lupin",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Lupin",
        "Avoid lupin and lupin flour.",
    ),
    option(
        "sulfites",
        PreferenceOptionGroup.ALLERGENS,
        PreferenceKind.ALLERGY,
        "Sulphites",
        "Flag foods that may contain added sulphites.",
    ),
    option(
        "vegetarian",
        PreferenceOptionGroup.DIETARY,
        PreferenceKind.DIETARY,
        "Vegetarian",
        "Avoid meat, poultry, fish and seafood.",
    ),
    option(
        "vegan",
        PreferenceOptionGroup.DIETARY,
        PreferenceKind.DIETARY,
        "Vegan",
        "Avoid animal-derived foods and ingredients.",
    ),
    option(
        "pescatarian",
        PreferenceOptionGroup.DIETARY,
        PreferenceKind.DIETARY,
        "Pescatarian",
        "Avoid meat and poultry while allowing fish and seafood.",
    ),
    option(
        "gluten_free",
        PreferenceOptionGroup.DIETARY,
        PreferenceKind.DIETARY,
        "Gluten-free",
        "Prefer dishes without gluten-containing ingredients.",
    ),
    option(
        "dairy_free",
        PreferenceOptionGroup.DIETARY,
        PreferenceKind.DIETARY,
        "Dairy-free",
        "Avoid milk and dairy-derived ingredients.",
    ),
    option(
        "lactose_free",
        PreferenceOptionGroup.DIETARY,
        PreferenceKind.DIETARY,
        "Lactose-free",
        "Avoid milk and ingredients likely to contain lactose.",
    ),
    option(
        "egg_free",
        PreferenceOptionGroup.DIETARY,
        PreferenceKind.DIETARY,
        "Egg-free",
        "Avoid egg and egg-derived ingredients.",
    ),
    option(
        "no_pork",
        PreferenceOptionGroup.RELIGIOUS,
        PreferenceKind.RELIGIOUS,
        "No pork",
        "Avoid pork and pork-derived ingredients.",
    ),
    option(
        "halal_required",
        PreferenceOptionGroup.RELIGIOUS,
        PreferenceKind.RELIGIOUS,
        "Halal required",
        "Flag pork, alcohol and unverified preparation.",
    ),
    option(
        "kosher_required",
        PreferenceOptionGroup.RELIGIOUS,
        PreferenceKind.RELIGIOUS,
        "Kosher required",
        "Require staff confirmation when certification or preparation is unknown.",
    ),
    option(
        "no_beef",
        PreferenceOptionGroup.RELIGIOUS,
        PreferenceKind.RELIGIOUS,
        "No beef",
        "Avoid beef and beef-derived ingredients.",
    ),
    option(
        "no_alcohol",
        PreferenceOptionGroup.RELIGIOUS,
        PreferenceKind.RELIGIOUS,
        "No alcohol",
        "Avoid alcoholic ingredients.",
    ),
    option(
        "alcohol",
        PreferenceOptionGroup.AVOID,
        PreferenceKind.AVOID,
        "Avoid alcohol",
        "Avoid dishes containing alcoholic ingredients.",
        PreferenceStrength.SOFT,
    ),
    option(
        "spicy",
        PreferenceOptionGroup.AVOID,
        PreferenceKind.AVOID,
        "Avoid spicy food",
        "Avoid dishes explicitly described as spicy or containing chilli.",
        PreferenceStrength.SOFT,
    ),
    option(
        "mushroom",
        PreferenceOptionGroup.AVOID,
        PreferenceKind.AVOID,
        "Avoid mushrooms",
        "Avoid dishes containing mushrooms.",
        PreferenceStrength.SOFT,
    ),
]


def list_preference_options() -> list[PreferenceOption]:
    return PREFERENCE_OPTIONS.copy()


def get_preference_option(code: str) -> PreferenceOption | None:
    return next((option for option in PREFERENCE_OPTIONS if option.code == code), None)
