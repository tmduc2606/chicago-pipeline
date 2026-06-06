import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pipeline_status(client: AsyncClient):
    response = await client.get("/api/pipeline/status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_pipeline_runs(client: AsyncClient):
    response = await client.get("/api/pipeline/runs?dag_id=test_dag")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)