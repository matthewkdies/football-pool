"""Shared pytest fixtures for the football-pool test suite."""

import asyncio
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.football_pool.database import Base, get_db
from apps.football_pool.models import Pot
from apps.football_pool.seed.historical_seed import seed_database
from apps.football_pool.api.auth import router as auth_router
from apps.football_pool.api.pool import router as pool_router
from apps.football_pool.api.scoreboard import router as scoreboard_router
from fastapi import FastAPI


@pytest_asyncio.fixture
async def test_db_engine():
    """Creates an in-memory SQLite async engine initialized with all tables."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed historical data
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        await seed_database(session)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yields a clean async session for tests."""
    session_factory = async_sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_app(test_db_engine) -> FastAPI:
    """Builds a test FastAPI application with overridden database session."""
    session_factory = async_sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app = FastAPI()
    app.dependency_overrides[get_db] = override_get_db
    app.include_router(auth_router)
    app.include_router(pool_router)
    app.include_router(scoreboard_router)
    return app


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Yields an HTTPX AsyncClient wired to the test FastAPI app."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
