import httpx
import pytest

from services.database.themealdb_client import (
    TheMealDBClient,
    TheMealDBUnavailableError,
)


@pytest.mark.asyncio
async def test_themealdb_client_maps_meal_and_ingredients() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["s"] == "French Onion Soup"
        return httpx.Response(
            200,
            json={
                "meals": [
                    {
                        "idMeal": "52996",
                        "strMeal": "French Onion Soup",
                        "strArea": "French",
                        "strCategory": "Starter",
                        "strMealThumb": "https://example.com/soup.jpg",
                        "strIngredient1": "Onion",
                        "strIngredient2": "Gruyere Cheese",
                        "strIngredient3": " ",
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = TheMealDBClient(http_client, "https://example.com/api/v1", "1")
        candidates = await client.search_by_name("French Onion Soup")

    assert len(candidates) == 1
    assert candidates[0].external_id == "52996"
    assert candidates[0].ingredients == ["Onion", "Gruyere Cheese"]


@pytest.mark.asyncio
async def test_themealdb_client_returns_empty_for_null_meals() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"meals": None})
    )
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = TheMealDBClient(http_client, "https://example.com/api/v1", "1")
        assert await client.search_by_name("Unknown Dish") == []


@pytest.mark.asyncio
async def test_themealdb_client_classifies_http_failure_as_unavailable() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(503, json={"error": "unavailable"})
    )
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = TheMealDBClient(http_client, "https://example.com/api/v1", "1")
        with pytest.raises(TheMealDBUnavailableError):
            await client.search_by_name("French Onion Soup")
