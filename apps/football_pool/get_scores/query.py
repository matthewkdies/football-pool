import requests

from .exceptions import NoESPNDataError
from .make_games import CurrentWeek

DEFAULT_URL = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
DEFAULT_PARAMS = {}


def get_live_scores(url: str = DEFAULT_URL, params: dict = DEFAULT_PARAMS) -> CurrentWeek:
    query_json = requests.get(url=url, params=params).json()
    if not query_json:
        raise NoESPNDataError(url=url)
    return CurrentWeek.get_from_json(query_json)


if __name__ == "__main__":
    import time

    from ...football_pool import create_app

    app = create_app()
    with app.app_context():
        start_time = time.perf_counter()
        _ = get_live_scores()
        end_time = time.perf_counter()

    print(f"{round(end_time - start_time, 6)} seconds to get via request.")
