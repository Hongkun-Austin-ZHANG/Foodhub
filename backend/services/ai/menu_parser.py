import asyncio
import base64
from typing import Any, Protocol

from schemas.menu import BackendBMenuPayload, MenuParseResult
from services.ai.prompts import MENU_PARSE_SYSTEM_PROMPT

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class MenuUnderstandingError(RuntimeError):
    """Raised when Backend B cannot return a valid structured result."""


class MenuParser(Protocol):
    """Boundary implemented by Backend B's image-to-JSON service."""

    async def parse(
        self,
        image: bytes,
        content_type: str,
        output_language: str = "en",
    ) -> MenuParseResult: ...

    async def parse_many(
        self,
        images: list[tuple[bytes, str]],
        output_language: str = "en",
    ) -> MenuParseResult: ...


class OpenAIMenuParser:
    def __init__(self, api_key: str, model: str, timeout_seconds: float) -> None:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise MenuUnderstandingError(
                "The openai package is not installed. Run pip install -r requirements.txt"
            ) from error
        self._client: Any = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._model = model

    async def parse(
        self,
        image: bytes,
        content_type: str,
        output_language: str = "en",
    ) -> MenuParseResult:
        return await self.parse_many([(image, content_type)], output_language)

    async def parse_many(
        self,
        images: list[tuple[bytes, str]],
        output_language: str = "en",
    ) -> MenuParseResult:
        if not images:
            raise ValueError("At least one menu image is required")
        for image, content_type in images:
            if not image:
                raise ValueError("Menu image is empty")
            if content_type not in SUPPORTED_IMAGE_TYPES:
                raise ValueError(f"Unsupported menu image type: {content_type}")
        if not output_language.strip():
            raise ValueError("output_language is required")
        try:
            parsed = await asyncio.to_thread(
                self._parse_sync,
                images,
                output_language,
            )
        except (ValueError, MenuUnderstandingError):
            raise
        except Exception as error:
            raise MenuUnderstandingError("Backend B menu parsing failed") from error
        return parsed.to_menu_parse_result()

    def _parse_sync(
        self,
        images: list[tuple[bytes, str]],
        output_language: str,
    ) -> BackendBMenuPayload:
        content: list[dict[str, str]] = [
            {
                "type": "input_text",
                "text": (
                    "Parse all attached menu pages as one menu. Remove duplicate "
                    "items repeated across overlapping photos. Use "
                    f"'{output_language}' for user-facing translations."
                ),
            }
        ]
        for image, content_type in images:
            image_base64 = base64.b64encode(image).decode("ascii")
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{content_type};base64,{image_base64}",
                }
            )
        response = self._client.responses.parse(
            model=self._model,
            store=False,
            input=[
                {"role": "system", "content": MENU_PARSE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": content,
                },
            ],
            text_format=BackendBMenuPayload,
        )
        if response.output_parsed is None:
            raise MenuUnderstandingError(
                "Backend B did not return a valid structured menu"
            )
        return response.output_parsed.model_copy(
            update={"target_language": output_language}
        )
