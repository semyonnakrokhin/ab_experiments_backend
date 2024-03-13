"""empty message

Revision ID: d871b1829a2b
Revises:
Create Date: 2024-03-13 13:43:27.309308

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d871b1829a2b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "experiment_table",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_token", sa.String(), nullable=False),
        sa.Column("button_color", sa.String(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("experiment_table")
    # ### end Alembic commands ###