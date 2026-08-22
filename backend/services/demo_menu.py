from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.language import primary_language
from schemas.dish import EvidenceLevel, EvidenceSource, IngredientEvidence, ParsedDish
from schemas.recommendation import (
    AnalyzedDish,
    DishEnrichment,
    DishEvidence,
    RecommendationAnalyzeResponse,
)
from schemas.resolution import DishResolutionStatus
from services.database.models import DemoMenuTemplate
from services.recommendation.allergen_mapper import assess_allergens
from services.recommendation.engine import decide_dish
from services.recommendation.ingredient_localizer import (
    build_evidence_display,
    localize_cuisine,
    localize_ingredients,
)
from services.recommendation.pipeline import load_effective_preferences

DEMO_TEMPLATE_ID = "foodhub-showcase-v1"

DEFAULT_DEMO_PAYLOAD = {
    "source_language": "fr",
    "dishes": [
        {
            "original_name": "Soupe à l'oignon",
            "canonical_name_en": "French Onion Soup",
            "names": {
                "en": "French Onion Soup",
                "zh": "法式洋葱汤",
                "fr": "Soupe à l'oignon",
            },
            "menu_description": "Bouillon d'oignons, gruyère affiné et croûtons.",
            "descriptions": {
                "en": "Onion broth with aged Gruyère and croutons.",
                "zh": "洋葱高汤配陈年格鲁耶尔奶酪和面包丁。",
                "fr": "Bouillon d'oignons, gruyère affiné et croûtons.",
            },
            "summary": {
                "en": "A classic French onion soup with a rich cheese topping.",
                "zh": "经典法式洋葱汤，搭配浓郁奶酪表层。",
                "fr": "Une soupe à l'oignon classique gratinée au fromage.",
            },
            "price_text": "€18,50",
            "price": "18.50",
            "currency": "EUR",
            "explicit_ingredients": ["onion broth", "aged Gruyère", "croutons"],
            "reference_ingredients": [],
            "inferred_ingredients": [],
            "cuisine": "French",
            "confidence": 0.98,
        },
        {
            "original_name": "Ratatouille provençale",
            "canonical_name_en": "Ratatouille",
            "names": {
                "en": "Provençal Ratatouille",
                "zh": "普罗旺斯炖蔬菜",
                "fr": "Ratatouille provençale",
            },
            "menu_description": "Aubergine, courgette, tomate, poivron et basilic.",
            "descriptions": {
                "en": "Aubergine, courgette, tomato, capsicum and basil.",
                "zh": "茄子、西葫芦、番茄、甜椒和罗勒。",
                "fr": "Aubergine, courgette, tomate, poivron et basilic.",
            },
            "summary": {
                "en": "A light vegetable dish with soft texture and fresh herbs.",
                "zh": "口感柔软、带有新鲜香草风味的清爽蔬菜菜肴。",
                "fr": "Un plat de légumes léger, fondant et parfumé aux herbes.",
            },
            "price_text": "€16",
            "price": "16",
            "currency": "EUR",
            "explicit_ingredients": [
                "aubergine",
                "courgette",
                "tomato",
                "capsicum",
                "basil",
            ],
            "reference_ingredients": [],
            "inferred_ingredients": [],
            "cuisine": "French",
            "confidence": 0.99,
        },
        {
            "original_name": "Moules marinières",
            "canonical_name_en": "Mussels Mariniere",
            "names": {
                "en": "Mussels Marinière",
                "zh": "法式白酒青口",
                "fr": "Moules marinières",
            },
            "menu_description": "Moules, vin blanc, ail et persil.",
            "descriptions": {
                "en": "Mussels with white wine, garlic and parsley.",
                "zh": "青口配白葡萄酒、大蒜和欧芹。",
                "fr": "Moules, vin blanc, ail et persil.",
            },
            "summary": {
                "en": "Steamed mussels in an aromatic white-wine broth.",
                "zh": "以香气浓郁的白葡萄酒汤汁蒸制青口。",
                "fr": "Des moules vapeur dans un bouillon parfumé au vin blanc.",
            },
            "price_text": "€14/24",
            "price": None,
            "currency": "EUR",
            "explicit_ingredients": ["mussels", "white wine", "garlic", "parsley"],
            "reference_ingredients": [],
            "inferred_ingredients": [],
            "cuisine": "French",
            "confidence": 0.98,
        },
        {
            "original_name": "Steak frites, sauce au poivre",
            "canonical_name_en": "Peppercorn Steak Frites",
            "names": {
                "en": "Peppercorn Steak Frites",
                "zh": "胡椒汁牛排配薯条",
                "fr": "Steak frites, sauce au poivre",
            },
            "menu_description": "Filet de bœuf, frites et sauce au poivre.",
            "descriptions": {
                "en": "Beef fillet, fries and peppercorn sauce.",
                "zh": "牛菲力、薯条和胡椒汁。",
                "fr": "Filet de bœuf, frites et sauce au poivre.",
            },
            "summary": {
                "en": "A savoury beef dish with crisp fries and a rich sauce.",
                "zh": "咸香牛排搭配酥脆薯条和浓郁酱汁。",
                "fr": "Un filet de bœuf savoureux avec frites croustillantes.",
            },
            "price_text": "€29",
            "price": "29",
            "currency": "EUR",
            "explicit_ingredients": ["beef fillet", "fries", "peppercorn sauce"],
            "reference_ingredients": ["butter"],
            "inferred_ingredients": [
                {
                    "name": "cream",
                    "confidence": 0.65,
                    "reasoning": "Often used in a traditional peppercorn sauce.",
                }
            ],
            "cuisine": "French",
            "confidence": 0.88,
        },
    ],
}


