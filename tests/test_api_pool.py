"""Tests for pool assignments, seasons, standings, and pot endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_seasons(async_client: AsyncClient):
    resp = await async_client.get("/api/pool/seasons")
    assert resp.status_code == 200
    data = resp.json()
    assert "current_season" in data
    assert 2024 in data["tracked_seasons"]
    assert 2025 in data["tracked_seasons"]


@pytest.mark.asyncio
async def test_get_pot(async_client: AsyncClient):
    resp = await async_client.get("/api/pool/pot?season_year=2025")
    assert resp.status_code == 200
    data = resp.json()
    assert data["season_year"] == 2025
    assert data["amount"] == 10


@pytest.mark.asyncio
async def test_get_assignments(async_client: AsyncClient):
    # 2024 has 29 assignments
    resp_2024 = await async_client.get("/api/pool/assignments?season_year=2024")
    assert resp_2024.status_code == 200
    assignments_2024 = resp_2024.json()
    assert len(assignments_2024) == 29

    # 2025 has 31 assignments
    resp_2025 = await async_client.get("/api/pool/assignments?season_year=2025")
    assert resp_2025.status_code == 200
    assignments_2025 = resp_2025.json()
    assert len(assignments_2025) == 31


@pytest.mark.asyncio
async def test_get_results_standings(async_client: AsyncClient):
    resp = await async_client.get("/api/pool/results?season_year=2025")
    assert resp.status_code == 200
    data = resp.json()
    assert data["season_year"] == 2025
    assert "standings" in data
    assert len(data["standings"]) == 31
    # Check that each standing item has member, team, and total_winnings
    first = data["standings"][0]
    assert "member" in first
    assert "team" in first
    assert "total_winnings" in first
