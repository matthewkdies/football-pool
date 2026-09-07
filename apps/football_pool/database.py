"""Database engine and async session configuration using SQLAlchemy 2.0."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.0 ORM models."""

    pass


def create_engine(url: str | None = None) -> AsyncEngine:
    """Create and configure an AsyncEngine."""
    db_url = url or settings.async_database_url
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_async_engine(
        db_url,
        echo=settings.debug,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = create_engine()

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
