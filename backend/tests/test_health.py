import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Verify that GET /health returns 200 OK and vigilX application metadata."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "vigilX"
    assert "version" in data


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    """Verify that GET /ready returns 200 OK and confirms database connectivity."""
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["app_name"] == "vigilX"
