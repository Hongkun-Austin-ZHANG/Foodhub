"""Add neutral safety assessments to cached LLM dishes.

Revision ID: 0002_fallback_safety
Revises: 0001_initial_schema
Create Date: 2026-08-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_fallback_safety"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "fallback_dishes",
        sa.Column("allergen_assessments", sa.JSON(), nullable=True),
    )
    op.add_column(
        "fallback_dishes",
        sa.Column("dietary_assessments", sa.JSON(), nullable=True),
    )
    op.add_column(
        "fallback_dishes",
        sa.Column("model_id", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("fallback_dishes", "model_id")
    op.drop_column("fallback_dishes", "dietary_assessments")
    op.drop_column("fallback_dishes", "allergen_assessments")
