"""changed_id_type_documents

Revision ID: b6c449cca2e5
Revises: 48abc949ab7c
Create Date: 2025-09-25 15:18:58.435380

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b6c449cca2e5"
down_revision: Union[str, Sequence[str], None] = "48abc949ab7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("documents", "id")

    op.add_column(
        "documents",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("documents", "id")
    op.add_column(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
    )
