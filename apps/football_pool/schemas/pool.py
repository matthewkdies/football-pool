"""Schemas for pool assignments, results, standings, and pot."""

from __future__ import annotations

from pydantic import BaseModel

from .auth import MemberResponse
from .scoreboard import TeamSummary


class SeasonAssignmentResponse(BaseModel):
    """A member's team assignment for a specific season."""

    id: int
    season_year: int
    member: MemberResponse
    team: TeamSummary


class WinningGameResponse(BaseModel):
    """Historical payout record for a team in a given week."""

    id: int
    season_year: int
    week: int
    winnings: int
    winning_type: str
    team: TeamSummary
    winning_owner_name: str


class StandingItem(BaseModel):
    """Leaderboard entry showing a member's dynamic winnings for a season."""

    member: MemberResponse
    team: TeamSummary
    total_winnings: int


class PoolResultsResponse(BaseModel):
    """Aggregate results response containing winning games and member standings."""

    season_year: int
    winning_games: list[WinningGameResponse]
    standings: list[StandingItem]


class PotResponse(BaseModel):
    """Current pot amount for a season."""

    season_year: int
    amount: int


class SeasonsResponse(BaseModel):
    """Listing of tracked seasons."""

    current_season: int
    tracked_seasons: list[int]
