# Football Pool (UCMFPTDCYAMBCMYR)

This started as a project I threw together in roughly two weeks to track the results of my family's football pool — officially known as the **Uncle Charles Memorial Football Pool That Doesn't Cost You Any Money But Can Make You Rich** (UCMFPTDCYAMBCMYR).

The rules are pretty simple: members of our family each get an NFL team assigned every season, and weekly payouts and season standings are determined by how those teams perform.

What started out as a quick Flask prototype has since gotten a complete 2.0 overhaul: a modern async backend, an interactive React frontend, background scoreboard caching, and real-time family chat.

---

## The 2.0 Overhaul: What's New?

The original version got the job done, but it had some obvious pain points: rendering everything with server-side Jinja templates was clunky, clicking into the scoreboard hit ESPN's API synchronously while running dozens of database queries per page load, and there was no easy way for family members to chat during games.

Here's what changed in the rewrite:

- **FastAPI + Async SQLAlchemy 2.0 Backend**: Swapped out Flask for an asynchronous backend powered by FastAPI, Uvicorn, and SQLAlchemy 2.0 async. Dependency management is handled by [`uv`](https://github.com/astral-sh/uv), which makes environment setup and installs essentially instantaneous.
- **Smart Scoreboard Caching**: Instead of hammering ESPN on every single request, an adaptive background poller fetches scores at sensible intervals (frequent when games are live, relaxed when they're not) and keeps an in-memory cache. The `/api/scoreboard` endpoint responds in less than a millisecond.
- **Real-Time Family Chat**: Built a slide-out chat drawer powered by WebSockets (`/ws/chat`). Family members can talk smack live during games, with messages persisted to the database and a built-in profanity filter so things stay family-friendly.
- **Passwordless Profile Claiming**: Nobody in the family wants to manage another password. Users simply pick their name from a list to claim their profile, which issues a secure signed session cookie. Once claimed, the site highlights their assigned team, personal winnings, and chat handle.
- **Modern React + TypeScript + DaisyUI Frontend**: The frontend was completely rewritten from scratch as a Single Page Application using React, TypeScript, Vite, Tailwind CSS v4, and DaisyUI. Game cards highlight live winning conditions (Most Points, Least Points, 50-point bonus), with full standings, weekly payout logs, and historical archives for past seasons.
- **Automated Tuesday Scoring & Pot Rollover**: Weekly winners and payouts are computed automatically every Tuesday morning, handling multi-winner splits and rolling the pot forward whenever an unowned team wins.
- **Tests & CI**: Backed by a full test suite using `pytest`, `pytest-asyncio`, and `httpx`, plus GitHub Actions running automated checks on every push and pull request.

---

## Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async) with [asyncpg](https://github.com/MagicStack/asyncpg) (PostgreSQL) and [aiosqlite](https://github.com/omnilib/aiosqlite) (local tests)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Package Management**: [`uv`](https://github.com/astral-sh/uv)
- **Testing**: [pytest](https://docs.pytest.org/), `pytest-asyncio`, [HTTPX](https://www.python-httpx.org/)

### Frontend
- **Framework & Build**: [React 18](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Vite](https://vitejs.dev/)
- **Styling & UI**: [Tailwind CSS v4](https://tailwindcss.com/), [DaisyUI](https://daisyui.com/), [Lucide React](https://lucide.dev/)
- **Routing & Networking**: React Router v6, native Fetch & WebSockets

### DevOps & Tooling
- **Containers**: Multi-stage Docker build (`prod/prod.dockerfile`) & VS Code Devcontainers
- **CI**: GitHub Actions (`.github/workflows/ci.yml`)

---

## Project Layout

```text
football-pool/
├── apps/
│   └── football_pool/       # FastAPI application
│       ├── api/             # REST endpoints (auth, pool, scoreboard, chat)
│       ├── models/          # SQLAlchemy async models
│       ├── schemas/         # Pydantic v2 schemas
│       ├── services/        # Business logic (poller, scoreboard, chat, scoring)
│       ├── static/dist/     # Compiled frontend assets served by FastAPI
│       └── utils/           # Helper utilities
├── frontend/                # React + TypeScript + Vite SPA
│   ├── src/                 # Components, pages, hooks, contexts, api client
│   └── package.json
├── migrations/              # Alembic database migrations
├── tests/                   # Pytest test suite
├── prod/                    # Production Dockerfile and entrypoints
├── pyproject.toml           # Python dependencies and tool configs
└── prek.toml                # Git hooks configuration
```

---

## Local Development

### Option 1: Devcontainer (Recommended)
If you use VS Code, open the repository in a Devcontainer (`.devcontainer`). All dependencies, Python, Node, and tooling are pre-configured.

### Option 2: Local Setup

#### 1. Backend Setup
Make sure you have [`uv`](https://github.com/astral-sh/uv) installed.

```bash
# Install dependencies
uv sync

# Run database migrations (or run with SQLite locally)
uv run alembic upgrade head

# Start the FastAPI server
uv run uvicorn apps.football_pool.main:app --reload --port 8000
```

The API docs are available at `http://localhost:8000/docs`.

#### 2. Frontend Setup
In another terminal:

```bash
# Install dependencies
npm --prefix frontend install

# Start the Vite dev server (proxies /api and /ws to :8000)
npm --prefix frontend run dev
```

The frontend will be running at `http://localhost:5173`.

#### 3. Running Tests

```bash
uv run pytest
```

---

## Production Build

The production container uses a multi-stage Docker build ([`prod/prod.dockerfile`](prod/prod.dockerfile)) that compiles the frontend into static assets and bundles them into the FastAPI container. FastAPI then serves the SPA directly, handling client-side routing fallback:

```bash
docker build -f prod/prod.dockerfile -t football-pool:latest .
```

---

## What did I learn?

That I love development, dude.

It isn't often that I get a sudden strike of inspiration like this, but I absolutely could not put this idea away once it came to me. Taking this from a weekend hack thrown together for the family into a clean, modern, real-time application has been an absolute blast.

I also learned a ton about the history of the football pool and my family -- I'm so lucky to have such an amazing family that can support and enjoy a project like this one!
