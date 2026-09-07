"""Historical results seed script.

Fetches game data from the ESPN Scoreboard API for prior seasons (2024, 2025),
computes pool winners (most/least points, 50-point bonus, playoff wins, Super Bowl),
tracks the rolling pot, and records all WinningGame entries into PostgreSQL.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import async_session_factory, engine
from ..models import Pot, SeasonAssignment, Team, WinningGame, WinningType
from ..services.espn_client import ESPNClient
from ..services.scoreboard import parse_scoreboard_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

POSTSEASON_MAPPING = [
    (1, 19, "Wild Card"),
    (2, 20, "Divisional"),
    (3, 21, "Conference Championship"),
    (5, 22, "Super Bowl"),
]


async def seed_season_results(
    session: AsyncSession,
    client: ESPNClient,
    season_year: int,
    force: bool = False,
) -> int:
    """Seeds historical results and winning games for a single NFL season."""
    logger.info(f"--- Seeding historical results for season {season_year} ---")

    # Check if results already exist
    existing_res = await session.execute(
        select(WinningGame).where(WinningGame.season_year == season_year)
    )
    existing_count = len(existing_res.scalars().all())
    if existing_count > 0 and not force:
        logger.info(
            f"Season {season_year} already has {existing_count} winning games. "
            "Skipping (use --force to overwrite)."
        )
        return existing_count

    if existing_count > 0 and force:
        logger.info(f"Force overwrite requested: deleting {existing_count} existing winning games for {season_year}...")
        from sqlalchemy import delete

        await session.execute(delete(WinningGame).where(WinningGame.season_year == season_year))
        await session.flush()

    # Load teams
    teams_res = await session.execute(select(Team))
    db_teams: dict[str, Team] = {t.abbreviation: t for t in teams_res.scalars().all()}
    if not db_teams:
        raise RuntimeError("No teams found in database. Please run the base historical_seed first.")

    # Load owned teams for this season
    assignments_res = await session.execute(
        select(SeasonAssignment.team_id).where(SeasonAssignment.season_year == season_year)
    )
    owned_team_ids = set(assignments_res.scalars().all())
    logger.info(f"Found {len(owned_team_ids)} owned teams for season {season_year}.")

    # Load or initialize Pot
    pot_res = await session.execute(select(Pot).where(Pot.season_year == season_year))
    pot = pot_res.scalar_one_or_none()
    if not pot:
        pot = Pot(season_year=season_year, amount=10)
        session.add(pot)
        await session.flush()
    else:
        pot.amount = 10

    total_games_created = 0
    winning_games_to_save: list[WinningGame] = []

    # 1. Regular Season (Weeks 1 through 18)
    for week_num in range(1, 19):
        logger.info(f"Fetching {season_year} Regular Season Week {week_num} (current pot: ${pot.amount})...")
        try:
            raw_data = await client.fetch_scoreboard(
                params={"dates": str(season_year), "seasontype": "2", "week": str(week_num)}
            )
        except Exception as exc:
            logger.warning(f"Failed to fetch {season_year} Week {week_num}: {exc}")
            continue

        parsed = parse_scoreboard_data(raw_data, pot_amount=pot.amount)
        w_type = WinningType.MOST if week_num % 2 == 1 else WinningType.LEAST

        played_games = [g for g in parsed.games if not g.is_queued]
        if not played_games:
            continue

        target_score = (
            max(g.max_score for g in played_games)
            if w_type == WinningType.MOST
            else min(g.min_score for g in played_games)
        )

        winner_abbrs: list[str] = []
        for g in played_games:
            if g.home_team_score == target_score:
                winner_abbrs.append(g.home_team.abbreviation)
            if g.away_team_score == target_score:
                winner_abbrs.append(g.away_team.abbreviation)

        payout = pot.amount

        # Update Pot based on whether an owned team won
        has_real_winner = any(
            db_teams[abbr].id in owned_team_ids for abbr in winner_abbrs if abbr in db_teams
        )
        if has_real_winner:
            logger.info(f"  Week {week_num} won by owned team! Winners: {winner_abbrs}, payout: ${payout}. Pot resets to $10.")
            pot.amount = 10
        else:
            pot.amount += 10
            logger.info(f"  Week {week_num} won by unowned team. Winners: {winner_abbrs}. Pot rolls over to ${pot.amount}.")

        for abbr in winner_abbrs:
            if abbr in db_teams:
                winning_games_to_save.append(
                    WinningGame(
                        season_year=season_year,
                        week=week_num,
                        winnings=payout,
                        winning_type=w_type,
                        team_id=db_teams[abbr].id,
                    )
                )

        # Fifty-point bonuses ($50)
        for g in parsed.games:
            for team_summary, score in ((g.home_team, g.home_team_score), (g.away_team, g.away_team_score)):
                if score == 50 and team_summary.abbreviation in db_teams:
                    logger.info(f"  50-point bonus! {team_summary.abbreviation} scored exactly 50 in Week {week_num}!")
                    winning_games_to_save.append(
                        WinningGame(
                            season_year=season_year,
                            week=week_num,
                            winnings=50,
                            winning_type=WinningType.FIFTY,
                            team_id=db_teams[team_summary.abbreviation].id,
                        )
                    )

    # 2. Postseason (Wild Card = W19, Divisional = W20, Conf Champ = W21, Super Bowl = W22)
    for espn_week, display_week, round_name in POSTSEASON_MAPPING:
        logger.info(f"Fetching {season_year} Postseason {round_name} (ESPN week {espn_week}, display W{display_week})...")
        try:
            raw_data = await client.fetch_scoreboard(
                params={"dates": str(season_year), "seasontype": "3", "week": str(espn_week)}
            )
        except Exception as exc:
            logger.warning(f"Failed to fetch {season_year} Postseason week {espn_week}: {exc}")
            continue

        parsed = parse_scoreboard_data(raw_data, pot_amount=pot.amount)
        is_sb = espn_week == 5
        w_type = WinningType.SUPER_BOWL if is_sb else WinningType.PLAYOFF
        payout = 25 if is_sb else 10

        winners = [g.winning_team_abbr for g in parsed.games if g.is_final and g.winning_team_abbr]
        for abbr in winners:
            if abbr in db_teams:
                winning_games_to_save.append(
                    WinningGame(
                        season_year=season_year,
                        week=display_week,
                        winnings=payout,
                        winning_type=w_type,
                        team_id=db_teams[abbr].id,
                    )
                )

        # 50-point bonus in postseason
        for g in parsed.games:
            for team_summary, score in ((g.home_team, g.home_team_score), (g.away_team, g.away_team_score)):
                if score == 50 and team_summary.abbreviation in db_teams:
                    winning_games_to_save.append(
                        WinningGame(
                            season_year=season_year,
                            week=display_week,
                            winnings=50,
                            winning_type=WinningType.FIFTY,
                            team_id=db_teams[team_summary.abbreviation].id,
                        )
                    )

    session.add_all(winning_games_to_save)
    await session.commit()
    total_games_created = len(winning_games_to_save)
    logger.info(f"Successfully saved {total_games_created} winning games for season {season_year}.")
    return total_games_created


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed historical results for football-pool seasons.")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2024, 2025],
        help="Season years to seed (default: 2024 2025)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-seed by overwriting existing winning games for the given years",
    )
    args = parser.parse_args()

    client = ESPNClient()
    async with async_session_factory() as session:
        for year in args.years:
            await seed_season_results(session, client, year, force=args.force)

    await engine.dispose()
    logger.info("All historical results seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
