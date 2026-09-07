"""Adaptive background polling loop for ESPN scoreboard data."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from ..config import settings
from ..database import async_session_factory
from ..models.pot import Pot
from .espn_client import ESPNAPIError, ESPNClient
from .scoreboard import ScoreboardCache, parse_scoreboard_data

logger = logging.getLogger(__name__)


def calculate_poll_interval(week_data, now: datetime | None = None) -> int:
    """Calculates the adaptive wait time in seconds based on game activity."""
    if not week_data:
        return settings.poll_interval_active_seconds

    if week_data.has_active_games:
        return settings.poll_interval_active_seconds

    cur_time = now or datetime.now(timezone.utc)

    # Check if any game starts in the next 2 hours or today
    for game in week_data.games:
        if game.is_queued:
            diff_seconds = (game.gametime - cur_time).total_seconds()
            if 0 <= diff_seconds <= 7200:  # within 2 hours
                return settings.poll_interval_upcoming_seconds

    # If in regular or postseason, idle wait
    if not week_data.is_preseason:
        return settings.poll_interval_idle_seconds

    # Off-season fallback
    return settings.poll_interval_offseason_seconds


async def fetch_current_pot_amount(season_year: int) -> int:
    """Reads current pot amount from database."""
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Pot).where(Pot.season_year == season_year))
            pot = result.scalar_one_or_none()
            if pot:
                return pot.amount
    except Exception as exc:
        logger.warning(f"Could not read pot amount from database, using default: {exc}")
    return 10


async def run_poller_cycle(client: ESPNClient, cache: ScoreboardCache) -> int:
    """Executes a single poll of the ESPN API, updates the cache, and returns next interval."""
    try:
        raw_data = await client.fetch_scoreboard()
        cached = await cache.get()
        season_year = cached.season_year if cached else datetime.now(timezone.utc).year
        pot_amount = await fetch_current_pot_amount(season_year)
        parsed_week = parse_scoreboard_data(raw_data, pot_amount=pot_amount)
        await cache.set(parsed_week)
        logger.info(
            f"Updated scoreboard cache for Week {parsed_week.week} "
            f"({len(parsed_week.games)} games, {len(parsed_week.pool_winning_team_abbrs)} pool winners)"
        )
        return calculate_poll_interval(parsed_week)
    except ESPNAPIError as exc:
        logger.warning(f"ESPN API poll failed: {exc}. Retrying in 30 seconds.")
        return 30
    except Exception as exc:
        logger.error(f"Unexpected error in scoreboard poller cycle: {exc}", exc_info=True)
        return 30


async def scoreboard_polling_loop(
    cache: ScoreboardCache,
    stop_event: asyncio.Event,
    client: ESPNClient | None = None,
) -> None:
    """Long-running background task that polls ESPN adaptively until stop_event is set."""
    espn_client = client or ESPNClient()
    logger.info("Starting adaptive ESPN scoreboard poller loop...")

    while not stop_event.is_set():
        interval = await run_poller_cycle(espn_client, cache)

        try:
            # Wait for either timeout or manual refresh trigger or stop_event
            wait_task = asyncio.create_task(cache.refresh_event.wait())
            stop_task = asyncio.create_task(stop_event.wait())

            done, pending = await asyncio.wait(
                [wait_task, stop_task],
                timeout=interval,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for p in pending:
                p.cancel()

            if stop_event.is_set():
                break

            if cache.refresh_event.is_set():
                cache.refresh_event.clear()
                logger.info("Manual scoreboard refresh triggered. Running immediate cycle.")

        except asyncio.CancelledError:
            logger.info("Scoreboard poller cancelled.")
            break
        except Exception as exc:
            logger.error(f"Poller wait loop error: {exc}")

    logger.info("Adaptive ESPN scoreboard poller loop stopped.")
