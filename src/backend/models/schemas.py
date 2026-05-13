from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class TradeCreate(BaseModel):
    coin_id: str
    coin_symbol: str
    coin_name: str
    amount: float
    price_usd: float
    trade_type: str

class TradeResponse(BaseModel):
    id: str
    user_id: Optional[str]
    coin_id: str
    coin_symbol: str
    coin_name: str
    amount: float
    price_usd: float
    timestamp: datetime
    trade_type: str
    model_config = ConfigDict(from_attributes=True)

class ThesisCreate(BaseModel):
    coin_id: str
    coin_symbol: str
    title: str
    content: str
    sentiment: str
    target_price: Optional[float] = None
    time_horizon: Optional[str] = None

class ThesisResponse(BaseModel):
    id: str
    user_id: str
    username: Optional[str] = None
    coin_id: str
    coin_symbol: str
    title: str
    content: str
    sentiment: str
    target_price: Optional[float]
    time_horizon: Optional[str]
    created_at: datetime
    votes_count: int = 0
    user_vote: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class VoteRequest(BaseModel):
    vote_type: int # 1 for agree, -1 for disagree

class Holding(BaseModel):
    coin_id: str
    coin_symbol: str
    coin_name: str
    total_amount: float
    total_cost_usd: float
    average_buy_price: float
    current_price_usd: float
    current_value_usd: float
    pnl_usd: float
    pnl_percentage: float

class PortfolioSummary(BaseModel):
    total_value_usd: float
    total_cost_usd: float
    total_pnl_usd: float
    total_pnl_percentage: float
    holdings: List[Holding]

class MarketCoin(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: float
    price_change_percentage_24h: float
