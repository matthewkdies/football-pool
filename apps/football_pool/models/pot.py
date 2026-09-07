"""Pot domain model."""

from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Pot(Base):
    """Stores the current rolling pot balance for a season."""

    __tablename__ = "pots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_year: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    def __repr__(self) -> str:
        return f"<Pot id={self.id} year={self.season_year} amount=${self.amount}>"
