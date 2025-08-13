from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Callable

from flask import current_app
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from pytz import timezone

from ..models import Team, WinningType
from .exceptions import GameNotOverError, GameTiedError

EST = timezone("US/Eastern")


def find_teams_with_most_points(current_week: CurrentWeek) -> list[Team]:
    """Finds the teams that scored the most points in the current week.

    Args:
        current_week (CurrentWeek): The CurrentWeek containing scores of Game objects.

    Returns:
        list[Team]: A list of Team objects that scored the most points.
    """
    not_queued_games = [game for game in current_week.games if game.status != GameStatus.QUEUED]
    if not not_queued_games:
        most_points = 0
    else:
        most_points = max(game.max_score for game in not_queued_games)
    current_app.logger.debug("The most points scored in the week is %s.", most_points)
    winning_teams: list[Team] = []
    for game in current_week.games:
        if game.home_team_score == most_points:
            winning_teams.append(game.home_team)
        if game.away_team_score == most_points:
            winning_teams.append(game.away_team)
    current_app.logger.debug("%s team(s) scored the most points this week.", len(winning_teams))
    return winning_teams


def find_teams_with_least_points(current_week: CurrentWeek) -> list[Team]:
    """Finds the teams that scored the least points in the current week.

    Args:
        current_week (CurrentWeek): The CurrentWeek containing scores of Game objects.

    Returns:
        list[Team]: A list of Team objects that scored the least points.
    """
    not_queued_games = [game for game in current_week.games if game.status != GameStatus.QUEUED]
    if not not_queued_games:
        least_points = 0
    else:
        least_points = min(game.min_score for game in not_queued_games)
    current_app.logger.debug("The least points scored in the week is %s.", least_points)
    winning_teams: list[Team] = []
    for game in current_week.games:
        if game.home_team_score == least_points:
            winning_teams.append(game.home_team)
        if game.away_team_score == least_points:
            winning_teams.append(game.away_team)
    current_app.logger.debug("%s team(s) scored the least points this week.", len(winning_teams))
    return winning_teams


def find_teams_with_fifty_points(current_week: CurrentWeek) -> list[Team]:
    """Finds the teams that scored fifty in the current week.

    Args:
        current_week (CurrentWeek): The CurrentWeek containing scores of Game objects.

    Returns:
        list[Team]: A list of Team objects that scored fifty points.
    """
    winning_teams: list[Team] = []
    for game in current_week.games:
        if game.home_team_score == 50:
            winning_teams.append(game.home_team)
        if game.away_team_score == 50:
            winning_teams.append(game.away_team)
    current_app.logger.debug("%s team(s) scored fifty points this week.", len(winning_teams))
    return winning_teams


WINNING_TEAM_FUNC_MAP: dict[WinningType, Callable[[CurrentWeek], list[Team]]] = {
    WinningType.MOST: find_teams_with_most_points,
    WinningType.LEAST: find_teams_with_least_points,
}
"""Maps the MOST and LEAST WinningTypes to functions to retrieve winners for the current week."""


class SeasonType(StrEnum):
    """An Enum class that handles the type of season (pre, regular, post)."""

    PRESEASON = "PRESEASON"
    REGULAR_SEASON = "REGULAR_SEASON"
    POSTSEASON = "POSTSEASON"

    @classmethod
    def _missing_(cls, value: str | int) -> SeasonType:  # pyright: ignore[reportIncompatibleMethodOverride]
        if value == 1:
            return SeasonType.PRESEASON
        if value == 2:
            return SeasonType.REGULAR_SEASON
        if value == 3:
            return SeasonType.POSTSEASON
        raise ValueError


