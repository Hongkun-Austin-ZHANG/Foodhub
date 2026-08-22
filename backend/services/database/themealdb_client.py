import httpx
from pydantic import ValidationError

from schemas.dish import ExternalDishCandidate


class TheMealDBUnavailableError(RuntimeError):
    pass


class TheMealDBClient:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        base_url: str,
        api_key: str,
    ) -> None:
        self._http_client = http_client
        self._search_url = f"{base_url.rstrip('/')}/{api_key}/search.php"

    async def search_by_name(
        self, canonical_name_en: str
    ) -> list[ExternalDishCandidate]:
        query = canonical_name_en.strip()
        if not query:
            return []

        try:
            response = await self._http_client.get(
                self._search_url, params={"s": query}
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as error:
            raise TheMealDBUnavailableError("TheMealDB request timed out") from error
        except (httpx.HTTPError, ValueError) as error:
            raise TheMealDBUnavailableError("TheMealDB request failed") from error

        meals = payload.get("meals") if isinstance(payload, dict) else None
        if meals is None:
            return []
        if not isinstance(meals, list):
            raise TheMealDBUnavailableError("TheMealDB returned an invalid payload")

        candidates: list[ExternalDishCandidate] = []
        for meal in meals:
            if not isinstance(meal, dict):
                continue
            ingredients = self._extract_ingredients(meal)
            try:
                candidates.append(
                    ExternalDishCandidate(
                        external_id=meal.get("idMeal", ""),
                        name=meal.get("strMeal", ""),
                        area=meal.get("strArea") or None,
                        category=meal.get("strCategory") or None,
                        image_url=meal.get("strMealThumb") or None,
                        ingredients=ingredients,
                    )
                )
            except ValidationError:
                continue
        return candidates

    @staticmethod
    def _extract_ingredients(meal: dict[str, object]) -> list[str]:
        ingredients: list[str] = []
        seen: set[str] = set()
        for index in range(1, 21):
            raw_ingredient = meal.get(f"strIngredient{index}")
            if not isinstance(raw_ingredient, str):
                continue
            ingredient = " ".join(raw_ingredient.strip().split())
            key = ingredient.casefold()
            if ingredient and key not in seen:
                seen.add(key)
                ingredients.append(ingredient)
        return ingredients
