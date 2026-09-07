"""Tests for scoreboard caching and adaptive interval calculation."""

from datetime import datetime, timezone
import pytest

from apps.football_pool.models.enums import GameStatus, SeasonType, WinningType
from apps.football_pool.schemas.scoreboard import ScoreboardGame, ScoreboardWeek
from apps.football_pool.services.poller import calculate_poll_interval
from apps.football_pool.services.scoreboard import ScoreboardCache, get_team_summary


@pytest.fixture
def empty_cache() -> ScoreboardCache:
    return ScoreboardCache()


@pytest.mark.asyncio
async def test_scoreboard_cache_get_set(empty_cache):
    assert await empty_cache.get() is None

    week = ScoreboardWeek(
        season_year=2026,
        season_type=SeasonType.REGULAR_SEASON,
        week=1,
        winning_type=WinningType.MOST,
        games=[],
    )
    await empty_cache.set(week)

    retrieved = await empty_cache.get()
    assert retrieved is not None
    assert retrieved.season_year == 2026
    assert retrieved.week == 1


def test_calculate_poll_interval_active():
    game = ScoreboardGame(
        id="1",
        home_team=get_team_summary("KC"),
        away_team=get_team_summary("BAL"),
        gametime=datetime.now(timezone.utc),
        status=GameStatus.IN_PROGRESS,
    )
    week = ScoreboardWeek(
        season_year=2026,
        season_type=SeasonType.REGULAR_SEASON,
        week=1,
        winning_type=WinningType.MOST,
        games=[game],
    )
    # Active games should poll at 60s
    assert calculate_poll_interval(week) == 60


def test_calculate_poll_interval_idle():
    game = ScoreboardGame(
        id="1",
        home_team=get_team_summary("KC"),
        away_team=get_team_summary("BAL"),
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
    # Final games should poll at idle 900s
    assert calculate_poll_interval(week) == 900
