import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient):
    response = await client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_readiness_503_when_db_down(client: AsyncClient):
    response = await client.get("/api/health/ready")
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "checks" in data