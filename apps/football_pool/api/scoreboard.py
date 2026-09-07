"""Scoreboard API router for live game data."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from ..schemas.scoreboard import ScoreboardWeek
from ..services.espn_client import ESPNClient
from ..services.poller import run_poller_cycle
from ..services.scoreboard import scoreboard_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Scoreboard"])


@router.get("/scoreboard", response_model=ScoreboardWeek)
async def get_scoreboard() -> ScoreboardWeek:
    """Returns the latest parsed scoreboard and current pool winning teams.

    Served from memory in sub-millisecond time. If uninitialized, fetches immediately.
    """
    cached = await scoreboard_cache.get()
    if cached:
        return cached

    # Cache is empty (e.g. initial boot before first cycle completed)
    logger.info("Scoreboard cache empty, executing initial fetch...")
    client = ESPNClient()
    await run_poller_cycle(client, scoreboard_cache)
    cached = await scoreboard_cache.get()

    if not cached:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scoreboard data is currently unavailable.",
        )
    return cached


@router.post("/scoreboard/refresh", response_model=ScoreboardWeek)
async def refresh_scoreboard() -> ScoreboardWeek:
    """Forces an immediate refresh of the scoreboard from the ESPN API."""
    logger.info("Manual scoreboard refresh triggered via API endpoint.")
    client = ESPNClient()
    await run_poller_cycle(client, scoreboard_cache)
    cached = await scoreboard_cache.get()
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to refresh scoreboard data from ESPN.",
        )
    return cached
