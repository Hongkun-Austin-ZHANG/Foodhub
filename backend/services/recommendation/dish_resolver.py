import asyncio

from schemas.dish import ParsedDish
from schemas.menu import MenuParseResult
from schemas.resolution import (
    DishResolution,
    DishResolutionStatus,
    MenuResolutionResponse,
)
from schemas.unknown_dish import (
    FallbackDishBatchRequest,
    UnknownDishAnalysisRequest,
)
from services.database.dish_matcher import select_best_candidate
from services.database.repository import FallbackDishRepository
from services.database.themealdb_client import (
    TheMealDBClient,
    TheMealDBUnavailableError,
)


class MenuDishResolver:
    def __init__(
        self,
        repository: FallbackDishRepository,
        themealdb: TheMealDBClient,
        match_threshold: float,
        max_concurrency: int = 5,
    ) -> None:
        self._repository = repository
        self._themealdb = themealdb
        self._match_threshold = match_threshold
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def resolve_menu(self, menu: MenuParseResult) -> MenuResolutionResponse:
        resolutions: list[DishResolution | None] = [None] * len(menu.dishes)
        external_lookups: list[tuple[int, ParsedDish]] = []

        for index, dish in enumerate(menu.dishes):
            cached = await self._repository.find_by_name(
                dish.canonical_name_en,
                [dish.original_name, dish.translated_name or ""],
            )
            if cached is not None:
                resolutions[index] = DishResolution(
                    dish_id=dish.dish_id,
                    canonical_name_en=dish.canonical_name_en,
                    status=DishResolutionStatus.LOCAL_FALLBACK,
                    match_score=1.0,
                    local_fallback=cached,
                )
            else:
                external_lookups.append((index, dish))

        lookup_results = await asyncio.gather(
            *(self._resolve_external(index, dish) for index, dish in external_lookups)
        )
        fallback_requests: list[UnknownDishAnalysisRequest] = []
        for index, resolution, fallback_request in lookup_results:
            resolutions[index] = resolution
            if fallback_request is not None:
                fallback_requests.append(fallback_request)

        return MenuResolutionResponse(
            menu_id=menu.menu_id,
            dishes=[resolution for resolution in resolutions if resolution is not None],
            fallback_batch_request=(
                FallbackDishBatchRequest(dishes=fallback_requests)
                if fallback_requests
                else None
            ),
        )

    async def _resolve_external(
        self,
        index: int,
        dish: ParsedDish,
    ) -> tuple[int, DishResolution, UnknownDishAnalysisRequest | None]:
        try:
            async with self._semaphore:
                candidates = await self._themealdb.search_by_name(
                    dish.canonical_name_en
                )
        except TheMealDBUnavailableError as error:
            return (
                index,
                DishResolution(
                    dish_id=dish.dish_id,
                    canonical_name_en=dish.canonical_name_en,
                    status=DishResolutionStatus.LOOKUP_UNAVAILABLE,
                    error=str(error),
                ),
                None,
            )

        match = select_best_candidate(
            dish.canonical_name_en,
            candidates,
            threshold=self._match_threshold,
        )
        if match.candidate is not None:
            return (
                index,
                DishResolution(
                    dish_id=dish.dish_id,
                    canonical_name_en=dish.canonical_name_en,
                    status=DishResolutionStatus.THEMEALDB_MATCH,
                    match_score=match.score,
                    themealdb_candidate=match.candidate,
                ),
                None,
            )

        fallback_request = UnknownDishAnalysisRequest.from_dish(dish)
        return (
            index,
            DishResolution(
                dish_id=dish.dish_id,
                canonical_name_en=dish.canonical_name_en,
                status=DishResolutionStatus.NEEDS_LLM,
                match_score=match.score,
                fallback_request_id=fallback_request.request_id,
            ),
            fallback_request,
        )
