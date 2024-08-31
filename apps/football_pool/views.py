# keep this file even if you don't need traditional views
# as it holds the blueprint app instance
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, url_for

app = Blueprint("football_pool", __name__, template_folder=Path(__file__).parent / "templates")


@app.route("/")
def hello_world():
    return render_template("index.html")
