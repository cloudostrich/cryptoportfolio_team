from fastapi import APIRouter, HTTPException, Depends
from typing import List, Annotated
from ..models.schemas import TradeCreate, TradeResponse, PortfolioSummary
from ..db import queries
from ..services import portfolio
from .auth import get_current_user

router = APIRouter(prefix="/api", tags=["portfolio"])

MAX_COINS_PER_MEMBER = 5

@router.get("/trades", response_model=List[TradeResponse])
def get_trades(current_user: Annotated[dict, Depends(get_current_user)]):
    trades = queries.get_all_trades(user_id=current_user["id"])
    return trades

@router.post("/trades", response_model=TradeResponse)
def add_trade(trade: TradeCreate, current_user: Annotated[dict, Depends(get_current_user)]):
    # Enforce coin limit: check if this is a NEW coin for this user
    if trade.trade_type == 'buy':
        user_trades = queries.get_all_trades(user_id=current_user["id"])
        existing_coins = set()
        coin_balances = {}
        for t in user_trades:
            cid = t['coin_id']
            coin_balances.setdefault(cid, 0.0)
            if t['trade_type'] == 'buy':
                coin_balances[cid] += t['amount']
            else:
                coin_balances[cid] -= t['amount']
        existing_coins = {cid for cid, bal in coin_balances.items() if bal > 0.000001}
        
        if trade.coin_id not in existing_coins and len(existing_coins) >= MAX_COINS_PER_MEMBER:
            raise HTTPException(
                status_code=400, 
                detail=f"You can hold a maximum of {MAX_COINS_PER_MEMBER} different coins. Remove a coin before adding a new one."
            )
    
    try:
        new_trade = queries.add_trade(
            user_id=current_user["id"],
            coin_id=trade.coin_id,
            coin_symbol=trade.coin_symbol,
            coin_name=trade.coin_name,
            amount=trade.amount,
            price_usd=trade.price_usd,
            trade_type=trade.trade_type
        )
        return new_trade
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/trades/{trade_id}")
def delete_trade(trade_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    success = queries.delete_trade(trade_id, user_id=current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Trade not found or unauthorized")
    return {"status": "success"}

@router.delete("/portfolio/coin/{coin_id}")
def delete_coin(coin_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        queries.delete_all_coin_trades(coin_id, user_id=current_user["id"])
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Individual summary (for current user) ──────────────────────────────────

@router.get("/portfolio/summary", response_model=PortfolioSummary)
async def get_summary(current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        return await portfolio.get_portfolio_summary(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/chart")
async def get_portfolio_chart(current_user: Annotated[dict, Depends(get_current_user)], days: int = 365):
    try:
        return await portfolio.get_portfolio_history(days, user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Team endpoints ─────────────────────────────────────────────────────────

@router.get("/team/summary")
async def get_team_summary(current_user: Annotated[dict, Depends(get_current_user)]):
    """Overall team portfolio summary (all members combined)."""
    try:
        return await portfolio.get_team_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/members")
async def get_team_members(current_user: Annotated[dict, Depends(get_current_user)]):
    """Per-member performance data for the bar chart."""
    try:
        return await portfolio.get_team_members_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/allocation")
async def get_team_allocation(current_user: Annotated[dict, Depends(get_current_user)]):
    """Per-member allocation breakdown for the doughnut chart."""
    try:
        return await portfolio.get_team_allocation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/chart")
async def get_team_chart(current_user: Annotated[dict, Depends(get_current_user)], days: int = 365):
    """Team + per-member portfolio history for line charts."""
    try:
        return await portfolio.get_team_history(days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/holdings")
async def get_team_holdings(current_user: Annotated[dict, Depends(get_current_user)]):
    """All members' holdings with trader name attached."""
    try:
        return await portfolio.get_team_holdings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/trades")
def get_team_trades(current_user: Annotated[dict, Depends(get_current_user)]):
    """All team trades with trader name attached."""
    try:
        return queries.get_team_trades()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
