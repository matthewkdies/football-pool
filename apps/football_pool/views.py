from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from flask import Blueprint, Response, current_app, g, make_response, render_template, request

from .get_scores import get_live_scores
from .models import Owner, WinningGame

__APPPATH = Path(__file__).parent

app_blueprint = Blueprint(
    "football_pool",
    __name__,
    static_folder=__APPPATH / "static",
    template_folder=__APPPATH / "templates",
)


@app_blueprint.before_request
def load_theme():
    """Loads the theme from the cookies and puts it into the g variables."""
    if request.method == "GET":  # Only handle theme setting for GET requests
        theme = Theme.get_from_cookie()
        g.theme = theme.value
        g.other_theme = theme.opposite.value


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
    return render_template(
        "index.html",
        current_week=current_week,
        sorted_games=sorted_games,
        winning_teams=winning_teams,
    )


@app_blueprint.route("/assignments")
def assignments():
    owners: list[Owner] = sorted(Owner.query.all(), key=lambda x: x.team.name_str)
    return render_template("assignments.html", owners=owners)


@app_blueprint.route("/results")
def results():
    winning_games = WinningGame.query.all()
    winning_owners = Owner.query.where(Owner.winnings > 0).order_by(Owner.winnings.desc())
    return render_template(
        "results.html", winning_games=winning_games, winning_owners=winning_owners
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

        This is useful for swapping the theme and providing the "other" value when making the checkbox.

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
def healthcheck():
    return "ok"
