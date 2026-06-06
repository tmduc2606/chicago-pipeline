from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_geo_clusters(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/geo/clusters")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_choropleth(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/geo/choropleth?level=district&metric=count")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_choropleth_invalid_level(client: AsyncClient):
    response = await client.get("/api/geo/choropleth?level=city")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_choropleth_invalid_metric(client: AsyncClient):
    response = await client.get("/api/geo/choropleth?metric=density")
    assert response.status_code == 422
