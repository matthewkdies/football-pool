from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, url_for

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
    teams: list[Team] = Team.query.all()
    return render_template("index.html", teams=teams)
