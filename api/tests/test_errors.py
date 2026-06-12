"""H15 — Error-path tests for all 422 validation responses."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_timeseries_invalid_granularity(client: AsyncClient):
    response = await client.get("/api/timeseries?granularity=hourly")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_timeseries_valid_weekly(client: AsyncClient, db_session):
    mock = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()
    mock.fetchall.return_value = []
    db_session.execute.return_value = mock
    response = await client.get("/api/timeseries?granularity=weekly")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_timeseries_valid_monthly(client: AsyncClient, db_session):
    mock = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()
    mock.fetchall.return_value = []
    db_session.execute.return_value = mock
    response = await client.get("/api/timeseries?granularity=monthly")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_forecast_horizon_zero(client: AsyncClient):
    response = await client.get("/api/timeseries/forecast?horizon=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_forecast_horizon_over_60(client: AsyncClient):
    response = await client.get("/api/timeseries/forecast?horizon=61")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_forecast_horizon_one(client: AsyncClient, db_session):
    mock = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()
    mock.fetchall.return_value = []
    db_session.execute.return_value = mock
    response = await client.get("/api/timeseries/forecast?horizon=1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crime_types_top_limit_zero(client: AsyncClient):
    response = await client.get("/api/crime-types/top?limit=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_crime_types_top_limit_over_50(client: AsyncClient):
    response = await client.get("/api/crime-types/top?limit=51")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_crime_type_trend_missing_type(client: AsyncClient):
    response = await client.get("/api/crime-types/trend")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_choropleth_invalid_level(client: AsyncClient):
    response = await client.get("/api/geo/choropleth?level=city")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_choropleth_invalid_metric(client: AsyncClient):
    response = await client.get("/api/geo/choropleth?metric=density")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pipeline_runs_missing_dag_id(client: AsyncClient):
    response = await client.get("/api/pipeline/runs")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pipeline_runs_limit_zero(client: AsyncClient):
    response = await client.get("/api/pipeline/runs?dag_id=test&limit=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pipeline_runs_limit_over_100(client: AsyncClient):
    response = await client.get("/api/pipeline/runs?dag_id=test&limit=101")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_live_returns_200(client: AsyncClient):
    response = await client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_ready_returns_200_or_503(client: AsyncClient):
    response = await client.get("/api/health/ready")
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_health_returns_200_or_503(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_overview_no_params(client: AsyncClient, db_session):
    mock = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()
    mock.one.return_value = type("Row", (), {"total": 100, "arrest_rate": 25.0, "domestic_pct": 12.0, "delta_pct": 0.0, "prev_total": 50})()
    db_session.execute.return_value = mock
    response = await client.get("/api/overview")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_overview_invalid_date_format(client: AsyncClient):
    response = await client.get("/api/overview?from_date=not-a-date")
    assert response.status_code == 200
