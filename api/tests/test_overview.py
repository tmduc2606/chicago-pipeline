from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_overview_returns_kpis(client: AsyncClient, db_session):
    class MockRow:
        total = 57931
        arrest_rate = 25.3
        domestic_pct = 12.1
        delta_pct = -5.2
        prev_total = 50000

    mock_result = MagicMock()
    mock_result.one.return_value = MockRow()
    db_session.execute.return_value = mock_result

    response = await client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "arrest_rate" in data
    assert "domestic_pct" in data
    assert "delta_pct" in data
    assert "prev_total" in data


@pytest.mark.asyncio
async def test_overview_with_dates(client: AsyncClient, db_session):
    mock_result = MagicMock()
    mock_result.one.return_value = type(
        "Row", (), {
            "total": 1000, "arrest_rate": 30.0, "domestic_pct": 15.0,
            "delta_pct": 0.0, "prev_total": 500,
        }
    )()
    db_session.execute.return_value = mock_result

    response = await client.get("/api/overview?from_date=2024-01-01&to_date=2024-03-31")
    assert response.status_code == 200
