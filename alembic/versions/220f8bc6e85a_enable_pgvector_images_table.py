"""enable pgvector + images table

Revision ID: 220f8bc6e85a
Revises:
Create Date: 2025-08-19 11:13:28.764115

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "220f8bc6e85a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        op.create_table(
            "images",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("filename", sa.String, nullable=False, unique=True),
            sa.Column("url_path", sa.String, nullable=False),
            sa.Column("embedding", Vector(512), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("TIMEZONE('utc', now())"),
                nullable=False,
            ),
        )
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS images_embedding_hnsw
            ON images USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """
        )


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS images_embedding_hnsw;")
        op.drop_table("images")
        # (usually keep the extension; drop only if you really need to)
        # op.execute("DROP EXTENSION IF EXISTS vector;")
