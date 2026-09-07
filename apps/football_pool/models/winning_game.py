"""WinningGame domain model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .enums import WinningType

if TYPE_CHECKING:
    from .team import Team


class WinningGame(Base):
    """Stores payouts earned by teams during weekly pool scoring."""

    __tablename__ = "winning_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    winnings: Mapped[int] = mapped_column(Integer, nullable=False)
    winning_type: Mapped[WinningType] = mapped_column(Enum(WinningType), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)

    team: Mapped["Team"] = relationship("Team", back_populates="winning_games")

    def __repr__(self) -> str:
        return f"<WinningGame id={self.id} year={self.season_year} week={self.week} team_id={self.team_id} ${self.winnings}>"
