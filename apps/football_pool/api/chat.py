"""Chat REST and WebSocket API router with real-time broadcasting and moderation."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..config import settings
from ..database import async_session_factory, get_db
from ..models import ChatMessage, Member
from ..schemas.chat import ChatMessageResponse
from ..services.chat_manager import ChatClient, chat_manager
from ..services.moderation import censor_message, is_valid_message
from ..utils.security import verify_session_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.get("/api/chat/history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[ChatMessageResponse]:
    """Returns recent chat messages in chronological order."""
    query = (
        select(ChatMessage)
        .options(selectinload(ChatMessage.member))
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    messages = list(result.scalars().all())

    # Return in ascending chronological order
    messages.reverse()

    return [
        ChatMessageResponse(
            id=m.id,
            member_id=m.member_id,
            author_name=m.member.full_name if m.member else "Unknown",
            content=m.content,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time family-friendly chat."""
    await websocket.accept()

    # 1. Resolve claimed identity from session cookie
    token = websocket.cookies.get(settings.session_cookie_name)
    member_id = verify_session_token(token)
    author_name: str | None = None

    if member_id:
        async with async_session_factory() as session:
            result = await session.execute(select(Member).where(Member.id == member_id))
            member = result.scalar_one_or_none()
            if member:
                author_name = member.full_name
            else:
                member_id = None

    client = ChatClient(websocket=websocket, member_id=member_id, author_name=author_name)
    await chat_manager.connect(client)

    # Send initial connection status
    await websocket.send_json(
        {
            "type": "connected",
            "claimed": client.is_claimed,
            "author_name": client.author_name,
        }
    )

    try:
        while True:
            raw_text = await websocket.receive_text()

            # Support both raw text and JSON payloads {"content": "..."}
            try:
                payload = json.loads(raw_text)
                content = payload.get("content", "") if isinstance(payload, dict) else str(payload)
            except (json.JSONDecodeError, TypeError):
                content = raw_text

            if not is_valid_message(content):
                continue

            if not client.is_claimed or not client.member_id or not client.author_name:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "You must claim a member profile to post in the chat.",
                    }
                )
                continue

            # Apply family-friendly moderation filter
            censored_content = censor_message(content)

            # Persist message to database
            async with async_session_factory() as session:
                msg = ChatMessage(
                    member_id=client.member_id,
                    content=censored_content,
                )
                session.add(msg)
                await session.commit()
                await session.refresh(msg)
                msg_id = msg.id
                created_at_str = msg.created_at.isoformat()

            # Broadcast to all connected clients
            await chat_manager.broadcast(
                {
                    "type": "chat_message",
                    "id": msg_id,
                    "member_id": client.member_id,
                    "author_name": client.author_name,
                    "content": censored_content,
                    "created_at": created_at_str,
                }
            )

    except WebSocketDisconnect:
        await chat_manager.disconnect(client)
    except Exception as exc:
        logger.error(f"WebSocket error: {exc}")
        await chat_manager.disconnect(client)
