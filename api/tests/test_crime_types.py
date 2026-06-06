from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crime_types_top(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/crime-types/top?limit=5")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crime_type_trend(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/crime-types/trend?type=THEFT")
    assert response.status_code == 200
