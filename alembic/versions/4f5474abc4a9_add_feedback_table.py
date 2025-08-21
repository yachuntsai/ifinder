"""add feedback table

Revision ID: 4f5474abc4a9
Revises: 220f8bc6e85a
Create Date: 2025-08-19 11:16:03.741445

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f5474abc4a9"
down_revision: Union[str, Sequence[str], None] = "220f8bc6e85a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # Still create the table on other dialects (e.g., sqlite in tests),
        # but skip the Postgres-specific bits if you prefer.
        pass

    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column(
            "image_id",
            sa.Integer(),
            sa.ForeignKey("images.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("is_good", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
    )

    op.create_index("ix_feedbacks_image_id", "feedbacks", ["image_id"])
    op.create_index("ix_feedbacks_created_at", "feedbacks", ["created_at"])
    op.create_index("ix_feedbacks_is_good", "feedbacks", ["is_good"])


def downgrade():
    op.drop_index("ix_feedbacks_is_good", table_name="feedbacks")
    op.drop_index("ix_feedbacks_created_at", table_name="feedbacks")
    op.drop_index("ix_feedbacks_image_id", table_name="feedbacks")
    op.drop_table("feedbacks")