class GameStatus(StrEnum):
    """An Enum class that handles the status of games."""

    QUEUED = "STATUS_SCHEDULED"
    IN_PROGRESS = "STATUS_IN_PROGRESS"
    HALFTIME = "STATUS_HALFTIME"
    FINAL = "STATUS_FINAL"

    @classmethod
    def _missing_(cls, value: str) -> GameStatus:  # pyright: ignore[reportIncompatibleMethodOverride]
        value = value.upper()
        for member in cls:
            if member.value == value:
                return member

        # fallback to returning the in progress status
        # there are some weird statuses that I have seen only in passing
        # I know for a fact that STATUS_SCHEDULED and STATUS_FINAL are valid, so anything
        # in between probably means the game is being played lol
        return GameStatus.IN_PROGRESS


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Game:
    """Contains all of the information about a single game currently being played.

    Is *not* a database object, these aren't stored over time.
    When a family member does win, this information is stored in the `WinningGame` class.
    """

    home_team: Team
    home_team_score: int
    away_team: Team
    away_team_score: int
    espn_url: str
    gametime: datetime
    status: GameStatus
    display_clock: str | None
    quarter: int | None

    @staticmethod
    def get_all_from_events_list(events_list: list[dict]) -> list[Game]:
        games: list[Game] = []
        for event in events_list:
            status = GameStatus(event["status"]["type"]["name"])
            if status == GameStatus.QUEUED:
                display_clock = None
                quarter = None
            else:
                display_clock = event["status"]["displayClock"]
                quarter = int(event["status"]["period"])
            home_idx = 0 if event["competitions"][0]["competitors"][0]["homeAway"] == 0 else 1
            away_idx = 1 - home_idx
            home_dict = event["competitions"][0]["competitors"][home_idx]
            away_dict = event["competitions"][0]["competitors"][away_idx]
            gametime: datetime = datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ")
            gametime = gametime.astimezone(EST)
            games.append(
                Game(
                    home_team=Team.from_abbr(home_dict["team"]["abbreviation"]),
                    home_team_score=int(home_dict["score"]),
                    away_team=Team.from_abbr(away_dict["team"]["abbreviation"]),
                    away_team_score=int(away_dict["score"]),
                    espn_url=event["links"][0]["href"],
                    gametime=gametime,
                    status=status,
                    display_clock=display_clock,
                    quarter=quarter,
                )
            )
        return games

    @property
    def is_in_progress(self) -> bool:
        """Returns True if the game is in progress, otherwise returns False.

        Returns:
            bool: Whether the game is in progress.
        """
        return self.status == GameStatus.IN_PROGRESS

    @property
    def is_in_halftime(self) -> bool:
        """Returns True if the game is in halftime, otherwise returns False.

        Returns:
            bool: Whether the game is in halftime.
        """
        return self.status == GameStatus.HALFTIME

    @property
    def is_final(self) -> bool:
        """Returns True if the game is final, otherwise returns False.

        Returns:
            bool: Whether the game is final.
        """
        return self.status == GameStatus.FINAL

    @property
    def is_queued(self) -> bool:
        """Returns True if the game is queued, otherwise returns False.

        Returns:
            bool: Whether the game is queued.
        """
        return self.status == GameStatus.QUEUED

    @property
    def date_str(self) -> str:
        """Gets the start date of the game as a string.

        Returns:
            str: The start date of the game.
        """
        return self.gametime.strftime("%b %-d")

    @property
    def start_time_str(self) -> str:
        """Gets the start time of the game as a string.

        Returns:
            str: The start time of the game.
        """
        return self.gametime.strftime("%-I:%M %p")

    @property
    def max_score(self) -> int:
        """Returns the max score from the game.

        Returns:
            int: The maximum score from the game.
        """
        higher_score = max(self.home_team_score, self.away_team_score)
        current_app.logger.debug(
            "The higher score from the %s@%s game is %s.",
            self.away_team.abbreviation,
            self.home_team.abbreviation,
            higher_score,
        )
        return higher_score

    @property
    def min_score(self) -> int:
        """Returns the minimum score from the game.

        Returns:
            int: The minimum score from the game.
        """
        lower_or_equal_score = min(self.home_team_score, self.away_team_score)
        current_app.logger.debug(
            "The lower (or equal) points scored in the %s@%s game is %s.",
            self.away_team.abbreviation,
            self.home_team.abbreviation,
            lower_or_equal_score,
        )
        return lower_or_equal_score

    @property
    def winning_team(self) -> Team:
        """Computes the game's winner. Should only be called when the game is not tied!

        Raises:
            GameNotOverError: If the game isn't over yet.
            GameTiedError: If the game is tied.

        Returns:
            Team: The team that won the game.
        """
        if self.display_clock != "0:00":
            raise GameNotOverError()
        if self.home_team_score == self.away_team_score:
            raise GameTiedError()
        if self.home_team_score > self.away_team_score:
            current_app.logger.debug("Winning team is %s.", self.home_team.abbreviation)
            return self.home_team
        current_app.logger.debug("Winning team is %s.", self.away_team.abbreviation)
        return self.away_team


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class CurrentWeek:
    """Contains all of the information about the current week of games.

    Is *not* a database object.
    """

    week: int
    games: list[Game]
    season_type: SeasonType

    @property
    def winning_type(self) -> WinningType:
        """Finds what WinningType corresponds to the current week.

        - `number` % 2 == 1 -> `number` is odd.
        - Odd weeks are most weeks.
        - Even weeks are least weeks.
        """
        if self.is_super_bowl:
            current_app.logger.debug("It's Super Bowl week! The winner is the Super Bowl team's owner.")
            return WinningType.SUPER_BOWL
        if self.is_postseason:
            current_app.logger.debug("It's the postseason. The winners are the winning team's owners.")
            return WinningType.PLAYOFF
        if self.week % 2:
            # it's an odd week
            current_app.logger.debug("It's an ODD week, so it's a MOST points week.")
            return WinningType.MOST
        # it's an even week
        current_app.logger.debug("It's an EVEN week, so it's a LEAST points week.")
        return WinningType.LEAST

    def get_weekly_winning_teams(self) -> list[Team]:
        """Gets the most or least winners for the current week.

        Returns:
            list[Team]: A list of winning teams.
        """
        if not self.is_regular_season:
            current_app.logger.debug(
                "It's not a regular season week, so there are no most or least winners. Returning empty list."
            )
            return []
        return WINNING_TEAM_FUNC_MAP[self.winning_type](self)

    def get_fifty_point_winners(self) -> list[Team]:
        """Gets the fifty point-scoring teams for the current week.

        Returns:
            list[Team]: A list of winning teams.
        """
        return find_teams_with_fifty_points(self)

    @property
    def is_preseason(self) -> bool:
        """Returns whether the current week is a preseason week or not.

        Returns:
            bool: Whether the current week is a preseason game.
        """
        is_preseason = self.season_type == SeasonType.PRESEASON
        current_app.logger.debug("is_preseason=%s", is_preseason)
        return is_preseason

    @property
    def is_postseason(self) -> bool:
        """Returns whether the current week is a postseason week or not.

        There are 18 weeks in the regular season, then the postseason goes:
        1 -> Wild Card
        2 -> Divisional
        3 -> Conference Champs
        4 -> Pro Bowl
        5 -> Super Bowl

        Returns:
            bool: Whether the current week is a postseason game.
        """
        is_postseason = self.season_type == SeasonType.POSTSEASON
        current_app.logger.debug("is_postseason=%s", is_postseason)
        return is_postseason

    @property
    def is_pro_bowl(self) -> bool:
        """Returns whether the current week is Pro Bowl week.

        There are 18 weeks in the regular season, then the postseason goes:
        1 -> Wild Card
        2 -> Divisional
        3 -> Conference Champs
        4 -> Pro Bowl
        5 -> Super Bowl

        Returns:
            bool: Whether the current week is Pro Bowl week.
        """
        is_pro_bowl = self.season_type == SeasonType.POSTSEASON and self.week == 4
        current_app.logger.debug("is_pro_bowl=%s", is_pro_bowl)
        return is_pro_bowl

    @property
    def is_super_bowl(self) -> bool:
        """Returns whether the current week is Super Bowl week.

        There are 18 weeks in the regular season, then the postseason goes:
        1 -> Wild Card
        2 -> Divisional
        3 -> Conference Champs
        4 -> Pro Bowl
        5 -> Super Bowl

        Returns:
            bool: Whether the current week is Super Bowl week.
        """
        is_super_bowl = self.season_type == SeasonType.POSTSEASON and self.week == 5
        current_app.logger.debug("is_super_bowl=%s", is_super_bowl)
        return is_super_bowl

    @property
    def is_regular_season(self) -> bool:
        """Whether the current week is a regular season week."""
        return not self.is_preseason and not self.is_postseason

    def get_postseason_winners(self) -> list[Team]:
        """Gets the postseason winners, if the week if a postseason week.

        Returns:
            list[Team]: The list of Teams that won a postseason game this week.
        """
        if not self.is_postseason:
            current_app.logger.debug("It's not the postseason. Returning an empty list.")
            return []
        winning_teams: list[Team] = []
        for game in self.games:
            try:
                winner = game.winning_team
            except GameNotOverError:
                current_app.logger.debug(
                    "%s @ %s is not over. Skipping.",
                    game.away_team.abbreviation,
                    game.home_team.abbreviation,
                )
                continue
            current_app.logger.debug(
                "%s won a postseason game! Congrats, unless they're an AFCN team that isn't the Steelers.",
                winner.abbreviation,
            )
            winning_teams.append(winner)
        return winning_teams

    def get_super_bowl_winners(self) -> list[Team]:
        """Gets the Super Bowl winners, if the week is Super Bowl week.

        Returns a list (despite there only ever being one winner) since other methods return a list.
        This makes it easier to treat the winners equally later on.

        Returns:
            list[Team]: The list of Teams that won the Super Bowl this week.
        """
        if not self.is_super_bowl:
            current_app.logger.debug("It's not Super Bowl week. Returning an empty list.")
            return []
        winning_teams: list[Team] = []
        for game in self.games:
            winner = game.winning_team
            current_app.logger.debug(
                "%s won the Super Bowl. If the Steelers just won, I'll definitely be crying right now.",
                winner.abbreviation,
            )
            winning_teams.append(winner)
        return winning_teams

    def get_pool_winning_teams(self) -> set[Team]:
        """Returns all teams that are currently winning the football pool.

        Returns:
            set[Team]: A set of Teams that are currently winning the football pool.
        """
        winning_team_funcs: tuple[Callable[[], list[Team]], ...] = (
            self.get_weekly_winning_teams,
            self.get_fifty_point_winners,
            self.get_postseason_winners,
            self.get_super_bowl_winners,
        )
        return set(team for winning_team_func in winning_team_funcs for team in winning_team_func())

    @staticmethod
    def get_from_json(query_json: dict) -> CurrentWeek:
        """Gets the CurrentWeek object from a JSON response to an ESPN query.

        Args:
            query_json (dict): The JSON response returned from the ESPN query.

        Returns:
            CurrentWeek: The CurrentWeek object.
        """
        events_list = query_json["events"]
        games = Game.get_all_from_events_list(events_list=events_list)
        season_type = SeasonType(query_json["leagues"][0]["season"]["type"]["type"])
        return CurrentWeek(
            week=int(query_json["week"]["number"]),
            games=games,
            season_type=season_type,
        )


if __name__ == "__main__":
    import json
    from pathlib import Path

    with (Path(__file__).parent / "example.json").open("r") as infile:
        query_json = json.load(infile)

    import time

    from ...football_pool import create_app

    app = create_app()
    with app.app_context():
        start_time = time.perf_counter()
        current_week = CurrentWeek.get_from_json(query_json=query_json)
        end_time = time.perf_counter()
        print(current_week.get_pool_winning_teams())

    print(f"{round(end_time - start_time, 6)} seconds to get from JSON.")
