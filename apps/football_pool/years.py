"""Functionality related to years and the current season, for history tracking purposes."""

from datetime import datetime


def get_current_year() -> int:
    """Gets the current year."""
    return datetime.now().year


def get_current_season_start_year() -> int:
    """An NFL season spans two years. This returns the year in which the current season began.

    The NFL season transitions in the ESPN API on July 1.
    If the current month is that date or later, the current year is correct.
    If it's earlier in the year than that, the previous year is correct.
    """
    now = datetime.now()
    cur_year = get_current_year()
    if now.month >= 7:
        return cur_year
    return cur_year - 1


def get_season_str(season_start_year: int) -> str:
    """Represents the current season via years.

    Format: {<season_start_year>}-{<season_end_year>[2:]}
    Example: "2025-26"
    """
    return f"{season_start_year!s}-{str(season_start_year + 1)[2:]}"
