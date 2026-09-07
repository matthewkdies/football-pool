"""allow multiple members per team

Revision ID: 0002_multi_members
Revises: 0001_initial_schema
Create Date: 2026-09-07 18:15:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0002_multi_members"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_season_team", "season_assignments", type_="unique")
    op.create_unique_constraint(
        "uq_season_team_member",
        "season_assignments",
        ["season_year", "team_id", "member_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_season_team_member", "season_assignments", type_="unique")
    op.create_unique_constraint(
        "uq_season_team",
        "season_assignments",
        ["season_year", "team_id"],
    )
