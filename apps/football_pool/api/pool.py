"""Pool information, assignments, results, and standings API router."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Member, Pot, SeasonAssignment, Team, WinningGame
from ..schemas.auth import MemberResponse
from ..schemas.pool import (
    PoolResultsResponse,
    PotResponse,
    SeasonAssignmentResponse,
    SeasonsResponse,
    StandingItem,
    WinningGameResponse,
)
from ..services.scoreboard import get_team_summary
from ..utils.seasons import get_current_season_start_year, list_of_tracked_seasons

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pool", tags=["Pool"])


@router.get("/seasons", response_model=SeasonsResponse)
async def get_seasons() -> SeasonsResponse:
    """Returns the current season and all tracked seasons."""
    cur_year = get_current_season_start_year()
    tracked = list_of_tracked_seasons()
    return SeasonsResponse(current_season=cur_year, tracked_seasons=tracked)


@router.get("/pot", response_model=PotResponse)
async def get_pot(
    season_year: int | None = Query(default=None, description="Season start year (e.g. 2025)"),
    db: AsyncSession = Depends(get_db),
) -> PotResponse:
    """Returns the pot amount for the requested season year."""
    target_year = season_year or get_current_season_start_year()
    result = await db.execute(select(Pot).where(Pot.season_year == target_year))
    pot = result.scalar_one_or_none()
    amount = pot.amount if pot else 10
    return PotResponse(season_year=target_year, amount=amount)


@router.get("/assignments", response_model=list[SeasonAssignmentResponse])
async def get_assignments(
    season_year: int | None = Query(default=None, description="Season start year (e.g. 2025)"),
    db: AsyncSession = Depends(get_db),
) -> list[SeasonAssignmentResponse]:
    """Returns the team assignments for a given season year, ordered by team city and name."""
    target_year = season_year or get_current_season_start_year()

    query = (
        select(SeasonAssignment)
        .options(selectinload(SeasonAssignment.member), selectinload(SeasonAssignment.team))
        .join(Team, SeasonAssignment.team_id == Team.id)
        .where(SeasonAssignment.season_year == target_year)
        .order_by(Team.city.asc(), Team.name.asc())
    )
    result = await db.execute(query)
    assignments = result.scalars().all()

    return [
        SeasonAssignmentResponse(
            id=a.id,
            season_year=a.season_year,
            member=MemberResponse(
                id=a.member.id,
                first_name=a.member.first_name,
                last_name=a.member.last_name,
                full_name=a.member.full_name,
                created_at=a.member.created_at,
            ),
            team=get_team_summary(a.team.abbreviation),
        )
        for a in assignments
    ]


@router.get("/results", response_model=PoolResultsResponse)
async def get_results(
    season_year: int | None = Query(default=None, description="Season start year (e.g. 2025)"),
    db: AsyncSession = Depends(get_db),
) -> PoolResultsResponse:
    """Returns historical winning games and member standings for a given season."""
    target_year = season_year or get_current_season_start_year()

    # 1. Fetch winning games
    wg_query = (
        select(WinningGame)
        .options(selectinload(WinningGame.team))
        .where(WinningGame.season_year == target_year)
        .order_by(WinningGame.week.asc(), WinningGame.id.asc())
    )
    wg_result = await db.execute(wg_query)
    winning_games_raw = list(wg_result.scalars().all())

    # Map team_id to member full name for this season
    assignments_query = (
        select(SeasonAssignment)
        .options(selectinload(SeasonAssignment.member))
        .where(SeasonAssignment.season_year == target_year)
    )
    assignments_res = await db.execute(assignments_query)
    team_to_owner = {a.team_id: a.member.full_name for a in assignments_res.scalars().all()}

    winning_games_resp: list[WinningGameResponse] = []
    for wg in winning_games_raw:
        owner_name = team_to_owner.get(wg.team_id, "No one (Unclaimed)")
        winning_games_resp.append(
            WinningGameResponse(
                id=wg.id,
                season_year=wg.season_year,
                week=wg.week,
                winnings=wg.winnings,
                winning_type=wg.winning_type.display_name,
                team=get_team_summary(wg.team.abbreviation),
                winning_owner_name=owner_name,
            )
        )

    # 2. Dynamic standings aggregation
    # Query all assigned members and sum their winning games for this season
    standings_query = (
        select(
            Member,
            Team,
            func.coalesce(func.sum(WinningGame.winnings), 0).label("total_winnings"),
        )
        .join(SeasonAssignment, SeasonAssignment.member_id == Member.id)
        .join(Team, SeasonAssignment.team_id == Team.id)
        .outerjoin(
            WinningGame,
            (WinningGame.team_id == SeasonAssignment.team_id)
            & (WinningGame.season_year == SeasonAssignment.season_year),
        )
        .where(SeasonAssignment.season_year == target_year)
        .group_by(Member.id, Team.id)
        .order_by(func.coalesce(func.sum(WinningGame.winnings), 0).desc(), Member.last_name.asc())
    )
    standings_result = await db.execute(standings_query)
    standings_rows = standings_result.all()

    standings: list[StandingItem] = [
        StandingItem(
            member=MemberResponse(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                full_name=member.full_name,
                created_at=member.created_at,
            ),
            team=get_team_summary(team.abbreviation),
            total_winnings=int(total_winnings),
        )
        for member, team, total_winnings in standings_rows
    ]

    return PoolResultsResponse(
        season_year=target_year,
        winning_games=winning_games_resp,
        standings=standings,
    )
