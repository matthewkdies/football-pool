"""0001 initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-06 20:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Members
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Teams
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("abbreviation", sa.String(length=5), nullable=False),
        sa.Column("logo_url", sa.String(length=255), nullable=False),
        sa.Column("conference", sa.Enum("AFC", "NFC", name="conference"), nullable=False),
        sa.Column("division", sa.Enum("North", "South", "East", "West", name="division"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teams_abbreviation"), "teams", ["abbreviation"], unique=True)

    # 3. Season Assignments
    op.create_table(
        "season_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season_year", "team_id", name="uq_season_team"),
    )
    op.create_index(op.f("ix_season_assignments_season_year"), "season_assignments", ["season_year"], unique=False)

    # 4. Winning Games
    op.create_table(
        "winning_games",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("winnings", sa.Integer(), nullable=False),
        sa.Column("winning_type", sa.Enum("MOST", "LEAST", "FIFTY", "PLAYOFF", "SUPER_BOWL", name="winningtype"), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_winning_games_season_year"), "winning_games", ["season_year"], unique=False)

    # 5. Pots
    op.create_table(
        "pots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False, default=10),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pots_season_year"), "pots", ["season_year"], unique=True)

    # 6. Chat Messages
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chat_messages_created_at"), "chat_messages", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("pots")
    op.drop_table("winning_games")
    op.drop_table("season_assignments")
    op.drop_table("teams")
    op.drop_table("members")
