import pytest

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_me(auth_client, auth_user):
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == auth_user["username"]
    assert data["email"] == auth_user["email"]

def test_add_and_get_trade(auth_client, auth_user):
    trade_data = {
        "coin_id": "bitcoin",
        "coin_symbol": "btc",
        "coin_name": "Bitcoin",
        "amount": 1.5,
        "price_usd": 50000.0,
        "trade_type": "buy"
    }
    
    # 1. Add Trade
    response = auth_client.post("/api/trades", json=trade_data)
    assert response.status_code == 200
    data = response.json()
    assert data["coin_id"] == "bitcoin"
    assert data["amount"] == 1.5
    trade_id = data["id"]
    
    # 2. Get Trades
    response = auth_client.get("/api/trades")
    assert response.status_code == 200
    trades = response.json()
    assert len(trades) == 1
    assert trades[0]["id"] == trade_id

def test_tenant_isolation_delete(client, auth_user):
    # Setup two users
    from src.backend.db.queries import create_user, add_trade
    user2 = create_user("user2", "user2@test.com", "hash")
    
    # User 1 (auth_user) creates a trade
    trade = add_trade(
        user_id=auth_user["id"],
        coin_id="ethereum",
        coin_symbol="eth",
        coin_name="Ethereum",
        amount=10,
        price_usd=2000.0,
        trade_type="buy"
    )
    
    # Mock auth to act as user2
    from src.backend.routes.auth import get_current_user
    from src.backend.main import app
    
    def override_get_current_user():
        return {"id": user2["id"], "username": user2["username"]}
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # User 2 tries to delete User 1's trade
    response = client.delete(f"/api/trades/{trade['id']}")
    
    # Should be 404 Not Found / Unauthorized because user2 doesn't own it
    assert response.status_code == 404
    
    app.dependency_overrides.clear()
