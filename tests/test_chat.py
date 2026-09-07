"""Tests for chat history, WebSocket broadcasting, and family-friendly moderation."""

import pytest
from starlette.testclient import TestClient

from apps.football_pool.api.auth import router as auth_router
from apps.football_pool.api.chat import router as chat_router
from apps.football_pool.config import settings
from apps.football_pool.database import get_db
from apps.football_pool.models import ChatMessage, Member
from apps.football_pool.services.moderation import censor_message
from apps.football_pool.utils.security import create_session_token
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from apps.football_pool.database import Base


def test_profanity_moderation_censor():
    clean_text = "Let's go Steelers!"
    assert censor_message(clean_text) == clean_text

    profane_text = "What the fuck was that play"
    censored = censor_message(profane_text)
    assert "****" in censored
    assert "fuck" not in censored.lower()


@pytest.fixture
def chat_app_and_db(tmp_path):
    # SQLite file db for synchronous TestClient compatibility
    db_file = tmp_path / "test_chat.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    import asyncio
    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            member = Member(first_name="Matt", last_name="Dies")
            session.add(member)
            await session.commit()

    asyncio.run(init())

    app = FastAPI()

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.include_router(auth_router)
    app.include_router(chat_router)

    # Patch async_session_factory used in chat websocket endpoint
    import apps.football_pool.api.chat as chat_module
    chat_module.async_session_factory = session_factory

    return app, session_factory


def test_websocket_chat_unclaimed(chat_app_and_db):
    app, _ = chat_app_and_db
    client = TestClient(app)

    with client.websocket_connect("/ws/chat") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert data["claimed"] is False

        # Attempt to send message
        websocket.send_text("Hello everyone")
        err = websocket.receive_json()
        assert err["type"] == "error"
        assert "must claim a member profile" in err["message"]


def test_websocket_chat_claimed_and_moderated(chat_app_and_db):
    app, session_factory = chat_app_and_db
    client = TestClient(app)

    # Member ID 1 was created in fixture
    token = create_session_token(1)
    cookies = {settings.session_cookie_name: token}

    with client.websocket_connect("/ws/chat", cookies=cookies) as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert data["claimed"] is True
        assert data["author_name"] == "Matt Dies"

        # Send a message with profanity
        websocket.send_json({"content": "What the shit was that game"})
        msg = websocket.receive_json()
        assert msg["type"] == "chat_message"
        assert msg["author_name"] == "Matt Dies"
        assert "****" in msg["content"]
        assert "shit" not in msg["content"].lower()

    # Verify message was persisted to DB
    import asyncio
    async def verify_db():
        async with session_factory() as session:
            result = await session.execute(select(ChatMessage))
            messages = result.scalars().all()
            assert len(messages) == 1
            assert "****" in messages[0].content

    asyncio.run(verify_db())


def test_chat_history_rest_endpoint(chat_app_and_db):
    app, session_factory = chat_app_and_db
    client = TestClient(app)

    # Seed 2 messages
    import asyncio
    async def seed_msgs():
        async with session_factory() as session:
            session.add(ChatMessage(member_id=1, content="Message 1"))
            session.add(ChatMessage(member_id=1, content="Message 2"))
            await session.commit()

    asyncio.run(seed_msgs())

    response = client.get("/api/chat/history?limit=10")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 2
    assert history[0]["content"] == "Message 1"
    assert history[1]["content"] == "Message 2"
