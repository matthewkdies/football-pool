from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, url_for

__APPPATH = Path(__file__).parent

app_blueprint = Blueprint(
    "football_pool",
    __name__,
    static_folder=__APPPATH / "static",
    template_folder=__APPPATH / "templates",
)


@app_blueprint.route("/")
def index():
    return render_template("index.html")
