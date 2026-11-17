import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import async_session_factory, engine
from ..models import Member, SeasonAssignment, Team

logger = logging.getLogger(__name__)


async def seed_database(session: AsyncSession) -> None:
    """Updates Julia's last name, adds Jack, and replaces Carolina ownership with Jack."""
    logger.info("Starting database seeding...")

    # 1. Update Julia's last name
    result = await session.execute(select(Member).where(Member.first_name == "Julia", Member.last_name == "Klein"))
    julia = result.scalar_one()
    julia.last_name = "Lippincott"
    await session.flush()

    # 2. New baby Jack!
    # 2.1: Add Jack as a member
    jack = Member(first_name="Jack", last_name="Lippincott")
    session.add(jack)
    await session.flush()

    # 2.2: Add assignment
    result = await session.execute(select(Team).where(Team.abbreviation == "CAR"))
    carolina_panthers = result.scalar_one()
    assignment = SeasonAssignment(season_year=2026, member_id=jack.id, team_id=carolina_panthers.id)
    session.add(assignment)
    await session.flush()

    # 2.3: Remove Aunt Janet's assignment
    result = await session.execute(select(Member).where(Member.first_name == "Janet", Member.last_name == "Lippincott"))
    aunt_janet = result.scalar_one()
    result = await session.execute(
        select(SeasonAssignment).where(
            SeasonAssignment.season_year == 2026,
            SeasonAssignment.member_id == aunt_janet.id,
            SeasonAssignment.team_id == carolina_panthers.id,
        )
    )
    janet_assignment = result.scalar_one()
    await session.delete(janet_assignment)
    await session.flush()

    try:
        await session.commit()
    except Exception:
        logger.exception("Database updates failed, rolling back...")
        await session.rollback()
    logger.info("Database seeding successfully completed.")


async def main() -> None:
    """CLI entrypoint for running database seed."""
    logging.basicConfig(level=logging.INFO)
    async with async_session_factory() as session:
        await seed_database(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
