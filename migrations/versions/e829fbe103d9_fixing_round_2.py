"""Fixing round 2

Revision ID: e829fbe103d9
Revises: 6797067bbf7c
Create Date: 2024-09-03 01:02:57.614074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e829fbe103d9'
down_revision = '6797067bbf7c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('winning_games', schema=None) as batch_op:
        batch_op.drop_constraint('winning_games_owner_id_fkey', type_='foreignkey')
        batch_op.drop_column('owner_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('winning_games', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('winning_games_owner_id_fkey', 'owners', ['owner_id'], ['id'])

    # ### end Alembic commands ###
