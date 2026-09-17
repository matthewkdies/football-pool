"""Weekly Tuesday scoring resolution scheduler service."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..database import async_session_factory
from .espn_client import ESPNAPIError, ESPNClient
from .poller import fetch_current_pot_amount
from .results import resolve_weekly_results
from .scoreboard import parse_scoreboard_data, scoreboard_cache

logger = logging.getLogger(__name__)

EST = ZoneInfo("US/Eastern")


def calculate_seconds_until_next_tuesday_1am(now: datetime | None = None) -> float:
    """Calculates the number of seconds until the next Tuesday at 1:00 AM US/Eastern.

    Args:
        now: Optional reference datetime. Defaults to current UTC time.

    Returns:
        Number of seconds until the next Tuesday at 1:00 AM US/Eastern.
    """
    eastern = EST
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    now_eastern = now_utc.astimezone(eastern)

    # Tuesday is weekday 1 (Monday is 0, Sunday is 6)
    days_ahead = (1 - now_eastern.weekday()) % 7
    target_time = time(hour=1, minute=0, second=0)

    # If today is Tuesday, check if 1:00 AM has already arrived or passed
    if days_ahead == 0 and now_eastern.time() >= target_time:
        days_ahead = 7

    target_date = now_eastern.date() + timedelta(days=days_ahead)
    target_eastern = datetime.combine(target_date, target_time, tzinfo=eastern)
    target_utc = target_eastern.astimezone(timezone.utc)

    seconds = (target_utc - now_utc).total_seconds()
    if seconds <= 0:
        target_date = target_date + timedelta(days=7)
        target_eastern = datetime.combine(target_date, target_time, tzinfo=eastern)
        target_utc = target_eastern.astimezone(timezone.utc)
        seconds = (target_utc - now_utc).total_seconds()

    return max(0.0, seconds)


async def execute_tuesday_resolution(
    client: ESPNClient | None = None,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> bool:
    """Executes the weekly Tuesday scoring resolution.

    Fetches current scoreboard data, checks that games are completed, and records
    winners and pot updates via resolve_weekly_results.

    Args:
        client: Optional ESPNClient instance.
        session_factory: Optional SQLAlchemy async session factory.

    Returns:
        True if a retry is recommended (e.g. games still active or ESPN error), False on success.
    """
    espn_client = client or ESPNClient()

    try:
        raw_data = await espn_client.fetch_scoreboard()
    except ESPNAPIError as exc:
        logger.warning("ESPN API fetch failed during Tuesday scoring resolution: %s", exc)
        return True
    except Exception as exc:
        logger.error("Unexpected error fetching scoreboard for Tuesday resolution: %s", exc, exc_info=True)
        return True

    try:
        cached = await scoreboard_cache.get()
        season_year = cached.season_year if cached else datetime.now(timezone.utc).year
        pot_amount = await fetch_current_pot_amount(season_year)
        parsed_week = parse_scoreboard_data(raw_data, pot_amount=pot_amount)
    except Exception as exc:
        logger.error("Failed to parse scoreboard data for Tuesday resolution: %s", exc, exc_info=True)
        return True

    if not parsed_week.games:
        logger.warning(
            "No games found in scoreboard data for season %s week %s.",
            parsed_week.season_year,
            parsed_week.week,
        )
        return False

    # Check if any games are still in progress or at halftime
    if any(g.is_in_progress or g.is_in_halftime for g in parsed_week.games):
        logger.warning(
            "Games are still in progress for season %s week %s. Postponing Tuesday scoring resolution.",
            parsed_week.season_year,
            parsed_week.week,
        )
        return True

    factory = session_factory or async_session_factory
    try:
        async with factory() as session:
            winning_games = await resolve_weekly_results(session, parsed_week)
            logger.info(
                "Tuesday scoring resolution completed for season %s, week %s: recorded %d winning records.",
                parsed_week.season_year,
                parsed_week.week,
                len(winning_games),
            )
        # Update cache so pot and standings reflect immediately
        scoreboard_cache.trigger_refresh()
        return False
    except Exception as exc:
        logger.error("Failed executing resolve_weekly_results for Tuesday resolution: %s", exc, exc_info=True)
        return True


async def tuesday_scoring_loop(
    stop_event: asyncio.Event,
    client: ESPNClient | None = None,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
    retry_delay_seconds: float = 900.0,
) -> None:
    """Background loop that executes weekly winner resolution every Tuesday at 1:00 AM US/Eastern.

    Runs until stop_event is set.

    Args:
        stop_event: Asyncio event signaling the loop to terminate.
        client: Optional ESPNClient instance.
        session_factory: Optional SQLAlchemy async session factory.
        retry_delay_seconds: Seconds to wait before retrying if games are still active or error occurs.
    """
    espn_client = client or ESPNClient()
    logger.info("Starting Tuesday scoring resolution scheduler loop...")

    while not stop_event.is_set():
        wait_seconds = calculate_seconds_until_next_tuesday_1am()
        logger.info(
            "Next Tuesday scoring resolution scheduled in %.2f hours (at 1:00 AM US/Eastern).",
            wait_seconds / 3600,
        )

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=wait_seconds)
            # If wait_for returns without TimeoutError, stop_event was set
            break
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            logger.info("Tuesday scoring scheduler cancelled.")
            break

        if stop_event.is_set():
            break

        logger.info("Tuesday 1:00 AM US/Eastern reached. Executing weekly scoring resolution...")
        retry_needed = await execute_tuesday_resolution(client=espn_client, session_factory=session_factory)

        while retry_needed and not stop_event.is_set():
            logger.info(
                "Weekly resolution requested retry. Sleeping %.0f seconds before re-checking.",
                retry_delay_seconds,
            )
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=retry_delay_seconds)
                break  # stop_event was set
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                break

            if stop_event.is_set():
                break

            retry_needed = await execute_tuesday_resolution(client=espn_client, session_factory=session_factory)

    logger.info("Tuesday scoring resolution scheduler loop stopped.")
