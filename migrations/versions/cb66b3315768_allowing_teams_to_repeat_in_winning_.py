"""Allowing teams to repeat in winning_games table.

Revision ID: cb66b3315768
Revises: c0cb9bf1b6a9
Create Date: 2024-09-08 02:44:31.884069

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb66b3315768'
down_revision = 'c0cb9bf1b6a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('winning_games', schema=None) as batch_op:
        batch_op.alter_column('team_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_constraint('winning_games_team_id_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('winning_games', schema=None) as batch_op:
        batch_op.create_unique_constraint('winning_games_team_id_key', ['team_id'])
        batch_op.alter_column('team_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###
