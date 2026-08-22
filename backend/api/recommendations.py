from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from api.dependencies import CurrentUserDep, SessionDep
from schemas.frontend import (
    MenuRecommendationsRequest,
    MenuRecommendationsResponse,
)
from schemas.recommendation import RecommendationAnalyzeResponse
from services.database.models import MenuScan
from services.recommendation.pipeline import load_effective_preferences
from services.recommendation.ranking import merge_current_preference, rank_dishes

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=MenuRecommendationsResponse)
async def recommend_saved_menu(
    request: MenuRecommendationsRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> MenuRecommendationsResponse:
    scan = await session.scalar(
        select(MenuScan).where(
            MenuScan.id == str(request.menu_id),
            MenuScan.user_id == str(user.id),
        )
    )
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu scan not found",
        )

    stored = RecommendationAnalyzeResponse.model_validate(scan.analysis)
    preferences = await load_effective_preferences(str(user.id), [], session)
    current = merge_current_preference(preferences, request.current_preference)
    recommendations = rank_dishes(
        stored.dishes,
        preferences,
        current,
        scan.target_language,
    )
    return MenuRecommendationsResponse(
        menu_id=request.menu_id,
        target_language=scan.target_language,
        mode=stored.mode,
        effective_preferences=preferences,
        effective_current_preference=current,
        recommendations=recommendations,
    )
