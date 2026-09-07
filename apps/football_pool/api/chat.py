"""Chat REST and WebSocket API router with real-time broadcasting and moderation."""

from __future__ import annotations

import json
import logging
import time
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..config import settings
from ..database import async_session_factory, get_db
from ..models import ChatMessage, Member
from ..schemas.chat import ChatMessageResponse, IncomingChatPayload
from ..services.chat_manager import ChatClient, chat_manager
from ..services.moderation import censor_message, is_valid_message
from ..utils.security import verify_session_token
from .auth import get_optional_current_member

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


def is_allowed_origin(origin: str | None, host: str | None) -> bool:
    """Validates that the Origin header matches host or configured CORS origins."""
    if not origin:
        return True  # Non-browser clients (native apps, curl, test clients)
    try:
        parsed_origin = urlparse(origin)
        origin_netloc = parsed_origin.netloc.lower()
        if host and origin_netloc == host.lower():
            return True
        for allowed in settings.cors_origins:
            if allowed == "*":
                continue
            allowed_netloc = urlparse(allowed).netloc.lower()
            if origin_netloc == allowed_netloc or origin.rstrip("/") == allowed.rstrip("/"):
                return True
    except Exception:
        return False
    return False


@router.get("/api/chat/history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    limit: int = Query(default=50, ge=1, le=100),
    current_member: Member | None = Depends(get_optional_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[ChatMessageResponse]:
    """Returns recent chat messages in chronological order (authenticated members only)."""
    if not current_member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must claim a member profile to view chat history.",
        )
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


@router.post(
    "/api/chat/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_chat_message(
    payload: IncomingChatPayload,
    current_member: Member | None = Depends(get_optional_current_member),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """Posts a new chat message via authenticated session cookie."""
    if not current_member:
        logger.warning("Unauthenticated chat message post attempted.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must claim a member profile to post in the chat.",
        )

    content = payload.content.strip()
    if not is_valid_message(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty.",
        )

    # Apply family-friendly moderation filter
    censored_content = censor_message(content)

    msg = ChatMessage(
        member_id=current_member.id,
        content=censored_content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    logger.info(f"Chat message #{msg.id} posted by {current_member.full_name}: {censored_content[:40]}")

    # Broadcast to all connected WebSocket clients
    await chat_manager.broadcast(
        {
            "type": "chat_message",
            "id": msg.id,
            "member_id": current_member.id,
            "author_name": current_member.full_name,
            "content": censored_content,
            "created_at": msg.created_at.isoformat(),
        }
    )

    return ChatMessageResponse(
        id=msg.id,
        member_id=current_member.id,
        author_name=current_member.full_name,
        content=censored_content,
        created_at=msg.created_at,
    )


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time family-friendly chat."""
    origin = websocket.headers.get("origin")
    host = websocket.headers.get("host")
    if not is_allowed_origin(origin, host):
        logger.warning(f"Rejecting WebSocket connection with unauthorized origin: {origin}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Origin not allowed")
        return

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

    if not member_id or not author_name:
        logger.warning("Unclaimed WebSocket client attempted to connect to family chat.")
        await websocket.send_json(
            {
                "type": "error",
                "message": "You must claim a member profile to join the chat.",
            }
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Claimed profile required")
        return

    client = ChatClient(websocket=websocket, member_id=member_id, author_name=author_name)
    await chat_manager.connect(client)
    logger.info(f"WebSocket client connected: author={client.author_name} (claimed={client.is_claimed})")

    # Send initial connection status
    await websocket.send_json(
        {
            "type": "connected",
            "claimed": True,
            "author_name": client.author_name,
        }
    )

    message_timestamps: list[float] = []

    try:
        while True:
            raw_text = await websocket.receive_text()

            # Rate limiting: max 5 messages per 5 seconds per connection
            now = time.time()
            message_timestamps = [t for t in message_timestamps if now - t < 5.0]
            if len(message_timestamps) >= 5:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "You are sending messages too quickly. Please wait a moment.",
                    }
                )
                continue
            message_timestamps.append(now)

            # Message payload size limit
            if len(raw_text) > 1000:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Message exceeds maximum allowed length.",
                    }
                )
                continue

            # Support both raw text and JSON payloads {"content": "..."}
            try:
                payload = json.loads(raw_text)
                content = payload.get("content", "") if isinstance(payload, dict) else str(payload)
            except (json.JSONDecodeError, TypeError):
                content = raw_text

            if not is_valid_message(content):
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

            logger.info(f"WebSocket message #{msg_id} from {client.author_name}: {censored_content[:40]}")

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
        logger.info(f"WebSocket client disconnected: author={client.author_name}")
        await chat_manager.disconnect(client)
    except Exception as exc:
        logger.error(f"WebSocket error for author={client.author_name}: {exc}")
        await chat_manager.disconnect(client)
