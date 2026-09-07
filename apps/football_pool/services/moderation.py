"""Content moderation service for family-friendly chat."""

from __future__ import annotations

import logging

from better_profanity import profanity

logger = logging.getLogger(__name__)

# Initialize the default profanity word list
profanity.load_censor_words()


def censor_message(text: str, max_length: int = 500) -> str:
    """Sanitizes and censors message content to ensure family-friendly language.

    Replaces profane words with asterisks and enforces maximum character limits.
    """
    cleaned = text.strip()[:max_length]
    return profanity.censor(cleaned)


def is_valid_message(text: str | None) -> bool:
    """Checks if message is non-empty after trimming."""
    return bool(text and text.strip())
