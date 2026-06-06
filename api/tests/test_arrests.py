from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_arrests_by_district(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/arrests/by-district")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_arrests_by_type(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    db_session.execute.return_value = mock_result
    response = await client.get("/api/arrests/by-type")
    assert response.status_code == 200
