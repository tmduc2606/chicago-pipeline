from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_filters(client: AsyncClient, db_session):
    mock_date = MagicMock()
    mock_date.one.return_value = type("Row", (), {"date_min": "2024-01-01", "date_max": "2024-03-31"})()

    mock_types = MagicMock()
    mock_types.fetchall.return_value = [
        type("Row", (), {"primary_type": "THEFT"}),
        type("Row", (), {"primary_type": "BATTERY"}),
    ]

    mock_districts = MagicMock()
    mock_districts.fetchall.return_value = [
        type("Row", (), {"district": 1}),
        type("Row", (), {"district": 2}),
    ]

    mock_ca = MagicMock()
    mock_ca.fetchall.return_value = [
        type("Row", (), {"community_area": 10}),
        type("Row", (), {"community_area": 20}),
    ]

    db_session.execute.side_effect = [mock_date, mock_types, mock_districts, mock_ca]

    response = await client.get("/api/filters")
    assert response.status_code == 200
    data = response.json()
    assert "date_min" in data
    assert "date_max" in data
    assert "primary_types" in data
    assert "districts" in data
    assert "community_areas" in data
    assert len(data["community_areas"]) == 2
