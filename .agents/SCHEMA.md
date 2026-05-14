# DuckDB Schema (Multi-User Dashboard)

This project uses DuckDB to store all user and portfolio data. Because this is a **multi-user/team collaborative platform**, all queries must respect tenant isolation (filtering by `user_id`).

## 1. users
Stores registered users.
- `id` (VARCHAR PRIMARY KEY)
- `username` (VARCHAR UNIQUE)
- `email` (VARCHAR UNIQUE)
- `password_hash` (VARCHAR)
- `role` (VARCHAR) - Default 'analyst'
- `created_at` (DATETIME)

## 2. trades
Stores all buy/sell trades for the team. 
**CRITICAL**: Always scope queries by `user_id` when fetching personal holdings, or aggregate by coin for team-wide views.
- `id` (VARCHAR PRIMARY KEY)
- `user_id` (VARCHAR) - Foreign Key to users
- `coin_id` (VARCHAR) - CoinGecko ID
- `coin_symbol` (VARCHAR)
- `coin_name` (VARCHAR)
- `amount` (DOUBLE)
- `price_usd` (DOUBLE)
- `timestamp` (DATETIME)
- `trade_type` (VARCHAR) - 'buy' or 'sell'

## 3. theses
Stores user-written investment theses for specific coins.
- `id` (VARCHAR PRIMARY KEY)
- `user_id` (VARCHAR)
- `coin_id` (VARCHAR)
- `coin_symbol` (VARCHAR)
- `title` (VARCHAR)
- `content` (TEXT)
- `sentiment` (VARCHAR) - 'bullish' or 'bearish'
- `target_price` (DOUBLE)
- `time_horizon` (VARCHAR)
- `created_at` (DATETIME)

## 4. votes
Stores up/down votes on theses by users.
- `thesis_id` (VARCHAR)
- `user_id` (VARCHAR)
- `vote_type` (INTEGER) - 1 or -1
- PRIMARY KEY (thesis_id, user_id)
