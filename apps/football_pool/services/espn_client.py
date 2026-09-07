"""Asynchronous HTTP client for querying ESPN Scoreboard API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class ESPNAPIError(Exception):
    """Raised when ESPN API request fails or returns invalid data."""

    pass


class ESPNClient:
    """Async client for fetching scoreboard data from ESPN."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0):
        self.base_url = base_url or settings.espn_api_url
        self.timeout = timeout

    async def fetch_scoreboard(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Queries ESPN scoreboard API and returns JSON response."""
        headers = {"Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params or {}, headers=headers)
                response.raise_for_status()
                data = response.json()
                if not data or not isinstance(data, dict):
                    raise ESPNAPIError(f"Empty or non-dictionary response from ESPN: {self.base_url}")
                return data
        except httpx.HTTPError as exc:
            logger.error(f"HTTP error connecting to ESPN API: {exc}")
            raise ESPNAPIError(f"Failed to query ESPN API: {exc}") from exc
        except Exception as exc:
            logger.error(f"Unexpected error querying ESPN API: {exc}")
            raise ESPNAPIError(f"Unexpected error: {exc}") from exc
