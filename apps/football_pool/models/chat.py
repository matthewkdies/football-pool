"""ChatMessage domain model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .member import Member


class ChatMessage(Base):
    """Stores chat messages sent between pool members."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )

    member: Mapped["Member"] = relationship("Member", back_populates="chat_messages")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} member_id={self.member_id} at={self.created_at}>"
