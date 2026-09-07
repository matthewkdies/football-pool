"""Season assignment domain model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .member import Member
    from .team import Team


class SeasonAssignment(Base):
    """Maps a pool member to an NFL team for a given season."""

    __tablename__ = "season_assignments"
    __table_args__ = (UniqueConstraint("season_year", "team_id", "member_id", name="uq_season_team_member"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)

    member: Mapped["Member"] = relationship("Member", back_populates="assignments")
    team: Mapped["Team"] = relationship("Team", back_populates="assignments")

    def __repr__(self) -> str:
        return (
            f"<SeasonAssignment id={self.id} year={self.season_year} member_id={self.member_id} team_id={self.team_id}>"
        )
