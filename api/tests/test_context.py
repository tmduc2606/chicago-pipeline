from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_domestic_split(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.one.return_value = type("Row", (), {"true_count": 100, "false_count": 900})()
    db_session.execute.return_value = mock_result

    response = await client.get("/api/context/domestic")
    assert response.status_code == 200
    data = response.json()
    assert "true_count" in data
    assert "false_count" in data


@pytest.mark.asyncio
async def test_top_locations(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/context/location")
    assert response.status_code == 200
