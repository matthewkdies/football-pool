"""Schemas for chat messages and WebSocket communication."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageResponse(BaseModel):
    """Historical or broadcasted chat message."""

    id: int
    member_id: int
    author_name: str
    content: str
    created_at: datetime


class IncomingChatPayload(BaseModel):
    """Payload sent by a WebSocket client to send a chat message."""

    content: str = Field(..., max_length=500)
