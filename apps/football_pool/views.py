from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, url_for

from .get_scores import get_live_scores
from .models import Owner, Team

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
    return render_template("index.html", current_week=current_week)


@app_blueprint.route("/assignments")
def assignments():
    owners: list[Owner] = sorted(Owner.query.all(), key=lambda x: x.team.name_str)
    return render_template("assignments.html", owners=owners)


@app_blueprint.route("/results")
def results():
    return render_template("results.html")


@app_blueprint.route("/about")
def about():
    return render_template("about.html")


@app_blueprint.route("/rules")
def rules():
    return render_template("rules.html")


@app_blueprint.route("/test")
def test():
    teams: list[Team] = Team.query.all()
    return render_template("test.html", teams=teams)
