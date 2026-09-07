"""Tests for chat history, WebSocket broadcasting, and family-friendly moderation."""

import pytest
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

from apps.football_pool.api.auth import router as auth_router
from apps.football_pool.api.chat import router as chat_router
from apps.football_pool.config import settings
from apps.football_pool.database import Base, get_db
from apps.football_pool.models import ChatMessage, Member
from apps.football_pool.services.moderation import censor_message
from apps.football_pool.utils.security import create_session_token


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

    orig_factory = chat_module.async_session_factory
    chat_module.async_session_factory = session_factory

    yield app, session_factory

    chat_module.async_session_factory = orig_factory
    asyncio.run(engine.dispose())


def test_websocket_chat_unclaimed(chat_app_and_db):
    app, _ = chat_app_and_db
    client = TestClient(app)

    with client.websocket_connect("/ws/chat") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "must claim a member profile" in data["message"]


def test_websocket_cswsh_rejected(chat_app_and_db):
    """Verifies that cross-origin WebSocket connection attempts are rejected (CSWSH defense)."""
    app, _ = chat_app_and_db
    client = TestClient(app)
    token = create_session_token(1)
    cookies = {settings.session_cookie_name: token}
    headers = {"origin": "https://malicious-attacker.com"}

    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/chat", cookies=cookies, headers=headers):
            pass


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


def test_websocket_rate_limiting(chat_app_and_db):
    """Verifies that sending messages too quickly triggers rate limiting error."""
    app, _ = chat_app_and_db
    client = TestClient(app)
    token = create_session_token(1)
    cookies = {settings.session_cookie_name: token}

    with client.websocket_connect("/ws/chat", cookies=cookies) as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connected"

        for i in range(5):
            websocket.send_json({"content": f"Message {i}"})
            res = websocket.receive_json()
            assert res["type"] == "chat_message"

        # 6th rapid message should be throttled
        websocket.send_json({"content": "Message 6 flood"})
        err = websocket.receive_json()
        assert err["type"] == "error"
        assert "too quickly" in err["message"]


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

    # Unauthenticated request is rejected with 401
    unauth_response = client.get("/api/chat/history?limit=10")
    assert unauth_response.status_code == 401

    # Authenticated request succeeds
    token = create_session_token(member_id=1)
    client.cookies.set(settings.session_cookie_name, token)
    response = client.get("/api/chat/history?limit=10")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 2
    assert history[0]["content"] == "Message 1"
    assert history[1]["content"] == "Message 2"


def test_post_chat_message_unauthenticated(chat_app_and_db):
    app, _ = chat_app_and_db
    client = TestClient(app)

    response = client.post("/api/chat/messages", json={"content": "Hello unauthenticated"})
    assert response.status_code == 401
    assert "claim" in response.json()["detail"].lower()


def test_post_chat_message_authenticated_and_moderated(chat_app_and_db):
    app, session_factory = chat_app_and_db
    client = TestClient(app)

    token = create_session_token(member_id=1)
    client.cookies.set(settings.session_cookie_name, token)

    response = client.post(
        "/api/chat/messages",
        json={"content": "Holy shit that was a great play!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["member_id"] == 1
    assert data["author_name"] == "Matt Dies"
    assert "****" in data["content"]
    assert "shit" not in data["content"].lower()

    # Verify persisted in database
    import asyncio

    async def verify_persisted():
        async with session_factory() as session:
            result = await session.execute(select(ChatMessage).where(ChatMessage.id == data["id"]))
            msg = result.scalar_one_or_none()
            assert msg is not None
            assert "****" in msg.content

    asyncio.run(verify_persisted())
