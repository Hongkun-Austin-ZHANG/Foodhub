import asyncio
from typing import Any, Protocol

from schemas.unknown_dish import (
    FallbackDishBatchRequest,
    FallbackDishBatchResponse,
)
from services.ai.menu_parser import MenuUnderstandingError
from services.ai.prompts import UNKNOWN_DISH_SYSTEM_PROMPT


class UnknownDishResolver(Protocol):
    """Backend B fallback used only after local and TheMealDB matching fail."""

    async def resolve_batch(
        self,
        request: FallbackDishBatchRequest,
    ) -> FallbackDishBatchResponse: ...


class OpenAIUnknownDishResolver:
    def __init__(self, api_key: str, model: str, timeout_seconds: float) -> None:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise MenuUnderstandingError(
                "The openai package is not installed. Run pip install -r requirements.txt"
            ) from error
        self._client: Any = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._model = model

    async def resolve_batch(
        self,
        request: FallbackDishBatchRequest,
    ) -> FallbackDishBatchResponse:
        try:
            result = await asyncio.to_thread(self._resolve_sync, request)
        except MenuUnderstandingError:
            raise
        except Exception as error:
            raise MenuUnderstandingError(
                "Backend B unknown-dish fallback failed"
            ) from error

        expected_ids = {dish.request_id for dish in request.dishes}
        returned_ids = {dish.request_id for dish in result.results}
        if expected_ids != returned_ids:
            raise MenuUnderstandingError(
                "Backend B fallback request_ids do not match the input batch"
            )
        return result.model_copy(
            update={"schema_version": "1.1", "batch_id": request.batch_id}
        )

    def _resolve_sync(
        self,
        request: FallbackDishBatchRequest,
    ) -> FallbackDishBatchResponse:
        response = self._client.responses.parse(
            model=self._model,
            store=False,
            input=[
                {"role": "system", "content": UNKNOWN_DISH_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Provide fallback culinary knowledge for this confirmed "
                        "batch of misses:\n\n" + request.model_dump_json(indent=2)
                    ),
                },
            ],
            text_format=FallbackDishBatchResponse,
        )
        if response.output_parsed is None:
            raise MenuUnderstandingError(
                "Backend B did not return a valid fallback batch"
            )
        return response.output_parsed.model_copy(
            update={
                "schema_version": "1.1",
                "batch_id": request.batch_id,
                "results": [
                    result.model_copy(update={"model_id": self._model})
                    for result in response.output_parsed.results
                ],
            }
        )
