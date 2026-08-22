from collections.abc import Iterable

from core.language import primary_language
from schemas.dish import IngredientEvidence, normalize_lookup_name
from schemas.recommendation import (
    DishEvidenceDisplay,
    IngredientEvidenceDisplay,
)

INGREDIENT_TRANSLATIONS: dict[str, dict[str, str]] = {
    "onion broth": {"zh": "洋葱高汤", "fr": "bouillon d'oignons"},
    "aged gruyere": {"zh": "陈年格鲁耶尔奶酪", "fr": "gruyère affiné"},
    "croutons": {"zh": "面包丁", "fr": "croûtons"},
    "aubergine": {"zh": "茄子", "fr": "aubergine"},
    "courgette": {"zh": "西葫芦", "fr": "courgette"},
    "tomato": {"zh": "番茄", "fr": "tomate"},
    "capsicum": {"zh": "甜椒", "fr": "poivron"},
    "basil": {"zh": "罗勒", "fr": "basilic"},
    "mussels": {"zh": "青口", "fr": "moules"},
    "white wine": {"zh": "白葡萄酒", "fr": "vin blanc"},
    "garlic": {"zh": "大蒜", "fr": "ail"},
    "parsley": {"zh": "欧芹", "fr": "persil"},
    "beef fillet": {"zh": "牛菲力", "fr": "filet de bœuf"},
    "fries": {"zh": "薯条", "fr": "frites"},
    "peppercorn sauce": {"zh": "胡椒汁", "fr": "sauce au poivre"},
    "butter": {"zh": "黄油", "fr": "beurre"},
    "cream": {"zh": "奶油", "fr": "crème"},
    "milk": {"zh": "牛奶", "fr": "lait"},
    "egg": {"zh": "鸡蛋", "fr": "œuf"},
    "eggs": {"zh": "鸡蛋", "fr": "œufs"},
    "peanuts": {"zh": "花生", "fr": "cacahuètes"},
    "soy": {"zh": "大豆", "fr": "soja"},
    "sesame": {"zh": "芝麻", "fr": "sésame"},
    "wheat": {"zh": "小麦", "fr": "blé"},
    "fish": {"zh": "鱼", "fr": "poisson"},
    "chicken": {"zh": "鸡肉", "fr": "poulet"},
    "pork": {"zh": "猪肉", "fr": "porc"},
    "beef": {"zh": "牛肉", "fr": "bœuf"},
    "prawn": {"zh": "大虾", "fr": "grosse crevette"},
    "prawns": {"zh": "大虾", "fr": "grosses crevettes"},
    "olive oil": {"zh": "橄榄油", "fr": "huile d'olive"},
    "red chili": {"zh": "红辣椒", "fr": "piment rouge"},
    "red chilli": {"zh": "红辣椒", "fr": "piment rouge"},
    "nduja butter": {"zh": "恩杜亚黄油", "fr": "beurre à la nduja"},
}

CUISINE_TRANSLATIONS: dict[str, dict[str, str]] = {
    "french": {"zh": "法国菜", "fr": "française"},
    "italian": {"zh": "意大利菜", "fr": "italienne"},
    "chinese": {"zh": "中国菜", "fr": "chinoise"},
    "japanese": {"zh": "日本菜", "fr": "japonaise"},
    "indian": {"zh": "印度菜", "fr": "indienne"},
    "mexican": {"zh": "墨西哥菜", "fr": "mexicaine"},
}

REASONING_TRANSLATIONS: dict[str, dict[str, str]] = {
    "often used in a traditional peppercorn sauce": {
        "zh": "传统胡椒汁中经常使用。",
        "fr": "Souvent utilisée dans une sauce au poivre traditionnelle.",
    },
    "olive oil or butter is often used to baste grilled prawns": {
        "zh": "烤大虾通常会用橄榄油或黄油涂抹烹制。",
        "fr": "L'huile d'olive ou le beurre sert souvent à arroser les grosses crevettes grillées.",
    },
    "garlic is commonly used in flavored butters like nduja butter": {
        "zh": "大蒜常用于恩杜亚黄油等调味黄油。",
        "fr": "L'ail est couramment utilisé dans les beurres aromatisés comme le beurre à la nduja.",
    },
    "nduja butter typically includes spicy chili content": {
        "zh": "恩杜亚黄油通常带有辛辣的辣椒成分。",
        "fr": "Le beurre à la nduja contient généralement du piment relevé.",
    },
}

SUMMARY_TRANSLATIONS: dict[str, dict[str, str]] = {
    "prawns char grilled and usually served with a spicy flavored butter such as nduja butter": {
        "zh": "炭烤大虾，通常搭配恩杜亚黄油等辛辣调味黄油。",
        "fr": "Grosses crevettes grillées, généralement servies avec un beurre relevé comme le beurre à la nduja.",
    },
}

GENERIC_SUMMARIES = {
    "zh": "该菜品的补充信息来自本地菜品知识库。",
    "fr": "Les informations complémentaires de ce plat proviennent de la base locale.",
}

GENERIC_REASONING = {
    "zh": "根据常见烹饪方式推断该成分可能出现。",
    "fr": "Cet ingrédient est possible selon une préparation culinaire courante.",
}


def _translated(value: str, language: str, catalog: dict[str, dict[str, str]]) -> str:
    code = primary_language(language)
    if code == "en":
        return value
    translations = catalog.get(normalize_lookup_name(value))
    return translations.get(code, value) if translations else value


def localize_ingredient(value: str, language: str) -> str:
    return _translated(value, language, INGREDIENT_TRANSLATIONS)


def localize_cuisine(value: str | None, language: str) -> str | None:
    return _translated(value, language, CUISINE_TRANSLATIONS) if value else None


def localize_reasoning(value: str | None, language: str) -> str | None:
    if not value:
        return None
    code = primary_language(language)
    translated = _translated(value, language, REASONING_TRANSLATIONS)
    if translated != value or code == "en":
        return translated
    return GENERIC_REASONING.get(code, value)


def localize_summary(value: str | None, language: str) -> str | None:
    if not value:
        return None
    code = primary_language(language)
    translated = _translated(value, language, SUMMARY_TRANSLATIONS)
    if translated != value or code == "en":
        return translated
    return GENERIC_SUMMARIES.get(code, value)


def localize_ingredients(values: Iterable[str], language: str) -> list[str]:
    return [localize_ingredient(value, language) for value in values]


def build_evidence_display(
    explicit: list[str],
    reference: list[str],
    inferred: list[IngredientEvidence],
    language: str,
    translated_explicit: list[str] | None = None,
) -> DishEvidenceDisplay:
    explicit_display = (
        translated_explicit
        if translated_explicit and len(translated_explicit) == len(explicit)
        else localize_ingredients(explicit, language)
    )
    return DishEvidenceDisplay(
        explicit_ingredients=explicit_display,
        reference_ingredients=localize_ingredients(reference, language),
        inferred_ingredients=[
            IngredientEvidenceDisplay(
                name=localize_ingredient(value.name, language),
                reasoning=localize_reasoning(value.reasoning, language),
            )
            for value in inferred
        ],
    )
