import pytest
import time
import asyncio
from src.backend.services.coingecko import get_current_prices, get_top_coins

# Mark these tests as async
pytestmark = pytest.mark.asyncio

async def test_live_coingecko_retrieval():
    """
    Test 1: Verifies the API connects correctly and retrieves real data.
    Note: We do NOT use the `mock_coingecko` fixture here, so this hits the live API.
    """
    coins = ["bitcoin", "ethereum"]
    
    prices = await get_current_prices(coins)
    
    # Assert we got a dictionary back
    assert isinstance(prices, dict)
    
    # Assert both coins are in the response
    assert "bitcoin" in prices
    assert "ethereum" in prices
    
    # Assert the prices are positive numbers
    assert isinstance(prices["bitcoin"], float)
    assert prices["bitcoin"] > 0.0
    
    assert isinstance(prices["ethereum"], float)
    assert prices["ethereum"] > 0.0

async def test_live_coingecko_speed():
    """
    Test 2: Tests the speed of retrieval for a larger data payload (Top 50 coins).
    """
    start_time = time.perf_counter()
    
    top_coins = await get_top_coins(per_page=50)
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    # Assert we actually got data
    assert isinstance(top_coins, list)
    assert len(top_coins) > 0
    
    # Assert the speed is reasonable (e.g., under 3.0 seconds).
    # You can adjust this threshold based on your network and plan.
    MAX_ALLOWED_SECONDS = 3.0
    assert elapsed_time < MAX_ALLOWED_SECONDS, f"API retrieval was too slow! Took {elapsed_time:.2f} seconds."
    
    print(f"\n[Performance] CoinGecko Top 50 retrieval took {elapsed_time:.2f} seconds.")
