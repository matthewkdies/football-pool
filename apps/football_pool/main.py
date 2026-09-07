"""Main entrypoint for the Football Pool FastAPI application."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

    # Static assets and SPA distribution
    static_dir = Path(__file__).parent / "static"
    dist_dir = static_dir / "dist"
    dist_assets = dist_dir / "assets"
    dist_index = dist_dir / "index.html"

    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    if dist_assets.exists():
        app.mount("/assets", StaticFiles(directory=str(dist_assets)), name="assets")

    @app.get("/healthcheck", tags=["Health"])
    async def healthcheck() -> dict[str, str]:
        """Health check endpoint for container orchestrators."""
        return {"status": "ok"}

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        """Favicon fallback."""
        fav = static_dir / "favicon" / "favicon.ico"
        if fav.exists():
            return FileResponse(str(fav))
        raise HTTPException(status_code=404)

    @app.get("/", include_in_schema=False)
    async def root_or_spa():
        """Root endpoint serving SPA index if built, or API metadata."""
        if dist_index.exists():
            return FileResponse(str(dist_index))
        return {
            "name": "Football Pool API",
            "version": "2.0.0",
            "docs": "/docs",
            "status": "healthy",
        }

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        """Fallback router for client-side SPA routing."""
        if full_path.startswith(("api/", "ws/", "healthcheck", "docs", "redoc", "openapi.json", "static/", "assets/")):
            raise HTTPException(status_code=404, detail="Not Found")
        if dist_index.exists():
            return FileResponse(str(dist_index))
        raise HTTPException(status_code=404, detail="Not Found")

    return app


app = create_app()
