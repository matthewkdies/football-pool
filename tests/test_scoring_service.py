"""Tests for Tuesday scoring resolution, pot rollover, and idempotency."""

from datetime import datetime, timezone
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.football_pool.database import Base
from apps.football_pool.models import Member, Pot, SeasonAssignment, Team, WinningGame, WinningType
from apps.football_pool.models.enums import GameStatus, SeasonType
from apps.football_pool.schemas.scoreboard import ScoreboardGame, ScoreboardWeek
from apps.football_pool.seed.teams_data import TEAMS_DATA
from apps.football_pool.services.results import resolve_weekly_results
from apps.football_pool.services.scoreboard import get_team_summary


@pytest_asyncio.fixture
async def test_session():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        # Seed teams
        for t in TEAMS_DATA:
            session.add(Team(**t))
        # Seed test member and assignment
        member = Member(first_name="Matt", last_name="Dies")
        session.add(member)
        await session.flush()

        kc_res = await session.execute(select(Team).where(Team.abbreviation == "KC"))
        kc = kc_res.scalar_one()

        assignment = SeasonAssignment(season_year=2026, member_id=member.id, team_id=kc.id)
        session.add(assignment)

        # Seed pot
        session.add(Pot(season_year=2026, amount=20))
        await session.commit()

        yield session

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_scoring_owner_wins_resets_pot(test_session: AsyncSession):
    # Week 1 (MOST) - KC scores 35 (highest), owned by Matt
    game = ScoreboardGame(
        id="1",
        home_team=get_team_summary("KC"),
        home_team_score=35,
        away_team=get_team_summary("BAL"),
        away_team_score=20,
        gametime=datetime.now(timezone.utc),
        status=GameStatus.FINAL,
    )
    week = ScoreboardWeek(
        season_year=2026,
        season_type=SeasonType.REGULAR_SEASON,
        week=1,
        winning_type=WinningType.MOST,
        games=[game],
    )

    created = await resolve_weekly_results(test_session, week)
    assert len(created) == 1
    assert created[0].winnings == 20  # initial pot was 20
    assert created[0].winning_type == WinningType.MOST

    # Pot should now be reset to 10 because a real owner won
    pot_res = await test_session.execute(select(Pot).where(Pot.season_year == 2026))
    pot = pot_res.scalar_one()
    assert pot.amount == 10


@pytest.mark.asyncio
async def test_scoring_unowned_team_wins_increments_pot(test_session: AsyncSession):
    # Week 1 (MOST) - BAL scores 35 (highest), BAL is NOT owned in test fixture
    game = ScoreboardGame(
        id="1",
        home_team=get_team_summary("BAL"),
        home_team_score=35,
        away_team=get_team_summary("KC"),
        away_team_score=10,
        gametime=datetime.now(timezone.utc),
        status=GameStatus.FINAL,
    )
    week = ScoreboardWeek(
        season_year=2026,
        season_type=SeasonType.REGULAR_SEASON,
        week=1,
        winning_type=WinningType.MOST,
        games=[game],
    )

    created = await resolve_weekly_results(test_session, week)
    assert len(created) == 1
    assert created[0].winnings == 20

    # Pot should increment from 20 to 30 because no owner won
    pot_res = await test_session.execute(select(Pot).where(Pot.season_year == 2026))
    pot = pot_res.scalar_one()
    assert pot.amount == 30


@pytest.mark.asyncio
async def test_scoring_idempotency(test_session: AsyncSession):
    game = ScoreboardGame(
        id="1",
        home_team=get_team_summary("KC"),
        home_team_score=35,
        away_team=get_team_summary("BAL"),
        away_team_score=20,
        gametime=datetime.now(timezone.utc),
        status=GameStatus.FINAL,
    )
    week = ScoreboardWeek(
        season_year=2026,
        season_type=SeasonType.REGULAR_SEASON,
        week=1,
        winning_type=WinningType.MOST,
        games=[game],
    )

    # First run
    first_run = await resolve_weekly_results(test_session, week)
    assert len(first_run) == 1

    # Second run should detect existing results and not duplicate
    second_run = await resolve_weekly_results(test_session, week)
    assert len(second_run) == 1

    total_games_res = await test_session.execute(select(WinningGame).where(WinningGame.week == 1))
    assert len(list(total_games_res.scalars().all())) == 1
