"""Historical database seeding for teams, members, season assignments, and pots."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import async_session_factory, engine
from ..models import Member, Pot, SeasonAssignment, Team
from .teams_data import TEAMS_DATA

logger = logging.getLogger(__name__)

ASSIGNMENTS_2024: list[tuple[str, str, str]] = [
    # (First, Last, Team Abbr)
    ("Madison", "Dies", "ATL"),
    ("Mike", "Dies", "BAL"),
    ("Jeep", "Dies", "BUF"),
    ("Aaron", "Smith", "CAR"),
    ("Thomas", "Iodice", "CIN"),
    ("Janet", "Lippincott", "CLE"),
    ("Kathy", "Dies", "DAL"),
    ("Judi", "Carlson", "DEN"),
    ("Charlotte", "Lippincott", "DET"),
    ("Aidan", "Grass", "GB"),
    ("Pam", "Smith", "HOU"),
    ("Missy", "Dies", "IND"),
    ("Nathan", "Smith", "JAX"),
    ("Matt", "Dies", "KC"),
    ("Colin", "Lippincott", "LAC"),
    ("Dennis", "Smith", "LAR"),
    ("Dave", "Hasman", "MIA"),
    ("Natalia", "Carlson", "MIN"),
    ("Doug", "Carlson", "NE"),
    ("Ashley", "Dies", "NO"),
    ("Anna", "Lippincott-Hasman", "NYJ"),
    ("Julia", "Klein", "LV"),
    ("Alex", "Lippincott", "PHI"),
    ("Janice", "Dies", "PIT"),
    ("Lauryn", "Dies", "SF"),
    ("Jeremy", "Carlson", "SEA"),
    ("Ashley", "Lippincott", "TB"),
    ("Chip", "Lippincott", "TEN"),
    ("Moira", "Healy", "WSH"),
]

ASSIGNMENTS_2025: list[tuple[str, str, str]] = [
    ("Aaron", "Smith", "ATL"),
    ("Dave", "Hasman", "BAL"),
    ("Nathan", "Smith", "BUF"),
    ("Jeep", "Dies", "CAR"),
    ("Ashley", "Dies", "CIN"),
    ("Charlotte", "Lippincott", "CLE"),
    ("Aidan", "Grass", "DAL"),
    ("Kathy", "Dies", "DEN"),
    ("Moira", "Healy", "DET"),
    ("Madison", "Dies", "HOU"),
    ("Janet", "Lippincott", "IND"),
    ("Natalia", "Carlson", "JAX"),
    ("Ashley", "Lippincott", "KC"),
    ("Dennis", "Smith", "LAC"),
    ("Pam", "Smith", "MIA"),
    ("Judi", "Carlson", "MIN"),
    ("Chip", "Lippincott", "NE"),
    ("Anna", "Lippincott-Hasman", "NO"),
    ("Doug", "Carlson", "NYJ"),
    ("Matt", "Dies", "LV"),
    ("Thomas", "Iodice", "PHI"),
    ("Mike", "Dies", "PIT"),
    ("Jeremy", "Carlson", "SF"),
    ("Janice", "Dies", "SEA"),
    ("Julia", "Klein", "TB"),
    ("Lauryn", "Dies", "TEN"),
    ("Colin", "Lippincott", "NYG"),
    ("Missy", "Dies", "ARI"),
    ("Alex", "Lippincott", "CHI"),
    ("Katherine", "Hatton", "GB"),
    ("Richard", "Hatton", "LAR"),
]


ASSIGNMENTS_2026: list[tuple[str, str, str]] = [
    ("Dave", "Hasman", "ATL"),
    ("Natalia", "Carlson", "BAL"),
    ("Moira", "Healy", "BUF"),
    ("Janet", "Lippincott", "CAR"),
    ("Richard", "Bilotti", "CHI"),
    ("Colin", "Lippincott", "CHI"),
    ("Ashley", "Dies", "CIN"),
    ("Mike", "Dies", "CIN"),
    ("Aidan", "Grass", "CLE"),
    ("Kevin", "Hider", "DAL"),
    ("Paul", "Rasmussen", "DEN"),
    ("Madison", "Dies", "DET"),
    ("Nathan", "Smith", "GB"),
    ("Aaron", "Smith", "IND"),
    ("Missy", "Dies", "JAX"),
    ("Kathy", "Dies", "KC"),
    ("Judi", "Carlson", "LAC"),
    ("Lauryn", "Dies", "LAR"),
    ("Ashley", "Lippincott", "MIA"),
    ("Thomas", "Iodice", "MIN"),
    ("Julia", "Klein", "NE"),
    ("Doug", "Carlson", "NO"),
    ("Charlotte", "Lippincott", "NYG"),
    ("Matt", "Dies", "NYJ"),
    ("Alex", "Lippincott", "LV"),
    ("Anna", "Lippincott-Hasman", "PHI"),
    ("Lori", "Rasmussen", "PIT"),
    ("Dennis", "Smith", "PIT"),
    ("Chip", "Lippincott", "SF"),
    ("Katherine", "Hatton", "SEA"),
    ("Pam", "Smith", "SEA"),
    ("Jeep", "Dies", "TB"),
    ("Jeremy", "Dies", "TEN"),
    ("Janice", "Carlson", "WSH"),
]


async def seed_database(session: AsyncSession) -> None:
    """Seeds all 32 teams, members, season assignments, and pots idempotently."""
    logger.info("Starting database seeding...")

    # 1. Seed Teams
    team_map: dict[str, Team] = {}
    for team_data in TEAMS_DATA:
        result = await session.execute(select(Team).where(Team.abbreviation == team_data["abbreviation"]))
        team = result.scalar_one_or_none()
        if not team:
            team = Team(**team_data)
            session.add(team)
            await session.flush()
        team_map[team.abbreviation] = team

    # 2. Extract unique members from assignments
    all_members_raw = {(first, last) for first, last, _ in ASSIGNMENTS_2024 + ASSIGNMENTS_2025 + ASSIGNMENTS_2026}
    member_map: dict[tuple[str, str], Member] = {}

    for first, last in sorted(all_members_raw):
        result = await session.execute(select(Member).where(Member.first_name == first, Member.last_name == last))
        member = result.scalar_one_or_none()
        if not member:
            member = Member(first_name=first, last_name=last)
            session.add(member)
            await session.flush()
        member_map[(first, last)] = member

    # 3. Seed Season Assignments for 2024, 2025, and 2026
    season_assignments_by_year = [
        (2024, ASSIGNMENTS_2024),
        (2025, ASSIGNMENTS_2025),
        (2026, ASSIGNMENTS_2026),
    ]

    for year, assignments in season_assignments_by_year:
        for first, last, abbr in assignments:
            team = team_map[abbr]
            member = member_map[(first, last)]
            result = await session.execute(
                select(SeasonAssignment).where(
                    SeasonAssignment.season_year == year,
                    SeasonAssignment.team_id == team.id,
                    SeasonAssignment.member_id == member.id,
                )
            )
            existing_assignment = result.scalar_one_or_none()
            if not existing_assignment:
                assignment = SeasonAssignment(
                    season_year=year,
                    member_id=member.id,
                    team_id=team.id,
                )
                session.add(assignment)

    # 4. Seed Pots
    for year in (2024, 2025, 2026):
        result = await session.execute(select(Pot).where(Pot.season_year == year))
        existing_pot = result.scalar_one_or_none()
        if not existing_pot:
            session.add(Pot(season_year=year, amount=10))

    await session.commit()
    logger.info("Database seeding successfully completed.")


async def main() -> None:
    """CLI entrypoint for running database seed."""
    logging.basicConfig(level=logging.INFO)
    async with async_session_factory() as session:
        await seed_database(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
