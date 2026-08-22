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


def message(key: str, language: str = "en", **values: object) -> str:
    catalog = MESSAGES.get(primary_language(language), MESSAGES["en"])
    template = catalog.get(key, MESSAGES["en"][key])
    return template.format(**values)
