"""Season and year helper utilities."""

from datetime import datetime

FIRST_SEASON = 2024


def get_current_season_start_year(now: datetime | None = None) -> int:
    """Returns the starting year of the current NFL season.

    The NFL season transitions on July 1.
    If the current month is July or later, the current year is the season start.
    Otherwise, the previous year is the season start.
    """
    dt = now or datetime.now()
    if dt.month >= 7:
        return dt.year
    return dt.year - 1


def get_season_display_str(season_start_year: int) -> str:
    """Formats season year as '2025-26'."""
    return f"{season_start_year}-{str(season_start_year + 1)[2:]}"


def list_of_tracked_seasons(now: datetime | None = None) -> list[int]:
    """Returns a list of all tracked season start years from 2024 to current."""
    current_year = get_current_season_start_year(now)
    return list(range(FIRST_SEASON, current_year + 1))
