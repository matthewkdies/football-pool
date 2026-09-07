"""Team domain model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .enums import Conference, Division

if TYPE_CHECKING:
    from .assignment import SeasonAssignment
    from .winning_game import WinningGame


class Team(Base):
    """Represents an NFL team (32 total)."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(5), unique=True, index=True, nullable=False)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=False)
    conference: Mapped[Conference] = mapped_column(Enum(Conference), nullable=False)
    division: Mapped[Division] = mapped_column(
        Enum(Division, values_callable=lambda enum: [e.value for e in enum]), nullable=False
    )

    assignments: Mapped[list["SeasonAssignment"]] = relationship(
        "SeasonAssignment",
        back_populates="team",
    )
    winning_games: Mapped[list["WinningGame"]] = relationship(
        "WinningGame",
        back_populates="team",
    )

    @property
    def full_name(self) -> str:
        """Returns the city and team name combined."""
        return f"{self.city} {self.name}"

    def __hash__(self) -> int:
        return hash(self.abbreviation)

    def __repr__(self) -> str:
        return f"<Team id={self.id} abbr='{self.abbreviation}' name='{self.full_name}'>"
