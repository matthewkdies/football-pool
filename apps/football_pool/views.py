from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from flask import Blueprint, Response, current_app, make_response, render_template, request

from .get_scores import get_live_scores
from .models import Owner, Pot, WinningGame
from .years import get_current_season_start_year

__APPPATH = Path(__file__).parent

app_blueprint = Blueprint(
    "football_pool",
    __name__,
    static_folder=__APPPATH / "static",
    template_folder=__APPPATH / "templates",
)


@app_blueprint.route("/")
def index():
    current_week = get_live_scores()
    sorted_games = sorted(current_week.games, key=lambda game: game.gametime)
    winning_teams = current_week.get_pool_winning_teams()
    if len(winning_teams) >= 16:
        current_app.logger.debug(
            "It's likely that there aren't 16 teams actually winning the pool. Not rendering winners."
        )
        winning_teams = []
    pot = Pot.query.one()
    return render_template(
        "index.html",
        current_week=current_week,
        sorted_games=sorted_games,
        winning_teams=winning_teams,
        pot=pot,
    )


@app_blueprint.route("/assignments")
def assignments():
    season_start_year = int(request.cookies.get("season_start_year", get_current_season_start_year()))
    cur_year_owners = Owner.query.where(Owner.season_start_year == season_start_year).all()
    owners: list[Owner] = sorted(cur_year_owners, key=lambda x: x.team.name_str)
    return render_template("assignments.html", owners=owners, show_year_dropdown=True)


@app_blueprint.route("/results")
def results():
    season_start_year = int(request.cookies.get("season_start_year", get_current_season_start_year()))
    winning_games = WinningGame.query.where(WinningGame.season_start_year == season_start_year).order_by(
        WinningGame.week
    )
    winning_owners = (
        Owner.query.where((Owner.winnings > 0) & (Owner.season_start_year == season_start_year))
        .order_by(Owner.winnings.desc())
        .all()
    )
    return render_template(
        "results.html", winning_games=winning_games, winning_owners=winning_owners, show_year_dropdown=True
    )


@app_blueprint.route("/about")
def about():
    return render_template("about.html")


class Theme(StrEnum):
    """An Enum class to handle the light and dark mode themes."""

    LIGHT = "light"
    DARK = "dark"

    @property
    def opposite(self) -> Theme:
        """Returns the opposite theme of the current.

        This is useful for swapping the theme and providing the "other" value
        when making the checkbox.

        Returns:
            Theme: The opposite theme of the current.
        """
        if self == Theme.LIGHT:
            return Theme.DARK
        return Theme.LIGHT

    @classmethod
    def default(cls) -> Theme:
        """The default theme: light mode. Sorry Xavi, it's who I am.

        Returns:
            Theme: The default theme.
        """
        current_app.logger.debug("Getting theme from default.")
        return Theme.LIGHT

    @staticmethod
    def get_from_cookie() -> Theme:
        """Gets the current theme from the cookies, calling back to the default.

        Returns:
            Theme: The theme set in cookies, falling back on the default if not set.
        """
        theme_cookie = request.cookies.get("theme", None)
        if theme_cookie is None:
            return Theme.default()
        current_app.logger.debug(f"Found {theme_cookie} in cookies.")
        return Theme(theme_cookie)


@app_blueprint.route("/set-year", methods=["POST"])
def set_year():
    season_start_year = request.form.get("season_start_year")
    if not season_start_year or not season_start_year.isdigit():
        current_app.logger.debug("season_start_year='%s' failed validation.", season_start_year)
        return "Invalid year", 400

    resp = make_response("")
    resp.set_cookie("season_start_year", season_start_year)
    current_app.logger.debug("COOKIE: Set season_start_year='%s'.", season_start_year)
    return resp


@app_blueprint.route("/swap-theme-cookie", methods=["POST"])
def swap_theme_cookie() -> Response:
    """Handles an HTMX POST to swap the cookie, for storing the theme in the cookies.

    Returns:
        Response: The same page, but with the cookie set.
    """
    theme = Theme.get_from_cookie()
    current_app.logger.debug(f"Swapping theme cookie from {theme.value} to {theme.opposite.value}.")
    resp = make_response("")  # no need to do anything with a response, just set the cookie
    resp.set_cookie("theme", theme.opposite.value, max_age=31536000)
    return resp


@app_blueprint.route("/healthcheck", methods=["GET"])
def healthcheck() -> str:
    """Provides an endpoint to make healthchecks possible.

    Returns:
        str: The str "ok", if healthy.
    """
    return "ok"
