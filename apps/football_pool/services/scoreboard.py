"""ESPN Scoreboard JSON parsing and in-memory caching service."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from ..models.enums import GameStatus, SeasonType, WinningType
from ..schemas.scoreboard import ScoreboardGame, ScoreboardWeek, TeamSummary
from ..seed.teams_data import TEAMS_DATA

logger = logging.getLogger(__name__)

EST = ZoneInfo("US/Eastern")

# Pre-populated in-memory dictionary of all 32 NFL teams
TEAM_MAP: dict[str, TeamSummary] = {
    team["abbreviation"]: TeamSummary(
        abbreviation=team["abbreviation"],
        city=team["city"],
        name=team["name"],
        full_name=f"{team['city']} {team['name']}",
        logo_url=team["logo_url"],
        conference=str(team["conference"].value if hasattr(team["conference"], "value") else team["conference"]),
        division=str(team["division"].value if hasattr(team["division"], "value") else team["division"]),
    )
    for team in TEAMS_DATA
}  # ty: ignore[invalid-assignment]


def get_team_summary(abbr: str) -> TeamSummary:
    """Returns TeamSummary for an abbreviation, with a fallback if not found."""
    if abbr in TEAM_MAP:
        return TEAM_MAP[abbr]
    # Fallback for unexpected or relocated team codes
    return TeamSummary(
        abbreviation=abbr,
        city="Unknown",
        name=abbr,
        full_name=abbr,
        logo_url="logos/unknown.png",
    )


def determine_winning_type(season_type: SeasonType, week: int) -> WinningType:
    """Determines the WinningType for a given week and season type."""
    if season_type == SeasonType.POSTSEASON:
        if week == 5:
            return WinningType.SUPER_BOWL
        return WinningType.PLAYOFF
    if week % 2 == 1:
        return WinningType.MOST
    return WinningType.LEAST


def compute_pool_winners(games: list[ScoreboardGame], season_type: SeasonType, week: int) -> list[str]:
    """Computes the list of winning team abbreviations according to pool rules."""
    if season_type == SeasonType.PRESEASON:
        return []

    winners: set[str] = set()

    # 1. Fifty-point scorers (applies to all weeks)
    for game in games:
        if game.home_team_score == 50:
            winners.add(game.home_team.abbreviation)
        if game.away_team_score == 50:
            winners.add(game.away_team.abbreviation)

    # 2. Super Bowl (Postseason Week 5)
    if season_type == SeasonType.POSTSEASON and week == 5:
        for game in games:
            if game.is_final and game.winning_team_abbr:
                winners.add(game.winning_team_abbr)
        return sorted(winners)

    # 3. Pro Bowl (Postseason Week 4 - no winners)
    if season_type == SeasonType.POSTSEASON and week == 4:
        return sorted(winners)

    # 4. Playoff rounds (Postseason Weeks 1, 2, 3)
    if season_type == SeasonType.POSTSEASON:
        for game in games:
            if game.is_final and game.winning_team_abbr:
                winners.add(game.winning_team_abbr)
        return sorted(winners)

    # 5. Regular Season (Odd = Most points, Even = Least points)
    played_games = [g for g in games if not g.is_queued]
    if played_games:
        winning_type = determine_winning_type(season_type, week)
        if winning_type == WinningType.MOST:
            target_score = max(g.max_score for g in played_games)
        else:
            target_score = min(g.min_score for g in played_games)

        for game in played_games:
            if game.home_team_score == target_score:
                winners.add(game.home_team.abbreviation)
            if game.away_team_score == target_score:
                winners.add(game.away_team.abbreviation)

    # Safeguard from original code: if >= 16 teams qualify, scores are likely unplayed
    if len(winners) >= 16:
        logger.debug("More than 16 teams matched winning criteria; returning empty list.")
        return []

    return sorted(winners)


def parse_scoreboard_data(data: dict[str, Any], pot_amount: int = 10) -> ScoreboardWeek:
    """Parses raw ESPN scoreboard JSON into a validated ScoreboardWeek."""
    events = data.get("events", [])
    games: list[ScoreboardGame] = []

    for event in events:
        status_name = event.get("status", {}).get("type", {}).get("name", "STATUS_SCHEDULED")
        status = GameStatus.from_espn_status(status_name)

        if status == GameStatus.SCHEDULED:
            display_clock = None
            quarter = None
        else:
            display_clock = event.get("status", {}).get("displayClock")
            quarter = int(event.get("status", {}).get("period", 0))

        competitions = event.get("competitions", [{}])[0]
        competitors = competitions.get("competitors", [])

        home_comp = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away_comp = next((c for c in competitors if c.get("homeAway") == "away"), None)

        if not home_comp or not away_comp:
            continue

        home_abbr = home_comp.get("team", {}).get("abbreviation", "")
        away_abbr = away_comp.get("team", {}).get("abbreviation", "")

        date_str = event.get("date", "")
        try:
            # Parse ISO 8601 UTC date and convert to US/Eastern
            clean_date_str = date_str.replace("Z", "+00:00")
            dt_utc = datetime.fromisoformat(clean_date_str)
            gametime = dt_utc.astimezone(EST)
        except Exception:
            gametime = datetime.now(EST)

        links = event.get("links", [{}])
        espn_url = links[0].get("href", "") if links else ""

        game = ScoreboardGame(
            id=str(event.get("id", "")),
            home_team=get_team_summary(home_abbr),
            home_team_score=int(home_comp.get("score", 0)),
            away_team=get_team_summary(away_abbr),
            away_team_score=int(away_comp.get("score", 0)),
            espn_url=espn_url,
            gametime=gametime,
            status=status,
            display_clock=display_clock,
            quarter=quarter,
        )
        games.append(game)

    # Extract season metadata
    season_type_val = 2
    season_year = datetime.now(timezone.utc).year
    week_number = 1

    leagues = data.get("leagues", [])
    if leagues:
        season_info = leagues[0].get("season", {})
        season_year = int(season_info.get("year", season_year))
        season_type_val = season_info.get("type", {}).get("type", 2)

    week_info = data.get("week", {})
    if week_info:
        week_number = int(week_info.get("number", 1))

    season_type = SeasonType.from_espn_type(season_type_val)
    winning_type = determine_winning_type(season_type, week_number)
    pool_winners = compute_pool_winners(games, season_type, week_number)

    return ScoreboardWeek(
        season_year=season_year,
        season_type=season_type,
        week=week_number,
        winning_type=winning_type,
        games=games,
        pool_winning_team_abbrs=pool_winners,
        pot_amount=pot_amount,
        last_polled_at=datetime.now(timezone.utc),
    )


class ScoreboardCache:
    """Thread-safe and async-safe in-memory cache for live scoreboard data."""

    def __init__(self) -> None:
        self._cache: ScoreboardWeek | None = None
        self._lock = asyncio.Lock()
        self.refresh_event = asyncio.Event()

    async def get(self) -> ScoreboardWeek | None:
        """Retrieves cached scoreboard."""
        async with self._lock:
            return self._cache

    async def set(self, week: ScoreboardWeek) -> None:
        """Updates cached scoreboard."""
        async with self._lock:
            self._cache = week

    def trigger_refresh(self) -> None:
        """Signals the background poller to fetch immediately."""
        self.refresh_event.set()


scoreboard_cache = ScoreboardCache()
