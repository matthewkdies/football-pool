"""Tests for the Tuesday 1:00 AM scoring scheduler service."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.football_pool.database import Base
from apps.football_pool.models import Member, Pot, SeasonAssignment, Team, WinningGame, WinningType
from apps.football_pool.seed.teams_data import TEAMS_DATA
from apps.football_pool.services.espn_client import ESPNAPIError, ESPNClient
from apps.football_pool.services.scheduler import (
    calculate_seconds_until_next_tuesday_1am,
    execute_tuesday_resolution,
    tuesday_scoring_loop,
)


@pytest_asyncio.fixture
async def test_session_factory():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        for t in TEAMS_DATA:
            session.add(Team(**t))
        member = Member(first_name="Matt", last_name="Dies")
        session.add(member)
        await session.flush()

        kc_res = await session.execute(select(Team).where(Team.abbreviation == "KC"))
        kc = kc_res.scalar_one()

        assignment = SeasonAssignment(season_year=2026, member_id=member.id, team_id=kc.id)
        session.add(assignment)
        session.add(Pot(season_year=2026, amount=20))
        await session.commit()

    yield session_factory
    await test_engine.dispose()


def test_calculate_seconds_until_next_tuesday_1am_various_days():
    eastern = ZoneInfo("US/Eastern")

    # 1. Monday at 23:30 (11:30 PM) -> Tuesday 01:00 is 1.5 hours away
    mon = datetime(2026, 9, 14, 23, 30, tzinfo=eastern)
    seconds = calculate_seconds_until_next_tuesday_1am(mon)
    assert seconds == 5400.0  # 1.5 hours = 5400s

    # 2. Tuesday at 00:30 (12:30 AM) -> Tuesday 01:00 is 30 minutes away
    tue_early = datetime(2026, 9, 15, 0, 30, tzinfo=eastern)
    seconds = calculate_seconds_until_next_tuesday_1am(tue_early)
    assert seconds == 1800.0  # 0.5 hours = 1800s

    # 3. Tuesday at exactly 01:00:00 -> Next Tuesday 01:00 is 7 days away
    tue_exact = datetime(2026, 9, 15, 1, 0, tzinfo=eastern)
    seconds = calculate_seconds_until_next_tuesday_1am(tue_exact)
    assert seconds == 604800.0  # 7 * 24 * 3600 = 604800s

    # 4. Tuesday at 02:00 -> Next Tuesday 01:00 is 7 days minus 1 hour
    tue_late = datetime(2026, 9, 15, 2, 0, tzinfo=eastern)
    seconds = calculate_seconds_until_next_tuesday_1am(tue_late)
    assert seconds == 601200.0  # (7 * 24 - 1) * 3600

    # 5. Thursday at 13:00 (1:00 PM) -> Next Tuesday 01:00 is 108 hours away (4.5 days)
    thu = datetime(2026, 9, 17, 13, 0, tzinfo=eastern)
    seconds = calculate_seconds_until_next_tuesday_1am(thu)
    assert seconds == 108.0 * 3600


def test_calculate_seconds_until_next_tuesday_1am_dst_transitions():
    eastern = ZoneInfo("US/Eastern")

    # Fall-back DST (Nov 1, 2026): Oct 27, 2026 01:00 EDT to Nov 3, 2026 01:00 EST
    # Clocks "fall back" by 1 hour, so 169 actual elapsed hours
    oct27 = datetime(2026, 10, 27, 1, 0, tzinfo=eastern)
    seconds = calculate_seconds_until_next_tuesday_1am(oct27)
    assert seconds == 169.0 * 3600

    # Spring-forward DST (Mar 14, 2027): Mar 9, 2027 01:00 EST to Mar 16, 2027 01:00 EDT
    # Clocks "spring forward" by 1 hour, so 167 actual elapsed hours
    mar9 = datetime(2027, 3, 9, 1, 0, tzinfo=eastern)
    seconds = calculate_seconds_until_next_tuesday_1am(mar9)
    assert seconds == 167.0 * 3600


@pytest.mark.asyncio
async def test_execute_tuesday_resolution_success(test_session_factory):
    # Mock ESPN client returning completed game
    mock_client = AsyncMock(spec=ESPNClient)
    mock_data = {
        "events": [
            {
                "id": "1",
                "date": "2026-09-14T20:15:00Z",
                "status": {"type": {"name": "STATUS_FINAL"}},
                "competitions": [
                    {
                        "competitors": [
                            {"homeAway": "home", "score": "35", "team": {"abbreviation": "KC"}},
                            {"homeAway": "away", "score": "21", "team": {"abbreviation": "BAL"}},
                        ]
                    }
                ],
            }
        ],
        "season": {"year": 2026, "type": 2},
        "week": {"number": 1},
    }
    mock_client.fetch_scoreboard.return_value = mock_data

    retry_needed = await execute_tuesday_resolution(client=mock_client, session_factory=test_session_factory)
    assert retry_needed is False

    # Check database: WinningGame was recorded for week 1
    async with test_session_factory() as session:
        result = await session.execute(
            select(WinningGame).where(WinningGame.season_year == 2026, WinningGame.week == 1)
        )
        winning_games = list(result.scalars().all())
        assert len(winning_games) == 1
        assert winning_games[0].winnings == 20
        assert winning_games[0].winning_type == WinningType.MOST


@pytest.mark.asyncio
async def test_execute_tuesday_resolution_postpones_when_games_in_progress(test_session_factory):
    mock_client = AsyncMock(spec=ESPNClient)
    mock_data = {
        "events": [
            {
                "id": "1",
                "date": "2026-09-14T20:15:00Z",
                "status": {"type": {"name": "STATUS_IN_PROGRESS"}},
                "competitions": [
                    {
                        "competitors": [
                            {"homeAway": "home", "score": "14", "team": {"abbreviation": "KC"}},
                            {"homeAway": "away", "score": "10", "team": {"abbreviation": "BAL"}},
                        ]
                    }
                ],
            }
        ],
        "season": {"year": 2026, "type": 2},
        "week": {"number": 1},
    }
    mock_client.fetch_scoreboard.return_value = mock_data

    retry_needed = await execute_tuesday_resolution(client=mock_client, session_factory=test_session_factory)
    assert retry_needed is True

    # No WinningGame records should have been written
    async with test_session_factory() as session:
        result = await session.execute(
            select(WinningGame).where(WinningGame.season_year == 2026, WinningGame.week == 1)
        )
        winning_games = list(result.scalars().all())
        assert len(winning_games) == 0


@pytest.mark.asyncio
async def test_execute_tuesday_resolution_handles_espn_error(test_session_factory):
    mock_client = AsyncMock(spec=ESPNClient)
    mock_client.fetch_scoreboard.side_effect = ESPNAPIError("Connection timeout")

    retry_needed = await execute_tuesday_resolution(client=mock_client, session_factory=test_session_factory)
    assert retry_needed is True


@pytest.mark.asyncio
async def test_tuesday_scoring_loop_shutdown():
    stop_event = asyncio.Event()
    mock_client = AsyncMock(spec=ESPNClient)

    task = asyncio.create_task(tuesday_scoring_loop(stop_event=stop_event, client=mock_client))
    # Let task start and begin waiting
    await asyncio.sleep(0.05)
    assert not task.done()

    # Trigger shutdown
    stop_event.set()
    await asyncio.wait_for(task, timeout=1.0)
    assert task.done()
