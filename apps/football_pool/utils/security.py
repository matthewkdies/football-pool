"""Cryptographic session cookie signing and verification using itsdangerous."""

from __future__ import annotations

import logging
from typing import Any

from itsdangerous import BadSignature, URLSafeSerializer

from ..config import settings

logger = logging.getLogger(__name__)

SALT = "football-pool-session-salt"


def get_serializer() -> URLSafeSerializer:
    """Returns a serializer configured with the application secret key."""
    return URLSafeSerializer(secret_key=settings.secret_key, salt=SALT)


def create_session_token(member_id: int) -> str:
    """Generates a signed session token containing the member_id."""
    serializer = get_serializer()
    return serializer.dumps({"member_id": member_id})


def verify_session_token(token: str | None) -> int | None:
    """Verifies a signed token and returns the member_id, or None if invalid."""
    if not token:
        return None
    serializer = get_serializer()
    try:
        data: Any = serializer.loads(token)
        if isinstance(data, dict) and "member_id" in data:
            return int(data["member_id"])
    except (BadSignature, ValueError, TypeError) as exc:
        logger.debug(f"Invalid or tampered session token: {exc}")
    return None
