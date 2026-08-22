"""Remove LLM dietary conclusions from fallback cache.

Revision ID: 0003_remove_llm_dietary
Revises: 0002_fallback_safety
Create Date: 2026-08-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_remove_llm_dietary"
down_revision: str | None = "0002_fallback_safety"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("fallback_dishes", "dietary_assessments")


def downgrade() -> None:
    op.add_column(
        "fallback_dishes",
        sa.Column("dietary_assessments", sa.JSON(), nullable=True),
    )
