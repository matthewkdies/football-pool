"""Cryptographic session cookie signing and verification using itsdangerous."""

from __future__ import annotations

import logging
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from ..config import settings

logger = logging.getLogger(__name__)

SALT = "football-pool-session-salt"


def get_serializer() -> URLSafeTimedSerializer:
    """Returns a timed serializer configured with the application secret key."""
    return URLSafeTimedSerializer(secret_key=settings.secret_key, salt=SALT)


def create_session_token(member_id: int) -> str:
    """Generates a signed, timestamped session token containing the member_id."""
    serializer = get_serializer()
    return serializer.dumps({"member_id": member_id})


def verify_session_token(token: str | None, max_age: int | None = None) -> int | None:
    """Verifies a signed token and its expiration, returning the member_id or None."""
    if not token:
        return None
    serializer = get_serializer()
    effective_max_age = max_age if max_age is not None else settings.session_max_age_seconds
    try:
        data: Any = serializer.loads(token, max_age=effective_max_age)
        if isinstance(data, dict) and "member_id" in data:
            return int(data["member_id"])
    except (BadSignature, SignatureExpired, ValueError, TypeError) as exc:
        logger.debug(f"Invalid, expired, or tampered session token: {exc}")
    return None
