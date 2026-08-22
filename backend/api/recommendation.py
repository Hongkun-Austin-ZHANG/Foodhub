from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import select

from api.dependencies import (
    CurrentUserDep,
    MenuParserDep,
    SessionDep,
    TheMealDBDep,
    UnknownDishResolverDep,
)
from core.config import get_settings
from schemas.menu import MenuParseResult, normalize_menu_payload
from schemas.preference import DailyPreferenceOverride
from schemas.recommendation import (
    MenuRecommendationResponse,
    RecommendationAnalyzeRequest,
    RecommendationAnalyzeResponse,
    RecommendationPreviewRequest,
)
from services.ai.menu_parser import SUPPORTED_IMAGE_TYPES, MenuUnderstandingError
from services.database.models import UserProfile
from services.recommendation.engine import recommend_dish
from services.recommendation.pipeline import analyze_menu
from services.recommendation.reconciler import resolve_preferences

router = APIRouter(prefix="/recommendation", tags=["recommendation"])
DAILY_OVERRIDES_ADAPTER = TypeAdapter(list[DailyPreferenceOverride])


@router.post(
    "/preview",
    response_model=MenuRecommendationResponse,
    summary="Preview deterministic matching with explicit menu ingredients",
)
async def preview_recommendation(
    request: RecommendationPreviewRequest,
) -> MenuRecommendationResponse:
    effective_preferences = resolve_preferences(request.preferences)
    recommendations = [
        recommend_dish(dish, effective_preferences.preferences)
        for dish in request.menu.dishes
    ]
    return MenuRecommendationResponse(
        menu_id=request.menu.menu_id,
        effective_preferences=effective_preferences.preferences,
        dishes=recommendations,
    )


async def _run_analysis(
    menu: MenuParseResult,
    daily_overrides: list[DailyPreferenceOverride],
    user_id: str,
    session: SessionDep,
    themealdb: TheMealDBDep,
    fallback_resolver: UnknownDishResolverDep,
) -> RecommendationAnalyzeResponse:
    settings = get_settings()
    try:
        return await analyze_menu(
            menu=menu,
            user_id=user_id,
            daily_overrides=daily_overrides,
            session=session,
            themealdb=themealdb,
            fallback_resolver=fallback_resolver,
            match_threshold=settings.dish_match_threshold,
            max_concurrency=settings.themealdb_max_concurrency,
        )
    except (MenuUnderstandingError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error


@router.post(
    "/analyze",
    response_model=RecommendationAnalyzeResponse,
    summary="Analyze Backend B menu JSON and apply the user's preferences",
)
async def analyze_recommendation(
    request: RecommendationAnalyzeRequest,
    user: CurrentUserDep,
    session: SessionDep,
    themealdb: TheMealDBDep,
    fallback_resolver: UnknownDishResolverDep,
) -> RecommendationAnalyzeResponse:
    return await _run_analysis(
        normalize_menu_payload(request.menu),
        request.daily_overrides,
        user.id,
        session,
        themealdb,
        fallback_resolver,
    )


@router.post(
    "/analyze-image",
    response_model=RecommendationAnalyzeResponse,
    summary="Upload one menu image and run the complete B-to-C pipeline",
)
async def analyze_menu_image(
    image: Annotated[UploadFile, File(description="JPEG, PNG, or WebP menu image")],
    user: CurrentUserDep,
    session: SessionDep,
    themealdb: TheMealDBDep,
    menu_parser: MenuParserDep,
    fallback_resolver: UnknownDishResolverDep,
    daily_overrides: Annotated[str, Form()] = "[]",
) -> RecommendationAnalyzeResponse:
    content_type = image.content_type or ""
    if content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Menu image must be JPEG, PNG, or WebP",
        )

    settings = get_settings()
    image_bytes = await image.read(settings.menu_image_max_bytes + 1)
    await image.close()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Menu image is empty",
        )
    if len(image_bytes) > settings.menu_image_max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Menu image exceeds the configured size limit",
        )

    try:
        overrides = DAILY_OVERRIDES_ADAPTER.validate_json(daily_overrides)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=error.errors(),
        ) from error

    profile = await session.scalar(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    target_language = profile.preferred_language if profile is not None else "en"
    try:
        menu = await menu_parser.parse(
            image_bytes,
            content_type,
            target_language,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except MenuUnderstandingError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return await _run_analysis(
        menu,
        overrides,
        user.id,
        session,
        themealdb,
        fallback_resolver,
    )
