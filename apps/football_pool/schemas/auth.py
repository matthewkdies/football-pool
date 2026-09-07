"""Schemas for member profiles, claim authentication, and session state."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from .scoreboard import TeamSummary


class MemberResponse(BaseModel):
    """Public representation of a pool member."""

    id: int
    first_name: str
    last_name: str
    full_name: str
    created_at: datetime


class ClaimRequest(BaseModel):
    """Request payload to claim a member identity."""

    member_id: int


class AuthMeResponse(BaseModel):
    """Current session claim status response."""

    claimed: bool
    member: MemberResponse | None = None
    current_team: TeamSummary | None = None
