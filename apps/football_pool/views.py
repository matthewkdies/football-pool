import logging
from pathlib import Path

from flask import Blueprint, render_template

from .get_scores import get_live_scores
from .models import Owner, WinningGame

logger = logging.getLogger(__name__)

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
        logger.debug(
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


@app_blueprint.route("/rules")
def rules():
    return render_template("rules.html")
