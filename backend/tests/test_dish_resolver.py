import pytest

from schemas.dish import (
    EvidenceSource,
    ExternalDishCandidate,
    FallbackDishRecord,
    ParsedDish,
)
from schemas.menu import MenuParseResult
from schemas.resolution import DishResolutionStatus
from services.database.repository import InMemoryFallbackDishRepository
from services.database.themealdb_client import TheMealDBUnavailableError
from services.recommendation.dish_resolver import MenuDishResolver

pytestmark = pytest.mark.asyncio


class FakeTheMealDBClient:
    def __init__(
        self,
        candidates: list[ExternalDishCandidate] | None = None,
        unavailable: bool = False,
    ) -> None:
        self.candidates = candidates or []
        self.unavailable = unavailable
        self.queries: list[str] = []

    async def search_by_name(
        self, canonical_name_en: str
    ) -> list[ExternalDishCandidate]:
        self.queries.append(canonical_name_en)
        if self.unavailable:
            raise TheMealDBUnavailableError("TheMealDB request timed out")
        return self.candidates


def build_menu(name: str) -> MenuParseResult:
    return MenuParseResult(
        source_language="en",
        dishes=[
            ParsedDish(
                original_name=name,
                canonical_name_en=name,
                extraction_confidence=0.9,
            )
        ],
    )


async def test_resolver_uses_local_fallback_before_external_api() -> None:
    repository = InMemoryFallbackDishRepository()
    await repository.save(
        FallbackDishRecord(
            canonical_name_en="House Special",
            normalized_name="house special",
            description="Cached description",
            confidence=0.8,
            generated_by=EvidenceSource.LLM,
        )
    )
    external = FakeTheMealDBClient()
    resolver = MenuDishResolver(repository, external, match_threshold=0.85)

    result = await resolver.resolve_menu(build_menu("House Special"))

    assert result.dishes[0].status == DishResolutionStatus.LOCAL_FALLBACK
    assert external.queries == []


@pytest.mark.asyncio
async def test_resolver_matches_cached_original_name_alias() -> None:
    repository = InMemoryFallbackDishRepository()
    await repository.save(
        FallbackDishRecord(
            canonical_name_en="Beetroot Salad",
            normalized_name="beetroot salad",
            aliases=["Salade de betteraves"],
            description="Cached beetroot salad",
            confidence=0.8,
            generated_by=EvidenceSource.LLM,
        )
    )
    themealdb = FakeTheMealDBClient([])
    resolver = MenuDishResolver(repository, themealdb, match_threshold=0.8)
    menu = MenuParseResult(
        source_language="fr",
        dishes=[
            ParsedDish(
                original_name="Salade de betteraves",
                canonical_name_en="French Beet Salad",
                extraction_confidence=0.9,
            )
        ],
    )

    result = await resolver.resolve_menu(menu)

    assert result.dishes[0].status == DishResolutionStatus.LOCAL_FALLBACK
    assert themealdb.queries == []


async def test_resolver_selects_themealdb_match() -> None:
    external = FakeTheMealDBClient(
        [ExternalDishCandidate(external_id="1", name="French Onion Soup")]
    )
    resolver = MenuDishResolver(
        InMemoryFallbackDishRepository(), external, match_threshold=0.85
    )

    result = await resolver.resolve_menu(build_menu("French Onion Soup"))

    assert result.dishes[0].status == DishResolutionStatus.THEMEALDB_MATCH
    assert result.dishes[0].match_score == 1.0


async def test_resolver_creates_llm_request_only_for_real_miss() -> None:
    resolver = MenuDishResolver(
        InMemoryFallbackDishRepository(),
        FakeTheMealDBClient(),
        match_threshold=0.85,
    )

    result = await resolver.resolve_menu(build_menu("Unknown House Dish"))

    resolution = result.dishes[0]
    assert resolution.status == DishResolutionStatus.NEEDS_LLM
    assert result.fallback_batch_request is not None
    assert len(result.fallback_batch_request.dishes) == 1
    assert (
        result.fallback_batch_request.dishes[0].canonical_name_en
        == "Unknown House Dish"
    )
    assert (
        resolution.fallback_request_id
        == result.fallback_batch_request.dishes[0].request_id
    )


async def test_resolver_does_not_use_llm_during_themealdb_outage() -> None:
    resolver = MenuDishResolver(
        InMemoryFallbackDishRepository(),
        FakeTheMealDBClient(unavailable=True),
        match_threshold=0.85,
    )

    result = await resolver.resolve_menu(build_menu("French Onion Soup"))

    resolution = result.dishes[0]
    assert resolution.status == DishResolutionStatus.LOOKUP_UNAVAILABLE
    assert resolution.fallback_request_id is None
    assert result.fallback_batch_request is None


async def test_resolver_batches_multiple_misses_into_one_request() -> None:
    menu = MenuParseResult(
        source_language="en",
        dishes=[
            ParsedDish(
                original_name="Unknown One",
                canonical_name_en="Unknown One",
                extraction_confidence=0.9,
            ),
            ParsedDish(
                original_name="Unknown Two",
                canonical_name_en="Unknown Two",
                extraction_confidence=0.9,
            ),
        ],
    )
    resolver = MenuDishResolver(
        InMemoryFallbackDishRepository(),
        FakeTheMealDBClient(),
        match_threshold=0.85,
    )

    result = await resolver.resolve_menu(menu)

    assert result.fallback_batch_request is not None
    assert len(result.fallback_batch_request.dishes) == 2
    assert {
        dish.canonical_name_en for dish in result.fallback_batch_request.dishes
    } == {"Unknown One", "Unknown Two"}
