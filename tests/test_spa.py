import pytest
from httpx import ASGITransport, AsyncClient

from apps.football_pool.main import app


@pytest.mark.asyncio
async def test_spa_root_serves_html():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "<div id=\"root\"></div>" in response.text


@pytest.mark.asyncio
async def test_spa_client_routes_serve_html():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for path in ["/results", "/assignments", "/about"]:
            response = await client.get(path)
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
            assert "<div id=\"root\"></div>" in response.text


@pytest.mark.asyncio
async def test_spa_static_and_assets():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test logos static mount
        response = await client.get("/static/logos/buffalo-bills-logo-transparent.png")
        assert response.status_code == 200
        assert "image/png" in response.headers.get("content-type", "")

        # Test favicon fallback
        fav_response = await client.get("/favicon.ico")
        assert fav_response.status_code == 200


@pytest.mark.asyncio
async def test_api_404_not_intercepted_by_spa():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/does_not_exist")
        assert response.status_code == 404
        assert response.headers.get("content-type", "").startswith("application/json")
