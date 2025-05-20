"""creates stage_earthquakes table

Revision ID: 3335f792e59e
Revises: 52a3dc27eb5b
Create Date: 2025-05-19 19:02:46.435770

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3335f792e59e"
down_revision: Union[str, None] = "52a3dc27eb5b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stage_earthquakes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dt", sa.DateTime(), nullable=True),
        sa.Column("region", sa.String(length=255), nullable=True),
        sa.Column("place", sa.String(length=255), nullable=True),
        sa.Column("magnitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stage_earthquakes_dt"), "stage_earthquakes", ["dt"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stage_earthquakes_dt"), table_name="stage_earthquakes")
    op.drop_table("stage_earthquakes")