async def get_demo_template(session: AsyncSession) -> DemoMenuTemplate:
    template = await session.scalar(
        select(DemoMenuTemplate).where(
            DemoMenuTemplate.id == DEMO_TEMPLATE_ID,
            DemoMenuTemplate.enabled.is_(True),
        )
    )
    if template is None:
        template = DemoMenuTemplate(
            id=DEMO_TEMPLATE_ID,
            name="FoodHub French showcase",
            payload=DEFAULT_DEMO_PAYLOAD,
            enabled=True,
        )
        session.add(template)
        await session.flush()
    return template


def localized(values: dict[str, str], language: str) -> str:
    code = primary_language(language)
    return values.get(code, values["en"])


async def build_demo_analysis(
    user_id: str,
    target_language: str,
    session: AsyncSession,
) -> RecommendationAnalyzeResponse:
    template = await get_demo_template(session)
    payload = template.payload
    preferences = await load_effective_preferences(user_id, [], session)
    analyzed: list[AnalyzedDish] = []

    for item in payload["dishes"]:
        inferred = [
            IngredientEvidence(
                name=value["name"],
                source=EvidenceSource.LOCAL_FALLBACK,
                evidence_level=EvidenceLevel.CACHED_INFERENCE,
                confidence=value["confidence"],
                reasoning=value["reasoning"],
            )
            for value in item["inferred_ingredients"]
        ]
        evidence = DishEvidence(
            explicit_ingredients=item["explicit_ingredients"],
            reference_ingredients=item["reference_ingredients"],
            inferred_ingredients=inferred,
        )
        evidence.allergen_assessments = assess_allergens(
            evidence.explicit_ingredients,
            evidence.reference_ingredients,
            evidence.inferred_ingredients,
        )
        evidence.display = build_evidence_display(
            evidence.explicit_ingredients,
            evidence.reference_ingredients,
            evidence.inferred_ingredients,
            target_language,
        )
        dish = ParsedDish(
            original_name=item["original_name"],
            translated_name=localized(item["names"], target_language),
            canonical_name_en=item["canonical_name_en"],
            menu_description=item["menu_description"],
            translated_description=localized(
                item["descriptions"],
                target_language,
            ),
            explicit_ingredients=item["explicit_ingredients"],
            canonical_ingredients_en=item["explicit_ingredients"],
            translated_explicit_ingredients=localize_ingredients(
                item["explicit_ingredients"],
                target_language,
            ),
            price=(Decimal(item["price"]) if item["price"] is not None else None),
            price_text=item["price_text"],
            currency=item["currency"],
            source_text=(
                f"{item['original_name']} {item['menu_description']} "
                f"{item['price_text']}"
            ),
            extraction_confidence=item["confidence"],
        )
        analyzed.append(
            AnalyzedDish(
                dish=dish,
                resolution_status=DishResolutionStatus.LOCAL_FALLBACK,
                match_score=1.0,
                enrichment=DishEnrichment(
                    summary=localized(item["summary"], target_language),
                    display_summary=localized(item["summary"], target_language),
                    cuisine=item["cuisine"],
                    display_cuisine=localize_cuisine(
                        item["cuisine"],
                        target_language,
                    ),
                    source="demo_database",
                    confidence=item["confidence"],
                ),
                evidence=evidence,
                decision=decide_dish(
                    evidence,
                    preferences,
                    DishResolutionStatus.LOCAL_FALLBACK,
                    target_language,
                ),
            )
        )

    return RecommendationAnalyzeResponse(
        menu_id=uuid4(),
        source_language=payload["source_language"],
        target_language=target_language,
        mode="demo",
        analysis_complete=True,
        effective_preferences=preferences,
        dishes=analyzed,
    )
