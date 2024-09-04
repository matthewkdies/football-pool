from __future__ import annotations

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from ..models import Team, WinningType


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
    is_active: bool
    espn_url: str
    display_clock: str | None
    quarter: int | None

    @staticmethod
    def get_all_from_events_list(events_list: list[dict]) -> list[Game]:
        games: list[Game] = []
        for event in events_list:
            activity_status = event["status"]["type"]["name"]
            if activity_status != "STATUS_IN_PROGRESS":
                is_active = False
                display_clock = None
                quarter = None
            else:
                is_active = True
                display_clock = event["status"]["displayClock"]
                quarter = int(event["status"]["period"])
            home_idx = 0 if event["competitions"][0]["competitors"][0]["homeAway"] == 0 else 1
            away_idx = 1 - home_idx
            home_dict = event["competitions"][0]["competitors"][home_idx]
            away_dict = event["competitions"][0]["competitors"][away_idx]
            games.append(
                Game(
                    home_team=Team.from_abbr(home_dict["team"]["abbreviation"]),
                    home_team_score=int(home_dict["score"]),
                    away_team=Team.from_abbr(away_dict["team"]["abbreviation"]),
                    away_team_score=int(away_dict["score"]),
                    is_active=is_active,
                    display_clock=display_clock,
                    quarter=quarter,
                    espn_url=event["links"][0]["href"],
                )
            )
        return games


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class CurrentWeek:
    """Contains all of the information about the current week of games.

    Is *not* a database object.
    """

    week: int
    games: list[Game]

    @property
    def winning_type(self) -> WinningType:
        """Finds whether the week is a most or least week.

        - `number` % 2 == 1 -> `number` is odd.
        - Odd weeks are most weeks.
        - Even weeks are least weeks.
        """
        if self.week % 2:
            # it's an odd week
            return WinningType.MOST
        # it's an even week
        return WinningType.LEAST

    @staticmethod
    def get_from_json(query_json: dict) -> CurrentWeek:
        events_list = query_json["events"]
        games = Game.get_all_from_events_list(events_list=events_list)
        return CurrentWeek(
            week=int(query_json["week"]["number"]),
            games=games,
        )


if __name__ == "__main__":
    import json
    from pathlib import Path

    with (Path(__file__).parent / "example.json").open("r") as infile:
        query_json = json.load(infile)

    from ...football_pool import create_app
    import time

    app = create_app()
    with app.app_context():
        start_time = time.perf_counter()
        _ = CurrentWeek.get_from_json(query_json=query_json)
        end_time = time.perf_counter()

    print(f"{round(end_time - start_time, 6)} seconds to get from JSON.")
