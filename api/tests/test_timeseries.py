from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_timeseries_daily(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/timeseries?granularity=daily")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_timeseries_invalid_granularity(client: AsyncClient):
    response = await client.get("/api/timeseries?granularity=hourly")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_forecast(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/timeseries/forecast?horizon=7")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert "forecast" in data


@pytest.mark.asyncio
async def test_anomalies(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/timeseries/anomalies?z=2.0")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_heatmap(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert "matrix" in data
    assert len(data["matrix"]) == 7
