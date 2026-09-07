"""Member domain model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .assignment import SeasonAssignment
    from .chat import ChatMessage


class Member(Base):
    """Represents a human member/participant in the football pool."""

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    assignments: Mapped[list["SeasonAssignment"]] = relationship(
        "SeasonAssignment",
        back_populates="member",
        cascade="all, delete-orphan",
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="member",
        cascade="all, delete-orphan",
    )

    @property
    def full_name(self) -> str:
        """Returns the member's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Member id={self.id} name='{self.full_name}'>"
