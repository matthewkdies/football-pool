"""WebSocket connection manager for real-time chat broadcasting."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ChatClient:
    """Represents a connected WebSocket client."""

    def __init__(
        self,
        websocket: WebSocket,
        member_id: int | None = None,
        author_name: str | None = None,
    ) -> None:
        self.websocket = websocket
        self.member_id = member_id
        self.author_name = author_name

    @property
    def is_claimed(self) -> bool:
        return self.member_id is not None


class ChatConnectionManager:
    """Manages active WebSocket connections and broadcasts messages in real time."""

    def __init__(self) -> None:
        self._connections: set[ChatClient] = set()
        self._lock = asyncio.Lock()

    async def connect(self, client: ChatClient) -> None:
        """Registers a new WebSocket connection."""
        async with self._lock:
            self._connections.add(client)
        logger.debug(f"WebSocket client connected. Active: {len(self._connections)}")

    async def disconnect(self, client: ChatClient) -> None:
        """Unregisters a disconnected WebSocket."""
        async with self._lock:
            self._connections.discard(client)
        logger.debug(f"WebSocket client disconnected. Active: {len(self._connections)}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcasts a JSON message to all currently connected clients in parallel."""
        async with self._lock:
            current_clients = list(self._connections)

        if not current_clients:
            return

        dead_clients: list[ChatClient] = []

        async def send_to_client(client: ChatClient) -> None:
            try:
                await client.websocket.send_json(message)
            except Exception as exc:
                logger.debug(f"Failed to send to client, marking for removal: {exc}")
                dead_clients.append(client)

        await asyncio.gather(*(send_to_client(c) for c in current_clients), return_exceptions=True)

        if dead_clients:
            async with self._lock:
                for dead in dead_clients:
                    self._connections.discard(dead)


chat_manager = ChatConnectionManager()
