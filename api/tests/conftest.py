from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.main import app


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.ping.return_value = True
    return mock


@pytest.fixture
def mock_cursor_result():
    mock = MagicMock()
    mock.fetchall.return_value = []
    mock.one.return_value = MagicMock()
    return mock


@pytest_asyncio.fixture
async def db_session(mock_cursor_result) -> AsyncGenerator[AsyncSession]:
    mock = AsyncMock(spec=AsyncSession)
    mock.execute = AsyncMock(return_value=mock_cursor_result)
    mock.close = AsyncMock()
    yield mock


@pytest_asyncio.fixture
async def client(db_session, mock_redis) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_redis] = lambda: mock_redis
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
