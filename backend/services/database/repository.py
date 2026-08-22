from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.dish import (
    FallbackDishRecord,
    IngredientEvidence,
    normalize_lookup_name,
)
from schemas.safety import AllergenAssessment
from services.database.models import FallbackDish


class FallbackDishRepository(Protocol):
    async def find_by_name(
        self,
        canonical_name_en: str,
        aliases: list[str] | None = None,
    ) -> FallbackDishRecord | None: ...

    async def save(self, record: FallbackDishRecord) -> FallbackDishRecord: ...


class InMemoryFallbackDishRepository:
    """Small test implementation that requires no running database."""

    def __init__(self) -> None:
        self._records: dict[str, FallbackDishRecord] = {}

    async def find_by_name(
        self,
        canonical_name_en: str,
        aliases: list[str] | None = None,
    ) -> FallbackDishRecord | None:
        lookup_names = {
            normalize_lookup_name(value)
            for value in [canonical_name_en, *(aliases or [])]
            if value
        }
        direct = next(
            (self._records[name] for name in lookup_names if name in self._records),
            None,
        )
        if direct is not None:
            return direct
        return next(
            (
                record
                for record in self._records.values()
                if lookup_names
                & {
                    normalize_lookup_name(value)
                    for value in [record.canonical_name_en, *record.aliases]
                    if value
                }
            ),
            None,
        )

    async def save(self, record: FallbackDishRecord) -> FallbackDishRecord:
        self._records[record.normalized_name] = record
        return record


class SqlAlchemyFallbackDishRepository:
    """MySQL-backed cache for dishes produced by the unknown-dish LLM."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_name(
        self,
        canonical_name_en: str,
        aliases: list[str] | None = None,
    ) -> FallbackDishRecord | None:
        lookup_names = {
            normalize_lookup_name(value)
            for value in [canonical_name_en, *(aliases or [])]
            if value
        }
        direct = await self._session.scalar(
            select(FallbackDish).where(FallbackDish.normalized_name.in_(lookup_names))
        )
        if direct is not None:
            return self._to_record(direct)

        models = (await self._session.scalars(select(FallbackDish))).all()
        for model in models:
            stored_names = {
                normalize_lookup_name(value)
                for value in [model.canonical_name_en, *(model.aliases or [])]
                if value
            }
            if lookup_names & stored_names:
                return self._to_record(model)
        return None

    async def save(self, record: FallbackDishRecord) -> FallbackDishRecord:
        statement = select(FallbackDish).where(
            FallbackDish.normalized_name == record.normalized_name
        )
        model = await self._session.scalar(statement)
        values = self._to_values(record)

        if model is None:
            model = FallbackDish(id=str(record.record_id), **values)
            self._session.add(model)
        else:
            for field, value in values.items():
                setattr(model, field, value)

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_record(model)

    @staticmethod
    def _to_values(record: FallbackDishRecord) -> dict[str, object]:
        return {
            "canonical_name_en": record.canonical_name_en,
            "normalized_name": record.normalized_name,
            "aliases": record.aliases,
            "description": record.description,
            "cuisine": record.cuisine,
            "ingredients": [
                ingredient.model_dump(mode="json") for ingredient in record.ingredients
            ],
            "allergen_assessments": [
                assessment.model_dump(mode="json")
                for assessment in record.allergen_assessments
            ],
            "image_url": str(record.image_url) if record.image_url else None,
            "confidence": record.confidence,
            "model_id": record.model_id,
            "generated_by": record.generated_by.value,
        }

    @staticmethod
    def _to_record(model: FallbackDish) -> FallbackDishRecord:
        return FallbackDishRecord(
            record_id=model.id,
            canonical_name_en=model.canonical_name_en,
            normalized_name=model.normalized_name,
            aliases=model.aliases,
            description=model.description,
            cuisine=model.cuisine,
            ingredients=[
                IngredientEvidence.model_validate(item) for item in model.ingredients
            ],
            allergen_assessments=[
                AllergenAssessment.model_validate(item)
                for item in (model.allergen_assessments or [])
            ],
            image_url=model.image_url,
            confidence=float(model.confidence),
            model_id=model.model_id,
            generated_by=model.generated_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
