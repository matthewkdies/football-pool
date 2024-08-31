"""Contains the database schema definition for the dashboard.

Talking out loud:
On the homepage, I don't think any of the scores/matches there will
come from the database; those should just be objects created via pydantic.
Once a week goes final, everything can then be put into the database.
So the database should be focused around two things:
  1. Storing the results of previous weeks, meaning which team/person won
  2. Storing information for teams, like names, location, abbreviation, etc.
"""

from .extensions import db


class Conference(db.Model):  # TODO
    id = db.Column(db.Integer, unique=True, primary_key=True)


class Division(db.Model):  # TODO
    id = db.Column(db.Integer, unique=True, primary_key=True)


class Team(db.Model):  # TODO
    id = db.Column(db.Integer, unique=True, primary_key=True)
    city = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    abbreviation = db.Column(db.String(3), unique=True, nullable=False)
    logo_url = db.Column(db.String)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)
