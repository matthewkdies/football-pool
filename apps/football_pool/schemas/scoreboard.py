"""Pydantic schemas for the ESPN scoreboard and live games."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from ..models.enums import GameStatus, SeasonType, WinningType


class TeamSummary(BaseModel):
    """Concise representation of an NFL team for scoreboard display."""

    abbreviation: str
    city: str
    name: str
    full_name: str
    logo_url: str


class ScoreboardGame(BaseModel):
    """A single game event within a week."""

    id: str
    home_team: TeamSummary
    home_team_score: int = 0
    away_team: TeamSummary
    away_team_score: int = 0
    espn_url: str = ""
    gametime: datetime
    status: GameStatus
    display_clock: str | None = None
    quarter: int | None = None

    @property
    def is_in_progress(self) -> bool:
        return self.status == GameStatus.IN_PROGRESS

    @property
    def is_in_halftime(self) -> bool:
        return self.status == GameStatus.HALFTIME

    @property
    def is_final(self) -> bool:
        return self.status == GameStatus.FINAL

    @property
    def is_queued(self) -> bool:
        return self.status == GameStatus.SCHEDULED

    @property
    def max_score(self) -> int:
        return max(self.home_team_score, self.away_team_score)

    @property
    def min_score(self) -> int:
        return min(self.home_team_score, self.away_team_score)

    @property
    def winning_team_abbr(self) -> str | None:
        """Returns winning team abbreviation if game is final and not tied."""
        if not self.is_final or self.home_team_score == self.away_team_score:
            return None
        if self.home_team_score > self.away_team_score:
            return self.home_team.abbreviation
        return self.away_team.abbreviation


class ScoreboardWeek(BaseModel):
    """Aggregate snapshot of the current NFL week and pool winners."""

    season_year: int
    season_type: SeasonType
    week: int
    winning_type: WinningType
    games: list[ScoreboardGame] = Field(default_factory=list)
    pool_winning_team_abbrs: list[str] = Field(default_factory=list)
    pot_amount: int = 10
    last_polled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_preseason(self) -> bool:
        return self.season_type == SeasonType.PRESEASON

    @property
    def is_postseason(self) -> bool:
        return self.season_type == SeasonType.POSTSEASON

    @property
    def is_super_bowl(self) -> bool:
        return self.is_postseason and self.week == 5

    @property
    def is_pro_bowl(self) -> bool:
        return self.is_postseason and self.week == 4

    @property
    def has_active_games(self) -> bool:
        return any(g.is_in_progress or g.is_in_halftime for g in self.games)
