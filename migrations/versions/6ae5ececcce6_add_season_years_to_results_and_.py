"""Add season years to results and assignments.

Revision ID: 6ae5ececcce6
Revises: 7cb5669c0bc6
Create Date: 2025-08-15 00:42:13.165582

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6ae5ececcce6"
down_revision = "7cb5669c0bc6"
branch_labels = None
depends_on = None


def upgrade():
    # randomly, the pot table now decided the id has to be unique? here's that
    with op.batch_alter_table("pot", schema=None) as batch_op:
        batch_op.create_unique_constraint("pot_id_unique", ["id"])

    # ------------------------------------------------------------------------

    # adding the season_start_year column to the owners
    #   1. add column as nullable
    with op.batch_alter_table("owners", schema=None) as batch_op:
        batch_op.add_column(sa.Column("season_start_year", sa.Integer(), nullable=True))

    #   2. add values, make non-nullable
    with op.batch_alter_table("owners", schema=None) as batch_op:
        batch_op.execute("UPDATE owners SET season_start_year = 2024 WHERE season_start_year IS NULL")
        batch_op.alter_column(column_name="season_start_year", nullable=False)

    # ------------------------------------------------------------------------

    # adding the season_start_year column to the winning_games
    #   1. add column as nullable
    with op.batch_alter_table("winning_games", schema=None) as batch_op:
        batch_op.add_column(sa.Column("season_start_year", sa.Integer(), nullable=True))

    #   2. add values, make non-nullable
    with op.batch_alter_table("winning_games", schema=None) as batch_op:
        batch_op.execute("UPDATE winning_games SET season_start_year = 2024 WHERE season_start_year IS NULL")
        batch_op.alter_column(column_name="season_start_year", nullable=False)


def downgrade():
    with op.batch_alter_table("pot", schema=None) as batch_op:
        batch_op.drop_constraint("pot_id_unique", type_="unique")

    with op.batch_alter_table("winning_games", schema=None) as batch_op:
        batch_op.drop_column("season_start_year")

    with op.batch_alter_table("owners", schema=None) as batch_op:
        batch_op.drop_column("season_start_year")
