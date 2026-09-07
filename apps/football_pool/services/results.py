"""Weekly scoring resolution and rollover pot service."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Pot, SeasonAssignment, Team, WinningGame, WinningType
from ..schemas.scoreboard import ScoreboardWeek

logger = logging.getLogger(__name__)


async def resolve_weekly_results(
    session: AsyncSession,
    scoreboard_week: ScoreboardWeek,
    force: bool = False,
) -> list[WinningGame]:
    """Computes and records weekly winners and updates the rollover pot idempotently."""
    season_year = scoreboard_week.season_year
    week_num = scoreboard_week.week

    logger.info(f"Resolving weekly results for season {season_year}, week {week_num}...")

    # 1. Idempotency check: don't duplicate awards for the same week unless forced
    existing_result = await session.execute(
        select(WinningGame).where(
            WinningGame.season_year == season_year,
            WinningGame.week == week_num,
        )
    )
    existing_games = list(existing_result.scalars().all())
    if existing_games and not force:
        logger.info(
            f"Results for season {season_year} week {week_num} already exist ({len(existing_games)} records). Skipping."
        )
        return existing_games

    # Pro Bowl week has no winners
    if scoreboard_week.is_pro_bowl:
        logger.info("Pro Bowl week - no pool winners to record.")
        return []

    # 2. Get or create the Pot record
    pot_result = await session.execute(select(Pot).where(Pot.season_year == season_year))
    pot = pot_result.scalar_one_or_none()
    if not pot:
        pot = Pot(season_year=season_year, amount=10)
        session.add(pot)
        await session.flush()

    # 3. Load all teams from DB keyed by abbreviation
    teams_result = await session.execute(select(Team))
    db_teams = {t.abbreviation: t for t in teams_result.scalars().all()}

    # 4. Load owned team IDs for this season
    assignments_result = await session.execute(
        select(SeasonAssignment.team_id).where(SeasonAssignment.season_year == season_year)
    )
    owned_team_ids = set(assignments_result.scalars().all())

    # 5. Determine winners and payouts
    winning_games_to_create: list[WinningGame] = []

    if scoreboard_week.is_super_bowl:
        payout = 25
        w_type = WinningType.SUPER_BOWL
        winner_abbrs = [g.winning_team_abbr for g in scoreboard_week.games if g.is_final and g.winning_team_abbr]
    elif scoreboard_week.is_postseason:
        payout = 15
        w_type = WinningType.PLAYOFF
        winner_abbrs = [g.winning_team_abbr for g in scoreboard_week.games if g.is_final and g.winning_team_abbr]
    else:
        # Regular Season
        payout = pot.amount
        w_type = scoreboard_week.winning_type
        # Extract most or least winners
        played_games = [g for g in scoreboard_week.games if not g.is_queued]
        if played_games:
            target_score = (
                max(g.max_score for g in played_games)
                if w_type == WinningType.MOST
                else min(g.min_score for g in played_games)
            )
            winner_abbrs = []
            for g in played_games:
                if g.home_team_score == target_score:
                    winner_abbrs.append(g.home_team.abbreviation)
                if g.away_team_score == target_score:
                    winner_abbrs.append(g.away_team.abbreviation)
        else:
            winner_abbrs = []

        # Update Pot based on whether any pool member owns the winning team
        has_real_winner = any(db_teams[abbr].id in owned_team_ids for abbr in winner_abbrs if abbr in db_teams)
        if has_real_winner:
            pot.amount = 10
            logger.info(f"Pool member won regular season week {week_num}! Resetting pot to $10.")
        elif not scoreboard_week.is_preseason:
            pot.amount += 10
            logger.info(f"No pool member won regular season week {week_num}. Incrementing pot to ${pot.amount}.")

    # Create WinningGame records for weekly winners
    for abbr in winner_abbrs:
        if abbr in db_teams:
            team = db_teams[abbr]
            winning_games_to_create.append(
                WinningGame(
                    season_year=season_year,
                    week=week_num,
                    winnings=payout,
                    winning_type=w_type,
                    team_id=team.id,
                )
            )

    # 6. Fifty-point scorers ($50 bonus)
    for g in scoreboard_week.games:
        for team_summary, score in ((g.home_team, g.home_team_score), (g.away_team, g.away_team_score)):
            if score == 50 and team_summary.abbreviation in db_teams:
                team = db_teams[team_summary.abbreviation]
                winning_games_to_create.append(
                    WinningGame(
                        season_year=season_year,
                        week=week_num,
                        winnings=50,
                        winning_type=WinningType.FIFTY,
                        team_id=team.id,
                    )
                )

    if winning_games_to_create:
        session.add_all(winning_games_to_create)

    await session.commit()
    logger.info(f"Successfully recorded {len(winning_games_to_create)} winning games for week {week_num}.")
    return winning_games_to_create
