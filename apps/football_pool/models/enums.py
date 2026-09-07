"""Enumerations used in football-pool domain models."""

from enum import StrEnum


class Conference(StrEnum):
    """The NFL conferences."""

    AFC = "AFC"
    NFC = "NFC"


class Division(StrEnum):
    """The NFL divisions within conferences."""

    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"


class WinningType(StrEnum):
    """The categories in which a team generates pool winnings."""

    MOST = "MOST"
    LEAST = "LEAST"
    FIFTY = "FIFTY"
    PLAYOFF = "PLAYOFF"
    SUPER_BOWL = "SUPER_BOWL"

    @property
    def display_name(self) -> str:
        """Formatted human-readable string (e.g. 'Super Bowl')."""
        return self.value.replace("_", " ").title()


class SeasonType(StrEnum):
    """NFL season types."""

    PRESEASON = "PRESEASON"
    REGULAR_SEASON = "REGULAR_SEASON"
    POSTSEASON = "POSTSEASON"

    @classmethod
    def from_espn_type(cls, value: int | str) -> "SeasonType":
        """Maps ESPN API season type numeric code to enum."""
        mapping = {1: cls.PRESEASON, 2: cls.REGULAR_SEASON, 3: cls.POSTSEASON}
        if isinstance(value, int) and value in mapping:
            return mapping[value]
        if isinstance(value, str) and value.isdigit() and int(value) in mapping:
            return mapping[int(value)]
        val_str = str(value).upper()
        for item in cls:
            if item.value == val_str:
                return item
        return cls.REGULAR_SEASON


class GameStatus(StrEnum):
    """Game status indicators."""

    SCHEDULED = "STATUS_SCHEDULED"
    IN_PROGRESS = "STATUS_IN_PROGRESS"
    HALFTIME = "STATUS_HALFTIME"
    FINAL = "STATUS_FINAL"

    @classmethod
    def from_espn_status(cls, value: str) -> "GameStatus":
        """Safely parses game status string from ESPN."""
        val = value.upper()
        for item in cls:
            if item.value == val:
                return item
        if "FINAL" in val:
            return cls.FINAL
        if "IN_PROGRESS" in val or "HALFTIME" in val:
            return cls.IN_PROGRESS
        return cls.SCHEDULED
