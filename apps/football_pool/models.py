"""Contains the database schema definition for the dashboard.

Talking out loud:
On the homepage, I don't think any of the scores/matches there will
come from the database; those should just be objects created via pydantic.
Once a week goes final, everything can then be put into the database.
So the database should be focused around two things:
  1. Storing the results of previous weeks, meaning which team/person won
  2. Storing information for teams, like names, location, abbreviation, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped

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


class WinningType(StrEnum):
    """The ways in which a game can create monetary winnings."""

    MOST = "MOST"
    LEAST = "LEAST"
    FIFTY = "FIFTY"
    PLAYOFF = "PLAYOFF"
    SUPER_BOWL = "SUPER_BOWL"

    @property
    def name_str(self) -> str:
        """Displays the WinningType as a formatted string.

        Returns:
            str: A formatted string for the WinningType.
        """
        return self.value.replace("_", " ").title()


@dataclass
class Team(db.Model):
    """Information about an NFL team that will be used for seeding the teams into the database."""

    __tablename__ = "teams"
    id: Mapped[int] = db.Column(db.Integer, unique=True, primary_key=True)
    city: Mapped[str] = db.Column(db.String, nullable=False)
    name: Mapped[str] = db.Column(db.String, nullable=False)
    abbreviation: Mapped[str] = db.Column(db.String(3), unique=True, nullable=False)
    logo_url: Mapped[str] = db.Column(db.String)
    conference: Mapped[Conference] = db.Column(db.Enum(Conference), nullable=False)
    division: Mapped[Division] = db.Column(db.Enum(Division), nullable=False)
    wins: Mapped[int] = db.Column(db.Integer, default=0)
    losses: Mapped[int] = db.Column(db.Integer, default=0)
    ties: Mapped[int] = db.Column(db.Integer, default=0)
    owner_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("owners.id"), unique=True)
    owner: Mapped["Owner"] = db.relationship(
        "Owner", back_populates="team", uselist=False, foreign_keys=[owner_id], single_parent=True
    )  # type: ignore

    def __hash__(self) -> int:
        """Makes the Team class hashable.

        Returns:
            int: The hash of the Team's abbreviation (which is unique).
        """
        return hash(self.abbreviation)

    @property
    def name_str(self) -> str:
        """Displays the team's name as a string."""
        return f"{self.city} {self.name}"

    @staticmethod
    def from_abbr(abbr: str) -> Team:
        """Gets the team with the given abbreviation.

        Args:
            abbr (str): The abbreviation of the desired team.

        Returns:
            Team: The Team with the corresponding abbreviation.
        """
        return Team.query.where(Team.abbreviation == abbr).one()


@dataclass
class Owner(db.Model):
    """Contains all team owners and their information."""

    __tablename__ = "owners"
    id: Mapped[int] = db.Column(db.Integer, unique=True, primary_key=True)
    first_name: Mapped[str] = db.Column(db.String, nullable=False)
    last_name: Mapped[str] = db.Column(db.String, nullable=False)
    winnings: Mapped[int] = db.Column(db.Integer, nullable=False, default=0)
    team: Mapped[Team] = db.relationship("Team", back_populates="owner", uselist=False, single_parent=True)  # type: ignore
    season_start_year: Mapped[int] = db.Column(db.Integer, nullable=False)

    @property
    def name_str(self) -> str:
        """Displays the owner's name as a string."""
        return f"{self.first_name} {self.last_name}"


@dataclass
class WinningGame(db.Model):
    """Contains all winning games, created via a scheduled job."""

    __tablename__ = "winning_games"
    id: Mapped[int] = db.Column(db.Integer, unique=True, primary_key=True)
    week: Mapped[int] = db.Column(db.Integer, nullable=False)
    winnings: Mapped[int] = db.Column(db.Integer, nullable=False)
    winning_type: Mapped[WinningType] = db.Column(db.Enum(WinningType), nullable=False)
    team_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    team: Mapped[Team] = db.relationship("Team", uselist=False, single_parent=True)  # type: ignore
    season_start_year: Mapped[int] = db.Column(db.Integer, nullable=False)


@dataclass
class Pot(db.Model):
    """Contains the current pot of winnings."""

    __tablename__ = "pot"
    id: Mapped[int] = db.Column(db.Integer, unique=True, primary_key=True)
    amount: Mapped[int] = db.Column(db.Integer, nullable=False)
