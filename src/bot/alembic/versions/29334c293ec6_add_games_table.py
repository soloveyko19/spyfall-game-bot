"""Add games table

Revision ID: 29334c293ec6
Revises: 1861afbdcfa9
Create Date: 2024-02-08 17:37:18.029199

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "29334c293ec6"
down_revision: Union[str, None] = "1861afbdcfa9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("join_key", sa.String(), nullable=True),
        sa.Column("join_message_tg_id", sa.Integer(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.Column("state_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["location_id"], ["locations.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["state_id"], ["game_states.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_games_group_tg_id"),
        "games",
        ["group_tg_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_games_join_key"), "games", ["join_key"], unique=True
    )
    op.create_index(
        op.f("ix_games_join_message_tg_id"),
        "games",
        ["join_message_tg_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_games_join_message_tg_id"), table_name="games")
    op.drop_index(op.f("ix_games_join_key"), table_name="games")
    op.drop_index(op.f("ix_games_group_tg_id"), table_name="games")
    op.drop_table("games")
    # ### end Alembic commands ###
