import os
import tempfile
import pytest
from unittest.mock import AsyncMock, patch

# Important: We must set DB_PATH before importing any backend modules
# so that the duckdb connection points to our temporary test database.
temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".duckdb")
os.close(temp_db_fd)
os.remove(temp_db_path)
os.environ["DB_PATH"] = temp_db_path

from src.backend.main import app
from fastapi.testclient import TestClient
from src.backend.db.init_db import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes the database schema before any tests run, and cleans up after."""
    init_db()
    yield
    # Cleanup after all tests
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

@pytest.fixture
def client():
    """Returns a FastAPI TestClient."""
    return TestClient(app)

@pytest.fixture
def mock_coingecko():
    """Mocks the coingecko service client to avoid live API calls."""
    with patch("src.backend.services.coingecko.client") as mock_client:
        
        # Setup common mock responses
        mock_client.simple.price.get = AsyncMock(return_value={"bitcoin": {"usd": 50000.0}})
        mock_client.coins.market_chart.get = AsyncMock(return_value={"prices": [[1600000000, 45000], [1600086400, 50000]]})
        mock_client.search.get = AsyncMock(return_value={"coins": [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]})
        mock_client.coins.markets.get = AsyncMock(return_value=[{"id": "bitcoin", "symbol": "btc", "current_price": 50000}])
        
        yield mock_client

@pytest.fixture
def auth_user():
    """Creates a mock user and returns the user details."""
    from src.backend.db.queries import create_user
    import uuid
    random_id = str(uuid.uuid4())[:8]
    user = create_user(f"testuser_{random_id}", f"test_{random_id}@test.com", "fakehash")
    return user

@pytest.fixture
def auth_client(client, auth_user):
    """Returns a client logged in as the auth_user."""
    from src.backend.routes.auth import get_current_user
    
    def override_get_current_user():
        return auth_user
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()
