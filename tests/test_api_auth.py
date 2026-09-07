"""Tests for member listing and claim-based authentication endpoints."""

import asyncio

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from apps.football_pool.config import settings


@pytest.mark.asyncio
async def test_list_members(async_client: AsyncClient):
    response = await async_client.get("/api/members")
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 37
    assert any(m["first_name"] == "Matt" and m["last_name"] == "Dies" for m in members)


@pytest.mark.asyncio
async def test_claim_and_auth_me_flow(async_client: AsyncClient):
    # 1. Unclaimed check
    me_resp = await async_client.get("/api/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["claimed"] is False

    # 2. Get Matt Dies ID
    members_resp = await async_client.get("/api/members")
    matt = next(m for m in members_resp.json() if m["first_name"] == "Matt" and m["last_name"] == "Dies")

    # 3. Claim profile
    claim_resp = await async_client.post("/api/auth/claim", json={"member_id": matt["id"]})
    assert claim_resp.status_code == 200
    assert claim_resp.json()["full_name"] == "Matt Dies"

    # Verify cookie was set
    assert settings.session_cookie_name in claim_resp.cookies

    # 4. Check /api/auth/me with cookie persisted in client
    me_resp2 = await async_client.get("/api/auth/me")
    assert me_resp2.status_code == 200
    me_data = me_resp2.json()
    assert me_data["claimed"] is True
    assert me_data["member"]["first_name"] == "Matt"

    # 5. Unclaim
    unclaim_resp = await async_client.post("/api/auth/unclaim")
    assert unclaim_resp.status_code == 200
    assert unclaim_resp.json() == {"status": "unclaimed"}


@pytest.mark.asyncio
async def test_claim_invalid_member(async_client: AsyncClient):
    response = await async_client.post("/api/auth/claim", json={"member_id": 99999})
    assert response.status_code == 404


def test_session_token_expiration():
    """Verifies that expired session tokens are rejected by verify_session_token (SEC-07)."""
    from apps.football_pool.utils.security import create_session_token, verify_session_token

    token = create_session_token(member_id=42)
    # Valid with normal expiration
    assert verify_session_token(token, max_age=3600) == 42
    # Expired token rejected
    assert verify_session_token(token, max_age=-1) is None


@pytest.mark.asyncio
async def test_cors_disallows_untrusted_origin(async_client: AsyncClient):
    """Verifies that untrusted origins are not reflected in CORS headers (SEC-01)."""
    response = await async_client.get("/api/members", headers={"Origin": "https://malicious-site.example"})
    assert response.headers.get("access-control-allow-origin") != "https://malicious-site.example"


def test_production_secret_key_enforcement():
    """Verifies that lifespan rejects default insecure secret key in production mode (SEC-03)."""
    from apps.football_pool.main import lifespan

    app = FastAPI(lifespan=lifespan)
    prev_env = settings.env
    prev_key = settings.secret_key
    try:
        settings.env = "production"
        settings.secret_key = "dev-insecure-secret-key-change-in-prod"
        with pytest.raises(RuntimeError) as exc_info:

            async def run_lifespan():
                async with lifespan(app):
                    pass

            asyncio.run(run_lifespan())
        assert "Insecure secret key configured in production" in str(exc_info.value)
    finally:
        settings.env = prev_env
        settings.secret_key = prev_key
