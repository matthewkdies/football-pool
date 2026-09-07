"""Main entrypoint for the Football Pool FastAPI application."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.auth import router as auth_router
from .api.chat import router as chat_router
from .api.pool import router as pool_router
from .api.scoreboard import router as scoreboard_router
from .config import settings
from .database import engine
from .services.poller import scoreboard_polling_loop
from .services.scoreboard import scoreboard_cache

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing background poller and database connection pool."""
    logger.info("Initializing Football Pool FastAPI backend...")

    # Start adaptive ESPN poller task in background
    stop_event = asyncio.Event()
    poller_task = asyncio.create_task(scoreboard_polling_loop(cache=scoreboard_cache, stop_event=stop_event))

    yield

    logger.info("Shutting down Football Pool backend...")
    stop_event.set()
    scoreboard_cache.trigger_refresh()  # unblock poller wait if sleeping
    try:
        await asyncio.wait_for(poller_task, timeout=5.0)
    except (asyncio.TimeoutError, asyncio.CancelledError):
        poller_task.cancel()

    await engine.dispose()
    logger.info("Backend shutdown complete.")


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title="Football Pool API",
        version="2.0.0",
        description="A modern async backend for tracking NFL pool standings and live games.",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(auth_router)
    app.include_router(scoreboard_router)
    app.include_router(pool_router)
    app.include_router(chat_router)

    @app.get("/healthcheck", tags=["Health"])
    async def healthcheck() -> dict[str, str]:
        """Health check endpoint for container orchestrators."""
        return {"status": "ok"}

    @app.get("/", tags=["Root"])
    async def root() -> dict[str, str]:
        """Root API metadata."""
        return {
            "name": "Football Pool API",
            "version": "2.0.0",
            "docs": "/docs",
            "status": "healthy",
        }

    return app


app = create_app()
