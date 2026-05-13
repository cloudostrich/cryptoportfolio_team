import os
import duckdb

# Resolve DB path relative to project root (this file is at src/backend/db/init_db.py)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_default_db = os.path.join(_PROJECT_ROOT, "data", "portfolio.duckdb")
DB_PATH = os.environ.get("DB_PATH", _default_db)
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(_PROJECT_ROOT, DB_PATH)

def init_db():
    print(f"Initializing DuckDB database at {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            email VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR NOT NULL,
            role VARCHAR DEFAULT 'analyst',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trades (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR,
            coin_id VARCHAR NOT NULL,
            coin_symbol VARCHAR NOT NULL,
            coin_name VARCHAR NOT NULL,
            amount DOUBLE NOT NULL,
            price_usd DOUBLE NOT NULL,
            timestamp DATETIME NOT NULL,
            trade_type VARCHAR NOT NULL CHECK (trade_type IN ('buy', 'sell'))
        );

        CREATE TABLE IF NOT EXISTS theses (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            coin_id VARCHAR NOT NULL,
            coin_symbol VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            content TEXT NOT NULL,
            sentiment VARCHAR NOT NULL CHECK (sentiment IN ('bullish', 'bearish')),
            target_price DOUBLE,
            time_horizon VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS votes (
            thesis_id VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            vote_type INTEGER NOT NULL CHECK (vote_type IN (1, -1)),
            PRIMARY KEY (thesis_id, user_id),
            FOREIGN KEY (thesis_id) REFERENCES theses(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    
    # Check if user_id column exists in trades, if not add it
    columns = conn.execute("PRAGMA table_info('trades')").fetchall()
    column_names = [col[1] for col in columns]
    if 'user_id' not in column_names:
        conn.execute("ALTER TABLE trades ADD COLUMN user_id VARCHAR")
        
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
