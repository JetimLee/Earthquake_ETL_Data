"""adds date handling

Revision ID: 2f5bc7613c97
Revises: 3335f792e59e
Create Date: 2025-05-19 19:20:01.486683

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f5bc7613c97"
down_revision: Union[str, None] = "3335f792e59e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the new columns if they don't exist
    # Using try/except because we're also handling this in the script
    try:
        op.add_column(
            "stage_earthquakes", sa.Column("depth", sa.Float(), nullable=True)
        )
    except Exception:
        pass

    try:
        op.add_column(
            "stage_earthquakes", sa.Column("raw_time", sa.BigInteger(), nullable=True)
        )
    except Exception:
        pass


def downgrade() -> None:
    # Use try/except to avoid errors if columns don't exist
    try:
        op.drop_column("stage_earthquakes", "depth")
    except Exception:
        pass

    try:
        op.drop_column("stage_earthquakes", "raw_time")
    except Exception:
        pass
