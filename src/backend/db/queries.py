import os
import uuid
from datetime import datetime, timezone
import duckdb
from typing import Optional, List

# Resolve DB path relative to project root (this file is at src/backend/db/queries.py)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_default_db = os.path.join(_PROJECT_ROOT, "data", "portfolio.duckdb")
DB_PATH = os.environ.get("DB_PATH", _default_db)
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(_PROJECT_ROOT, DB_PATH)

def get_connection():
    return duckdb.connect(DB_PATH, read_only=False)

def get_read_connection():
    return duckdb.connect(DB_PATH, read_only=True)

# ─── User Queries ────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str, role: str = 'analyst') -> dict:
    user_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (id, username, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, email, password_hash, role))
        result = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        columns = [col[0] for col in conn.description]
        return dict(zip(columns, result))

def get_user_by_username(username: str) -> Optional[dict]:
    with get_read_connection() as conn:
        result = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not result:
            return None
        columns = [col[0] for col in conn.description]
        return dict(zip(columns, result))

def get_user_by_id(user_id: str) -> Optional[dict]:
    with get_read_connection() as conn:
        result = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not result:
            return None
        columns = [col[0] for col in conn.description]
        return dict(zip(columns, result))

def get_all_users() -> List[dict]:
    with get_read_connection() as conn:
        result = conn.execute("SELECT id, username, email, role, created_at FROM users ORDER BY created_at").fetchall()
        columns = [col[0] for col in conn.description]
        return [dict(zip(columns, row)) for row in result]

# ─── Trade Queries ───────────────────────────────────────────────────────────

def count_user_coins(user_id: str) -> int:
    """Count the number of distinct coins a user currently holds (with positive balance)."""
    with get_read_connection() as conn:
        result = conn.execute("""
            SELECT COUNT(DISTINCT coin_id) FROM (
                SELECT coin_id,
                       SUM(CASE WHEN trade_type='buy' THEN amount ELSE -amount END) as balance
                FROM trades
                WHERE user_id = ?
                GROUP BY coin_id
                HAVING balance > 0.000001
            )
        """, (user_id,)).fetchone()
        return result[0] if result else 0

def add_trade(user_id: str, coin_id: str, coin_symbol: str, coin_name: str, amount: float, price_usd: float, trade_type: str) -> dict:
    trade_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc)
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO trades (id, user_id, coin_id, coin_symbol, coin_name, amount, price_usd, timestamp, trade_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (trade_id, user_id, coin_id, coin_symbol, coin_name, amount, price_usd, timestamp, trade_type))
        
        result = conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
        columns = [col[0] for col in conn.description]
    return dict(zip(columns, result))

def get_all_trades(user_id: Optional[str] = None):
    with get_read_connection() as conn:
        if user_id:
            result = conn.execute("SELECT * FROM trades WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
        else:
            result = conn.execute("SELECT * FROM trades ORDER BY timestamp DESC").fetchall()
        columns = [col[0] for col in conn.description]
        return [dict(zip(columns, row)) for row in result]

def get_team_trades():
    """Get all trades from all users, with username attached."""
    with get_read_connection() as conn:
        result = conn.execute("""
            SELECT t.*, u.username
            FROM trades t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.timestamp DESC
        """).fetchall()
        columns = [col[0] for col in conn.description]
        return [dict(zip(columns, row)) for row in result]

def delete_trade(trade_id: str, user_id: str) -> bool:
    with get_connection() as conn:
        # Check ownership
        owner = conn.execute("SELECT user_id FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if not owner or owner[0] != user_id:
            return False
        conn.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
        return True

def delete_all_coin_trades(coin_id: str, user_id: str) -> bool:
    with get_connection() as conn:
        conn.execute("DELETE FROM trades WHERE coin_id = ? AND user_id = ?", (coin_id, user_id))
        return True
