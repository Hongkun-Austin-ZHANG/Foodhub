from core.language import primary_language

MESSAGES = {
    "en": {
        "allergen_evidence": "{code} allergen evidence is {status}: {reasoning}",
        "explicit_conflict": (
            "{code} conflicts with explicit menu evidence: {ingredients}"
        ),
        "reference_conflict": (
            "A reference recipe suggests possible {code} conflict: {ingredients}"
        ),
        "inferred_conflict": (
            "AI inference suggests possible {code} conflict: {ingredients}"
        ),
        "requires_confirmation": (
            "{code} cannot be confirmed from ingredient evidence alone"
        ),
        "needs_llm": "Dish is waiting for batched fallback analysis",
        "lookup_unavailable": "Reference lookup is temporarily unavailable",
        "confirm_allergy": "Confirm severe allergy information with restaurant staff.",
        "incomplete_evidence": "The available evidence may be incomplete.",
        "no_conflict": "No conflict was identified in the available evidence.",
        "not_guarantee": "This is not a food-safety guarantee.",
        "matches_protein": "Matches your {value} protein preference.",
        "matches_flavour": "Matches your {value} flavour preference.",
        "matches_texture": "Matches your {value} texture preference.",
        "matches_spice": "Matches your {value} spice-level preference.",
    },
    "zh": {
        "allergen_evidence": "检测到 {code} 过敏原风险（{status}，{source}）。",
        "explicit_conflict": "菜单明确成分与 {code} 要求冲突：{ingredients}",
        "reference_conflict": "参考食谱提示可能与 {code} 要求冲突：{ingredients}",
        "inferred_conflict": "AI 推断提示可能与 {code} 要求冲突：{ingredients}",
        "requires_confirmation": "仅根据成分信息无法确认是否符合 {code} 要求",
        "needs_llm": "菜品正在等待批量补充分析",
        "lookup_unavailable": "参考菜谱查询暂时不可用",
        "confirm_allergy": "严重过敏情况下，请务必向餐厅工作人员确认。",
        "incomplete_evidence": "当前证据信息可能不完整。",
        "no_conflict": "现有证据中未发现与用户要求冲突的内容。",
        "not_guarantee": "该结果不能替代餐厅提供的食品安全保证。",
        "matches_protein": "符合你本餐对 {value} 蛋白质的偏好。",
        "matches_flavour": "符合你本餐对 {value} 风味的偏好。",
        "matches_texture": "符合你本餐对 {value} 口感的偏好。",
        "matches_spice": "符合你本餐对 {value} 辣度的偏好。",
    },
    "fr": {
        "allergen_evidence": "Risque allergène {code} détecté ({status}, {source}).",
        "explicit_conflict": (
            "Les ingrédients du menu sont incompatibles avec {code} : {ingredients}"
        ),
        "reference_conflict": (
            "Une recette de référence suggère un risque {code} : {ingredients}"
        ),
        "inferred_conflict": (
            "L'inférence IA suggère un risque {code} : {ingredients}"
        ),
        "requires_confirmation": (
            "La conformité à {code} ne peut pas être confirmée par les seuls ingrédients"
        ),
        "needs_llm": "Le plat attend une analyse complémentaire groupée",
        "lookup_unavailable": "La recherche de recette est temporairement indisponible",
        "confirm_allergy": "En cas d'allergie sévère, confirmez auprès du personnel.",
        "incomplete_evidence": "Les informations disponibles peuvent être incomplètes.",
        "no_conflict": "Aucun conflit n'a été identifié dans les informations disponibles.",
        "not_guarantee": "Ce résultat ne constitue pas une garantie de sécurité alimentaire.",
        "matches_protein": "Correspond à votre préférence de protéine : {value}.",
        "matches_flavour": "Correspond à votre préférence de saveur : {value}.",
        "matches_texture": "Correspond à votre préférence de texture : {value}.",
        "matches_spice": "Correspond à votre préférence de piquant : {value}.",
    },
}

DISPLAY_LABELS = {
    "zh": {
        "peanut": "花生",
        "tree_nuts": "树坚果",
        "milk": "牛奶/乳制品",
        "egg": "鸡蛋",
        "fish": "鱼类",
        "shellfish": "甲壳类海鲜",
        "molluscs": "软体动物",
        "gluten": "小麦/麸质",
        "soy": "大豆",
        "sesame": "芝麻",
        "mustard": "芥末",
        "celery": "芹菜",
        "lupin": "羽扇豆",
        "sulfites": "亚硫酸盐",
        "contains": "明确含有",
        "may_contain": "可能含有",
        "unknown": "未知",
        "menu_evidence": "菜单证据",
        "reference_recipe": "参考食谱",
        "inferred": "AI 推断",
        "beef": "牛肉",
        "lamb": "羊肉",
        "chicken": "鸡肉",
        "plant_based": "植物蛋白",
        "savoury": "咸香",
        "rich": "浓郁",
        "light": "清爽",
        "creamy": "奶油感",
        "herby": "香草味",
        "smoky": "烟熏味",
        "tangy": "酸香",
        "sweet": "甜味",
        "crispy": "酥脆",
        "tender": "软嫩",
        "crunchy": "爽脆",
        "soft": "柔软",
        "chewy": "有嚼劲",
        "brothy": "汤汁感",
        "mild": "微辣",
        "medium": "中辣",
        "hot": "辣",
    },
    "fr": {
        "peanut": "cacahuètes",
        "tree_nuts": "fruits à coque",
        "milk": "lait / produits laitiers",
        "egg": "œufs",
        "fish": "poisson",
        "shellfish": "crustacés",
        "molluscs": "mollusques",
        "gluten": "blé / gluten",
        "soy": "soja",
        "sesame": "sésame",
        "mustard": "moutarde",
        "celery": "céleri",
        "lupin": "lupin",
        "sulfites": "sulfites",
        "contains": "contient",
        "may_contain": "peut contenir",
        "unknown": "inconnu",
        "menu_evidence": "preuve du menu",
        "reference_recipe": "recette de référence",
        "inferred": "inférence IA",
        "beef": "bœuf",
        "lamb": "agneau",
        "chicken": "poulet",
        "plant_based": "végétal",
        "savoury": "savoureux",
        "rich": "riche",
        "light": "léger",
        "creamy": "crémeux",
        "herby": "aux herbes",
        "smoky": "fumé",
        "tangy": "acidulé",
        "sweet": "sucré",
        "crispy": "croustillant",
        "tender": "tendre",
        "crunchy": "croquant",
        "soft": "fondant",
        "chewy": "moelleux",
        "brothy": "en bouillon",
        "mild": "doux",
        "medium": "moyen",
        "hot": "fort",
    },
}


def display_label(value: str, language: str = "en") -> str:
    return DISPLAY_LABELS.get(primary_language(language), {}).get(value, value)


def message(key: str, language: str = "en", **values: object) -> str:
    catalog = MESSAGES.get(primary_language(language), MESSAGES["en"])
    template = catalog.get(key, MESSAGES["en"][key])
    localized_values = {
        name: (
            display_label(str(value), language)
            if name in {"code", "status", "source", "value"}
            else value
        )
        for name, value in values.items()
    }
    return template.format(**localized_values)
