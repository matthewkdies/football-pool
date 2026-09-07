"""Authentication and member claim API router."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..config import settings
from ..database import get_db
from ..models import Member, SeasonAssignment
from ..schemas.auth import AuthMeResponse, ClaimRequest, MemberResponse
from ..services.scoreboard import get_team_summary
from ..utils.seasons import get_current_season_start_year
from ..utils.security import create_session_token, verify_session_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Auth & Members"])


async def get_optional_current_member(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Member | None:
    """Dependency that returns the claimed Member if a valid session cookie exists, else None."""
    token = request.cookies.get(settings.session_cookie_name)
    member_id = verify_session_token(token)
    if not member_id:
        return None

    result = await db.execute(select(Member).where(Member.id == member_id))
    return result.scalar_one_or_none()


@router.get("/members", response_model=list[MemberResponse])
async def list_members(db: AsyncSession = Depends(get_db)) -> list[MemberResponse]:
    """Returns a list of all pool members."""
    result = await db.execute(select(Member).order_by(Member.last_name.asc(), Member.first_name.asc()))
    members = result.scalars().all()
    return [
        MemberResponse(
            id=m.id,
            first_name=m.first_name,
            last_name=m.last_name,
            full_name=m.full_name,
            created_at=m.created_at,
        )
        for m in members
    ]


@router.post("/auth/claim", response_model=MemberResponse)
async def claim_member_identity(
    payload: ClaimRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> MemberResponse:
    """Claims a member profile and sets a signed session cookie."""
    result = await db.execute(select(Member).where(Member.id == payload.member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {payload.member_id} does not exist.",
        )

    token = create_session_token(member.id)
    is_secure = settings.is_production and request.url.scheme == "https"
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=is_secure,
    )
    logger.info(f"User claimed identity as member {member.id} ({member.full_name}).")
    return MemberResponse(
        id=member.id,
        first_name=member.first_name,
        last_name=member.last_name,
        full_name=member.full_name,
        created_at=member.created_at,
    )


@router.get("/auth/me", response_model=AuthMeResponse)
async def get_current_session(
    current_member: Member | None = Depends(get_optional_current_member),
    db: AsyncSession = Depends(get_db),
) -> AuthMeResponse:
    """Returns the current claimed member identity and their team for the current season."""
    if not current_member:
        return AuthMeResponse(claimed=False)

    current_year = get_current_season_start_year()
    assignment_res = await db.execute(
        select(SeasonAssignment)
        .options(selectinload(SeasonAssignment.team))
        .where(
            SeasonAssignment.member_id == current_member.id,
            SeasonAssignment.season_year == current_year,
        )
    )
    assignment = assignment_res.scalar_one_or_none()
    team_summary = get_team_summary(assignment.team.abbreviation) if assignment and assignment.team else None

    return AuthMeResponse(
        claimed=True,
        member=MemberResponse(
            id=current_member.id,
            first_name=current_member.first_name,
            last_name=current_member.last_name,
            full_name=current_member.full_name,
            created_at=current_member.created_at,
        ),
        current_team=team_summary,
    )


@router.post("/auth/unclaim")
async def unclaim_member_identity(response: Response) -> dict[str, str]:
    """Clears the session cookie."""
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
    )
    return {"status": "unclaimed"}
