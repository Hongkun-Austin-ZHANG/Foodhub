from datetime import UTC, datetime
from decimal import Decimal

from schemas.dish import (
    EvidenceLevel,
    EvidenceSource,
    FallbackDishRecord,
    IngredientEvidence,
)
from services.database import models  # noqa: F401
from services.database.base import Base
from services.database.models import FallbackDish
from services.database.repository import SqlAlchemyFallbackDishRepository


def test_expected_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "auth_sessions",
        "fallback_dishes",
        "demo_menu_templates",
        "menu_scans",
        "user_preferences",
        "user_profiles",
        "users",
    }


def test_normalized_fallback_name_is_unique() -> None:
    table = Base.metadata.tables["fallback_dishes"]
    unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }
    assert ("normalized_name",) in unique_columns


def test_user_preference_is_unique_per_user_and_code() -> None:
    table = Base.metadata.tables["user_preferences"]
    unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }
    assert ("user_id", "code") in unique_columns


def test_fallback_record_round_trip_mapping() -> None:
    record = FallbackDishRecord(
        canonical_name_en="Sample Stew",
        normalized_name="sample stew",
        aliases=["House Stew"],
        description="A sample dish generated for testing.",
        cuisine="Test",
        ingredients=[
            IngredientEvidence(
                name="Peanut",
                source=EvidenceSource.LLM,
                evidence_level=EvidenceLevel.INFERRED,
            )
        ],
        confidence=0.82,
    )
    values = SqlAlchemyFallbackDishRepository._to_values(record)
    now = datetime.now(UTC)
    model = FallbackDish(
        id=str(record.record_id),
        **values,
        created_at=now,
        updated_at=now,
    )

    restored = SqlAlchemyFallbackDishRepository._to_record(model)

    assert restored.record_id == record.record_id
    assert restored.ingredients == record.ingredients
    assert restored.confidence == float(Decimal("0.82"))
