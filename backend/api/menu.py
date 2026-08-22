from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select

from api.dependencies import (
    CurrentUserDep,
    MenuParserDep,
    SessionDep,
    TheMealDBDep,
    UnknownDishResolverDep,
)
from core.config import get_settings
from schemas.menu import MenuPayload, MenuValidationResponse, normalize_menu_payload
from schemas.recommendation import RecommendationAnalyzeResponse
from schemas.resolution import MenuResolutionResponse
from schemas.unknown_dish import (
    FallbackDishBatchResponse,
    FallbackDishBatchValidationResponse,
)
from services.ai.menu_parser import SUPPORTED_IMAGE_TYPES, MenuUnderstandingError
from services.database.models import MenuScan, UserProfile
from services.database.repository import SqlAlchemyFallbackDishRepository
from services.recommendation.dish_resolver import MenuDishResolver
from services.recommendation.pipeline import analyze_menu

router = APIRouter(prefix="/menu", tags=["menu"])


async def read_menu_images(
    images: list[UploadFile],
) -> list[tuple[bytes, str]]:
    settings = get_settings()
    if not images:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one menu image is required",
        )
    if len(images) > settings.menu_image_max_count:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"At most {settings.menu_image_max_count} menu images are allowed",
        )

    loaded: list[tuple[bytes, str]] = []
    total_bytes = 0
    try:
        for image in images:
            content_type = image.content_type or ""
            if content_type not in SUPPORTED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Menu images must be JPEG, PNG, or WebP",
                )
            image_bytes = await image.read(settings.menu_image_max_bytes + 1)
            if not image_bytes:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Menu image is empty: {image.filename or 'unnamed image'}",
                )
            if len(image_bytes) > settings.menu_image_max_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=("A menu image exceeds the configured per-image size limit"),
                )
            total_bytes += len(image_bytes)
            if total_bytes > settings.menu_images_total_max_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Combined menu images exceed the configured size limit",
                )
            loaded.append((image_bytes, content_type))
    finally:
        for image in images:
            await image.close()
    return loaded


@router.post(
    "/scan",
    response_model=RecommendationAnalyzeResponse,
    summary="Upload multiple menu pages and persist the analyzed menu",
)
async def scan_menu(
    menu_images: Annotated[
        list[UploadFile],
        File(description="One to five JPEG, PNG, or WebP menu pages"),
    ],
    user: CurrentUserDep,
    session: SessionDep,
    themealdb: TheMealDBDep,
    menu_parser: MenuParserDep,
    fallback_resolver: UnknownDishResolverDep,
) -> RecommendationAnalyzeResponse:
    loaded_images = await read_menu_images(menu_images)
    profile = await session.scalar(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    target_language = profile.preferred_language if profile is not None else "en"

    try:
        menu = await menu_parser.parse_many(loaded_images, target_language)
        settings = get_settings()
        result = await analyze_menu(
            menu=menu,
            user_id=user.id,
            daily_overrides=[],
            session=session,
            themealdb=themealdb,
            fallback_resolver=fallback_resolver,
            match_threshold=settings.dish_match_threshold,
            max_concurrency=settings.themealdb_max_concurrency,
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

    session.add(
        MenuScan(
            id=str(result.menu_id),
            user_id=str(user.id),
            source_language=result.source_language,
            target_language=result.target_language,
            analysis=result.model_dump(mode="json"),
        )
    )
    await session.commit()
    return result


@router.post(
    "/validate",
    response_model=MenuValidationResponse,
    summary="Validate Backend B's parsed menu payload",
)
async def validate_menu(
    menu: MenuPayload,
) -> MenuValidationResponse:
    """Accept the normalized contract or adapt Backend B's OCR payload."""
    normalized_menu = normalize_menu_payload(menu)
    return MenuValidationResponse(accepted=True, menu=normalized_menu)


@router.post(
    "/resolve",
    response_model=MenuResolutionResponse,
    summary="Resolve dishes from local LLM cache or TheMealDB",
)
async def resolve_menu(
    menu: MenuPayload,
    _: CurrentUserDep,
    session: SessionDep,
    themealdb: TheMealDBDep,
) -> MenuResolutionResponse:
    settings = get_settings()
    resolver = MenuDishResolver(
        repository=SqlAlchemyFallbackDishRepository(session),
        themealdb=themealdb,
        match_threshold=settings.dish_match_threshold,
        max_concurrency=settings.themealdb_max_concurrency,
    )
    return await resolver.resolve_menu(normalize_menu_payload(menu))


@router.post(
    "/fallback-dishes/validate",
    response_model=FallbackDishBatchValidationResponse,
    summary="Validate Backend B's batched fallback-dish LLM response",
)
async def validate_fallback_dishes(
    batch: FallbackDishBatchResponse,
) -> FallbackDishBatchValidationResponse:
    return FallbackDishBatchValidationResponse(batch=batch)
