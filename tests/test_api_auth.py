"""Tests for member listing and claim-based authentication endpoints."""

import pytest
from httpx import AsyncClient

from apps.football_pool.config import settings


@pytest.mark.asyncio
async def test_list_members(async_client: AsyncClient):
    response = await async_client.get("/api/members")
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 31
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
