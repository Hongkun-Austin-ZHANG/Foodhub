from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.dish import normalize_lookup_name
from schemas.menu import MenuParseResult
from schemas.preference import (
    DailyPreferenceOverride,
    PreferenceContext,
    UserPreference,
)
from schemas.recommendation import (
    AnalyzedDish,
    DishEvidence,
    RecommendationAnalyzeResponse,
)
from schemas.resolution import DishResolution, DishResolutionStatus
from schemas.unknown_dish import FallbackDishBatchRequest
from services.ai.unknown_dish import UnknownDishResolver
from services.database.models import UserPreference as UserPreferenceModel
from services.database.repository import SqlAlchemyFallbackDishRepository
from services.database.themealdb_client import TheMealDBClient
from services.recommendation.allergen_mapper import assess_allergens
from services.recommendation.dish_resolver import MenuDishResolver
from services.recommendation.engine import decide_dish
from services.recommendation.reconciler import resolve_preferences


async def load_effective_preferences(
    user_id: str,
    daily_overrides: list[DailyPreferenceOverride],
    session: AsyncSession,
) -> list[UserPreference]:
    stored_preferences = await session.scalars(
        select(UserPreferenceModel).where(UserPreferenceModel.user_id == user_id)
    )
    persistent = [
        UserPreference(
            code=preference.code,
            kind=preference.kind,
            strength=preference.strength,
            enabled=preference.enabled,
        )
        for preference in stored_preferences
    ]
    return resolve_preferences(
        PreferenceContext(
            persistent=persistent,
            daily_overrides=daily_overrides,
        )
    ).preferences


def build_evidence(
    explicit_ingredients: list[str],
    resolution: DishResolution,
) -> DishEvidence:
    evidence = DishEvidence(explicit_ingredients=explicit_ingredients)
    if resolution.themealdb_candidate is not None:
        evidence.reference_ingredients = resolution.themealdb_candidate.ingredients
    if resolution.local_fallback is not None:
        evidence.inferred_ingredients = resolution.local_fallback.ingredients
    evidence.allergen_assessments = assess_allergens(
        evidence.explicit_ingredients,
        evidence.reference_ingredients,
        evidence.inferred_ingredients,
    )
    return evidence


async def resolve_fallback_batch(
    resolutions: list[DishResolution],
    fallback_resolver: UnknownDishResolver,
    fallback_batch: FallbackDishBatchRequest,
    repository: SqlAlchemyFallbackDishRepository,
    session: AsyncSession,
) -> list[DishResolution]:
    response = await fallback_resolver.resolve_batch(fallback_batch)
    if response.batch_id != fallback_batch.batch_id:
        raise ValueError("Backend B returned a different batch_id")

    request_by_id = {dish.request_id: dish for dish in fallback_batch.dishes}
    result_by_id = {result.request_id: result for result in response.results}
    if set(request_by_id) != set(result_by_id):
        raise ValueError("Backend B returned incomplete fallback results")

    cached_by_request = {}
    for request_id, result in result_by_id.items():
        request = request_by_id[request_id]
        record = result.to_fallback_record()
        record = record.model_copy(
            update={
                "normalized_name": normalize_lookup_name(request.canonical_name_en),
                "aliases": list(
                    dict.fromkeys(
                        [
                            *record.aliases,
                            result.canonical_name_en,
                            request.canonical_name_en,
                            request.original_name,
                        ]
                    )
                ),
                "allergen_assessments": assess_allergens(
                    [],
                    [],
                    record.ingredients,
                ),
            }
        )
        cached_by_request[request_id] = await repository.save(record)
    await session.commit()

    return [
        resolution.model_copy(
            update={
                "status": DishResolutionStatus.LLM_FALLBACK,
                "local_fallback": cached_by_request[resolution.fallback_request_id],
            }
        )
        if resolution.fallback_request_id in cached_by_request
        else resolution
        for resolution in resolutions
    ]


async def analyze_menu(
    menu: MenuParseResult,
    user_id: str,
    daily_overrides: list[DailyPreferenceOverride],
    session: AsyncSession,
    themealdb: TheMealDBClient,
    fallback_resolver: UnknownDishResolver | None,
    match_threshold: float,
    max_concurrency: int,
) -> RecommendationAnalyzeResponse:
    preferences = await load_effective_preferences(
        user_id,
        daily_overrides,
        session,
    )
    repository = SqlAlchemyFallbackDishRepository(session)
    resolver = MenuDishResolver(
        repository=repository,
        themealdb=themealdb,
        match_threshold=match_threshold,
        max_concurrency=max_concurrency,
    )
    resolution_result = await resolver.resolve_menu(menu)
    resolutions = resolution_result.dishes
    remaining_batch = resolution_result.fallback_batch_request
    if remaining_batch is not None and fallback_resolver is not None:
        resolutions = await resolve_fallback_batch(
            resolutions,
            fallback_resolver,
            remaining_batch,
            repository,
            session,
        )
        remaining_batch = None

    resolution_by_dish = {resolution.dish_id: resolution for resolution in resolutions}
    analyzed_dishes: list[AnalyzedDish] = []
    for dish in menu.dishes:
        resolution = resolution_by_dish[dish.dish_id]
        evidence = build_evidence(dish.explicit_ingredients, resolution)
        candidate = resolution.themealdb_candidate
        fallback = resolution.local_fallback
        analyzed_dishes.append(
            AnalyzedDish(
                dish=dish,
                resolution_status=resolution.status,
                match_score=resolution.match_score,
                image_url=(
                    candidate.image_url
                    if candidate is not None
                    else fallback.image_url
                    if fallback is not None
                    else None
                ),
                image_is_reference=candidate is not None,
                evidence=evidence,
                decision=decide_dish(
                    evidence,
                    preferences,
                    resolution.status,
                    menu.target_language,
                ),
            )
        )

    return RecommendationAnalyzeResponse(
        menu_id=menu.menu_id,
        source_language=menu.source_language,
        target_language=menu.target_language,
        analysis_complete=remaining_batch is None
        and all(
            dish.resolution_status != DishResolutionStatus.LOOKUP_UNAVAILABLE
            for dish in analyzed_dishes
        ),
        effective_preferences=preferences,
        dishes=analyzed_dishes,
        fallback_batch_request=remaining_batch,
    )
