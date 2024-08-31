"""Contains the database schema definition for the dashboard.

Talking out loud:
On the homepage, I don't think any of the scores/matches there will
come from the database; those should just be objects created via pydantic.
Once a week goes final, everything can then be put into the database.
So the database should be focused around two things:
  1. Storing the results of previous weeks, meaning which team/person won
  2. Storing information for teams, like names, location, abbreviation, etc.
"""

from dataclasses import dataclass
from enum import StrEnum

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Conference(StrEnum):
    """The conferences splitting the NFL."""

    AFC = "AFC"
    NFC = "NFC"


class Division(StrEnum):
    """The divisions within conferences. Used in unison with the `Conference` class."""

    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"


@dataclass
class Team(db.Model):
    """Information about an NFL team that will be used for seeding the teams into the database."""

    __tablename__ = "teams"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    city = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    abbreviation = db.Column(db.String(3), unique=True, nullable=False)
    logo_url = db.Column(db.String)
    conference = db.Column(db.Enum(Conference), nullable=False)
    division = db.Column(db.Enum(Division), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id"), unique=True)
    owner = db.relationship("Owner", back_populates="team", uselist=False)

    @property
    def name_str(self) -> str:
        """Displays the team's name as a string."""
        return f"{self.city} {self.name}"


class Owner(db.Model):
    """Contains all team owners and their information."""

    __tablename__ = "owners"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    team = db.relationship("Team", back_populates="owner", uselist=False)

    @property
    def name_str(self) -> str:
        """Displays the owner's name as a string."""
        return f"{self.first_name} {self.last_name}"
